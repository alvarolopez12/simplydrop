#!venv/bin/python
# -*- coding: utf-8 -*-

__author__ = "Alvaro Lopez Alvarez"
__copyright__ = "2019 Tible Technologies"

__link__ = "https://tibletech.com/es"
__version__ = 1.0

# --------------------dhl.py--------------------------------
# Fichero que obtiene datos del pedido que se le ha pasado por Webhook.
# Comprueba datos y se los pasa a DHL en formato JSON para crear orden
# ---------------------------------------------------------------------

import json

import requests


# Sandbox Authentication API for GAPI APIs: https://api-qa.dhlecommerce.com/account/v1/auth/accesstoken
# Production GAPI APIs: https://api.dhlecommerce.com/account/v1/auth/accesstoken
# Caduca cada 5 horas
def get_dhl_token():
    response = requests.post("https://api-qa.dhlecommerce."
                             "com/account/v1/auth/accesstoken",
                             data={}, auth=('user', 'pass'))

    print(response)
    print(response.content)


def create_dhl_order(pickupAccount, shop_url, webhook_data):
    # variables del consigneeAddress
    customer_email = webhook_data["email"]
    customer_country = webhook_data["shipping_address"]["country"]
    customer_city = webhook_data["shipping_address"]["city"]
    customer_province = webhook_data["shipping_address"]["province"]
    customer_zip = webhook_data["shipping_address"]["zip"]
    customer_name = webhook_data["shipping_address"]["first_name"]
    customer_phone = webhook_data["shipping_address"]["first_name"]
    customer_address1 = webhook_data["shipping_address"]["address1"]
    customer_address2 = webhook_data["shipping_address"]["address2"]
    customer_company = webhook_data["shipping_address"]["company"]
    customer_id = webhook_data["customer"]["id"]
    amount_no_taxes = webhook_data["total_tax_set"]["shop_money"]["amount"]
    amount_no_shipping = \
        webhook_data["total_shipping_price_set"]["shop_money"]["amount"]
    total_amount = webhook_data["total_price_set"]["shop_money"]["amount"]
    shipping_type = webhook_data["shipping_lines"][0]["title"]
    currency = webhook_data["currency"]

    packages = []
    for item in webhook_data["line_items"]:
        packet = {
            {
                "consigneeAddress": {
                    "address1": customer_address1,
                    "address2": customer_address2,
                    "address3": "",
                    "city": customer_city,
                    "companyName": customer_company,
                    "country": customer_country,
                    "email": customer_email,
                    "idNumber": customer_id,
                    "idType": 4,
                    "name": customer_name,
                    "phone": customer_phone,
                    "postalCode": customer_zip,
                    "state": customer_province
                },
                "packageDetails": {
                    "orderedProduct": "exe",
                    "packageId": "id cillum",
                    "weight": 287369.558640813,
                    "weightUom": "OZ",
                    "billingRef1": "dolor",
                    "billingRef2": "exe",
                    "customerRef1": "dolor mollit ut",
                    "customerRef2": "do eu",
                    "codAmount": 310743647.59536636,
                    "currency": "qui",
                    "declaredValue": 279906907.8708184,
                    "dutyCharges": 813893088.3393347,
                    "freightCharges": 997974847.3983057,
                    "taxCharges": 459691978.0479687,
                    "deliveryConfirmationNo": "d",
                    "dgCategory": "4",
                    "dimensionUom": "u",
                    "dutiesPaid": "DDP",
                    "insuredValue": 62825036.72637896,
                    "mailType": 6,
                    "packageDesc": "proident des",
                    "packageRefName": "dolore Duis sed e",
                    "service": "proi",
                    "serviceEndorsement": 4,
                    "height": 974671632.249972,
                    "length": 609892882.5456467,
                    "width": 757832170.7920452
                },
                "returnAddress": {
                    "address1": "minim sed",
                    "city": "Excepteur commodo sed occae",
                    "country": "do",
                    "address2": "d",
                    "address3": "fugiat dolo",
                    "companyName": "veli",
                    "name": "id fugiat ",
                    "email": "cillum consectetur irure fugiat culpa",
                    "phone": "sint id incididun",
                    "postalCode": "BXEEERR-REVWO",
                    "state": "nostrud"
                },
                "customsDetails": [
                    {
                        "itemDescription": "officia ipsum ex consectetur",
                        "packagedQuantity": 27788645,
                        "itemValue": 32761864.444047492,
                        "descriptionExport": "proident irure aliquip et",
                        "descriptionImport": "Ut consectetur",
                        "countryOfOrigin": "la",
                        "hsCode": "amet c",
                        "skuNumber": "incididunt v"
                    },
                    {
                        "itemDescription": "officia ipsum mollit ullamco",
                        "packagedQuantity": 24956300,
                        "itemValue": 420398832.690244,
                        "descriptionExport": "enim mollit",
                        "descriptionImport": "reprehenderit esse mollit",
                        "countryOfOrigin": "do",
                        "hsCode": "sint fu",
                        "skuNumber": "veniam laborum fugi"
                    },
                    {
                        "itemDescription": "sit laborum",
                        "packagedQuantity": 35437927,
                        "itemValue": 15715748.475756133,
                        "descriptionExport": "quis ea",
                        "descriptionImport": "non",
                        "countryOfOrigin": "in",
                        "hsCode": "fugiat",
                        "skuNumber": "e"
                    },
                    {
                        "itemDescription": "ipsum nisi officia non",
                        "packagedQuantity": 86582400,
                        "itemValue": 403731881.5206286,
                        "descriptionExport": "commodo in ut",
                        "descriptionImport": "dolor",
                        "countryOfOrigin": "al",
                        "hsCode": "sed labor",
                        "skuNumber": "conseq"
                    },
                    {
                        "itemDescription": "sunt ad adipisicing",
                        "packagedQuantity": 41484113,
                        "itemValue": 170207980.4040607,
                        "descriptionExport": "voluptate in ipsum ",
                        "descriptionImport": "sunt esse dolor",
                        "countryOfOrigin": "Ut",
                        "hsCode": "labo",
                        "skuNumber": "q"
                    }
                ]
            }
        }
        packages.append(packet)

    payload = {

        "shipments": [
            {
                "pickupAccount": "Duis Exc",
                "packages": [packages]
            }
        ],
        "distributionCenter": "aute m",
        "consignmentNumber": "eiusmod ",
        "isWorkshare": False
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer [place OAuth access token here, without brackets]'
    }
    response = requests.post('https://private-anon-c7287eefa2-dhlecglobal'
                             'shippingorderapi.apiary-mock.com/'
                             'shipping/v1/order/manifest',
                             data=json.dumps(payload), headers=headers)

    print(response)
    print(response.content)


