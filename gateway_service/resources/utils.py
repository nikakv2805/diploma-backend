from flask_jwt_extended import (
    get_jwt,
)
from flask_smorest import abort


def is_staff_member(shop_id: int):
    jwt = get_jwt()
    if jwt.get("shop_id") != shop_id:
        abort(401, message="Should belong to the shop staff.")


def is_shop_owner(shop_id: int):
    jwt = get_jwt()
    if jwt.get("shop_id") != shop_id or not jwt.get("is_owner"):
        abort(401, message="Should be the shop owner.")
