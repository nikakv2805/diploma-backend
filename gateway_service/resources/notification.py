import json
import os

import pika
from flask import current_app
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from rabbit import POOL
from resources.utils import is_staff_member, send_request
from schemas import MessageOnlySchema, ReceiverContactsSchema

blp = Blueprint("Notification", "notification", description="Operations on receipts")

REPORT_SERVICE_URL = os.environ.get("REPORT_SERVICE_URL")


@blp.route("/shop/<int:shop_id>/receipt/<id>/send_email")
class ReceiptSend(MethodView):
    @jwt_required()
    @blp.arguments(ReceiverContactsSchema, location="query")
    @blp.response(200, MessageOnlySchema, description="Receipt started sending.")
    @blp.alt_response(404, description="Receipt with this ID wasn't found.")
    def post(self, receiver_contacts, shop_id, id):
        is_staff_member(shop_id)

        receipt_result = send_request(
            "GET",
            f"{REPORT_SERVICE_URL}/shop/{shop_id}/receipt/{id}",
        )

        if receipt_result["status_code"] != 200:
            return receipt_result["result_json"], receipt_result["status_code"]

        receipt_object = receipt_result["result_obj"]
        receipt_object["receiver_email"] = receiver_contacts["email"]

        try:
            POOL.publish_message(
                "receipt_queue",
                json.dumps(receipt_object),
                pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ),
            )
        except Exception:
            current_app.logger.warn("Something went wrong with rabbit")
            abort(500, message="Something went wrong. Try again later")

        return {"message": "Notification sent to RabbitMQ"}


@blp.route("/shop/<int:shop_id>/report/<int:fn>/send_email")
class ReportSend(MethodView):
    @jwt_required()
    @blp.arguments(ReceiverContactsSchema, location="query")
    @blp.response(200, MessageOnlySchema, description="Report started sending.")
    @blp.alt_response(404, description="Report with this ID wasn't found.")
    def post(self, receiver_contacts, shop_id, fn):
        is_staff_member(shop_id)

        report_result = send_request(
            "GET",
            f"{REPORT_SERVICE_URL}/report/z/{fn}",
        )

        if report_result["status_code"] != 200:
            return report_result["result_json"], report_result["status_code"]

        report_object = report_result["result_obj"]
        report_object["receiver_email"] = receiver_contacts["email"]

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
            abort(500, message="Something went wrong. Try again later")

        return {"message": "Notification sent to RabbitMQ"}
