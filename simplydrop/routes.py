#!venv/bin/python
# -*- coding: utf-8 -*-

__author__ = "Alvaro Lopez Alvarez"
__copyright__ = "2019 Tible Technologies"

__link__ = "https://tibletech.com/es"
__version__ = 1.0

# -------------------------run.py---------------------------------
# Fichero con script principal de la aplicación Flask.
# Se crea la app y se definen los métodos de atención a las peticiones.
# Estas peticiones vendrán a través de GET o POST.
# ---------------------------------------------------------------------


import json
from datetime import datetime, timedelta
from random import randint

import shopify

from flask import render_template, request, \
    redirect, Response, session, jsonify
from sqlalchemy import or_

import simplydrop.json_schemas
from simplydrop import Cfg
from simplydrop import app
from simplydrop import db
from simplydrop import shopify_api_connect
from simplydrop.models.items import Items
from simplydrop.models.orders import Orders
from simplydrop.models.shop import Shop
from simplydrop.models.user import User
from simplydrop.notifier.send_telegram_message import \
    telegram_bot_send_welkome, telegram_bot_send_user_hello, \
    telegram_bot_send_user_help

from simplydrop.scheduled_tasks import daily_summary,weekly_summary, monthly_summary

# Declaramos los permisos a los que necesitamos acceder de la tienda Shopify
scope = Cfg.scope
redirect_uri = Cfg.SHOPIFY_CONFIG["REDIRECT_URI"]

shopify.Session.setup(
    api_key=Cfg.SHOPIFY_CONFIG["API_KEY"],
    secret=Cfg.SHOPIFY_CONFIG["API_SECRET"])

# ----------------- FIN INICIO DE VARIABLES Y APP ----------------

# ----------------- CADUCIDAD DEL TOKEN DE SESSION ----------------

# ponemos un límite de sesión de 5 minutos para evitar riesgo de seguridad
# en ordenadores públicos. Obliga a entrar a la app a través de shopify
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=150)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# ----------------- FIN CADUCIDAD DEL TOKEN DE SESSION -------------

# ----------------- ATENCION INSTALACION APP  -------------
# Funciones que atienden las peticiones de instalacion de la app
# en Shopify
# ------------------------------------------------------------

# Función lanzada en la instalacion o lanzamiento de la app desde el panel de
# control de shopify
@app.route('/install', methods=['GET'])
def install_app_tienda():
    try:
        # Comprobamos si la petición de instalación contiene el campo shop
        if request.args.get('shop'):
            shop_url = request.args.get('shop')
            session['shop_url'] = shop_url

        else:
            return render_template('404.html')

        # si esta la tienda en la bbdd y esta activa, no la instalamos otra vez
        shop = Shop.query.filter(Shop.url == shop_url,
                                 Shop.shop_status == 1).all()
        if not shop:

            # Usamos la API de Shopify - Python para configurar la sesión
            # Construimos la url de autenticación y redirigimos a connect
            shopify_session = shopify.Session(shop_url, '2019-04')
            permission_url = shopify_session.create_permission_url(scope,
                                                                   redirect_uri)
            return redirect(permission_url)

        else:
            return redirect('index')

    except shopify.session.ValidationException:
        return render_template('404.html')


# Evento lanzado después de la instalación de la app para conectar la tienda
@app.route('/connect', methods=['GET'])
def connect_app_shop():
    try:
        # Guardamos el token de autenticación devuelto por Shopify
        # y la url de la tienda en la sesión de Flask
        shop_url = request.args.get("shop")
        token = shopify.Session(shop_url, '2019-04').request_token(
            request.args)

        session['shop_url'] = shop_url

        # Sacamos la información que nos falta para
        # insertar en tabla Shop (email del propietario)
        shop_info = shopify_api_connect.post_and_req.obtain_shop_info(shop_url,
                                                                      token)

        # Lanzamos eventos de suscripción a webhooks necesarios
        shopify_api_connect.post_and_req. \
            register_webhook_order_create(shop_url, token)

        shopify_api_connect.post_and_req. \
            register_webhook_shop_uninstalled(shop_url, token)

        billing_id = shopify_api_connect. \
            post_and_req.implement_recurrent_change(shop_url, token)

        # Insertamos Tienda
        new_shop = Shop(url=shop_url, token=token, shop_name=shop_info[0],
                        owner_email=shop_info[1], owner_phone=shop_info[2],
                        shop_status=True,
                        carrier_json=json.dumps(
                            simplydrop.json_schemas.carriers),
                        billing_id=billing_id, currency=shop_info[3])

        db.session.add(new_shop)
        db.session.commit()

        # Renderizamos el index
        return redirect('index')

    except shopify.session.ValidationException:
        return render_template('404.html')


