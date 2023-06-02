import os

from db import db
from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from flask_smorest import Api
from resources import FolderBlueprint, ItemBlueprint

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


def create_app():
    app = Flask(__name__)
    app.config["API_TITLE"] = "Ostrich Item Service REST API"
    app.config["API_VERSION"] = os.environ.get("API_VERSION")
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    db.init_app(app)

    Migrate(app, db)
    api = Api(app)

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(FolderBlueprint)

    return app
