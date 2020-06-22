#!venv/bin/python
# -*- coding: utf-8 -*-

__author__ = "Alvaro Lopez Alvarez"
__copyright__ = "2019 Tible Technologies"

__link__ = "https://tibletech.com/es"
__version__ = 1.0

# -------------------------orders.py---------------------------------
# Modelo de la tabla orders en sqlalchemy
# ------------------------------------------------------------------

from datetime import datetime

from simplydrop import db


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shopify_order_number = db.Column(db.Integer, nullable=False)
    customer_email = db.Column(db.String(100), nullable=True)
    customer_country = db.Column(db.String(100), nullable=False)
    customer_country_code = db.Column(db.String(10), nullable=False)
    customer_city = db.Column(db.String(100), nullable=True)
    customer_province = db.Column(db.String(100), nullable=True)
    customer_zip = db.Column(db.String(100), nullable=True)
    customer_address1 = db.Column(db.String(100), nullable=False)
    customer_address2 = db.Column(db.String(100), nullable=True)
    amount_no_taxes = db.Column(db.String(100), nullable=False)
    amount_no_shipping = db.Column(db.String(100), nullable=False)
    total_amount = db.Column(db.String(100), nullable=False)
    order_status = db.Column(db.String(100), nullable=False)
    shipping_type = db.Column(db.String(100), nullable=True)
    currency = db.Column(db.String(100), nullable=True)
    carrier = db.Column(db.String(100), nullable=True)
    label = db.Column(db.String(100), nullable=True)

    added_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    shop = db.relationship('Shop',
                           backref=db.backref('orders', lazy=True))

    def __repr__(self):
        return '<Orders %r>' % self.id
