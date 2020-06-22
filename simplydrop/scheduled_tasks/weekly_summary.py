#!venv/bin/python
# -*- coding: utf-8 -*-

__author__ = "Alvaro Lopez Alvarez"
__copyright__ = "2019 Tible Technologies"

__link__ = "https://tibletech.com/es"
__version__ = 1.0

from collections import Counter
from datetime import datetime, timedelta

from simplydrop.models.items import Items
from simplydrop.models.orders import Orders
# -------------------------monthly_summary.py---------------------------------
# Script que se ejecuta cada lunes las 9 am: 0 9 * * 1
# extrae las estadísticas y manda correo de resumen
# -------------------------------------------------------------------------
from simplydrop.models.shop import Shop
from simplydrop.models.user import User
from simplydrop.notifier import send_email, send_telegram_message


def main():
    users = User.query.filter(User.notify_freq == "Monthly summary").all()

    frequency = "week"
    today = datetime.today().replace(
        hour=00, minute=00, second=00, microsecond=00)

    first_of_past_week = today - timedelta(days=7)

    first_of_two_weeks_before = today - timedelta(days=7)

    for user in users:

        shop = Shop.query.filter(Shop.id == user.shop_id).first()

        orders = Orders.query.filter(Orders.shop_id == shop.id,
                                     Orders.added_on >= first_of_past_week,
                                     Orders.added_on < today).all()

        items = Items.query.filter(Items.shop_id == shop.id,
                                   Items.added_on > first_of_past_week,
                                   Items.added_on < today).all()

        orders_last_period = Orders.query.filter(Orders.shop_id == shop.id,
                                                 Orders.added_on >= first_of_two_weeks_before,
                                                 Orders.added_on < first_of_past_week).all()

        total_orders = len(orders)
        total_items = len(items)
        total_amount = sum(float(order.total_amount) for order in orders)
        try:
            compare_orders_last_period = total_orders / len(orders_last_period)
        except ZeroDivisionError:
            compare_orders_last_period = 0

        countries_array = (order.customer_country for order in orders)
        countries_array = list(countries_array)

        carriers_array = (order.carrier for order in orders)
        carriers_array = list(carriers_array)

        items_array = (item.title for item in items)
        items_array = list(items_array)

        if countries_array:
            top_country = Counter(countries_array).most_common(1)[0][0]
            top_carrier = Counter(carriers_array).most_common(1)[0][0]
            top_product = Counter(items_array).most_common(1)[0][0]

            try:
                average_products_order = total_items / total_orders
            except ZeroDivisionError:
                average_products_order = 0

            send_email.send_order_email_summary(user.name, user.email,
                                                shop.url,
                                                frequency, shop.currency,
                                                total_items, total_orders,
                                                total_amount,
                                                compare_orders_last_period,
                                                top_country, top_carrier,
                                                top_product,
                                                average_products_order)

            if user.telegram_chat_id:
                send_telegram_message.telegram_bot_send_summary(user.name,
                                                                user.telegram_chat_id,
                                                                shop.url,
                                                                frequency,
                                                                shop.currency,
                                                                total_items,
                                                                total_orders,
                                                                total_amount,
                                                                compare_orders_last_period,
                                                                top_country,
                                                                top_carrier,
                                                                top_product,
                                                                average_products_order)

