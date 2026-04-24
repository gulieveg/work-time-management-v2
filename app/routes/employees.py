from typing import List

from flask import Blueprint, jsonify, request
from flask_login import login_required
from werkzeug.wrappers import Response

from app.db import db_manager

employees_bp: Blueprint = Blueprint("employees", __name__, url_prefix="/employees")


@employees_bp.route("", methods=["GET"])
@login_required
def get_employees() -> Response:
    query: str = request.args.get("query", "")
    employee_data: List[str] = db_manager.employees.get_employees_by_partial_match(query)
    return jsonify(employee_data)