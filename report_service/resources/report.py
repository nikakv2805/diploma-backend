import random
from datetime import datetime
from decimal import Decimal

import numpy as np
from db import db
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from resources.receipt import convert_decimal
from schemas import ShopAndUserCheckSchema, ShopCheckSchema, XReport, ZReport

blp = Blueprint("Report", "report", description="Operations on reports")


@blp.route("/report/x")
class XReports(MethodView):
    @blp.arguments(ShopAndUserCheckSchema, location="query")
    @blp.response(201, XReport, description="Successfully created X report")
    @blp.alt_response(400, description="There are more then 1 shift opened now.")
    @blp.alt_response(
        401, description="You should be the person who opened the shift to do this."
    )
    @blp.alt_response(404, description="Opened shifts not found.")
    def post(self, shop_user_check_data):
        shop_id = shop_user_check_data["shop_id"]
        opened_shifts = list(
            db.db.shifts.find({"shop_id": shop_id, "status": "opened"})
        )
        if not opened_shifts or len(opened_shifts) == 0:
            abort(404, message="No shifts are opened.")
        if len(opened_shifts) > 1:
            abort(400, message="There shouldn't be more then 1 shifts opened at once.")
        shift = opened_shifts[0]
        if shift["seller"]["id"] != shop_user_check_data["user_id"]:
            abort(
                401,
                message="Should be the person who opened the shift to create receipts.",
            )

        receipts_cash_query = {
            "shop_id": shop_id,
            "datetime": {"$gt": shift["open_time"]},
            "sell_type": "CASH",
        }
        result_receipts_cash = list(db.db.receipts.find(receipts_cash_query))

        receipts_card_query = {
            "shop_id": shop_id,
            "datetime": {"$gt": shift["open_time"]},
            "sell_type": "CARD",
        }
        result_receipts_card = list(db.db.receipts.find(receipts_card_query))

        report_time = datetime.now()

        checks_count = len(result_receipts_card) + len(result_receipts_cash)
        checks_cash_sum = Decimal(
            np.sum([receipt["sum"].to_decimal() for receipt in result_receipts_cash])
        )
        checks_card_sum = Decimal(
            np.sum([receipt["sum"].to_decimal() for receipt in result_receipts_card])
        )

        report = {
            "seller": shift["seller"],
            "datetime": report_time,
            "checks_count": checks_count,
            "cash_sum": checks_cash_sum,
            "card_sum": checks_card_sum,
            "sum": checks_card_sum + checks_cash_sum,
        }

        db.db.reports.insert_one(
            {**convert_decimal(report), "type": "X", "shop_id": shop_id}
        )

        return report

    @blp.arguments(ShopCheckSchema, location="query")
    @blp.response(200, XReport(many=True), description="Return list of x reports.")
    def get(self, shop_check_data):
        x_reports = list(
            db.db.reports.find({"type": "X", "shop_id": shop_check_data["shop_id"]})
        )

        return x_reports


@blp.route("/report/z")
class ZReports(MethodView):
    @blp.arguments(ShopAndUserCheckSchema, location="query")
    @blp.response(201, ZReport, description="Successfully created Z report")
    @blp.alt_response(400, description="There are more then 1 shift opened now.")
    @blp.alt_response(
        401, description="You should be the person who opened the shift to do this."
    )
    @blp.alt_response(404, description="Opened shifts not found.")
    def post(self, shop_user_check_data):
        shop_id = shop_user_check_data["shop_id"]
        opened_shifts = list(
            db.db.shifts.find({"shop_id": shop_id, "status": "opened"})
        )
        if not opened_shifts or len(opened_shifts) == 0:
            abort(404, message="No shifts are opened.")
        if len(opened_shifts) > 1:
            abort(400, message="There shouldn't be more then 1 shifts opened at once.")
        shift = opened_shifts[0]
        if shift["seller"]["id"] != shop_user_check_data["user_id"]:
            abort(
                401,
                message="Should be the person who opened the shift to create receipts.",
            )

        receipts_cash_query = {
            "shop_id": shop_id,
            "datetime": {"$gt": shift["open_time"]},
            "sell_type": "CASH",
        }
        result_receipts_cash = list(db.db.receipts.find(receipts_cash_query))

        receipts_card_query = {
            "shop_id": shop_id,
            "datetime": {"$gt": shift["open_time"]},
            "sell_type": "CARD",
        }
        result_receipts_card = list(db.db.receipts.find(receipts_card_query))

        report_time = datetime.now()

        checks_count = len(result_receipts_card) + len(result_receipts_cash)
        checks_cash_sum = Decimal(
            np.sum([receipt["sum"].to_decimal() for receipt in result_receipts_cash])
        )
        checks_card_sum = Decimal(
            np.sum([receipt["sum"].to_decimal() for receipt in result_receipts_card])
        )

        fn = random.randint(10**12, 10**13 - 1)  # TODO: use podatkova API

        report = {
            "seller": shift["seller"],
            "datetime": report_time,
            "checks_count": checks_count,
            "cash_sum": checks_cash_sum,
            "card_sum": checks_card_sum,
            "sum": checks_card_sum + checks_cash_sum,
            "fn": fn,
            "cash_given": checks_cash_sum,
        }

        shift["status"] = "closed"
        shift["close_time"] = report_time
        db.db.shifts.update_one(
            {"shop_id": shop_id, "status": "opened"}, {"$set": shift}
        )

        db.db.reports.insert_one(
            {**convert_decimal(report), "type": "Z", "shop_id": shop_id}
        )

        return report

    @blp.arguments(ShopCheckSchema, location="query")
    @blp.response(200, ZReport(many=True), description="Return list of z reports.")
    def get(self, shop_check_data):
        z_reports = list(
            db.db.reports.find({"type": "Z", "shop_id": shop_check_data["shop_id"]})
        )

        return z_reports


@blp.route("/report/z/<int:fn>")
class ZReport(MethodView):
    @blp.response(200, ZReport, description="Found successfully")
    @blp.alt_response(404, description="Report not found")
    def get(self, fn):
        result_report = db.db.reports.find_one_or_404({"type": "Z", "fn": fn})
        return result_report
