import os
import pika
import json

from flask import current_app, jsonify
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint
from resources.utils import get_shop_id, get_shop_id_params, send_request
from schemas import XReport, ZReport, ZReportWWarning
from rabbit import POOL

blp = Blueprint("Report", "report", description="Operations on reports")

REPORT_SERVICE_URL = os.environ.get("REPORT_SERVICE_URL")
SHOP_SERVICE_URL = os.environ.get("SHOP_SERVICE_URL")
AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL")


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
    @blp.response(201, ZReportWWarning, description="Successfully created Z report")
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

        if result["status_code"] == 201:
            result_shop = send_request("GET", f"{SHOP_SERVICE_URL}/shop/{shop_id}")

            if result_shop["status_code"] != 200:
                result_warning = result["result_obj"]
                result_warning["warning"] = "Can't send email to the owner."
                return jsonify(result_warning), result["status_code"]

            owner_id = result_shop["result_obj"]["owner_id"]

            result_owner = send_request("GET", f"{AUTH_SERVICE_URL}/user/{owner_id}")

            if result_owner["status_code"] != 200:
                result_warning = result["result_obj"]
                result_warning["warning"] = "Can't send email to the owner."
                return jsonify(result_warning), result["status_code"]

            owner_email = result_owner["result_obj"]["email"]

            report_object = result["result_obj"]
            report_object["receiver_email"] = owner_email

            try:
                POOL.publish_message(
                    "report_queue",
                    json.dumps(report_object),
                    pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                    ),
                )
            except Exception:
                current_app.logger.warn("Something went wrong with rabbit")
                result_warning = result["result_obj"]
                result_warning["warning"] = "Can't send email to the owner."
                return jsonify(result_warning), result["status_code"]

        return result["result_json"], result["status_code"]

    @jwt_required()
    @blp.response(200, ZReport(many=True), description="Return list of z reports.")
    def get(self):
        result = send_request(
            "GET", f"{REPORT_SERVICE_URL}/report/z", params=get_shop_id_params()
        )
        return result["result_json"], result["status_code"]