def create_dhl_label():
    payload = {
        "distributionCenter": "HKHKG1",
        "pickupAccount": "[place your pickup account number here, without brackets]",
        "isWorkshare": True,
        "pickupAddress": {
            "address1": "Address Line 1",
            "address2": "Address Line 2",
            "city": "NY",
            "companyName": "ABCD",
            "country": "US",
            "email": "xyz@abcd.com",
            "name": "John Phil",
            "phone": "55-1233-4555",
            "postalCode": "55555",
            "state": "US"
        },
        "shipperAddress": {
            "address1": "Address Line 1",
            "address2": "Address Line 2",
            "city": "DE",
            "companyName": "NewCompnay",
            "state": "US"
        },
        "shipments": [
            {
                "consigneeAddress": {
                    "address1": "Address line 1",
                    "address2": "Apt 123",
                    "city": "Test City",
                    "companyName": "Test Company",
                    "country": "IE",
                    "email": "test@email.com",
                    "idNumber": "tempor sed lab",
                    "idType": "ma",
                    "name": "Test Name",
                    "phone": "555-555-5555",
                    "postalCode": "99999",
                    "state": "GA"
                },
                "shipmentDetails": {
                    "billingRef1": "Billing Ref1",
                    "orderedProduct": "Desc1",
                    "shipmentDesc": "Shipment description",
                    "shipmentId": "12345",
                    "dgCategory": "10",
                    "dutiesPaid": "DAP",
                    "insuranceCharges": 54913.5102,
                    "freightCharges": 70888.3118,
                    "taxCharges": 57515.2394,
                    "weightUom": "kg",
                    "dimensionUom": "m",
                    "currency": "USD",
                    "isCompleteDelivery": True
                },
                "pieces": [
                    {
                        "pieceId": "4567",
                        "packingType": "SMALL",
                        "weight": 10.59
                    }
                ]
            }
        ]
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer [place OAuth access token here, without brackets]'
    }

    response = requests.post(
        'https://private-anon-a28ef17d2b-dhlecglobalshippinglabelapi.'
        'apiary-mock.com/shipping/v3/label?'
        'format=PNG&labelSize=4x6&lang=EN',
        data=json.dumps(payload), headers=headers)

    print(response)
    print(response.content)
