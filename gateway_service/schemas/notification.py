from marshmallow import Schema, fields


class ReceiverContactsSchema(Schema):
    email = fields.Email(required=True)
