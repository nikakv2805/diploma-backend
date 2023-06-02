import os

from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint
from resources.utils import (
    get_shop_id,
    get_shop_id_params,
    is_staff_member,
    send_request,
)
from schemas import (
    FolderEditSchema,
    FolderReturnSchema,
    MessageOnlySchema,
    MessageWithIDSchema,
    PlainFolderSchema,
)

blp = Blueprint("Folder", "folder", description="Operations on item folders")

ITEM_SERVICE_URL = os.environ.get("ITEM_SERVICE_URL")


@blp.route("/folder")
class FolderCreate(MethodView):
    @jwt_required()
    @blp.arguments(PlainFolderSchema)
    @blp.response(201, MessageWithIDSchema, description="Folder created successfully.")
    @blp.alt_response(404, description="Folder with that id wasn't found.")
    @blp.alt_response(409, description="There is an item like this in the shop.")
    def post(self, folder_data):
        folder_data["shop_id"] = get_shop_id()
        result = send_request("POST", f"{ITEM_SERVICE_URL}/folder", data=folder_data)
        return result["result_json"], result["status_code"]


@blp.route("/shop/<int:shop_id>/folder")
class FolderList(MethodView):
    @jwt_required()
    @blp.response(
        200, FolderReturnSchema(many=True), description="Folders returned successfully."
    )
    def get(self, shop_id):
        is_staff_member(shop_id)
        result = send_request("GET", f"{ITEM_SERVICE_URL}/shop/{shop_id}/folder")
        return result["result_json"], result["status_code"]


@blp.route("/folder/<int:folder_id>")
class Folder(MethodView):
    @jwt_required()
    @blp.response(200, FolderReturnSchema, description="Folder returned successfully.")
    @blp.alt_response(404, description="Folder with this id wasn't found.")
    def get(self, folder_id):
        result = send_request(
            "GET", f"{ITEM_SERVICE_URL}/folder/{folder_id}", params=get_shop_id_params()
        )
        return result["result_json"], result["status_code"]

    @jwt_required()
    @blp.arguments(FolderEditSchema)
    @blp.response(200, FolderReturnSchema, description="Folder edited successfully.")
    @blp.alt_response(404, description="Folder with this id wasn't found.")
    @blp.alt_response(409, description="There is an item with this name in the shop.")
    def put(self, folder_edit_data, folder_id):
        result_put = send_request(
            "PUT",
            f"{ITEM_SERVICE_URL}/folder/{folder_id}",
            data=folder_edit_data,
            params=get_shop_id_params(),
        )
        return result_put["result_json"], result_put["status_code"]

    @jwt_required()
    @blp.response(200, MessageOnlySchema, description="Folder deleted successfully.")
    @blp.alt_response(404, description="Folder with this id wasn't found.")
    @blp.alt_response(409, description="There are still items in the folder.")
    def delete(self, folder_id):
        result_delete = send_request(
            "DELETE",
            f"{ITEM_SERVICE_URL}/folder/{folder_id}",
            params=get_shop_id_params(),
        )
        return result_delete["result_json"], result_delete["status_code"]
