from db import db

class BlocklistModel(db.Model):
    __tablename__ = "blocklist"

    token = db.Column(db.String(256), primary_key=True)
