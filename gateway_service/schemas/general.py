from marshmallow import Schema, fields


class MessageOnlySchema(Schema):
    message = fields.Str(required=True)
