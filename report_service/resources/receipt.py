import random
from decimal import Decimal

from bson.decimal128 import Decimal128
from bson.objectid import ObjectId
from db import db
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import (
    MessageWithIDandFNSchema,
    ReceiptQuerySchema,
    ReceiptSchema,
    UserCheckSchema,
)

blp = Blueprint("Receipt", "receipt", description="Operations on receipts")


def convert_decimal(dict_item):
    # This function iterates a dictionary looking for types of Decimal and converts them to Decimal128
    # Embedded dictionaries and lists are called recursively.
    if dict_item is None:
        return None

    for k, v in list(dict_item.items()):
        if isinstance(v, dict):
            convert_decimal(v)
        elif isinstance(v, list):
            for l in v:
                convert_decimal(l)
        elif isinstance(v, Decimal):
            dict_item[k] = Decimal128(str(v))

    return dict_item


@blp.route("/shop/<int:shop_id>/receipt")
class ReceiptList(MethodView):
    @blp.arguments(ReceiptSchema)
    @blp.arguments(UserCheckSchema, location="query")
    @blp.response(
        201, MessageWithIDandFNSchema, description="Receipt created successfully."
    )
    @blp.alt_response(400, description="There are more then 1 shift opened now.")
    @blp.alt_response(
        401, description="You should be the person who opened the shift to do this."
    )
    @blp.alt_response(404, description="Opened shifts not found.")
    def post(self, receipt_data, user_check_data, shop_id):
        opened_shifts = list(
            db.db.shifts.find({"shop_id": shop_id, "status": "opened"})
        )
        if not opened_shifts or len(opened_shifts) == 0:
            abort(404, message="No shifts are opened.")
        if len(opened_shifts) > 1:
            abort(400, message="There shouldn't be more then 1 shifts opened at once.")
        shift = opened_shifts[0]
        if shift["seller"]["id"] != user_check_data["user_id"]:
            abort(
                401,
                message="Should be the person who opened the shift to create receipts.",
            )
        receipt_data["shop_id"] = shop_id

        fn = random.randint(10**12, 10**13 - 1)  # TODO: use podatkova API

        receipt_data["fn"] = fn

        result = db.db.receipts.insert_one(convert_decimal(receipt_data))

        return {"message": "Receipt created.", "id": result.inserted_id, "fn": fn}

    @blp.arguments(ReceiptQuerySchema, location="query")
    @blp.response(200, ReceiptSchema(many=True))
    def get(self, query_data, shop_id):
        query = {"shop_id": shop_id}

        query_data = convert_decimal(query_data)

        if "id" in query_data:
            query["_id"] = ObjectId(query_data["id"])

        if "datetime_start" in query_data:
            if "datetime_end" in query_data:
                query["datetime"] = {
                    "$gte": query_data["datetime_start"],
                    "$lte": query_data["datetime_end"],
                }
            else:
                query["datetime"] = {
                    "$gte": query_data["datetime_start"],
                }
        elif "datetime_end" in query_data:
            query["datetime"] = {
                "$lte": query_data["datetime_end"],
            }

        if "sum_start" in query_data:
            if "sum_end" in query_data:
                query["sum"] = {
                    "$gte": query_data["sum_start"],
                    "$lte": query_data["sum_end"],
                }
            else:
                query["sum"] = {
                    "$gte": query_data["sum_start"],
                }
        elif "sum_end" in query_data:
            query["sum"] = {
                "$lte": query_data["sum_end"],
            }

        if "item_id" in query_data:
            query["items.id"] = query_data["item_id"]

        if "seller_id" in query_data:
            query["seller.id"] = query_data["seller_id"]

        if "sell_type" in query_data:
            query["sell_type"] = query_data["sell_type"]

        if "item_name_part" in query_data:
            query["items.item_name"] = {"$regex": query_data["item_name_part"]}

        result_receipts = list(db.db.receipts.find(query))

        return result_receipts
