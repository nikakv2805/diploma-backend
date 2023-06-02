from marshmallow import Schema, fields
from marshmallow.validate import Length, OneOf, Range
from models import ItemTypeEnum, UnitsEnum


class PlainItemSchema(Schema):
    id = fields.Int(dump_only=True)
    item_name = fields.Str(required=True, validate=Length(min=1, max=512))
    price = fields.Decimal(required=True, places=2)
    count_existing = fields.Float(dump_only=True)
    type = fields.Str(required=True, validate=OneOf([e.name for e in ItemTypeEnum]))
    unit = fields.Str(validate=OneOf([e.name for e in UnitsEnum]))
    article = fields.Int(
        required=True,
        validate=Range(
            min=1,
            max=10**5 - 1,
            error="Article should be between 1 and 99999 inclusive.",
        ),
    )
    # TODO: Add 6-symboled and other bar code types
    bar_code = fields.Int(
        required=True,
        validate=Range(
            min=10**12, max=10**13 - 1, error="Bar code should be 13-digits number."
        ),
    )


class PlainFolderSchema(Schema):
    id = fields.Int(dump_only=True)
    folder_name = fields.Str(required=True, validate=Length(max=80))


class FolderCreateSchema(PlainFolderSchema):
    shop_id = fields.Int(required=True, load_only=True)


class FolderReturnSchema(PlainFolderSchema):
    shop_id = fields.Int(dump_only=True)
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)


class FolderEditSchema(Schema):
    new_folder_name = fields.Str(validate=Length(max=80))


class ItemCreateSchema(PlainItemSchema):
    shop_id = fields.Int(required=True)
    folder_id = fields.Int(required=True)


class ItemReturnSchema(PlainItemSchema):
    shop_id = fields.Int(dump_only=True)
    folder = fields.Nested(PlainFolderSchema(), dump_only=True)


class ItemEditSchema(Schema):
    new_item_name = fields.Str(validate=Length(min=1, max=512))
    new_price = fields.Decimal(places=2)
    new_type = fields.Str(validate=OneOf([e.name for e in ItemTypeEnum]))
    new_unit = fields.Str(validate=OneOf([e.name for e in UnitsEnum]))
    new_article = fields.Int(
        validate=Range(
            min=1,
            max=10**5 - 1,
            error="Article should be between 1 and 99999 inclusive.",
        )
    )
    new_bar_code = fields.Int(
        validate=Range(
            min_inclusive=10**12,
            max=10**13 - 1,
            error="Bar code should be 13-digits number.",
        )
    )
    new_folder_id = fields.Int()


class ItemSearchSchema(Schema):
    name_part = fields.Str(validate=Length(min=1, max=512))
    article = fields.Int(
        validate=Range(
            min=1,
            max=10**5 - 1,
            error="Article should be between 1 and 99999 inclusive.",
        )
    )
    bar_code = fields.Int(
        validate=Range(
            min=10**12, max=10**13 - 1, error="Bar code should be 13-digits number."
        )
    )
    folder_id = fields.Int()


class ItemCountEditSchema(Schema):
    id = fields.Int(required=True)
    count_delta = fields.Float(required=True)


class ShopIDSchema(Schema):
    shop_id = fields.Int(required=True)


class MessageOnlySchema(Schema):
    message = fields.Str(required=True)
