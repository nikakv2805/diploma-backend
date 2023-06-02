from db import db
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models import ItemFolderModel, ItemModel
from schemas import (
    FolderCreateSchema,
    FolderEditSchema,
    FolderReturnSchema,
    MessageOnlySchema,
    ShopIDSchema,
)

blp = Blueprint("Folder", "folder", description="Operations on item folders")


@blp.route("/folder")
class FolderCreate(MethodView):
    @blp.arguments(FolderCreateSchema)
    @blp.response(201, MessageOnlySchema, description="Folder created successfully.")
    @blp.alt_response(404, description="Folder with that id wasn't found.")
    @blp.alt_response(409, description="There is an item like this in the shop.")
    def post(self, folder_data):
        if ItemFolderModel.query.filter(
            ItemFolderModel.shop_id == folder_data["shop_id"],
            ItemFolderModel.folder_name == folder_data["folder_name"],
        ).first():
            abort(409, message="There is already a folder with this name in the shop.")

        folder = ItemFolderModel(**folder_data)
        db.session.add(folder)
        db.session.commit()

        return {"id": folder.id, "message": "Folder created successfully."}


@blp.route("/shop/<int:shop_id>/folder")
class FolderList(MethodView):
    @blp.response(
        200, FolderReturnSchema(many=True), description="Folders returned successfully."
    )
    def get(self, shop_id):
        return ItemFolderModel.query.filter(ItemFolderModel.shop_id == shop_id).all()


@blp.route("/folder/<int:folder_id>")
class Folder(MethodView):
    @blp.arguments(ShopIDSchema, location="query")
    @blp.response(200, FolderReturnSchema, description="Folder returned successfully.")
    @blp.alt_response(404, description="Folder with this id wasn't found.")
    def get(self, shop_id_data, folder_id):
        shop_id = shop_id_data["shop_id"]
        folder = ItemFolderModel.query.get_or_404(folder_id)
        if folder.shop_id != shop_id:
            abort(401, message="You must be shop staff member!")
        return folder

    @blp.arguments(FolderEditSchema)
    @blp.arguments(ShopIDSchema, location="query")
    @blp.response(200, FolderReturnSchema, description="Folder edited successfully.")
    @blp.alt_response(404, description="Folder with this id wasn't found.")
    @blp.alt_response(409, description="There is an item with this name in the shop.")
    def put(self, folder_edit_data, shop_id_data, folder_id):
        shop_id = shop_id_data["shop_id"]
        folder = ItemFolderModel.query.get_or_404(folder_id)
        if folder.shop_id != shop_id:
            abort(401, message="You must be shop staff member!")

        if (
            "new_folder_name" in folder_edit_data
            and ItemFolderModel.query.filter(
                ItemFolderModel.shop_id == folder.shop_id,
                ItemFolderModel.folder_name == folder_edit_data["new_folder_name"],
            ).first()
        ):
            abort(409, message="There is already a folder with this name in the shop.")

        if "new_folder_name" in folder_edit_data:
            folder.folder_name = folder_edit_data["new_folder_name"]

        db.session.commit()
        return folder

    @blp.arguments(ShopIDSchema, location="query")
    @blp.response(200, MessageOnlySchema, description="Folder deleted successfully.")
    @blp.alt_response(404, description="Folder with this id wasn't found.")
    @blp.alt_response(409, description="There are still items in the folder.")
    def delete(self, shop_id_data, folder_id):
        shop_id = shop_id_data["shop_id"]
        folder = ItemFolderModel.query.get_or_404(folder_id)
        if folder.shop_id != shop_id:
            abort(401, message="You must be shop staff member!")

        if ItemModel.query.filter(ItemModel.folder_id == folder_id).first():
            # Not deleting if there are items in the folder
            abort(409, message="Folder still contains items.")

        db.session.delete(folder)
        db.session.commit()

        return {"message": "Folder deleted successfully."}
