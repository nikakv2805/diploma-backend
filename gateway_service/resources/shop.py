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
from resources.utils import is_staff_member, is_shop_owner, send_request


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

        result_shop_register = send_request('POST', f'{SHOP_SERVICE_URL}/shop/register', data=shop_data)

        if result_shop_register["status_code"] != 201:
            return result_shop_register["result_json"], result_shop_register["status_code"]

        shop_id = result_shop_register["result_obj"]["id"]

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

        result_owner_register = send_request('POST', f'{AUTH_SERVICE_URL}/register', data=owner_data)

        if result_owner_register["status_code"] != 201:
            send_request('DELETE', f'{SHOP_SERVICE_URL}/shop/{shop_id}')

            return result_owner_register["result_json"], result_owner_register["status_code"]

        owner_id = result_owner_register["result_obj"]["id"]

        result_shop_to_owner = send_request('POST', f'{SHOP_SERVICE_URL}/shop/{shop_id}/owner/{owner_id}')

        if result_shop_to_owner["status_code"] != 200:
            send_request('DELETE', f'{SHOP_SERVICE_URL}/shop/{shop_id}')
            send_request('DELETE', f'{AUTH_SERVICE_URL}/{owner_id}')
            return result_shop_to_owner["result_json"], result_shop_to_owner["status_code"]

        return {"message": "Shop and owner's account created successfully."}


@blp.route("/shop/<int:shop_id>")
class User(MethodView):
    @jwt_required()
    @blp.response(200, ShopSchema)
    @blp.alt_response(401, description="Requester doesn't belong to the requested shop.")
    @blp.alt_response(404, description='Shop wasn\'t found')
    def get(self, shop_id):
        is_staff_member(shop_id)
        result = send_request('GET', f'{SHOP_SERVICE_URL}/shop/{shop_id}')
        return result["result_json"], result["status_code"]

    @jwt_required(fresh=True)
    @blp.arguments(ShopEditSchema)
    @blp.response(200, ShopSchema)
    @blp.alt_response(401, description="Requester isn't requested shop's owner.")
    @blp.alt_response(404, description='Shop wasn\'t found.')
    @blp.alt_response(409, description='Returned if there is already a shop with new address in the database.')
    def put(self, shop_edit_details, shop_id):
        is_shop_owner(shop_id)
        result = send_request('PUT', f'{SHOP_SERVICE_URL}/shop/{shop_id}', data=shop_edit_details)
        return result["result_json"], result["status_code"]

    @jwt_required(fresh=True)
    @blp.response(200, MessageOnlySchema)
    @blp.alt_response(401, description="Requester isn't requested shop's owner.")
    @blp.alt_response(404, description='Shop wasn\'t found.')
    def delete(self, shop_id):
        is_shop_owner(shop_id)
        result = send_request('DELETE', f'{SHOP_SERVICE_URL}/shop/{shop_id}')
        return result["result_json"], result["status_code"]


@blp.route("/shop/<int:shop_id>/cash_edit")
class User(MethodView):
    @jwt_required()
    @blp.arguments(ShopEditCashSchema)
    @blp.response(200, MessageOnlySchema)
    @blp.alt_response(401, description="Requester doesn't belong to the requested shop.")
    @blp.alt_response(404, description='Shop wasn\'t found')
    def post(self, shop_cash_edit, shop_id):
        is_staff_member(shop_id)
        result = send_request('POST', f'{SHOP_SERVICE_URL}/shop/{shop_id}/cash_edit', data=shop_cash_edit)
        return result["result_json"], result["status_code"]
