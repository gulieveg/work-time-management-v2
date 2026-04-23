from typing import List

from flask import Blueprint, jsonify, request
from flask_login import login_required
from werkzeug.wrappers import Response

from app.db import DatabaseManager

orders_bp: Blueprint = Blueprint("orders", __name__, url_prefix="/orders")
db_manager: DatabaseManager = DatabaseManager()


@orders_bp.route("/names", methods=["GET"])
@login_required
def get_order_names() -> Response:
    query: str = request.args.get("query", "")
    order_names: List[str] = db_manager.orders.get_order_names_by_partial_match(query)
    return jsonify(order_names)


@orders_bp.route("/numbers", methods=["GET"])
@login_required
def get_order_numbers() -> Response:
    query: str = request.args.get("query", "")
    order_numbers: List[str] = db_manager.orders.get_order_numbers_by_partial_match(query)
    return jsonify(order_numbers)


@orders_bp.route("/<string:order_number>/name", methods=["GET"])
@login_required
def get_order_name(order_number: str) -> Response:
    order_name: str = db_manager.orders.get_order_name_by_number(order_number)
    return jsonify({"order_name": order_name})


@orders_bp.route("/<string:order_name>/number", methods=["GET"])
@login_required
def get_order_number(order_name: str) -> Response:
    order_number: str = db_manager.orders.get_order_number_by_name(order_name)
    return jsonify({"order_number": order_number})


@orders_bp.route("/<string:order_number>/works", methods=["GET"])
@login_required
def get_works_for_order(order_number: str) -> Response:
    works: List[str] = db_manager.works.get_works_for_order_by_number(order_number)
    return jsonify(works)
