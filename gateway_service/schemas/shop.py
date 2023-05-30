from marshmallow import Schema, fields
from marshmallow.validate import Length


class ShopSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=Length(max=256))
    legal_entity = fields.Str(required=True, validate=Length(max=256))
    address = fields.Str(required=True, validate=Length(max=256))
    current_cash = fields.Decimal(places=2, dump_only=True)


class ShopRegisterSchema(Schema):
    # Shop part
    shop_name = fields.Str(required=True, validate=Length(max=256))
    legal_entity = fields.Str(required=True, validate=Length(max=256))
    address = fields.Str(required=True, validate=Length(max=256))
    # User part
    username = fields.Str(required=True, validate=Length(min=6, max=80))
    password = fields.Str(required=True, load_only=True)
    email = fields.Email(required=True, load_only=True, validate=Length(max=255))
    surname = fields.Str(required=True, load_only=True)
    name = fields.Str(required=True, load_only=True)
    lastname = fields.Str(required=True, load_only=True)


class ShopEditSchema(Schema):
    new_name = fields.Str(load_only=True, validate=Length(max=256))
    new_legal_entity = fields.Str(load_only=True, validate=Length(max=256))
    new_address = fields.Str(load_only=True, validate=Length(max=256))
    new_owner_id = fields.Int(load_only=True)


class ShopEditCashSchema(Schema):
    cash_delta = fields.Decimal(places=2, load_only=True)
