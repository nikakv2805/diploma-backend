from flask import jsonify, current_app, request as flask_request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
)
import requests
import logging
import os
import json

from schemas import UserRegisterSchema, UserSchema, MessageOnlySchema, SelfEditSchema
from blocklist import BLOCKLIST

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

        if result.status_code != 200:
            return jsonify(eval(result.text)), result.status_code

        user_data = json.loads(result.text)

        access_token = create_access_token(identity=user_data["id"], fresh=True,
                                           additional_claims={'is_owner': user_data['is_owner'],
                                                              'shop_id': user_data['shop_id']})
        refresh_token = create_refresh_token(identity=user_data["id"],
                                             additional_claims={'is_owner': user_data['is_owner'],
                                                                'shop_id': user_data['shop_id']})

        return {"access_token": access_token, "refresh_token": refresh_token}


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    @blp.response(200, MessageOnlySchema)
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.put_blocklist(jti)
        return {"message": "Successfully logged out"}


@blp.route("/token/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    @blp.response(200,
                  description='Successfully refreshed token.',
                  example={"access_token": "string"})
    def post(self):
        current_user = get_jwt_identity()
        jwt = get_jwt()
        claims = {"is_owner": jwt.get("is_owner"),
                  "shop_id": jwt.get("shop_id")}
        new_token = create_access_token(identity=current_user, fresh=False,
                                        additional_claims=claims)

        jti = jwt["jti"]
        BLOCKLIST.put_blocklist(jti)

        return {"access_token": new_token}


@blp.route("/user/")
class UserActions(MethodView):
    @jwt_required()
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
