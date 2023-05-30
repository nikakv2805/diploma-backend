from flask import Flask
from flask_smorest import Api
from dotenv import load_dotenv
import os

from resources import AuthBlueprint

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)


def create_app():
    app = Flask(__name__)
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

    api.register_blueprint(AuthBlueprint)

    return app
