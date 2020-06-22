#!venv/bin/python
# -*- coding: utf-8 -*-

__author__ = "Alvaro Lopez Alvarez"
__copyright__ = "2019 Tible Technologies"

__link__ = "https://tibletech.com/es"
__version__ = 1.0

# --------------------VERIFY-ORDER-CREATE-WEBHOOK.PY--------------------------------
# COMPROBACIÓN DEL WEBHOOK QUE SE GENERA AL CREAR UNA ORDEN
# ---------------------------------------------------------------------

import base64
import hashlib
import hmac
import json
import logging

from simplydrop.config import Config as Cfg
from simplydrop.models.orders import Orders
from simplydrop.models.shop import Shop

# Creación de fichero log
logging.basicConfig(filename='order.log', level=logging.ERROR)


# ----------------- VERIFICAR WEBHOOK  ----------------------
# Funciones de comprobación y auntenticación del
# webhook
# ------------------------------------------------------------


def verify_webhook(shop_url, request):
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256")
    webhook_data = json.loads(request.data)
    webhook_topic = request.headers.get("X-Shopify-Topic")
    shop = Shop.query.filter(Shop.url == shop_url,
                             Shop.shop_status == 1).first()
    orders = Orders.query.filter(Orders.shop_id == shop.id).all()

    # comprobamos que la tienda y el payload del webhook sean validos
    if not shop_url or not webhook_data:
        logging.error("Se ha intentado acceder sin tienda valida")
        print("Se ha intentado acceder sin tienda valida")
        return False

    # comprobamos si el webhook es duplicado y la orden existe
    if webhook_topic == "orders/create":
        order_number = webhook_data["order_number"]
        for order in orders:
            if order.shopify_order_number == order_number:
                logging.error("Webhook duplicado")
                print("Webhook duplicado")
                return False

    # comprobamos si se cumple la verificación por hash
    if not hash_webhook(shop_url, request.data, hmac_header):
        logging.error("Webhook no verificado")
        print("Webhook no verificado")
        return False

    else:
        return True


def hash_webhook(shop_url, data, hmac_header):
    secret = Cfg.SHOPIFY_CONFIG["API_SECRET"]

    if not secret:
        logging.error(
            "No se ha encontrado el APP SECRET de la tienda: " + shop_url)
        return False

    secret = bytes(secret, 'utf-8')

    hash = hmac.new(secret, data, digestmod=hashlib.sha256).digest()
    hmac_calculated = base64.b64encode(hash).decode()

    return hmac_calculated == hmac_header

# ---- FIN VERIFICAR WEBHOOK ----
