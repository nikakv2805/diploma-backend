from db import db


class ShopModel(db.Model):
    __tablename__ = "shops"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    legal_entity = db.Column(db.String(256), nullable=False)
    address = db.Column(db.String(512), unique=True, nullable=False)
    owner_id = db.Column(db.Integer, nullable=True, unique=True)
