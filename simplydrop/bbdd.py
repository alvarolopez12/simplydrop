#!venv/bin/python
# -*- coding: utf-8 -*-

__author__ = "Alvaro Lopez Alvarez"
__copyright__ = "2019 Tible Technologies"

__link__ = "https://tibletech.com/es"
__version__ = 1.0

# ------------------------- bbdd.py---------------------------------
# Fichero con script de consultas a la BBDD SimplyDrop2.0.
# Se Utiliza la librería proporcionada por mysql de Python
# ---------------------------------------------------------------------

import mysql.connector

config = {
    'user': 'root',
    'password': 'root',
    'unix_socket': '/Applications/MAMP/tmp/mysql/mysql.sock',
    'database': 'SimplyDrop',
    'raise_on_warnings': True,
}

link = mysql.connector.connect(**config)


# ----------------- INSERTS ------------------
# En esta sección definimos las funciones de
# inserción a las tablas.
# --------------------------------------------

# Función que inserta una nueva tienda en la tabla Shop
def insert_new_shop(url, token, shop_name, owner_email, owner_phone,
                    shop_status, carrier_json, billing_id):
    mycursor = link.cursor(buffered=True)

    sql1 = "SELECT * FROM Shop WHERE url = %s AND shop_status = TRUE"
    val1 = (url,)
    mycursor.execute(sql1, val1)

    # Cuidamos no insertar Shops duplicadas
    if not mycursor.fetchone():
        mycursor.close()
        mycursor = link.cursor(buffered=True)
        sql = "INSERT INTO Shop (url, token, shop_name, owner_email, owner_phone, " \
              "shop_status, carrier_json, billing_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (url, token, shop_name, owner_email, owner_phone, shop_status,
               carrier_json, billing_id)
        mycursor.execute(sql, val)
        link.commit()
        mycursor.close()

    else:
        mycursor.close()


# Función que inserta una nueva orden en la tabla Orders
def insert_new_order(shopify_order_number, shop_id, customer_email,
                     customer_country, customer_city, customer_province,
                     customer_zip,
                     customer_address1, customer_address2, amount_no_taxes,
                     amount_no_shipping, total_amount, shipping_type, currency,
                     order_status):
    mycursor = link.cursor(buffered=True)

    sql1 = "SELECT * FROM Orders WHERE shopify_order_number = %s AND shop_id = %s"

    val1 = (shopify_order_number, shop_id)

    mycursor.execute(sql1, val1)

    # Cuidamos no insertar Orders duplicadas
    if not mycursor.fetchone():
        sql = "INSERT INTO Orders (shopify_order_number, shop_id, customer_email, " \
              "customer_country, customer_city, customer_province, " \
              "customer_zip, customer_address1, customer_address2, amount_no_taxes, " \
              "amount_no_shipping, total_amount, shipping_type, currency, order_status) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        val = (shopify_order_number, shop_id, customer_email,
               customer_country, customer_city, customer_province,
               customer_zip,
               customer_address1, customer_address2, amount_no_taxes,
               amount_no_shipping,
               total_amount, shipping_type, currency, order_status)

        mycursor.execute(sql, val)
        link.commit()
        mycursor.close()

    else:
        mycursor.close()


# Función que inserta un nuevo item en la tabla Itmes
def insert_new_item(shop_id, shopify_order_number, sku, quantity, title, price,
                    weigth):
    mycursor = link.cursor(buffered=True)

    sql = "INSERT INTO Items (shop_id, shopify_order_number, sku, quantity, title, price, weigth) " \
          "VALUES (%s, %s, %s, %s, %s, %s, %s)"

    val = (shop_id, shopify_order_number, sku, quantity, title, price, weigth)

    mycursor.execute(sql, val)
    link.commit()
    mycursor.close()


# Función que inserta un nuevo user en la tabla Users
def insert_new_user(shop_id, name, last_name, email, notify_freq):
    mycursor = link.cursor(buffered=True)

    sql1 = "SELECT * FROM User WHERE shop_id = %s AND email = %s"
    val1 = (shop_id, email)
    mycursor.execute(sql1, val1)

    # Cuidamos no insertar Users duplicados
    if not mycursor.fetchone():
        sql = "INSERT INTO User (shop_id, name, last_name, email, notify_freq) " \
              "VALUES (%s, %s, %s, %s, %s)"

        val = (shop_id, name, last_name, email, notify_freq)

        mycursor.execute(sql, val)
        link.commit()
        mycursor.close()
    else:
        mycursor.close()


