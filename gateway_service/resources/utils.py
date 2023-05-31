from flask import request as flask_request, jsonify, current_app
from flask_jwt_extended import (
    get_jwt,
)
from flask_smorest import abort
import requests
import json


def is_staff_member(shop_id: int):
    jwt = get_jwt()
    if jwt.get("shop_id") != shop_id:
        abort(401, message="Should belong to the shop staff.")


def is_shop_owner(shop_id: int):
    jwt = get_jwt()
    if jwt.get("shop_id") != shop_id or not jwt.get("is_owner"):
        abort(401, message="Should be the shop owner.")


def send_request(method, url, headers=None, data=None, params=None):
    if not headers:
        try:
            headers = flask_request.headers
        except Exception:
            headers = {}

    request_data = json.dumps(data, default=str) if data else None

    if method == 'GET':
        response = requests.get(url, headers=headers, params=params)
    elif method == 'POST':
        response = requests.post(url, headers=headers, data=request_data, params=params)
    elif method == 'PUT':
        response = requests.put(url, headers=headers, data=request_data, params=params)
    elif method == 'DELETE':
        response = requests.delete(url, headers=headers, params=params)
    else:
        raise ValueError(f"Invalid method: {method}")

    result_obj = json.loads(response.text)

    return {"plain_response": response,
            "status_code": response.status_code,
            "result_obj": result_obj,
            "result_json": jsonify(result_obj)}
