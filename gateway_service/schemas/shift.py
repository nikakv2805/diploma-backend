from marshmallow import Schema, fields
from marshmallow.validate import OneOf
from schemas.auth import SellerSchema


class PlainShiftSchema(Schema):
    id = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True, validate=OneOf(["opened", "closed"]))
    seller = fields.Nested(SellerSchema(), required=True)
    open_time = fields.DateTime(required=True)


class ShiftOpenSchema(Schema):
    open_time = fields.DateTime(required=True)


class ShiftSchema(PlainShiftSchema):
    shop_id = fields.Int(required=True)
    close_time = fields.DateTime()
