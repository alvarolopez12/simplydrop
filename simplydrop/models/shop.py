#!venv/bin/python
# -*- coding: utf-8 -*-

__author__ = "Alvaro Lopez Alvarez"
__copyright__ = "2019 Tible Technologies"

__link__ = "https://tibletech.com/es"
__version__ = 1.0

# -------------------------shop.py---------------------------------
# Modelo de la tabla shop en sqlalchemy
# ------------------------------------------------------------------


from datetime import datetime

from simplydrop import db


class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(80), nullable=False)
    token = db.Column(db.String(80), nullable=False)
    shop_name = db.Column(db.String(80), nullable=False)
    owner_email = db.Column(db.String(80), nullable=False)
    owner_phone = db.Column(db.String(80), nullable=False)
    carrier_json = db.Column(db.String(1000), nullable=False)
    shop_status = db.Column(db.Boolean, nullable=False)
    currency = db.Column(db.String(80), nullable=False)
    billing_id = db.Column(db.String(80), nullable=False)
    added_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Shop %r>' % self.url
