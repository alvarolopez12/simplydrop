#!venv/bin/python
# -*- coding: utf-8 -*-

__author__ = "Alvaro Lopez Alvarez"
__copyright__ = "2019 Tible Technologies"

__link__ = "https://tibletech.com/es"
__version__ = 1.0

import json

from flask import Response, session

from simplydrop import db
# -------------------------webhooks_dispatcher.py-----------------------------
# Script que recoge los webhooks que
# llegan a la aplicación y los gestiona según
# su procedencia hacia su destino
# ----------------------------------------------------------------------------
from simplydrop.carriers import select_carrier
from simplydrop.models.items import Items
from simplydrop.models.orders import Orders
from simplydrop.models.shop import Shop
from simplydrop.models.user import User
from simplydrop.notifier import send_email
from simplydrop.notifier.send_telegram_message import \
    telegram_bot_send_order_instant
from simplydrop.shopify_api_connect import post_and_req
from . import verify_webhook


def webhook_dispatcher(request):
    shop_url = request.headers.get("X-Shopify-Shop-Domain")
    webhook_topic = request.headers.get("X-Shopify-Topic")
    webhook_data = json.loads(request.data)
    shop = Shop.query.filter(Shop.url == shop_url,
                             Shop.shop_status == 1).first()
    token = shop.token
    users = User.query.filter(User.shop_id == shop.id).all()

    if verify_webhook.verify_webhook(shop_url, request):

        if webhook_topic == "orders/create" \
                and webhook_data["financial_status"] == "authorized":

            shopify_order_number = webhook_data["order_number"]
            customer_email = webhook_data["email"]
            customer_country = webhook_data["shipping_address"]["country"]
            customer_country_code = webhook_data["shipping_address"][
                "country_code"]
            customer_city = webhook_data["shipping_address"]["city"]
            customer_province = webhook_data["shipping_address"]["province"]
            customer_zip = webhook_data["shipping_address"]["zip"]
            customer_address1 = webhook_data["shipping_address"]["address1"]
            customer_address2 = webhook_data["shipping_address"]["address2"]
            shipping_type = webhook_data["shipping_lines"][0]["title"]
            amount_no_taxes = webhook_data["total_tax_set"]["shop_money"][
                "amount"]
            amount_no_shipping = \
                webhook_data["total_shipping_price_set"]["shop_money"][
                    "amount"]
            total_amount = webhook_data["total_price"]
            total_items = len(webhook_data["line_items"])
            currency = webhook_data["currency"]
            order_status = "Created"

            # Delegamos a la clase carrier_selected para que elija un trasportista
            # Si es elegido alguno y se cursa correctamente la orden, cambia el estado
            # de dicha orden y se le cobra a la tienda el uso del servicio
            carrier_selected = \
                select_carrier.select_carrier_service(shop_url, webhook_data)

            if carrier_selected != "No carrier":
                order_status = "Processed"
                post_and_req.usage_charge(shop)

            # procedemos a guardar en base de datos la orden y los items asociados
            new_order = Orders(shopify_order_number=shopify_order_number,
                               shop_id=shop.id,
                               customer_email=customer_email,
                               customer_country=customer_country,
                               customer_country_code=customer_country_code,
                               customer_city=customer_city,
                               customer_province=customer_province,
                               customer_zip=customer_zip,
                               customer_address1=customer_address1,
                               customer_address2=customer_address2,
                               amount_no_taxes=amount_no_taxes,
                               amount_no_shipping=amount_no_shipping,
                               total_amount=total_amount,
                               carrier=carrier_selected,
                               shipping_type=shipping_type, currency=currency,
                               order_status=order_status, label="")
            db.session.add(new_order)
            db.session.commit()

            for item in webhook_data["line_items"]:
                image = post_and_req.obtain_item_image(shop_url,
                                                       token,
                                                       item["product_id"])

                new_item = Items(shop_id=shop.id,
                                 order_number=webhook_data["order_number"],
                                 sku=item["sku"], quantity=item["quantity"],
                                 title=item["title"], price=item["price"],
                                 weigth=item["grams"],
                                 image=image)

                db.session.add(new_item)
                db.session.commit()

            for user in users:
                if user.notify_freq == "After each order":
                    send_email.send_order_email_instant(user.name,
                                                        user.email,
                                                        customer_country,
                                                        carrier_selected,
                                                        shop_url,
                                                        shopify_order_number,
                                                        total_amount,
                                                        currency,
                                                        total_items)

                    if user.telegram_chat_id != "":
                        print("holi")
                        telegram_bot_send_order_instant(user,
                                                        customer_country,
                                                        carrier_selected,
                                                        str(
                                                            shopify_order_number),
                                                        str(total_amount),
                                                        currency,
                                                        str(total_items))
            return Response(status=200)

        elif webhook_topic == "app/uninstalled":
            session.clear()
            shop.shop_status = False
            db.session.commit()

            for user in users:
                db.session.delete(user)
                db.session.commit()

            return Response(status=200)


        # ---- manejo de los nuevos webhooks obligatorios de GDPR---
        # elimina la info de un dueño de la tienda
        elif webhook_topic == "customers/data_request" or \
                webhook_topic == "shop/redact" or "customers/redact":

            # me envio el cuerpo del webhook y ya veo en tranquilo que pasa
            send_email.gdpr_email_warning(webhook_topic,
                                          json.dumps(webhook_data))
            return Response(status=200)

    else:
        # mandamos 200 porque aunque no haya pasado nuestro filtro,
        # el webhook ha llegado y se volverá a mandar.
        return Response(status=200)