# ----------------- DELETES ------------------
# En esta sección definimos las funciones de
# "delete" a las tablas. NUNCA ELIMINAMOS,
# CAMBIAMOS FLAG DE ESTADO.
# Por eso son en realidad UPDATES
# --------------------------------------------


# Función que desinstala la app de una tienda poniendo su shop_stare a False.
# Nunca eliminamos de la bbdd la tienda por lo que pueda pasar!!!!!
def uninstall_shop(url):
    mycursor = link.cursor(buffered=True)

    sql = "UPDATE Shop SET shop_status = FALSE  WHERE url = %s AND shop_status = TRUE"

    val = (url,)

    mycursor.execute(sql, val)
    link.commit()
    mycursor.close()


# Cambiamos el estado de una orden a cancelada
def order_cancel(shop_id, shopify_order_number):
    mycursor = link.cursor(buffered=True)

    sql = "UPDATE Orders SET order_status = 'Cancelled'  WHERE shop_id = %s AND shopify_order_number = %s "

    val = (shop_id, shopify_order_number)

    mycursor.execute(sql, val)
    link.commit()
    mycursor.close()


# Función que elimina a un usuario existente
def delete_user(shop_id, email, name):
    mycursor = link.cursor(buffered=True)

    sql = "DELETE FROM User WHERE shop_id = %s AND email = %s AND name = %s"

    val = (shop_id, email, name)

    mycursor.execute(sql, val)
    link.commit()
    mycursor.close()


# Función que elimina a un usuario existente
def delete_all_user_from_one_shop(shop_id):
    mycursor = link.cursor(buffered=True)

    sql = "DELETE FROM User WHERE shop_id = %s"

    val = (shop_id,)

    mycursor.execute(sql, val)
    link.commit()
    mycursor.close()


# ----------------- UPDATES ------------------
# En esta sección definimos las funciones de
# update a las tablas.
# --------------------------------------------


# Cambiamos el estado de una orden a cancelada
def user_freq_change(shop_id, email, notify_freq):
    mycursor = link.cursor(buffered=True)

    sql = "UPDATE User SET notify_freq = %s  WHERE shop_id = %s AND email = %s "

    val = (notify_freq, shop_id, email)

    mycursor.execute(sql, val)
    link.commit()
    mycursor.close()


def update_carrier_json(carrier_json, shop_id):
    mycursor = link.cursor(buffered=True)

    sql = "UPDATE Shop SET carrier_json = %s  WHERE id = %s AND shop_status = TRUE"

    val = (carrier_json, shop_id)

    mycursor.execute(sql, val)
    link.commit()
    mycursor.close()


# ----------------- SELECTS ------------------
# En esta sección definimos las funciones de
# selección a las tablas.
# --------------------------------------------

# Función que devuelve la shop pasándole la url de la tienda
def get_shop(url):
    mycursor = link.cursor(buffered=True)

    sql = "SELECT * FROM Shop WHERE url = %s AND shop_status = TRUE"
    val = (url,)
    mycursor.execute(sql, val)

    shop = mycursor.fetchall()
    mycursor.close()

    return shop


# Función que devuelve el id_shop pasandole la url de la tienda
def get_shop_id(url):
    mycursor = link.cursor(buffered=True)

    sql = "SELECT id FROM Shop WHERE url = %s AND shop_status = TRUE"
    val = (url,)
    mycursor.execute(sql, val)

    id_shop = mycursor.fetchall()
    mycursor.close()

    if id_shop:
        return id_shop[0][0]
    else:
        return 0


# Función que devuelve el id_shop pasandole la url de la tienda
def get_shop_contact(url):
    mycursor = link.cursor(buffered=True)

    sql = "SELECT owner_email FROM Shop WHERE url = %s AND shop_status = TRUE"
    val = (url,)
    mycursor.execute(sql, val)

    owner_email = mycursor.fetchall()
    mycursor.close()

    if owner_email:
        return owner_email[0][0]
    else:
        return 0


# Seleccionamos las ordenes de la tienda
def get_orders_by_id(shop_id):
    mycursor = link.cursor(buffered=True)

    sql = "SELECT shopify_order_number, total_amount, customer_country, " \
          "customer_email, carrier, shipping_type, order_status, currency FROM Orders WHERE shop_id = %s ORDER BY shopify_order_number "
    val = (shop_id,)
    mycursor.execute(sql, val)

    orders = mycursor.fetchall()
    mycursor.close()

    return orders


