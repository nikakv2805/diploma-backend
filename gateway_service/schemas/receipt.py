from marshmallow import Schema, fields
from marshmallow.validate import Length, OneOf
from schemas.item import ItemSchema


class ReceiptSchema(Schema):
    _id = fields.Str(dump_only=True)
    items = fields.List(fields.Nested(ItemSchema()), required=True)
    sum = fields.Decimal(required=True, places=2)
    datetime = fields.DateTime(required=True)
    sell_type = fields.Str(required=True, validate=OneOf(["CARD", "CASH"]))


class ReceiptQuerySchema(Schema):
    id = fields.Str()
    datetime_start = fields.DateTime()
    datetime_end = fields.DateTime()
    sum_start = fields.Decimal(places=2)
    sum_end = fields.Decimal(places=2)
    item_id = fields.Int()
    seller_id = fields.Int()
    sell_type = fields.Str(validate=OneOf(["CARD", "CASH"]))
    item_name_part = fields.Str(validate=Length(min=1, max=512))
