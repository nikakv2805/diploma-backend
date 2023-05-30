from marshmallow import Schema, fields
from marshmallow.validate import Length


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=Length(min=6, max=80))
    password = fields.Str(required=True, load_only=True)  # TODO: validation of the password


class UserRegisterSchema(UserSchema):
    email = fields.Email(required=True, load_only=True, validate=Length(max=255))
    is_owner = fields.Boolean(required=True, load_only=True)
    shop_id = fields.Int(required=True, load_only=True)
    surname = fields.Str(required=True, load_only=True)
    name = fields.Str(required=True, load_only=True)
    lastname = fields.Str(required=True, load_only=True)


class SelfEditSchema(UserSchema):
    new_password = fields.Str(required=True, load_only=True)


class OwnerRegisterSchema(UserSchema):
    email = fields.Email(required=True, load_only=True, validate=Length(max=255))
    surname = fields.Str(required=True, load_only=True)
    name = fields.Str(required=True, load_only=True)
    lastname = fields.Str(required=True, load_only=True)
