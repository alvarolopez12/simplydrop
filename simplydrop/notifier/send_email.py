#!venv/bin/python
# -*- coding: utf-8 -*-

__author__ = "Alvaro Lopez Alvarez"
__copyright__ = "2019 Tible Technologies"

__link__ = "https://tibletech.com/es"
__version__ = 1.0

# -------------------------send_email.py---------------------------------
# Fichero con script que maneja el envío de correos automáticos.
# Se utiliza la libreria smtplib para el control del servidor de correo smtp
# y la librería email para gestionar el cuerpo del correo.
# ---------------------------------------------------------------------

import email.message
import smtplib
import unidecode
from flask import render_template


# ------------------- EMAILS DE RESUMEN A CLIENTES --------------------------


def send_order_email_instant(name, user_email, country,
                             carrier, url_shop,
                             order_number, total_amount, currency,
                             total_items):

    name = unidecode.unidecode(name)
    # como el correo es chulo, partimos de una template en html
    email_content = render_template(
        'emails_templates/email_instant_order.html',
        country=country, url_shop=url_shop, carrier=carrier,
        order_number=order_number,
        total_amount=total_amount, total_items=total_items,
        name=name, currency=currency)

    msg = email.message.Message()
    msg['Subject'] = name + ' there has been a purchase in your store ' + url_shop + "!"

    msg['From'] = 'simplydrop.info@gmail.com'
    msg['To'] = user_email
    password = "simplydroppassword12"
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(email_content)

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()

    # Login Credentials for sending the mail
    s.login(msg['From'], password)

    s.sendmail(msg['From'], [msg['To']], msg.as_string())


def send_order_email_summary(name, user_email, url_shop, frequency, currency,
                             total_items, total_orders, total_amount,
                             comapare_orders_last_period, top_country,
                             top_carrier, top_product, average_products_order):

    name = unidecode.unidecode(name)

    # como el correo es chulo, partimos de una template en html
    email_content = render_template(
        'emails_templates/email_summary.html',
        name=name, url_shop=url_shop, frequency=frequency,
        currency=currency, total_items=total_items,
        total_orders=total_orders, total_amount=total_amount,
        comapare_orders_last_period=comapare_orders_last_period,
        top_country=top_country, top_carrier=top_carrier,
        top_product=top_product,
        average_products_order=average_products_order)

    msg = email.message.Message()
    msg[
        'Subject'] = name + ' heare is your ' + frequency + " report from " + url_shop + "!"

    msg['From'] = 'simplydrop.info@gmail.com'
    msg['To'] = user_email
    password = "simplydroppassword12"
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(email_content)

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()

    # Login Credentials for sending the mail
    s.login(msg['From'], password)

    s.sendmail(msg['From'], [msg['To']], msg.as_string())


# ------------------- FIN EMAILS DE RESUMEN A CLIENTES ------------------------


# --------------- EMAILS DE ERRORES DE ENVÍO CON TRANSPORTISTAS ---------------

def error_mrw_email(email_customer, order):

    msg = email.message.Message()
    msg['Subject'] = 'Your SimplyDrop2.0 billing '

    msg['From'] = 'simplydrop.info@gmail.com'
    msg['To'] = email_customer
    password = "simplydroppassword12"
    msg.add_header('Content-Type', 'text/html')

    body = """\
        We had a problem when generating order """ + str(order) + """ with MRW. 
        Check if the data you have entered in the MRW account is 
        correct and if you have received shipments outside of Spain.
        
        Greetings,
        
        The simplydrop team."""

    msg.set_payload(body)

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()

    # Login Credentials for sending the mail
    s.login(msg['From'], password)

    s.sendmail(msg['From'], [msg['To']], msg.as_string())


# -------------- FIN EMAILS DE ERRORES DE ENVÍO CON TRANSPORTISTAS ------------


# ------------------- EMAILS DE NOTIFICACIÓN DE DGPR---------------------------
# Emails que me mando a mi mismo para actuar manualmente
# según la ley de proteccion de datos

def gdpr_email_warning(webhook_topic, webhook_data):
    msg = email.message.Message()
    msg['Subject'] = 'Your SimplyDrop2.0 billing '

    msg['From'] = 'simplydrop.info@gmail.com'
    msg['To'] = 'alvaro.lopezalv@hotmail.com'
    password = "simplydroppassword12"
    msg.add_header('Content-Type', 'text/html')

    body = """ 
    Se ha lanzado un webhook del tipo: """ + webhook_topic + """ \n\n
    con la siguiente info: """ + webhook_data + """\n
    
    Suerte ;)
    """

    msg.set_payload(body)

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()

    # Login Credentials for sending the mail
    s.login(msg['From'], password)

    s.sendmail(msg['From'], [msg['To']], msg.as_string())
