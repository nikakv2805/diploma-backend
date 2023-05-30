from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from db import db
from models import ShopModel
from schemas import ShopSchema, MessageOnlySchema, ShopEditSchema, ShopEditCashSchema


blp = Blueprint("Shops", "shops", description="Operations on shops")


@blp.route("/shop/register")
class ShopRegister(MethodView):
    @blp.arguments(ShopSchema)
    @blp.response(201, MessageOnlySchema,
                  description="Registers new shop with unique address")
    @blp.alt_response(409, description='Returned if there is already a shop with this address in the database.')
    def post(self, shop_data):
        if ShopModel.query.filter(ShopModel.address == shop_data["address"]).first():
            abort(409, message="A shop is already registered on this address.")

        shop = ShopModel(
            name=shop_data["name"],
            legal_entity=shop_data["legal_entity"],
            address=shop_data["address"],
            current_cash=0
        )
        db.session.add(shop)
        db.session.commit()

        return {"message": "Shop created successfully."}


@blp.route("/shop/<int:shop_id>/owner/<int:owner_id>")
class ShopOwner(MethodView):
    @blp.response(200, MessageOnlySchema,
                  description="Owner added to shop.")
    @blp.alt_response(404, description="Shop with this ID doesn't exist.")
    @blp.alt_response(409, description="Shop with this ID already has its owner or vice versa.")
    def post(self, shop_id, owner_id):
        selected_shop = ShopModel.query.get_or_404(shop_id)

        if selected_shop.owner_id:
            abort(409, message="This shop already has an owner!")

        if ShopModel.query.filter(ShopModel.owner_id == owner_id).first():
            abort(409, message="This owner already has a shop!")

        selected_shop.owner_id = owner_id
        db.session.add(selected_shop)
        db.session.commit()

        return {"message": "Shop owner added successfully!"}


@blp.route("/shop/<int:shop_id>")
class User(MethodView):
    @blp.response(200, ShopSchema)
    @blp.alt_response(404, description='Shop wasn\'t found')
    def get(self, shop_id):
        shop = ShopModel.query.get_or_404(shop_id)
        return shop

    @blp.arguments(ShopEditSchema)
    @blp.response(200, ShopSchema)
    @blp.alt_response(404, description='Shop wasn\'t found')
    @blp.alt_response(409, description='Returned if there is already a shop with new address in the database.')
    def put(self, shop_edit_details, shop_id):
        shop = ShopModel.query.get_or_404(shop_id)

        if "new_name" in shop_edit_details:
            shop.name = shop_edit_details["new_name"]
        if "new_legal_entity" in shop_edit_details:
            shop.legal_entity = shop_edit_details["new_legal_entity"]
        if "new_address" in shop_edit_details:
            if ShopModel.query.filter(ShopModel.address == shop_edit_details["new_address"]).first():
                abort(409, message="A shop is already registered on proposed new address.")
            shop.address = shop_edit_details["new_address"]
        if "new_owner_id" in shop_edit_details:
            shop.owner_id = shop_edit_details["new_owner_id"]

        db.session.add(shop)
        db.session.commit()

        return shop

    @blp.response(200, MessageOnlySchema)
    @blp.alt_response(404, description='Shop wasn\'t found')
    def delete(self, shop_id):
        shop = ShopModel.query.get_or_404(shop_id)
        db.session.delete(shop)
        db.session.commit()
        return {"message": "Shop deleted."}


@blp.route("/shop/<int:shop_id>/cash_edit")
class User(MethodView):
    @blp.arguments(ShopEditCashSchema)
    @blp.response(200, MessageOnlySchema)
    @blp.alt_response(404, description='Shop wasn\'t found')
    def post(self, shop_cash_edit, shop_id):
        shop = ShopModel.query.get_or_404(shop_id)
        current_app.logger.info(shop_cash_edit["cash_delta"])
        current_app.logger.info(type(shop.current_cash))
        shop.current_cash += shop_cash_edit["cash_delta"]

        db.session.add(shop)
        db.session.commit()
        return {"message": "Cash amount edited."}
