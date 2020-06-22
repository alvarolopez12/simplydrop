#!venv/bin/python
# -*- coding: utf-8 -*-

__author__ = "Alvaro Lopez Alvarez"
__copyright__ = "2019 Tible Technologies"

__link__ = "https://tibletech.com/es"
__version__ = 1.0

# -------------------------select_carrier.py---------------------------------
# Script que según variables del pedido, elige el mejor transportista
# ---------------------------------------------------------------------------


import json

from simplydrop.models.shop import Shop


def select_carrier_service(shop_url, webhook_data):
    # codigo mágico que elige transportista MEJORAAAAS

    shop = Shop.query.filter_by(url=shop_url).first()

    carrier_json = json.loads(shop.carrier_json)

    if carrier_json['mrw']['state'] is True:
        pickup_account = carrier_json['mrw']

        # terminar de implementar cuando MRW nos de las credenciales
        # if mrw.create_mrw_order(pickup_account, shop_url, webhook_data):

        return "MRW"

    return "No carrier"
