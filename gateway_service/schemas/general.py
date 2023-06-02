from marshmallow import Schema, fields


class MessageOnlySchema(Schema):
    message = fields.Str(required=True)


class MessageWithIDSchema(MessageOnlySchema):
    id = fields.Int(required=True)


class MessageWithFNSchema(MessageOnlySchema):
    fn = fields.Int(required=True)


class MessageWithIDandFNSchema(MessageWithIDSchema):
    fn = fields.Int(required=True)
