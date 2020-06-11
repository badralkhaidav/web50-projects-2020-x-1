import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Adduser_class(db.Model):
    __tablename__ = "user_test"
    user_id = db.Column(db.Integer, primary_key=True)
    login_name = db.Column(db.String, nullable=False )
    password = db.Column(db.String)
