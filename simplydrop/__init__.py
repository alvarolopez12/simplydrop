#!venv/bin/python
# -*- coding: utf-8 -*-

__author__ = "Alvaro Lopez Alvarez"
__copyright__ = "2019 Tible Technologies"

__link__ = "https://tibletech.com/es"
__version__ = 1.0

# -------------------------run.py---------------------------------
# Fichero con script principal de la aplicación Flask.
# ---------------------------------------------------------------------

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from simplydrop.config import Config as Cfg

# ----------------- INICIO DE VARIABLES Y APP ------------------
# En esta sección definimos las variables e imports para la app
# --------------------------------------------------------------

# Objeto app de la clase Flask que recibe
# como parámetro name y la carpeta de tamplates html
app = Flask(__name__, template_folder="templates")

app.config["SECRET_KEY"] = Cfg.SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = Cfg.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.debug = True

db = SQLAlchemy(app)

# están declarados aqui porque dependen de la creación de bd y app
from simplydrop import routes
from simplydrop.shopify_api_connect import *
from simplydrop.models import *
from simplydrop.notifier.send_telegram_message import \
    suscribe_telegram_webhooks

# Descomentar una vez al desplegar por primera vez. Crea los campos de la BBDD
# Para cambiar de bbdd cambiar el config.py LA BBDD debe estar creada ya.

# db.create_all()
# suscribe_telegram_webhooks(Cfg.HOST)
