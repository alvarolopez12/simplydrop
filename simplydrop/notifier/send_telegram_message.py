#!venv/bin/python
# -*- coding: utf-8 -*-

__author__ = "Alvaro Lopez Alvarez"
__copyright__ = "2019 Tible Technologies"

__link__ = "https://tibletech.com/es"
__version__ = 1.0

# -------------------------send_telegram_message.py---------------------------
# Script de atención a los webhooks producidos en telegram.
# Genera respuestas del bot, tanto instántaneas como de resumen
# ----------------------------------------------------------------------------

import requests

from simplydrop.config import Config
from simplydrop.models.shop import Shop

bot_token = Config.TELEGRAM_BOT_TOKEN


# ----------------- SUSCRIPCION A WEBHOOKS DEL BOT ------------------
# Solo se ejecuta la primera vez, para susucribirse a los webhooks del bot
# ---------------------------------------------------------------------------

def suscribe_telegram_webhooks(host):
    send_text = 'https://api.telegram.org/bot' + \
                bot_token + '/setWebhook?url=' + \
                host + '/telegram-webhooks'

    print(send_text)
    response = requests.get(send_text)

    return response.json()


# ----------------- FIN SUSCRIPCION A WEBHOOKS DEL BOT ------------------


# ----------------- ANTENCIÓN A MENSAJES INSTANTÁNEOS ----------------------
# Contesta mensajes a tiempo real del bo
# ---------------------------------------------------------------------------
def telegram_bot_send_welkome(chat_id):
    bot_chat_id = chat_id

    bot_message = """
    
Welcome to SimplyDrop's chatbot.\n
Configure your notification account from our Shopify application .\
Once configured, send me your Telegram code provide by SimplyDrop. \n
 
I you still watching this and you think thath your code is good, \n
please contact with simplydrop.info@gmail.com because something is wrong.
    
Happy SimplyDroping on Telegram :)
    
    """

    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + str(
        bot_chat_id) + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()


def telegram_bot_send_user_hello(chat_id, user):
    shop = Shop.query.filter(Shop.id == user.shop_id).first()
    bot_chat_id = chat_id
    bot_message = """
    

Hello """ + user.name + """ from """ + shop.url + """,\n

Welcome to your private Simplydrop bot.\

I will send you here the notifications that occur in your SimplyDrop application \
the updates of the orders in your store.\n

If you delete your SimplyDrop user, this bot will be unusable and you will have to start a new one\

Happy SimplyDroping on Telegram :)

    """

    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + str(
        bot_chat_id) + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()


def telegram_bot_send_user_help(chat_id, user):
    shop = Shop.query.filter(Shop.id == user.shop_id).first()
    bot_chat_id = chat_id
    bot_message = """


Hello """ + user.name + """ from """ + shop.url + """,\n


You are already login in this bot.
Please wait for an order to be notified \n

Happy SimplyDroping on Telegram :)

    """

    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + str(
        bot_chat_id) + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()


# ----------------- FIN ATENCIÓN A MENSAJES INSTANTÁNEOS ------------------


# ----------------- ATENCIÓN A MENSAJES DE RESUMEN ------------------------
# Genera mensajes de información a los usuarios de SimplyDrop
# ---------------------------------------------------------------------------

# -----Mensaje instantáneo----
def telegram_bot_send_order_instant(user, country,
                                    carrier, order_number, total_amount,
                                    currency,
                                    total_items):
    shop = Shop.query.filter(Shop.id == user.shop_id).first()
    bot_chat_id = user.telegram_chat_id
    bot_message = """
        
Hello """ + user.name + """ it seems that someone just bought in your store """ + shop.url + """,\n

Here is the purchase info: \n

Country: """ + country + """
Carrier: """ + carrier + """
Order number: """ + order_number + """
Total amount: """ + total_amount + """
Total items: """ + total_items + """

Keep selling! ;)

    """

    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + str(
        bot_chat_id) + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)
    print(response.status_code)

    return response.json()


# -----Mensaje resumen programado---
def telegram_bot_send_summary(name, user_telegram_chat_id, url_shop, frequency,
                              currency,
                              total_items, total_orders, total_amount,
                              comapare_orders_last_period, top_country,
                              top_carrier, top_product,
                              average_products_order):
    bot_chat_id = user_telegram_chat_id
    bot_message = """

Hello """ + name + """

Here is your summary of the """ + frequency + """ of your shop """ + url_shop + """,\n

Total items: """ + str(total_orders) + """
Total orders: """ + str(total_items) + """
Total amount: """ + str(total_amount) + """
Sales compared to the """ + str(frequency) + """ before: """ + str(
        comapare_orders_last_period) + """
Top country: """ + str(top_country) + """
Top carrier: """ + str(top_carrier) + """
Top product: """ + str(top_product) + """
Average products in each order: """ + str(average_products_order) + """

Keep selling! ;)

    """

    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + str(
        bot_chat_id) + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)
    print(response.status_code)

    return response.json()

# ----------------- FIN ATENCIÓN A MENSAJES DE RESUMEN ----------------------
