#!venv/bin/python
# -*- coding: utf-8 -*-

__author__ = "Alvaro Lopez Alvarez"
__copyright__ = "2019 Tible Technologies"

__link__ = "https://tibletech.com/es"
__version__ = 1.0

# --------------------ORDER_ZELERIS.PY--------------------------------
# Fichero que obtiene datos del pedido que se le ha pasado por Webhook.
# Comprueba datos y se los pasa a Zeleris en formato XML para crear orden
# ---------------------------------------------------------------------

import base64
import datetime
import hashlib

import lxml.etree.cElementTree as ET
import unidecode

# ---------------- DECLARACIÓN DE CONSTANTES -----------------
# Declaración de las variables y constantes
# ------------------------------------------------------------

# ---------------- CONSTANTES ----------------

EU_COUNTRIES = [
    "AT",
    "BE",
    "BG",
    "CY",
    "CZ",
    "DE",
    "DK",
    "EE",
    "ES",
    "FI",
    "FR",
    "GB",
    "GR",
    "HR",
    "HU",
    "IE",
    "IT",
    "LT",
    "LU",
    "LV",
    "MT",
    "NL",
    "PL",
    "PT",
    "RO",
    "SE",
    "SI",
    "SK",
]


# ---------------- FIN DE CONSTANTES ----------------


# ----------------------- CREA ORDEN  ------------------------
# Se procede a crear la orden de envio para Zeleris
# ------------------------------------------------------------

