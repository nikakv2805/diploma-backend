from marshmallow import Schema, fields
from marshmallow.validate import Length, OneOf, Range


class SellerSchema(Schema):
    id = fields.Int(required=True)
    username = fields.Str(required=True, validate=Length(min=6, max=80))
    email = fields.Email(required=True, validate=Length(max=255))
    is_owner = fields.Boolean(required=True)
    shop_id = fields.Int(required=True)
    surname = fields.Str(required=True, validate=Length(max=80))
    name = fields.Str(required=True, validate=Length(max=80))
    lastname = fields.Str(required=True, validate=Length(max=80))


class PlainShiftSchema(Schema):
    id = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True, validate=OneOf(["opened", "closed"]))
    seller = fields.Nested(SellerSchema(), required=True)
    open_time = fields.DateTime(required=True)


class ShiftOpenSchema(PlainShiftSchema):
    pass


class ShiftSchema(PlainShiftSchema):
    shop_id = fields.Int(required=True)
    close_time = fields.DateTime()


class ShiftCloseSchema(Schema):
    close_time = fields.DateTime(required=True)


class PlainFolderSchema(Schema):
    id = fields.Int(required=True)
    folder_name = fields.Str(required=True, validate=Length(max=80))


class ItemSchema(Schema):
    id = fields.Int(required=True)
    item_name = fields.Str(required=True, validate=Length(min=1, max=512))
    price = fields.Decimal(required=True, places=2)
    count = fields.Float(required=True)
    type = fields.Str(required=True, validate=OneOf(["SERVICE", "COMMODITY"]))
    unit = fields.Str(validate=OneOf(["PIECE", "KILOGRAM", "LITER"]))
    article = fields.Int(
        required=True,
        validate=Range(
            min=1,
            max=10**5 - 1,
            error="Article should be between 1 and 99999 inclusive.",
        ),
    )
    bar_code = fields.Int(
        required=True,
        validate=Range(
            min=10**12, max=10**13 - 1, error="Bar code should be 13-digits number."
        ),
    )
    folder = fields.Nested(PlainFolderSchema())


class ShopInfoSchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True, validate=Length(max=256))
    legal_entity = fields.Str(required=True, validate=Length(max=256))
    address = fields.Str(required=True, validate=Length(max=256))
    owner = fields.Nested(SellerSchema(), required=True)


class ReceiptSchema(Schema):
    _id = fields.Str(dump_only=True)
    items = fields.List(fields.Nested(ItemSchema()), required=True)
    seller = fields.Nested(SellerSchema(), required=True)
    shop = fields.Nested(ShopInfoSchema(), required=True)
    sum = fields.Decimal(required=True, places=2)
    datetime = fields.DateTime(required=True)
    sell_type = fields.Str(required=True, validate=OneOf(["CARD", "CASH"]))
    fn = fields.Int(dump_only=True)


class ReceiptQuerySchema(Schema):
    id = fields.Str()
    datetime_start = fields.DateTime()
    datetime_end = fields.DateTime()
    sum_start = fields.Decimal(places=2)
    sum_end = fields.Decimal(places=2)
    item_id = fields.Int()
    seller_id = fields.Int()
    sell_type = fields.Str(validate=OneOf(["CARD", "CASH"]))
    item_name_part = fields.Str(validate=Length(min=1, max=512))


class UserCheckSchema(Schema):
    user_id = fields.Int(required=True)


class ShopCheckSchema(Schema):
    shop_id = fields.Int(required=True)


class ShopAndUserCheckSchema(UserCheckSchema):
    shop_id = fields.Int(required=True)


class MessageOnlySchema(Schema):
    message = fields.Str(required=True)


class MessageWithIDSchema(MessageOnlySchema):
    id = fields.Str(required=True)


class MessageWithFNSchema(MessageOnlySchema):
    fn = fields.Int(required=True)


class MessageWithIDandFNSchema(MessageWithIDSchema):
    fn = fields.Int(required=True)


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
