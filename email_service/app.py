import os

import pika
from callbacks import create_callback_receipt, create_callback_report
from dotenv import load_dotenv
from flask import Flask, render_template
from flask.views import MethodView
from flask_mail import Mail, Message
from flask_smorest import Api, Blueprint, abort
from redis import Redis
from schemas import ReceiptSchema, ReceiverEmailSchema, ReportSchema

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_DB = int(os.environ.get("REDIS_DB", "0"))
REDIS_USER = os.environ.get("REDIS_USER", "default")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")

redis_client = Redis(
    host="gateway_redis", port=6379, db=0, username=REDIS_USER, password=REDIS_PASSWORD
)


app = Flask(__name__)

app.config["API_TITLE"] = "Ostrich Gateway REST API"
app.config["API_VERSION"] = os.environ.get("API_VERSION")
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
app.config["PROPAGATE_EXCEPTIONS"] = True

MAIL_USERNAME = os.environ.get("MAIL_USERNAME")

app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
app.config["MAIL_PORT"] = os.environ.get("MAIL_PORT")
app.config["MAIL_USERNAME"] = MAIL_USERNAME
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
mail = Mail(app)

app.logger.info(os.environ.get("MAIL_PASSWORD"))

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_DB_RECEIPTS = int(os.environ.get("REDIS_DB_RECEIPTS", "0"))
REDIS_DB_REPORTS = int(os.environ.get("REDIS_DB_REPORTS", "1"))
REDIS_USER = os.environ.get("REDIS_USER", "default")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")

redis_client_receipts = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB_RECEIPTS,
    username=REDIS_USER,
    password=REDIS_PASSWORD,
)

redis_client_reports = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB_REPORTS,
    username=REDIS_USER,
    password=REDIS_PASSWORD,
)

api = Api(app)

EmailBlueprint = Blueprint("Shops", "shops", description="Operations on shops")


@EmailBlueprint.route("/send_receipt")
class SendReceipt(MethodView):
    @EmailBlueprint.arguments(ReceiptSchema)
    @EmailBlueprint.arguments(ReceiverEmailSchema, location="query")
    def post(self, receipt_data, email_data):
        receipt_id = receipt_data["_id"]
        if redis_client_receipts.get(receipt_id):
            abort(400, message="Email is already sent")
        msg = Message(
            f"Чек у {receipt_data['shop']['name']} №{receipt_id}",
            sender=MAIL_USERNAME,
            recipients=[email_data["email"]],
        )

        for item in receipt_data["items"]:
            item["item_sum"] = "{0:.2f}".format(item["count"] * float(item["price"]))

        fee = "{0:.2f}".format(float(receipt_data["sum"]) * 0.2)
        # receipt_datetime = datetime.fromisoformat(receipt_data["datetime"])
        fancy_datetime = receipt_data["datetime"].strftime("%d.%m.%y %H:%M:%S")

        msg.html = render_template(
            "receipt.html",
            **receipt_data,
            fee=fee,
            fancy_datetime=fancy_datetime,
        )

        # msg.body = "Hello Flask message sent from Flask-Mail"
        mail.send(msg)
        redis_client_receipts.set(receipt_id, 1)
        return "Sent", 200


@EmailBlueprint.route("/send_report")
class SendReport(MethodView):
    @EmailBlueprint.arguments(ReportSchema)
    @EmailBlueprint.arguments(ReceiverEmailSchema, location="query")
    def post(self, report_data, email_data):
        report_fn = report_data["fn"]
        if redis_client_reports.get(report_fn):
            abort(400, message="Email is already sent")

        fancy_datetime = report_data["datetime"].strftime("%d.%m.%y %H:%M:%S")
        fancy_date = report_data["datetime"].strftime("%d.%m.%y")
        fancy_time = report_data["datetime"].strftime("%H:%M:%S")

        msg = Message(
            f"Z-звіт за {fancy_datetime}",
            sender=MAIL_USERNAME,
            recipients=[email_data["email"]],
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
        return "Sent", 200


api.register_blueprint(EmailBlueprint)


app.logger.info(" Connecting to rabbitMQ ...")

RABBIT_HOST = os.environ.get("RABBIT_HOST")
RABBIT_PORT = os.environ.get("RABBIT_PORT")

with app.app_context():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBIT_HOST, port=RABBIT_PORT)
        )

        channel = connection.channel()
        channel.queue_declare(queue="task_queue", durable=True)

        app.logger.info(" Waiting for messages...")

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue="receipt_queue",
            on_message_callback=create_callback_receipt(
                app, redis_client_receipts, mail
            ),
        )
        channel.basic_consume(
            queue="report_queue",
            on_message_callback=create_callback_report(
                app, redis_client_receipts, mail
            ),
        )
        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError:
        app.logger.warning(
            "Failed to connect to RabbitMQ service. Message wont be sent."
        )
    except Exception as e:
        app.logger.warn(f"Unexpected exception: {e}")
