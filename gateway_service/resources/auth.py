from flask import jsonify, current_app, request as flask_request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
import requests
import logging
import os
import json

from schemas import UserRegisterSchema, UserSchema, MessageOnlySchema, SelfEditSchema


blp = Blueprint("Auth", "auth", description="Operations on users and with JWT tokens")

AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    @blp.response(201, MessageOnlySchema,
                  description="Registers new user with unique email and username")
    @blp.alt_response(409, description='Returned if user with this email or username already exists.')
    def post(self, user_data):
        # current_app.logger.info(type(user_data))
        result = requests.post(f'{AUTH_SERVICE_URL}/register',
                               data=json.dumps(user_data),
                               headers=flask_request.headers)
        return jsonify(eval(result.text)), result.status_code

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(200,
                  description='Successfully log in.',
                  example={"access_token": "string", "refresh_token": "string"})
    @blp.alt_response(401,
                      description='Invalid credentials.')
    def post(self, user_data):
        result = requests.post(f'{AUTH_SERVICE_URL}/login',
                               data=json.dumps(user_data),
                               headers=flask_request.headers)
        return jsonify(eval(result.text)), result.status_code


@blp.route("/logout")
class UserLogout(MethodView):
    @blp.response(200, MessageOnlySchema)
    def post(self):
        result = requests.post(f'{AUTH_SERVICE_URL}/logout',
                               headers=flask_request.headers)
        return jsonify(eval(result.text)), result.status_code


@blp.route("/token/refresh")
class TokenRefresh(MethodView):
    @blp.response(200,
                  description='Successfully refreshed token.',
                  example={"access_token": "string"})
    def post(self):
        result = requests.post(f'{AUTH_SERVICE_URL}/refresh',
                               headers=flask_request.headers)
        return jsonify(eval(result.text)), result.status_code


@blp.route("/user/")
class UserActions(MethodView):
    @blp.arguments(SelfEditSchema)
    @blp.response(200, MessageOnlySchema,
                  description='Successfully changed myself.')
    @blp.alt_response(401,
                      description='Invalid credentials.')
    def put(self, user_data):
        result = requests.put(f'{AUTH_SERVICE_URL}/',
                              data=json.dumps(user_data),
                              headers=flask_request.headers)
        return jsonify(eval(result.text)), result.status_code