def create_order_zeleris(shop_url, webhook_data, hmac_header):
    # ---------------- VARIABLES DEL USUARIO ----------------

    user = "CLOSW"
    user_ID = "CLO"
    # shared_secret = "SECRETO_COMPARTIDO"  PRUEBAS: Para generar la contraseña
    shared_secret = "SecretoAril"  # PRODUCCIÓN: Para generar la contraseña
    msg_date = datetime.datetime. \
        now().strftime("%y%m%d%H%M%S")  # Fecha para generar la contraseña
    store_id = "ZELAL"  # ID del almacén
    document_type_id = "ENT"  # Entrega
    service_type_id = 3  # Envío al dia siguiente (España) por defecto
    refund_sn = "N"  # Sin refund
    shipping_type_id = "P"  # Portes pagados
    total_refund = 0  # Total reembolso 0
    applicant_id = "002804609"  # ID del solicitante
    consignee_id = "N/A"  # Sin ID de consignatario
    total_toll_costs = 0  # Costes de aduana: 0 Repercutidos al comprador
    das_sn = "N"  # Devolución albarán n sellado Si

    # ---------------- FIN VARIABLES DEL USUARIO ----------------

    # ---------------- VARIABLES DEL CLIENTE ----------------

    # -- Cliente --
    # Nombre del destinatario. No puede estar vacio.
    cons_name = webhook_data["shipping_address"]["name"]
    # cons_name = webhook_data["shipping_address"]["name"] if webhook_data["shipping_address"]["name"] else "0"
    # cons_name = substr($cons_name, 0, 50);

    # No se pide en Shopify, pero es obligatorio en Zeleris
    cons_nif = webhook_data["shipping_address"]["company"]
    # cons_nif = !empty($data["shipping_address"]["company"]) ? $data["shipping_address"]["company"]: "0";
    # cons_nif = webhook_data["shipping_address"]["company"] if webhook_data["shipping_address"]["company"] else "0"

    # cons_nif = custom_specialchars($cons_nif);
    # cons_nif = substr($cons_nif, 0, 9);

    # Direccion del destinatario. No puede estar vacio.
    cons_address = webhook_data["shipping_address"]["address1"]
    cons_address = " " + webhook_data["shipping_address"]["address2"]
    # cons_address = trim($cons_address);
    # cons_address = !empty($cons_address) ? custom_specialchars($cons_address): "0";
    # cons_address = substr($cons_address, 0, 100);

    # Poblacion del destinatario.
    cons_town = webhook_data["shipping_address"]["city"]
    # cons_town = custom_specialchars($cons_town);
    # cons_town = substr($cons_town, 0, 50);

    # Provincia del destinatario. No puede estar vacio (al menos poblacion o provincia).
    cons_province = webhook_data["shipping_address"]["province"]
    # cons_province = empty($cons_province) ? $cons_town: custom_specialchars($cons_province);
    # cons_province = substr($cons_province, 0, 50);

    # Codigo postal del destinatario. No puede estar vacio.
    cons_zip = webhook_data["shipping_address"]["zip"]
    # cons_zip = !empty($cons_zip) ? custom_specialchars($cons_zip): "0";
    # cons_zip = substr($cons_zip, 0, 20);

    # Pais del destinatario (Código ISO del país P.E “ES”). No puede estar vacío.
    cons_country = webhook_data["shipping_address"]["country_code"]
    # cons_country = !empty($cons_country) ? custom_specialchars($cons_country): "0";
    # cons_country = substr($cons_country, 0, 2);

    # Teléfono del destinatario. No puede estar vacío.
    cons_phone = webhook_data["shipping_address"]["phone"]
    # cons_phone = !empty($cons_phone) ? custom_specialchars($cons_phone): "0";
    # cons_phone = substr($cons_phone, 0, 50);

    # Email del destinatario
    cons_email = webhook_data["email"]
    # cons_email = !empty($data["email"]) ? custom_specialchars($cons_email): "0";
    # cons_email = substr($cons_email, 0, 80);

    # -- Aduanas - -
    toll_description = ""  # Descripción del pedio para aduanas: Nombres de los productos
    for line_item_data in webhook_data["line_items"]:
        toll_description = toll_description + line_item_data["title"] + " "

    if not toll_description:
        global toll_description
        toll_description = "0"

    total_toll_amount = webhook_data[
        "total_line_items_price"]  # Importe pedido para declarar en aduana: total sin descuento

    if not total_toll_amount:
        global total_toll_amount
        total_toll_amount = "1.0"

    total_items = len(
        webhook_data["line_items"])  # Total artículos en el pedido

    client_weight = webhook_data["total_weight"]  # Peso

    # ---------------- FIN VARIABLES DEL CLIENTE ----------------

    # ------------ COMPROBACIÓN TIPO DE SERVICIO ----------------

    # Si no es España el código es 22 por defecto. UE (Carretera Internacional)
    if webhook_data["shipping_address"]["country_code"] != "ES":
        service_type_id = 22

    # Si el pedido es de fuera de la UE
    elif not (
            webhook_data["shipping_address"]["country_code"] in EU_COUNTRIES):
        service_type_id = 12

    # Envío NO gratuito.
    elif webhook_data.get(["shipping_lines"][0]["price"]) and \
            webhook_data["shipping_lines"][0]["price"] != 0 \
            and webhook_data["shipping_address"]["country_code"] != "ES":
        service_type_id = 12

    # Si el precio de la orden es de más de 75€ y no va a España
    elif webhook_data["shipping_address"]["country_code"] != "ES" and \
            webhook_data["total_price"] > 75:
        service_type_id = 12

    # Si va a Canarias o Baleares: Los códigos postales de Canarias empiezan por 35 y 38. Baleares es
    # código 3 que es lo que vale por defecto.
    elif (webhook_data["shipping_address"]["country_code"] == "ES") and \
            (("38" in webhook_data[["shipping_address"]["zip"]]) or (
                    "35" in webhook_data[["shipping_address"]["zip"]])):
        service_type_id = 12

    # ---------------- FIN COMPROBACIÓN TIPO DE SERVICIO ----------------

    # ---------------- GENERACIÓN DE LA CLAVE ----------------

    # Formamos la cadena con el usuario, el secreto compartido y fecha al revés
    # Se pasa esta cadena a formato UTF-8
    password = user + shared_secret + msg_date[::-1]
    password = unidecode(password, "utf-8")
    password = hashlib.sha256(password)

    # El resultado del algoritmo se convierte en una cadena en Base64
    password = base64.b64encode(password)

    # Mismo proceso pero con la cadena generada hasta ahora.
    # Usuario+password+fecha_invertida -> UTF-8 -> SHA-256-> Base64

    password = user + password + msg_date[::-1]
    password = unidecode(password, "utf-8")
    password = hashlib.sha256(password)
    password = base64.b64encode(password)

    # ---------------- FIN GENERACIÓN DE LA CLAVE ----------------

    # ---------------- CONSTRUCCIÓN XML ----------------

    SOAP_NS = 'http://schemas.xmlsoap.org/soap/envelope/'
    WEB_NS = 'http://webservice.ucr.oga.kesws.crimsonlogic.com/'
    ns_map = {'soapenv': SOAP_NS, 'web': WEB_NS}

    env = ET.Element(ET.QName(SOAP_NS, 'Envelope'), nsmap=ns_map)
    head = ET.SubElement(env, ET.QName(SOAP_NS, 'Header'), nsmap=ns_map)
    body = ET.SubElement(env, ET.QName(SOAP_NS, 'Body'), nsmap=ns_map)
    val = ET.SubElement(body, ET.QName(WEB_NS, 'ucrValidation'), nsmap=ns_map)
    arg = ET.SubElement(val, 'arg0')
    arg.text = ET.CDATA('Here is where you can put your CDATA text!!!')

    # now you have XML!
    print(ET.tostring(env, pretty_print=True))
