from flask import Flask
from redis import Redis
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

from resources import AuthBlueprint
from jwt_settings import jwt_set_up

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
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
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = int(os.environ.get("JWT_ACCESS_TOKEN_EXP", 900))
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = int(os.environ.get("JWT_REFRESH_TOKEN_EXP", 1800))
    jwt = JWTManager(app)
    jwt_set_up(jwt)

    api.register_blueprint(AuthBlueprint)

    return app
