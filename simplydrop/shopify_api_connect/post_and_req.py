#!venv/bin/python
# -*- coding: utf-8 -*-

__author__ = "Alvaro Lopez Alvarez"
__copyright__ = "2019 Tible Technologies"

__link__ = "https://tibletech.com/es"
__version__ = 1.0

# ------------------------Shopify_API_manager.py----------------------
# Fichero con script que procesa todas las llamadas
# a la API de Shopify y procesa sus respuestas
# --------------------------------------------------------------------

import json

import requests
from flask import Response

from simplydrop.config import Config as Cfg


# ----------------- REGISTRO WEBHOOKS ------------------------
# Definimos las funciones que construyen las respuestas para registrar
# los webhooks
# ------------------------------------------------------------

# ----REGISTRO A ORDER/CREATE ----
def register_webhook_order_create(shop_url, token):
    headers = {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    }

    payload = {
        "webhook": {
            "topic": "orders/create",
            "address": Cfg.HOST + "/webhooks",
            "format": "json"
        }
    }

    response = requests.post(
        "https://" + shop_url + "/admin/api/2019-04/webhooks.json",
        data=json.dumps(payload), headers=headers)

    if response.status_code == 201:
        print("registrado a order create")
        return Response(status=200)
    else:

        return Response(status=400)


# ----REGISTRO A APP/UNINSTALLED----
def register_webhook_shop_uninstalled(shop_url, token):
    headers = {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    }

    payload = {
        "webhook": {
            "topic": "app/uninstalled",
            "address": Cfg.HOST + "/webhooks",
            "format": "json"
        }
    }

    response = requests.post(
        "https://" + shop_url + "//admin/api/2019-04/webhooks.json",
        data=json.dumps(payload), headers=headers)

    if response.status_code == 201:
        print("registrado a app unistall")
        return Response(status=200)
    else:
        return Response(status=400)


# ----------------- FIN REGISTRO WEBHOOKS ------------------------


# ----------------- OBTENER INFO NEW SHOP ------------------------
# Obtenemos info de la nueva tienda
# ----------------------------------------------------------------
def obtain_shop_info(shop_url, token):
    headers = {
        "X-Shopify-Access-Token": token
    }

    response = requests.get(
        "https://" + shop_url + "/admin/api/2019-04/shop.json",
        headers=headers)

    if response.status_code == 200:
        resp_json = json.loads(response.text)
        info = [
            resp_json["shop"]["name"],
            resp_json["shop"]["email"],
            resp_json["shop"]["phone"],
            resp_json["shop"]["currency"]
        ]
        return info

    else:
        return "Email Error"


# ----------------- FIN OBTENER INFO NEW SHOP ------------------------


# -------------------- OBTENER FOTOS DE PRODUCTO -------------------
# Obtenemos en un array, todas las fotos de un producto determinado
# ----------------------------------------------------------------
def obtain_item_image(shop_url, token, item_id):
    headers = {
        "X-Shopify-Access-Token": token
    }

    response = requests.get(
        "https://" + shop_url +
        "/admin/api/2019-04/products/" + str(item_id) + "/images.json",
        headers=headers)

    if response.status_code == 200:
        resp_json = json.loads(response.text)

        if not resp_json["images"]:

            # si el producto no tiene imagen cargamos la imagen de error
            return "https://cdn.shopify.com/s/images/admin/no-image-large" \
                   ".gif?da5ac9ca38617f8fcfb1ee46268f66d451ca66b4"

        else:
            return resp_json["images"][0]["src"]

    else:
        return "Image Error"


# ----------------- OBTENER FOTOS DE PRODUCTO -----------------


# ----------------- IMPLEMENTACIÓN DEL COBRO RECURRENTE  ------------------
# Registramos en la tienda el cargo recurrente.
# --------------------------------------------------------------------
def implement_recurrent_change(shop_url, token):
    headers = {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    }

    payload = {
        "recurring_application_charge": {
            "name": "Orders processed with a carrier",
            "price": 0.00,
            "test": True,
            "capped_amount": 1000000,
            "terms": "0.50€ per order",
            "return_url": "http://super-duper.shopifyapps.com"
        }
    }

    response = requests.post(
        "https://" + shop_url + "/admin/api/2019-04/recurring_application_charges.json",
        data=json.dumps(payload), headers=headers)

    resp_json = json.loads(response.text)

    return resp_json["recurring_application_charge"]["id"]


# función que se ejecuta cada orden cursada correctamente con un transportista
# y cobra
def usage_charge(shop):
    headers = {
        "X-Shopify-Access-Token": shop.token,
        "Content-Type": "application/json"
    }

    payload = {
        "usage_charge": {
            "description": "Postcard for high order value customer",
            "price": 0.5,
            "test": True,
        }
    }
    response = requests.post(
        "https://"
        + shop.url +
        "/admin/api/2019-04/recurring_application_charges/"
        + shop.billing_id + "/usage_charges.json",
        data=json.dumps(payload),
        headers=headers)

# ----------------- IMPLEMENTACIÓN DEL COBRO RECURRENTE-----------------
