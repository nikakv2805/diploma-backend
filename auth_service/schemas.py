from marshmallow import Schema, fields
from marshmallow.validate import Length


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=Length(min=6, max=80))
    password = fields.Str(
        required=True, load_only=True
    )  # TODO: validation of the password


class UserRegisterSchema(UserSchema):
    email = fields.Email(required=True, load_only=True, validate=Length(max=255))
    is_owner = fields.Boolean(required=True, load_only=True)
    shop_id = fields.Int(required=True, load_only=True)
    surname = fields.Str(required=True, load_only=True, validate=Length(max=80))
    name = fields.Str(required=True, load_only=True, validate=Length(max=80))
    lastname = fields.Str(required=True, load_only=True, validate=Length(max=80))


class UserGetSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=Length(min=6, max=80))
    email = fields.Email(dump_only=True)
    is_owner = fields.Boolean(dump_only=True)
    shop_id = fields.Int(dump_only=True)
    surname = fields.Str(dump_only=True)
    name = fields.Str(dump_only=True)
    lastname = fields.Str(dump_only=True)


class MessageOnlySchema(Schema):
    message = fields.Str(required=True)


class SelfEditSchema(Schema):
    password = fields.Str(
        required=True, load_only=True
    )  # TODO: validation of the password
    new_password = fields.Str(required=True, load_only=True)