# ----------------- ATENCIÓN A WEBHOOKS  -------------
# Funciones que atienden los eventos de la app
# ------------------------------------------------------------

# Función de escucha de webhooks shopify
@app.route('/webhooks', methods=['POST'])
def listener_webhooks_shop():
    print("llego un shopywebhook")
    return shopify_api_connect.webhooks_dispatcher.webhook_dispatcher(request)


@app.route('/telegram-webhooks', methods=['POST'])
def listener_telegram_webhooks():
    print("llego un telewebhook")
    webhook_data = json.loads(request.data)
    telegram_bot_code = webhook_data["message"]["text"]
    telegram_chat_id = webhook_data["message"]["chat"]["id"]

    user = User.query.filter(or_(User.telegram_bot_code == telegram_bot_code,
                                 User.telegram_chat_id == telegram_chat_id)).all()

    if not user:
        telegram_bot_send_welkome(telegram_chat_id)
        return Response(status=200)

    # mira que es difícil que dos usuario tengan el mismo numero aletario entre
    # 0 y 1.000.000 pero me curo en salud por si mando cosas de otra tienda
    # a otro tio:
    elif len(user) > 1:
        return Response(status=200)

    # si hay usuario pero no hay asignado todavía nigun chat, se le asigna
    elif not user[0].telegram_chat_id:
        user[0].telegram_chat_id = telegram_chat_id
        db.session.commit()
        telegram_bot_send_user_hello(telegram_chat_id, user[0])
        return Response(status=200)

    # si el usuario ya tiene chat asignado y sigue jugando a mandar mensajes
    # se le dice que ya será notifcado cuando ocurra algo
    else:
        telegram_bot_send_user_help(telegram_chat_id, user[0])

    return Response(status=200)


# ----------------- FIN ATENCION INSTALACION APP  -------------


# ----------------- ATENCION AL PANEL DE CONTROL  -------------
# Funciones que atienden las peticiones de la navegacion por el panel
# de control
# --------------------------------------------------------------------
@app.route('/notify-manager')
def notify_manager():
    try:
        shop_url = session['shop_url']
        return render_template('notify-manager.html')

    except KeyError:
        return render_template('session-expired.html')


@app.route('/carrier-manager')
def carrier_manager():
    try:
        shop_url = session['shop_url']
        shop = Shop.query.filter(Shop.url == shop_url,
                                 Shop.shop_status == 1).first()
        carrier_json = json.loads(shop.carrier_json)

        print(json.dumps(carrier_json, indent=4, sort_keys=True))

        mrw_state = carrier_json['mrw']['state']
        mrw_user_hint = carrier_json['mrw']['user']
        cod_fran_hint = carrier_json['mrw']['codFran']
        cod_abon_hint = carrier_json['mrw']['codAbon']
        cod_depa_hint = carrier_json['mrw']['codDepa']
        mrw_password = "Password"

        if not (mrw_user_hint and cod_fran_hint and
                cod_abon_hint and cod_depa_hint and mrw_password):
            mrw_user_hint = "User"
            cod_fran_hint = "Franquicia"
            cod_abon_hint = "Abonado"
            cod_depa_hint = "Departamento"
            mrw_password = "Password"

        if mrw_state:
            check_mrw_state = 1
        else:
            check_mrw_state = 0

        return render_template('carrier-manager.html',
                               mrwUserHint=mrw_user_hint,
                               codFranHint=cod_fran_hint,
                               codAbonHint=cod_abon_hint,
                               codDepaHint=cod_depa_hint,
                               check_mrw_state=check_mrw_state,
                               mrwpassword=mrw_password)

    except KeyError:
        return render_template('session-expired.html')


