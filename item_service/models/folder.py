from db import db

class ItemFolderModel(db.Model):
    __tablename__ = 'folders'

    id = db.Column(db.Integer, primary_key=True)
    folder_name = db.Column(db.String(80), nullable=False)
    shop_id = db.Column(db.Integer, nullable=False, index=True)

    items = db.relationship("ItemModel", back_populates="folder", lazy="dynamic", cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint('shop_id', 'folder_name'),
        db.Index('shop_foldername_index', 'shop_id', 'folder_name'),
    )
