#!venv/bin/python
# -*- coding: utf-8 -*-

__author__ = "Alvaro Lopez Alvarez"
__copyright__ = "2019 Tible Technologies"

__link__ = "https://tibletech.com/es"
__version__ = 1.0


# -------------------------config.py---------------------------------
# Clase donde definir la configuración del objeto app de Flask
# ---------------------------------------------------------------------


class Config(object):
    # secret key es un valor que usa Flask en algunas ocasiones para
    # hacer criptografía con ella
    # firma las webs para protegerlas de ataques Cross Side etc
    # en producción podemos darle una vuelta de seguridad a algo como:
    # os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SECRET_KEY = "CantStopAddictedToTheShinDigChopTopHeSaysImGonnaWinBig"
    HOST = "https://876535bc.ngrok.io"
    TELEGRAM_BOT_TOKEN = "807431029:AAHkobcIDOyCmMczpU8FeSuMXTjq5iKN25Q"

    SHOPIFY_CONFIG = {
        'API_KEY': 'da3162e7f03d85a896b93738a61d95d0',
        'API_SECRET': '246bea95a82835ef923d4de4d752ffd6',
        'APP_HOME': HOST,
        'CALLBACK_URL': HOST + '/install',
        'REDIRECT_URI': HOST + '/connect',
    }

    scope = [
        "write_products", "read_products", "read_script_tags",
        "write_script_tags", "read_collection_listings", "read_orders",
        "write_orders"]

    SQLALCHEMY_DATABASE_URI = \
        'mysql+pymysql://root:root@localhost:8889/SimplyDrop'