@app.route('/index')
def index():
    try:

        shop_url = session['shop_url']

        # para obtener el mes pasado vamos al primer dia del mes actual,
        # usamos timedelta para restar un dia y volvernos al mes anterior
        # y con strftime("%Y%m") nos quitamos los dias dejando mes y año
        # ej: 201901
        today = datetime.today().replace(
            hour=00, minute=00, second=00, microsecond=00)

        first_of_this_month = today.replace(day=1)

        first_of_last_month = (first_of_this_month -
                               timedelta(days=1)).replace(day=1)

        first_of_the_year = today.replace(month=1, day=1)

        shop = Shop.query.filter(Shop.url == shop_url,
                                 Shop.shop_status == 1).first()

        orders_last_month_array = Orders.query.filter(
            Orders.shop_id == shop.id,
            Orders.added_on > first_of_last_month,
            Orders.added_on < first_of_this_month).all()

        orders_this_month_array = Orders.query.filter(
            Orders.shop_id == shop.id,
            Orders.added_on > first_of_this_month,
            Orders.added_on <= datetime.today()).all()

        orders_this_year_array = Orders.query.filter(
            Orders.shop_id == shop.id,
            Orders.added_on > first_of_the_year,
            Orders.added_on <= datetime.today()).all()

        orders_this_month = len(orders_this_month_array)

        earning_this_month = sum(float(order.total_amount) for order in
                                 orders_this_month_array)

        earning_last_month = sum(float(order.total_amount) for order in
                                 orders_last_month_array)

        earning_this_year = sum(float(order.total_amount) for order in
                                orders_this_year_array)

        try:
            compare_month_percent = earning_this_month * 100 / earning_last_month

        except ZeroDivisionError:
            compare_month_percent = 0

        return render_template('index.html',
                               earning_this_month=(str(
                                   earning_this_month) + " " + shop.currency),
                               earning_this_year=str(
                                   earning_this_year) + " " + shop.currency,
                               compare_month_percent=str(
                                   int(compare_month_percent)),
                               orders_this_month=orders_this_month,
                               currency=shop.currency)

    except KeyError:
        return render_template('session-expired.html')


@app.route('/shop')
def shop_return():
    try:
        shop_url = session['shop_url']
        return redirect("https://" + shop_url + "/admin/apps")

    except KeyError:
        return render_template('session-expired.html')


@app.route('/bot')
def bot_return():
    return redirect("http://t.me/SimplyDropBot", code=302)


# ----------------- FIN ATENCIÓN PANEL DE CONTROL  -------------


# ----------------- FUNCIONES ATENCIÓN FORMULARIOS -------------
# Funciones que atienden las peticiones de los formularios
# --------------------------------------------------------------

@app.route('/user-form', methods=['POST'])
def user_form():
    try:
        shop_url = session['shop_url']
        shop = Shop.query.filter(Shop.url == shop_url,
                                 Shop.shop_status == 1).first()

        name = request.form["Name"]
        last_name = request.form["LastName"]
        email = request.form["Email"]
        notify_type = request.form["NotifyType"]

        if notify_type is "After each order" or "Daily summary" or "Monthly summary" or "Monthly summary":

            new_user = User(name=name, last_name=last_name, email=email,
                            notify_freq=notify_type, shop_id=shop.id,
                            telegram_bot_code=randint(0, 10000000),
                            telegram_chat_id="")

            db.session.add(new_user)
            db.session.commit()

        return redirect('notify-manager')

    except KeyError:
        return render_template('404.html')


@app.route('/mrw-form', methods=['POST'])
def mrw_form():
    try:
        session['shop_url']
        user = request.form["mrwUser"]
        password = request.form["mrwPassword"]
        codFran = request.form["codFran"]
        codAbon = request.form["codAbon"]
        codDepa = request.form["codDepa"]

        shop_url = session['shop_url']
        shop = Shop.query.filter(Shop.url == shop_url,
                                 Shop.shop_status == 1).first()
        carrier_json = json.loads(shop.carrier_json)

        carrier_json['mrw']['user'] = user
        carrier_json['mrw']['password'] = password
        carrier_json['mrw']['codFran'] = codFran
        carrier_json['mrw']['codAbon'] = codAbon
        carrier_json['mrw']['codDepa'] = codDepa

        shop.carrier_json = json.dumps(carrier_json)
        db.session.commit()

        return redirect('carrier-manager')
    except KeyError:
        return render_template('404.html')


# ------------ FIN FUNCIONES ATENCIÓN FORMULARIOS  -------------


# ----------------- FUNCIONES ATENCIÓN BOTONES -------------
# Funciones que atienden las peticiones de los botones
# --------------------------------------------------------------

@app.route('/user-delete', methods=['POST'])
def user_delete():
    try:
        shop_url = session['shop_url']
        shop = Shop.query.filter(Shop.url == shop_url,
                                 Shop.shop_status == 1).first()
        users = User.query.filter(User.shop_id == shop.id).all()

        email = request.form["Email"]
        name = request.form["Name"]

        for user in users:
            if user.name == name and user.email == email:
                db.session.delete(user)
                db.session.commit()

        return redirect('notify-manager')

    except KeyError:
        return render_template('404.html')


@app.route('/user-freq-change', methods=['POST'])
def user_freq_change():
    try:
        shop_url = session['shop_url']
        shop = Shop.query.filter(Shop.url == shop_url,
                                 Shop.shop_status == 1).first()
        users = User.query.filter(User.shop_id == shop.id).all()

        email = request.form["Email"]
        new_freq = request.form["NewFreq"]

        if not (
                new_freq == "After each order" or new_freq == "Daily summary" or
                new_freq == "Weekly summary" or new_freq == "Monthly summary"):
            return redirect('notify-manager')

        for user in users:
            if user.email == email:
                user.notify_freq = new_freq
                db.session.commit()

        return redirect('notify-manager')

    except KeyError:
        return render_template('404.html')


