#!venv/bin/python
# -*- coding: utf-8 -*-

__author__ = "Alvaro Lopez Alvarez"
__copyright__ = "2019 Tible Technologies"

__link__ = "https://tibletech.com/es"
__version__ = 1.0

# -------------------------items.py---------------------------------
# Modelo de la tabla items en sqlalchemy
# ------------------------------------------------------------------

from datetime import datetime

from simplydrop import db


class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(80), nullable=True)
    order_number = db.Column(db.Integer, nullable=True)
    quantity = db.Column(db.Integer, nullable=True)
    title = db.Column(db.String(80), nullable=True)
    image = db.Column(db.String(1000), nullable=True)
    price = db.Column(db.String(80), nullable=True)
    weigth = db.Column(db.Integer, nullable=True)
    added_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    shop = db.relationship('Shop',
                           backref=db.backref('items', lazy=True))

    def __repr__(self):
        return '<Items %r>' % self.id