def get_all_shops():
    mycursor = link.cursor(buffered=True)

    sql = "SELECT * FROM Shop WHERE shop_status = 1"
    mycursor.execute(sql)

    shops = mycursor.fetchall()
    mycursor.close()

    return shops


# Seleccionamos los items de la tienda
def get_items_by_order(shopify_order_number, shop_id):
    mycursor = link.cursor(buffered=True)

    sql = "SELECT sku, quantity, title, " \
          "price, weigth FROM Items WHERE shop_id = %s AND shopify_order_number = %s"
    val = (shop_id, shopify_order_number)
    mycursor.execute(sql, val)

    orders = mycursor.fetchall()
    mycursor.close()

    return orders


# Seleccionamos una order dado su number y la url de la tienda
def get_specific_order(shopify_order_number, shop_id):
    mycursor = link.cursor(buffered=True)

    sql = "SELECT * FROM Orders WHERE shop_id = %s AND shopify_order_number = %s"
    val = (shop_id, shopify_order_number)
    mycursor.execute(sql, val)

    order = mycursor.fetchall()
    mycursor.close()

    return order


# ----- Seleccionamos los usuarios de notificación de la tienda ----
def get_users(shop_id):
    mycursor = link.cursor(buffered=True)

    sql = "SELECT name, last_name, email, notify_freq FROM User WHERE shop_id = %s"
    val = (shop_id,)
    mycursor.execute(sql, val)

    orders = mycursor.fetchall()
    mycursor.close()

    return orders


def get_users_freq_instant(shop_id):
    mycursor = link.cursor(buffered=True)

    sql = "SELECT name, last_name, email FROM User WHERE shop_id = %s AND notify_freq = 'After each order' "
    val = (shop_id,)
    mycursor.execute(sql, val)

    orders = mycursor.fetchall()
    mycursor.close()

    return orders


def get_users_freq_daily(shop_id):
    mycursor = link.cursor(buffered=True)

    sql = "SELECT name, last_name, email FROM User WHERE shop_id = %s AND notify_freq = 'After each order'"
    val = (shop_id,)
    mycursor.execute(sql, val)

    orders = mycursor.fetchall()
    mycursor.close()

    return orders


def get_users_freq_weekly(shop_id):
    mycursor = link.cursor(buffered=True)

    sql = "SELECT name, last_name, email FROM User WHERE shop_id = %s AND notify_freq = 'Weekly summary'"
    val = (shop_id,)
    mycursor.execute(sql, val)

    orders = mycursor.fetchall()
    mycursor.close()

    return orders


def get_users_freq_monthly(shop_id):
    mycursor = link.cursor(buffered=True)

    sql = "SELECT name, last_name, email FROM User WHERE shop_id = %s AND notify_freq = 'Monthly summary'"
    val = (shop_id,)
    mycursor.execute(sql, val)

    orders = mycursor.fetchall()
    mycursor.close()

    return orders


def get_carrier_json(shop_id):
    mycursor = link.cursor(buffered=True)

    sql = "SELECT carrier_json FROM Shop WHERE id = %s AND shop_status = TRUE "
    val = (shop_id,)
    mycursor.execute(sql, val)

    carrier_json = mycursor.fetchall()
    mycursor.close()

    return carrier_json


# ------ Funciones que rellenan tarjetas del panel de control ----

