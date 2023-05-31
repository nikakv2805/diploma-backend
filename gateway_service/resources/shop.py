from flask import current_app, request as flask_request, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    get_jwt_identity,
    get_jwt,
    jwt_required,
)
import requests
import json
import os

from schemas import ShopSchema, MessageOnlySchema, ShopEditSchema, ShopEditCashSchema, ShopRegisterSchema
from resources.utils import is_staff_member, is_shop_owner


blp = Blueprint("Shops", "shops", description="Operations on shops")

SHOP_SERVICE_URL = os.environ.get("SHOP_SERVICE_URL")
AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL")


@blp.route("/shop/register")
class ShopRegister(MethodView):
    @blp.arguments(ShopRegisterSchema)
    @blp.response(201, MessageOnlySchema,
                  description="Registers new shop and user")
    @blp.alt_response(409, description='Returned if there is already a shop with this address in the database,'
                                       'a user with that username or email or some internal error occurred.')
    def post(self, shop_owner_data):
        shop_data = {
            "name": shop_owner_data["shop_name"],
            "legal_entity": shop_owner_data["legal_entity"],
            "address": shop_owner_data["address"]
        }

        result = requests.post(f'{SHOP_SERVICE_URL}/shop/register',
                               data=json.dumps(shop_data),
                               headers=flask_request.headers)

        result_obj = json.loads(result.text)

        if result.status_code != 201:
            return jsonify(result_obj), result.status_code

        # current_app.logger.info(f'Shop ID: {result_obj["id"]}')

        shop_id = result_obj["id"]

        owner_data = {
            "name": shop_owner_data["name"],
            "surname": shop_owner_data["surname"],
            "lastname": shop_owner_data["lastname"],
            "email": shop_owner_data["email"],
            "password": shop_owner_data["password"],
            "username": shop_owner_data["username"],
            "is_owner": True,
            "shop_id": shop_id
        }

        result_2 = requests.post(f'{AUTH_SERVICE_URL}/register',
                                 data=json.dumps(owner_data),
                                 headers=flask_request.headers)

        result_2_obj = json.loads(result_2.text)

        if result_2.status_code != 201:
            requests.delete(f'{SHOP_SERVICE_URL}/shop/{shop_id}',
                            headers=flask_request.headers)
            return jsonify(result_obj), result_2.status_code

        owner_id = result_2_obj["id"]

        result_3 = requests.post(f'{SHOP_SERVICE_URL}/shop/{shop_id}/owner/{owner_id}',
                                 data=json.dumps(shop_data),
                                 headers=flask_request.headers)

        result_3_obj = json.loads(result_3.text)

        if result_3.status_code != 200:
            requests.delete(f'{SHOP_SERVICE_URL}/shop/{shop_id}',
                            headers=flask_request.headers)
            requests.delete(f'{AUTH_SERVICE_URL}/{owner_id}',
                            headers=flask_request.headers)
            return jsonify(result_3_obj), result_3.status_code

        return {"message": "Shop and owner's account created successfully."}


@blp.route("/shop/<int:shop_id>")
class User(MethodView):
    @jwt_required()
    @blp.response(200, ShopSchema)
    @blp.alt_response(401, description="Requester doesn't belong to the requested shop.")
    @blp.alt_response(404, description='Shop wasn\'t found')
    def get(self, shop_id):
        is_staff_member(shop_id)

        result = requests.get(f'{SHOP_SERVICE_URL}/shop/{shop_id}',
                              headers=flask_request.headers)

        result_obj = json.loads(result.text)
        return jsonify(result_obj), result.status_code

    @jwt_required(fresh=True)
    @blp.arguments(ShopEditSchema)
    @blp.response(200, ShopSchema)
    @blp.alt_response(401, description="Requester isn't requested shop's owner.")
    @blp.alt_response(404, description='Shop wasn\'t found.')
    @blp.alt_response(409, description='Returned if there is already a shop with new address in the database.')
    def put(self, shop_edit_details, shop_id):
        is_shop_owner(shop_id)

        result = requests.put(f'{SHOP_SERVICE_URL}/shop/{shop_id}',
                              data=json.dumps(shop_edit_details),
                              headers=flask_request.headers)

        result_obj = json.loads(result.text)
        return jsonify(result_obj), result.status_code

    @jwt_required(fresh=True)
    @blp.response(200, MessageOnlySchema)
    @blp.alt_response(401, description="Requester isn't requested shop's owner.")
    @blp.alt_response(404, description='Shop wasn\'t found.')
    def delete(self, shop_id):
        is_shop_owner(shop_id)

        result = requests.delete(f'{SHOP_SERVICE_URL}/shop/{shop_id}',
                                 headers=flask_request.headers)

        result_obj = json.loads(result.text)
        return jsonify(result_obj), result.status_code


@blp.route("/shop/<int:shop_id>/cash_edit")
class User(MethodView):
    @jwt_required()
    @blp.arguments(ShopEditCashSchema)
    @blp.response(200, MessageOnlySchema)
    @blp.alt_response(401, description="Requester doesn't belong to the requested shop.")
    @blp.alt_response(404, description='Shop wasn\'t found')
    def post(self, shop_cash_edit, shop_id):
        is_staff_member(shop_id)

        result = requests.post(f'{SHOP_SERVICE_URL}/shop/{shop_id}/cash_edit',
                               data=json.dumps(shop_cash_edit, default=str),
                               headers=flask_request.headers)

        result_obj = json.loads(result.text)
        return jsonify(result_obj), result.status_code
