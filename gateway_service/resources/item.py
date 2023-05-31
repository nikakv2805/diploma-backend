from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    get_jwt_identity,
    get_jwt,
    jwt_required,
)
import os

from schemas import ItemCreateSchema, MessageOnlySchema, ItemReturnSchema, \
    ItemEditSchema, ItemCountEditSchema, ItemSearchSchema
from resources.utils import is_staff_member, is_shop_owner, send_request, get_shop_id, get_shop_id_params


blp = Blueprint("Item", "item", description="Operations on items")

ITEM_SERVICE_URL = os.environ.get("ITEM_SERVICE_URL")


@blp.route("/item")
class ItemCreate(MethodView):
    @jwt_required()
    @blp.arguments(ItemCreateSchema)
    @blp.response(201, MessageOnlySchema, description="Item created successfully.")
    @blp.alt_response(404, description="Folder with that id wasn't found.")
    @blp.alt_response(409, description="There is an item like this in the shop.")
    def post(self, item_data):
        item_data["shop_id"] = get_shop_id()
        result = send_request('POST', f"{ITEM_SERVICE_URL}/item", data=item_data)
        return result["result_json"], result["status_code"]


@blp.route("/shop/<int:shop_id>/item")
class ItemList(MethodView):
    @jwt_required()
    @blp.response(200, ItemReturnSchema(many=True), description="Items returned successfully.")
    def get(self, shop_id):
        is_staff_member(shop_id)
        result = send_request('GET', f"{ITEM_SERVICE_URL}/shop/{shop_id}/item")
        return result["result_json"], result["status_code"]


@blp.route("/item/<int:item_id>")
class Item(MethodView):
    @jwt_required()
    @blp.response(200, ItemReturnSchema, description="Item returned successfully.")
    @blp.alt_response(404, description="Item wasn't found.")
    def get(self, item_id):
        result = send_request('GET', f"{ITEM_SERVICE_URL}/item/{item_id}",
                              params=get_shop_id_params())
        return result["result_json"], result["status_code"]

    @jwt_required()
    @blp.arguments(ItemEditSchema)
    @blp.response(200, ItemReturnSchema, description="Item edited successfully.")
    @blp.alt_response(404, description="Item or new folder wasn't found.")
    @blp.alt_response(409, description="One of new item's name, article or barcode is already in the DB.")
    def put(self, item_edit_data, item_id):
        result_put = send_request('PUT', f"{ITEM_SERVICE_URL}/item/{item_id}", data=item_edit_data,
                                  params=get_shop_id_params())
        return result_put["result_json"], result_put["status_code"]

    @jwt_required()
    @blp.response(200, MessageOnlySchema, description="Item deleted successfully.")
    @blp.alt_response(404, description="Item wasn't found")
    def delete(self, item_id):
        result_delete = send_request('DELETE', f"{ITEM_SERVICE_URL}/item/{item_id}",
                                     params=get_shop_id_params())
        return result_delete["result_json"], result_delete["status_code"]


@blp.route("/item/update_counts")
class ItemCounts(MethodView):
    @jwt_required()
    @blp.arguments(ItemCountEditSchema(many=True))
    @blp.response(200, MessageOnlySchema, description="All item's counts updated")
    @blp.alt_response(404, description="One of the items wasn't found.")
    def put(self, items_count_edit_data):
        shop_id = get_jwt().get("shop_id")
        result = send_request('PUT', f"{ITEM_SERVICE_URL}/item/update_counts",
                                     data=items_count_edit_data, params=get_shop_id_params())
        return result["result_json"], result["status_code"]


@blp.route("/shop/<int:shop_id>/item/search")
class ItemSearch(MethodView):
    @jwt_required()
    @blp.arguments(ItemSearchSchema, location="query")
    @blp.response(200, ItemReturnSchema(many=True), description="Search successful.")
    def get(self, item_search_params, shop_id):
        is_staff_member(shop_id)
        result = send_request('GET', f"{ITEM_SERVICE_URL}/shop/{shop_id}/item/search", params=item_search_params)
        return result["result_json"], result["status_code"]
