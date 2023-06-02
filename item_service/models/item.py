import enum

from db import db


class ItemTypeEnum(enum.Enum):
    COMMODITY = 1
    SERVICE = 2


class UnitsEnum(enum.Enum):
    PIECE = 1
    KILOGRAM = 2
    LITER = 3


class ItemModel(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(512), nullable=False, index=True)
    shop_id = db.Column(db.Integer, nullable=False, index=True)
    type = db.Column(db.Enum(ItemTypeEnum), nullable=False)
    price = db.Column(db.Numeric(scale=2), nullable=False)
    unit = db.Column(db.Enum(UnitsEnum), nullable=True)
    count_existing = db.Column(db.Double, nullable=True)
    article = db.Column(db.Numeric(precision=5, scale=0), nullable=False, index=True)
    bar_code = db.Column(db.Numeric(precision=13, scale=0), index=True)

    folder_id = db.Column(
        db.Integer,
        db.ForeignKey("folders.id"),
        unique=False,
        nullable=False,
        index=True,
    )
    folder = db.relationship("ItemFolderModel", back_populates="items")

    # shop_article_const = db.UniqueConstraint('shop_id', 'article')
    # shop_bar_code_const = db.UniqueConstraint('shop_id', 'bar_code')
    # shop_name_const = db.UniqueConstraint('shop_id', 'item_name')

    __table_args__ = (
        db.UniqueConstraint("shop_id", "article"),
        db.UniqueConstraint("shop_id", "bar_code"),
        db.UniqueConstraint("shop_id", "item_name"),
        db.Index("shop_name_index", "shop_id", "item_name"),
        db.Index("shop_ar_code_index", "shop_id", "bar_code"),
        db.Index("shop_article_index", "shop_id", "article"),
        db.Index("shop_folder_index", "shop_id", "folder_id"),
    )