@app.route('/download-label', methods=['POST'])
def download_label():
    # TODO
    return


@app.route('/checkbox-button-carrier', methods=['POST'])
def checkbox_button_carrier():
    try:
        shop_url = session['shop_url']
        shop = Shop.query.filter(Shop.url == shop_url,
                                 Shop.shop_status == 1).first()
        carrier_json = json.loads(shop.carrier_json)

        mrw_user_hint = carrier_json['mrw']['user']
        cod_fran_hint = carrier_json['mrw']['codFran']
        cod_abon_hint = carrier_json['mrw']['codAbon']
        cod_depa_hint = carrier_json['mrw']['codDepa']
        mrw_password = carrier_json['mrw']['password']

        if request.form["State"] == "on" and mrw_user_hint \
                and cod_fran_hint and cod_abon_hint and \
                cod_depa_hint and mrw_password:
            carrier_json['mrw']['state'] = True
        else:
            carrier_json['mrw']['state'] = False

        shop.carrier_json = json.dumps(carrier_json)
        db.session.commit()

        return redirect('carrier-manager')

    except KeyError:
        return render_template('404.html')


# ------------ FIN FUNCIONES ATENCIÓN FORMULARIOS  -------------


# ----------------- CARGA DE TABLAS DINÁMICAS  -------------
# Funciones que atienden las peticiones de la navegación por el panel
# de control
# --------------------------------------------------------------------
@app.route('/tableDataOrders')
def table_data_orders():
    try:
        shop_url = session['shop_url']

        data2 = []
        shop = Shop.query.filter(Shop.url == shop_url,
                                 Shop.shop_status == 1).first()
        items = Items.query.filter(Items.shop_id == shop.id).all()
        orders = Orders.query.filter(Orders.shop_id == shop.id).all()

        for order in orders:
            items_array = []
            for item in items:
                if item.order_number == order.shopify_order_number:
                    a = {
                        "sku": item.sku,
                        "quantity": item.quantity,
                        "title": item.title,
                        "price": item.price,
                        "weigth": item.weigth,
                        "image": item.image

                    }

                    items_array.append(a)
            order = {
                "Id": order.shopify_order_number,
                "Amount": order.total_amount,
                "Country": order.customer_country,
                "Email": order.customer_email,
                "Carrier": order.carrier,
                "Type": order.shipping_type,
                "State": order.order_status,
                "Currency": order.currency,
                "Items": items_array,
                "Label": order.label,
                "Customer_country_code": order.customer_country_code.lower()

            }

            data2.append(order)

        data = {
            "data": data2
        }

        # buena función para imprimir json
        # print(json.dumps(data, indent=4, sort_keys=True))
        return jsonify(data)

    except KeyError:
        return render_template('404.html')


@app.route('/tableDataNotify')
def table_data_notify():
    try:
        shop_url = session['shop_url']
        data2 = []
        shop_url = session['shop_url']
        shop = Shop.query.filter(Shop.url == shop_url,
                                 Shop.shop_status == 1).first()
        users = User.query.filter(User.shop_id == shop.id).all()

        for user in users:
            user = {
                "Name": user.name,
                "LastName": user.last_name,
                "Email": user.email,
                "NotifyFreq": user.notify_freq,
                "TelegramBotCode": user.telegram_bot_code
            }

            data2.append(user)

        data = {
            "data": data2
        }

        print(json.dumps(data, indent=4, sort_keys=True))
        return jsonify(data)

    except KeyError:
        return render_template('404.html')


# ----------------- FIN  CARGA DE TABLAS DINÁMICAS -------------


# -------------------------- TAREAS PERIÓDICAS PROGRAMADAS  ------------------

@app.route('/monthlySummary')
def monthly_summary_cron():

    monthly_summary.main()

    return Response(status=200)


@app.route('/dailySummary')
def daily_summary_cron():

    daily_summary.main()

    return Response(status=200)


@app.route('/weeklySummary')
def weekly_summary_cron():

    weekly_summary.main()

    return Response(status=200)


# producción: 0 0 2 * * = 2:00 AM del primero de cada mes de N a la Z shop url
# def monthly_billing_simplydrop_n_to_z():

# producción: 0 9 * * * = 9:00 AM de cada dia
# def monthly_billing_simplydrop():

# producción: 0 10 * 6 * = 10:00 AM de cada domingo
# def monthly_billing_simplydrop_test():

# producción: 0 8 1 * * = 8:00 AM de cada primero de  mes
# def monthly_billing_simplydrop_test():

# ----------------- FIN FACTURADOR -------------
