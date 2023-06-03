import json
import os
from datetime import datetime

from flask import render_template
from flask_mail import Message

MAIL_USERNAME = os.environ.get("MAIL_USERNAME")


def create_callback_receipt(redis_client_receipts, app, mail):
    def callback_receipt(ch, method, properties, body):
        try:
            receipt_obj = json.loads(body)
        except Exception:
            app.logger.warn("Unappropriate body income type")
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
            return

        receipt_id = receipt_obj["_id"]
        if redis_client_receipts.get(receipt_id):
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
            app.logger.info("Receipt already sent")
            return

        msg = Message(
            f"Чек у {receipt_obj['shop']['name']} №{receipt_id}",
            sender=MAIL_USERNAME,
            recipients=[receipt_obj["receiver_email"]],
        )

        for item in receipt_obj["items"]:
            item["item_sum"] = "{0:.2f}".format(item["count"] * float(item["price"]))

        fee = "{0:.2f}".format(float(receipt_obj["sum"]) * 0.2)
        receipt_datetime = datetime.fromisoformat(receipt_obj["datetime"])
        fancy_datetime = receipt_datetime.strftime("%d.%m.%y %H:%M:%S")

        msg.html = render_template(
            "receipt.html",
            **receipt_obj,
            fee=fee,
            fancy_datetime=fancy_datetime,
        )

        mail.send(msg)
        redis_client_receipts.set(receipt_id, 1)

        ch.basic_ack(delivery_tag=method.delivery_tag)
        app.logger.info("Receipt sent")

    return callback_receipt


def create_callback_report(app, redis_client_reports, mail):
    def callback_report(ch, method, properties, body):
        try:
            report_data = json.loads(body)
        except Exception:
            app.logger.warn("Unappropriate body income type")
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
            return

        report_fn = report_data["fn"]
        if redis_client_reports.get(report_fn):
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
            app.logger.info("Report already sent")
            return

        report_datetime = datetime.fromisoformat(report_data["datetime"])
        fancy_datetime = report_datetime.strftime("%d.%m.%y %H:%M:%S")
        fancy_date = report_datetime.strftime("%d.%m.%y")
        fancy_time = report_datetime.strftime("%H:%M:%S")

        msg = Message(
            f"Z-звіт за {fancy_datetime}",
            sender=MAIL_USERNAME,
            recipients=[report_data["receiver_email"]],
        )

        msg.html = render_template(
            "zreport.html",
            **report_data,
            fancy_datetime=fancy_datetime,
            fancy_date=fancy_date,
            fancy_time=fancy_time,
        )

        mail.send(msg)
        redis_client_reports.set(report_fn, 1)

        ch.basic_ack(delivery_tag=method.delivery_tag)
        app.logger.info("Report sent")

    return callback_report
