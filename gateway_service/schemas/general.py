from marshmallow import Schema, fields


class MessageOnlySchema(Schema):
    message = fields.Str(required=True)


class MessageWithIDSchema(Schema):
    id = fields.Int(required=True)
