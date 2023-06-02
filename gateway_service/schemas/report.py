from marshmallow import Schema, fields
from schemas.auth import SellerSchema


class XReport(Schema):
    datetime = fields.DateTime(dump_only=True)
    seller = fields.Nested(SellerSchema, dump_only=True)
    checks_count = fields.Int()
    card_sum = fields.Decimal(places=2)
    cash_sum = fields.Decimal(places=2)
    sum = fields.Decimal(places=2)


class ZReport(XReport):
    fn = fields.Int(dump_only=True)
    cash_given = fields.Decimal(places=2)
