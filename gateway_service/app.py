import os

from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_smorest import Api
from jwt_settings import jwt_set_up
from rabbit import POOL, init_queues
from resources import (
    AuthBlueprint,
    FolderBlueprint,
    ItemBlueprint,
    NotificationBlueprint,
    ReceiptBlueprint,
    ReportBlueprint,
    ShiftBlueprint,
    ShopBlueprint,
)

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


def create_app():
    app = Flask(__name__)
    app.config["REDIS_URL"] = os.environ.get("REDIS_URL")

    app.config["API_TITLE"] = "Ostrich Gateway REST API"
    app.config["API_VERSION"] = os.environ.get("API_VERSION")
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["PROPAGATE_EXCEPTIONS"] = True

    api = Api(app)

    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = int(
        os.environ.get("JWT_ACCESS_TOKEN_EXP", 900)
    )
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = int(
        os.environ.get("JWT_REFRESH_TOKEN_EXP", 1800)
    )
    jwt = JWTManager(app)
    jwt_set_up(jwt)

    api.register_blueprint(AuthBlueprint)
    api.register_blueprint(ShopBlueprint)
    api.register_blueprint(FolderBlueprint)
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(ShiftBlueprint)
    api.register_blueprint(ReceiptBlueprint)
    api.register_blueprint(ReportBlueprint)
    api.register_blueprint(NotificationBlueprint)
    POOL.init(app)

    init_queues()

    return app
