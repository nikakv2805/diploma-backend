import os

from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint
from resources.utils import get_shop_id_params, is_staff_member, send_request
from schemas import (
    MessageWithIDandFNSchema,
    ReceiptLoadSchema,
    ReceiptQuerySchema,
    ReceiptReturnSchema,
)

blp = Blueprint("Receipt", "receipt", description="Operations on receipts")

REPORT_SERVICE_URL = os.environ.get("REPORT_SERVICE_URL")
ITEM_SERVICE_URL = os.environ.get("ITEM_SERVICE_URL")
AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL")
SHOP_SERVICE_URL = os.environ.get("SHOP_SERVICE_URL")


@blp.route("/shop/<int:shop_id>/receipt")
class ReceiptList(MethodView):
    @jwt_required()
    @blp.arguments(ReceiptLoadSchema)
    @blp.response(
        201, MessageWithIDandFNSchema, description="Receipt created successfully."
    )
    @blp.alt_response(400, description="There are more then 1 shift opened now.")
    @blp.alt_response(
        401, description="You should be the person who opened the shift to do this."
    )
    @blp.alt_response(404, description="Opened shifts not found.")
    def post(self, receipt_data, shop_id):
        is_staff_member(shop_id)
        user_id = get_jwt_identity()

        seller_result = send_request("GET", f"{AUTH_SERVICE_URL}/user/{user_id}")
        if seller_result["status_code"] != 200:
            return seller_result["result_json"], seller_result["status_code"]

        shop_result = send_request("GET", f"{SHOP_SERVICE_URL}/shop/{shop_id}")
        if shop_result["status_code"] != 200:
            return shop_result["result_json"], shop_result["status_code"]

        owner_result = send_request(
            "GET", f"{AUTH_SERVICE_URL}/user/{shop_result['result_obj']['owner_id']}"
        )
        if seller_result["status_code"] != 200:
            return seller_result["result_json"], seller_result["status_code"]

        update_counts_data = [
            {"id": item["id"], "count_delta": -item["count"]}
            for item in receipt_data["items"]
            if item["type"] != "SERVICE"
        ]

        if len(update_counts_data) > 0:
            result_update_counts = send_request(
                "PUT",
                f"{ITEM_SERVICE_URL}/item/update_counts",
                data=update_counts_data,
                params=get_shop_id_params(),
            )
            if result_update_counts["status_code"] != 200:
                return (
                    result_update_counts["result_json"],
                    result_update_counts["status_code"],
                )

        receipt_data["seller"] = seller_result["result_obj"]

        shop_obj = shop_result["result_obj"]
        shop_obj.pop("owner_id")
        shop_obj["owner"] = owner_result["result_obj"]

        receipt_data["shop"] = shop_obj

        result_receipt = send_request(
            "POST",
            f"{REPORT_SERVICE_URL}/shop/{shop_id}/receipt",
            params={"user_id": user_id},
            data=receipt_data,
        )

        if result_receipt["status_code"] != 201 and len(update_counts_data) > 0:
            update_counts_data_back = [
                {"id": item["id"], "count_delta": item["count"]}
                for item in receipt_data["items"]
            ]

            send_request(
                "PUT",
                f"{ITEM_SERVICE_URL}/item/update_counts",
                data=update_counts_data_back,
                params=get_shop_id_params(),
            )

        return result_receipt["result_json"], result_receipt["status_code"]

    @jwt_required()
    @blp.arguments(ReceiptQuerySchema, location="query")
    @blp.response(200, ReceiptReturnSchema(many=True))
    def get(self, query_data, shop_id):
        is_staff_member(shop_id)

        result = send_request(
            "GET",
            f"{REPORT_SERVICE_URL}/shop/{shop_id}/receipt",
            params=query_data,
        )

        return result["result_json"], result["status_code"]
