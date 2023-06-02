import os

from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint
from resources.utils import get_shop_id, get_shop_id_params, send_request
from schemas import XReport, ZReport

blp = Blueprint("Report", "report", description="Operations on reports")

REPORT_SERVICE_URL = os.environ.get("REPORT_SERVICE_URL")


@blp.route("/report/x")
class XReports(MethodView):
    @jwt_required()
    @blp.response(201, XReport, description="Successfully created X report")
    @blp.alt_response(400, description="There are more then 1 shift opened now.")
    @blp.alt_response(
        401, description="You should be the person who opened the shift to do this."
    )
    @blp.alt_response(404, description="Opened shifts not found.")
    def post(self):
        shop_id = get_shop_id()
        user_id = get_jwt_identity()
        result = send_request(
            "POST",
            f"{REPORT_SERVICE_URL}/report/x",
            params={"user_id": user_id, "shop_id": shop_id},
        )
        return result["result_json"], result["status_code"]

    @jwt_required()
    @blp.response(200, XReport(many=True), description="Return list of x reports.")
    def get(self):
        result = send_request(
            "GET", f"{REPORT_SERVICE_URL}/report/x", params=get_shop_id_params()
        )
        return result["result_json"], result["status_code"]


@blp.route("/report/z")
class ZReports(MethodView):
    @jwt_required()
    @blp.response(201, ZReport, description="Successfully created Z report")
    @blp.alt_response(400, description="There are more then 1 shift opened now.")
    @blp.alt_response(
        401, description="You should be the person who opened the shift to do this."
    )
    @blp.alt_response(404, description="Opened shifts not found.")
    def post(self):
        shop_id = get_shop_id()
        user_id = get_jwt_identity()
        result = send_request(
            "POST",
            f"{REPORT_SERVICE_URL}/report/z",
            params={"user_id": user_id, "shop_id": shop_id},
        )
        return result["result_json"], result["status_code"]

    @jwt_required()
    @blp.response(200, ZReport(many=True), description="Return list of z reports.")
    def get(self):
        result = send_request(
            "GET", f"{REPORT_SERVICE_URL}/report/z", params=get_shop_id_params()
        )
        return result["result_json"], result["status_code"]
