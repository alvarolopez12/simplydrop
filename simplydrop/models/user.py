#!venv/bin/python
# -*- coding: utf-8 -*-

__author__ = "Alvaro Lopez Alvarez"
__copyright__ = "2019 Tible Technologies"

__link__ = "https://tibletech.com/es"
__version__ = 1.0

# -------------------------user.py---------------------------------
# Modelo de la tabla user en sqlalchemy
# ------------------------------------------------------------------

from datetime import datetime

from simplydrop import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    telegram_bot_code = db.Column(db.String(1000), nullable=False)
    telegram_chat_id = db.Column(db.String(1000), nullable=False)
    notify_freq = db.Column(db.String(80), nullable=False)
    added_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    shop = db.relationship('Shop',
                           backref=db.backref('users', lazy=True))

    def __repr__(self):
        return '<Users %r>' % self.name
