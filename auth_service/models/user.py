from db import db


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    surname = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=True)
    password = db.Column(db.String(87), nullable=False)
    is_owner = db.Column(db.Boolean, nullable=False)
    shop_id = db.Column(db.Integer, nullable=False)