def get_cards_info(shop_id):
    # --- Función que devuelve la suma del precio de las ordenes de este mes ---
    mycursor = link.cursor(buffered=True)

    sql = "SELECT SUM(price) FROM Items " \
          "WHERE " \
          "YEAR(added_on) = YEAR(now() - INTERVAL 1 MONTH) " \
          "AND MONTH(added_on) = MONTH(now() - INTERVAL 1 MONTH) " \
          "AND shop_id = %s "

    val = (shop_id,)
    mycursor.execute(sql, val)

    earning_month = mycursor.fetchall()
    mycursor.close()

    # --- Función que devuelve la suma del precio de las ordenes de este año ---
    mycursor = link.cursor(buffered=True)

    sql = "SELECT SUM(price) FROM Items WHERE YEAR(added_on) = YEAR(now()) AND shop_id = %s "

    val = (shop_id,)
    mycursor.execute(sql, val)

    earning_annual = mycursor.fetchall()
    mycursor.close()

    # --- Función que devuelve el % de diferencia entre ordenes de este mes y el pasado ---
    mycursor = link.cursor(buffered=True)

    sql = "SELECT COUNT(*) FROM Orders WHERE MONTH(added_on) = MONTH(now())-1 AND " \
          " YEAR(added_on) = YEAR(CURRENT_DATE - INTERVAL 1 MONTH) AND shop_id = %s "

    val = (shop_id,)
    mycursor.execute(sql, val)

    orders_last_month = mycursor.fetchall()
    mycursor.close()

    if orders_last_month:
        orders_last_month = orders_last_month[0][0]
    else:
        orders_last_month = 0

    mycursor = link.cursor(buffered=True)

    sql = "SELECT COUNT(*) FROM Orders WHERE  MONTH(added_on) = MONTH(now()) AND " \
          " YEAR(added_on) = YEAR(now()) AND shop_id = %s "

    val = (shop_id,)
    mycursor.execute(sql, val)

    orders_this_month = mycursor.fetchall()
    mycursor.close()

    if orders_this_month:
        orders_this_month = orders_this_month[0][0]
    else:
        orders_this_month = 0

    if orders_last_month == 0:
        equal_last_month_percent = 100

    else:
        equal_last_month_percent = (
                                           orders_this_month * 100) / orders_last_month

    # --- Función que devuelve el numero de ordenes en estado sin enviar ---
    mycursor = link.cursor(buffered=True)

    sql = "SELECT COUNT(*) FROM Orders WHERE shop_id = %s AND order_status = 'Created' "

    val = (shop_id,)
    mycursor.execute(sql, val)

    pending_pickup = mycursor.fetchall()
    mycursor.close()

    if pending_pickup[0][0]:
        pending_pickup = pending_pickup[0][0]
    else:
        pending_pickup = 0

    if earning_month[0][0]:
        earning_month = earning_month[0][0]
    else:
        earning_month = 0

    if earning_annual[0][0]:
        earning_annual = earning_annual[0][0]
    else:
        earning_annual = 0

    cards_info = {
        "earning_month": earning_month,
        "earning_annual": earning_annual,
        "equal_last_month_percent": equal_last_month_percent,
        "pending_pickup": pending_pickup
    }

    return cards_info


# ------ Funciones utilizadas en el proceso de cobro ----

# Contamos cuantas ordenes RECOGIDAS tuvieron cada tienda ACTIVA el mes pasado A-M
def get_shops_and_number_of_orders_a_to_m():
    mycursor = link.cursor(buffered=True)

    sql = "SELECT Shop.url, Shop.token, Shop.owner_email, COUNT(Orders.id) " \
          "FROM Shop " \
          "INNER JOIN Orders ON Shop.id = Orders.shop_id " \
          "WHERE " \
          "MONTH(Orders.added_on) = MONTH(now() - INTERVAL 1 MONTH) " \
          "AND YEAR(Orders.added_on) = YEAR(now() - INTERVAL 1 MONTH)" \
          "AND Orders.order_status = 'Created'" \
          "AND Shop.shop_status = TRUE " \
          "AND (Shop.url <= 'm' OR Shop.url <= '5')" \
          "GROUP BY Shop.url, Shop.token, Shop.owner_email"

    mycursor.execute(sql)

    shops_with_number_of_orders_last_month = mycursor.fetchall()
    mycursor.close()

    return shops_with_number_of_orders_last_month


# Contamos cuantas ordenes RECOGIDAS tuvieron cada tienda ACTIVA el mes pasado M-Z
def get_shops_and_number_of_orders_n_to_z():
    mycursor = link.cursor(buffered=True)

    sql = "SELECT Shop.url, Shop.token, Shop.owner_email, COUNT(Orders.id) " \
          "FROM Shop " \
          "INNER JOIN Orders ON Shop.id = Orders.shop_id " \
          "WHERE " \
          "MONTH(Orders.added_on) = MONTH(now() - INTERVAL 1 MONTH) " \
          "AND YEAR(Orders.added_on) = YEAR(now() - INTERVAL 1 MONTH)" \
          "AND Orders.order_status = 'Created'" \
          "AND Shop.shop_status = TRUE " \
          "AND (Shop.url >= 'n' OR Shop.url >= '6')" \
          "GROUP BY Shop.url, Shop.token, Shop.owner_email"

    mycursor.execute(sql)

    shops_with_number_of_orders_last_month = mycursor.fetchall()
    mycursor.close()

    return shops_with_number_of_orders_last_month
