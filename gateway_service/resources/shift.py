import os

from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint
from resources.utils import is_staff_member, send_request
from schemas import MessageOnlySchema, ShiftOpenSchema, ShiftSchema

blp = Blueprint("Shift", "shift", description="Operations on shifts")

REPORT_SERVICE_URL = os.environ.get("REPORT_SERVICE_URL")
AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL")


@blp.route("/shop/<int:shop_id>/shift")
class Shift(MethodView):
    @jwt_required()
    @blp.response(
        200, ShiftSchema, description="Shift found and returned successfully."
    )
    @blp.alt_response(400, description="There are more then 1 shift opened now.")
    @blp.alt_response(404, description="Opened shifts not found")
    def get(self, shop_id):
        is_staff_member(shop_id)
        result = send_request("GET", f"{REPORT_SERVICE_URL}/shop/{shop_id}/shift")
        return result["result_json"], result["status_code"]

    @jwt_required()
    @blp.arguments(ShiftOpenSchema)
    @blp.response(201, MessageOnlySchema, description="Shift opened successfully.")
    @blp.alt_response(409, description="There is already a shift in the shop.")
    def post(self, shift_open_data, shop_id):
        is_staff_member(shop_id)
        seller_id = get_jwt_identity()
        seller_result = send_request("GET", f"{AUTH_SERVICE_URL}/user/{seller_id}")
        if seller_result["status_code"] != 200:
            return seller_result["result_json"], seller_result["status_code"]
        shift_open_data["seller"] = seller_result["result_obj"]
        result = send_request(
            "POST", f"{REPORT_SERVICE_URL}/shop/{shop_id}/shift", data=shift_open_data
        )
        return result["result_json"], result["status_code"]
