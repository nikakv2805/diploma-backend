from marshmallow import Schema, fields
from marshmallow.validate import Length


class ShopSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=Length(max=256))
    legal_entity = fields.Str(required=True, validate=Length(max=256))
    address = fields.Str(required=True, validate=Length(max=256))
    owner_id = fields.Int()


class ShopEditSchema(Schema):
    new_name = fields.Str(load_only=True, validate=Length(max=256))
    new_legal_entity = fields.Str(load_only=True, validate=Length(max=256))
    new_address = fields.Str(load_only=True, validate=Length(max=256))
    new_owner_id = fields.Int(load_only=True)


class MessageOnlySchema(Schema):
    message = fields.Str(required=True)
