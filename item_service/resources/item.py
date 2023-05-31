from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort
import os

from db import db
from models import ItemModel, ItemFolderModel
from schemas import ItemCreateSchema, MessageOnlySchema, ItemReturnSchema, \
    ItemEditSchema, ItemCountEditSchema, ItemSearchSchema


blp = Blueprint("Item", "item", description="Operations on items")

MAX_SEARCH_VARIANTS = int(os.environ.get("MAX_SEARCH_VARS", "5"))


@blp.route("/item")
class ItemCreate(MethodView):
    @blp.arguments(ItemCreateSchema)
    @blp.response(201, MessageOnlySchema, description="Item created successfully.")
    @blp.alt_response(404, description="Folder with that id wasn't found.")
    @blp.alt_response(409, description="There is an item like this in the shop.")
    def post(self, item_data):
        if ItemModel.query.filter(ItemModel.shop_id == item_data["shop_id"],
                                  ItemModel.article == item_data["article"]).first():
            abort(409, message="There is already an item with this article in the shop.")

        if ItemModel.query.filter(ItemModel.shop_id == item_data["shop_id"],
                                  ItemModel.bar_code == item_data["bar_code"]).first():
            abort(409, message="There is already an item with this bar code in the shop.")

        if ItemModel.query.filter(ItemModel.shop_id == item_data["shop_id"],
                                  ItemModel.item_name == item_data["item_name"]).first():
            abort(409, message="There is already an item with this name in the shop.")

        folder = ItemFolderModel.query.get_or_404(item_data["folder_id"], description="Desired folder wasn't found.")

        if folder.shop_id != item_data["shop_id"]:
            abort(409, message="Shop ID of folder and new item are different.")

        current_app.logger.info(len(str(item_data["bar_code"])))

        item = ItemModel(
            **item_data,
            count_existing=0,
        )
        db.session.add(item)
        db.session.commit()

        return {"id": item.id, "message": "Item created successfully."}


@blp.route("/shop/<int:shop_id>/item")
class ItemList(MethodView):
    @blp.response(200, ItemReturnSchema(many=True), description="Items returned successfully.")
    def get(self, shop_id):
        return ItemModel.query.filter(ItemModel.shop_id == shop_id).all()


@blp.route("/item/<int:item_id>")
class Item(MethodView):
    @blp.response(200, ItemReturnSchema, description="Item returned successfully.")
    @blp.alt_response(404, description="Item wasn't found.")
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    @blp.arguments(ItemEditSchema)
    @blp.response(200, ItemReturnSchema, description="Item edited successfully.")
    @blp.alt_response(404, description="Item or new folder wasn't found.")
    @blp.alt_response(409, description="One of new item's name, article or barcode is already in the DB.")
    def put(self, item_edit_data, item_id):
        item = ItemModel.query.get_or_404(item_id)

        if "new_article" in item_edit_data and \
                ItemModel.query.filter(ItemModel.shop_id == item.shop_id,
                                       ItemModel.article == item_edit_data["new_article"]).first():
            abort(409, message="There is already an item with this article in the shop.")

        if "new_bar_code" in item_edit_data and \
                ItemModel.query.filter(ItemModel.shop_id == item.shop_id,
                                       ItemModel.bar_code == item_edit_data["new_bar_code"]).first():
            abort(409, message="There is already an item with this bar code in the shop.")

        if "new_item_name" in item_edit_data and \
                ItemModel.query.filter(ItemModel.shop_id == item.shop_id,
                                       ItemModel.item_name == item_edit_data["new_item_name"]).first():
            abort(409, message="There is already an item with this name in the shop.")

        if "new_folder_id" in item_edit_data:
            new_folder = ItemFolderModel.query.get(item_edit_data["new_folder_id"])
            if not new_folder:
                abort(404, message="This folder wasn't found.")
            if new_folder.shop_id != item.shop_id:
                abort(409, message="Folder and item belong to different shops.")

        if "new_article" in item_edit_data:
            item.article = item_edit_data["new_article"]
        if "new_bar_code" in item_edit_data:
            item.bar_code = item_edit_data["new_bar_code"]
        if "new_item_name" in item_edit_data:
            item.item_name = item_edit_data["new_item_name"]
        if "new_folder_id" in item_edit_data:
            item.folder_id = item_edit_data["new_folder_id"]
        if "new_price" in item_edit_data:
            item.price = item_edit_data["new_price"]
        if "new_type" in item_edit_data:
            item.type = item_edit_data["new_type"]
        if "new_unit" in item_edit_data:
            item.unit = item_edit_data["new_unit"]

        db.session.add(item)
        db.session.commit()

        return item

    @blp.response(200, MessageOnlySchema, description="Item deleted successfully.")
    @blp.alt_response(404, description="Item wasn't found")
    def delete(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted."}


@blp.route("/item/update_counts")
class ItemCounts(MethodView):
    @blp.arguments(ItemCountEditSchema(many=True))
    @blp.response(200, MessageOnlySchema, description="All item's counts updated")
    @blp.alt_response(404, description="One of the items wasn't found.")
    def put(self, items_count_edit_data):
        for item_count_data in items_count_edit_data:
            item = ItemModel.query.get(item_count_data["id"])
            if item is None:
                abort(404, message=f"Item with ID {item_count_data['id']} not found.")
            item.count_existing += item_count_data["count_delta"]

        db.session.commit()
        return {"message": "Counts updated successfully."}


@blp.route("/shop/<int:shop_id>/item/search")
class ItemSearch(MethodView):
    @blp.arguments(ItemSearchSchema, location="query")
    @blp.response(200, ItemReturnSchema(many=True), description="Search successful.")
    def get(self, item_search_params, shop_id):
        if not item_search_params:  # check if dict is empty
            abort(409, message="No search params were given.")

        if "article" in item_search_params and "name_part" in item_search_params or \
            "article" in item_search_params and "bar_code" in item_search_params or \
            "name_part" in item_search_params and "bar_code" in item_search_params:
            abort(409, message="Only one of {name_part, article, bar_code} should be given.")

        if "folder_id" in item_search_params:
            if not ItemFolderModel.query.get(item_search_params["folder_id"]):
                abort(404, message="Folder with specified ID wasn't found.")

            items = ItemModel.query.filter(ItemModel.shop_id == shop_id,
                                           ItemModel.folder_id == item_search_params["folder_id"])
        else:
            items = ItemModel.query.filter(ItemModel.shop_id == shop_id)

        if "article" in item_search_params:
            items = items.filter(ItemModel.article == item_search_params["article"])
        elif "bar_code" in item_search_params:
            items = items.filter(ItemModel.bar_code == item_search_params["bar_code"])
        elif "name_part" in item_search_params:
            items = items.filter(ItemModel.item_name.like("%" + item_search_params["name_part"] + "%"))

        return items.limit(MAX_SEARCH_VARIANTS).all()
