from marshmallow import Schema, fields
from marshmallow.validate import Length, OneOf


class SellerSchema(Schema):
    id = fields.Int(required=True)
    username = fields.Str(required=True, validate=Length(min=6, max=80))
    email = fields.Email(required=True, validate=Length(max=255))
    is_owner = fields.Boolean(required=True)
    shop_id = fields.Int(required=True)
    surname = fields.Str(required=True, validate=Length(max=80))
    name = fields.Str(required=True, validate=Length(max=80))
    lastname = fields.Str(required=True, validate=Length(max=80))


class ItemSchema(Schema):
    id = fields.Int(required=True)
    item_name = fields.Str(required=True, validate=Length(min=1, max=512))
    price = fields.Decimal(required=True, places=2)
    count = fields.Float(required=True)


class ShopInfoSchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True, validate=Length(max=256))
    legal_entity = fields.Str(required=True, validate=Length(max=256))
    address = fields.Str(required=True, validate=Length(max=256))


class ReceiptSchema(Schema):
    _id = fields.Str(required=True)
    items = fields.List(fields.Nested(ItemSchema()), required=True)
    seller = fields.Nested(SellerSchema(), required=True)
    shop = fields.Nested(ShopInfoSchema(), required=True)
    sum = fields.Decimal(required=True, places=2)
    datetime = fields.DateTime(required=True)
    sell_type = fields.Str(required=True, validate=OneOf(["CARD", "CASH"]))
    fn = fields.Int(required=True)


class ReceiverEmailSchema(Schema):
    email = fields.Email(required=True)


class ReportSchema(Schema):
    datetime = fields.DateTime()
    seller = fields.Nested(SellerSchema)
    checks_count = fields.Int()
    card_sum = fields.Decimal(places=2)
    cash_sum = fields.Decimal(places=2)
    sum = fields.Decimal(places=2)
    fn = fields.Int()
    cash_given = fields.Decimal(places=2)
