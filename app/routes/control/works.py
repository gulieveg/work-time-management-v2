from decimal import Decimal
from typing import Dict, List, Tuple, Union

from flask import Blueprint, Response, flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required

from app.db import DatabaseManager
from app.utils import MESSAGES, permission_required

works_bp: Blueprint = Blueprint("works", __name__, url_prefix="/works")
db_manager: DatabaseManager = DatabaseManager()


@works_bp.route("", methods=["GET"])
@login_required
@permission_required(["advanced"])
def works_table() -> str:
    order_id: int = request.args.get("order_id", type=int)

    order_number: str = request.args.get("order_number")
    work_name: str = request.args.get("work_name")

    args: Dict[str, str] = {
        "order_id": order_id,
        "order_number": order_number,
        "work_name": work_name,
    }

    filtered_works: List[Tuple[str]] = db_manager.works.get_works(**args)
    if not filtered_works:
        return render_template("control/works/works_table.html")

    page: int = request.args.get("page", 1, int)

    args: Dict[str, Union[str, int]] = {
        "order_id": order_id,
        "order_number": order_number,
        "work_name": work_name,
        "page": page,
    }

    filtered_works_page: List[Tuple[str]] = db_manager.works.get_works(**args)

    context: Dict[str, Union[int, List[Tuple[str]]]] = {
        "filtered_works": filtered_works,
        "filtered_works_page": filtered_works_page,
        "page": page,
    }
    return render_template("control/works/works_table.html", **context)


@works_bp.route("/add", methods=["GET", "POST"])
@login_required
@permission_required(["advanced"])
def add_work() -> str:
    if request.method == "POST":
        order_number: str = request.form.get("order_number")
        work_name: str = request.form.get("work_name")
        planned_hours: str = request.form.get("planned_hours")

        order_id: int = db_manager.orders.get_order_id_by_number(order_number)

        if db_manager.works.work_exists(order_id, work_name):
            flash(message=MESSAGES["works"]["work_exists"], category="warning")
            return render_template("control/works/add_work.html")

        args: Dict[str, str] = {
            "order_id": order_id,
            "work_name": work_name,
            "planned_hours": Decimal(planned_hours),
        }
        db_manager.works.add_work(**args)

        flash(message=MESSAGES["works"]["work_added"], category="info")
        return render_template("control/works/add_work.html")
    return render_template("control/works/add_work.html")


@works_bp.route("/edit/<int:work_id>", methods=["GET", "POST"])
@login_required
@permission_required(["advanced"])
def edit_work(work_id: int) -> Union[str, Response]:
    work_data: Dict[str, Union[str, int]] = db_manager.works.get_work_data_by_id(work_id)

    context: Dict[str, str] = {
        "work_name": work_data["work_name"],
        "planned_hours": work_data["planned_hours"],
    }

    if request.method == "POST":
        work_name: str = request.form.get("work_name")
        planned_hours: str = request.form.get("planned_hours")

        if db_manager.works.work_exists(work_data["order_id"], work_name, exclude_id=work_id):
            flash(message=MESSAGES["works"]["work_exists"], category="error")
            context_with_error: Dict[str, str] = context.copy()
            context_with_error.update(
                {
                    "work_name": work_name,
                    "work_name_error": True,
                }
            )
            return render_template("control/works/edit_work.html", **context_with_error)

        args: Dict[str, Union[int, str]] = {
            "work_id": work_id,
            "work_name": work_name,
            "planned_hours": Decimal(planned_hours),
        }
        db_manager.works.update_work(**args)

        flash(message=MESSAGES["works"]["work_updated"], category="info")
        return redirect(url_for("control.works.edit_work", work_id=work_id))
    return render_template("control/works/edit_work.html", **context)


@works_bp.route("/delete/<int:work_id>", methods=["POST"])
@login_required
@permission_required(["advanced"])
def delete_work(work_id: int) -> Response:
    page: int = request.form.get("page", 1, int)
    order_number: int = request.form.get("order_number")

    args: Dict[str, Union[int, str]] = {
        "page": page,
        "order_number": order_number,
    }

    db_manager.works.delete_work(work_id)
    return redirect(url_for("control.works.works_table", **args))


@works_bp.route("/names", methods=["GET"])
@login_required
def get_work_names() -> Response:
    query: str = request.args.get("query", "")
    order_number: str = request.args.get("order_number", "")

    order_id: int = db_manager.orders.get_order_id_by_number(order_number)

    work_names: List[str] = db_manager.works.get_work_names_by_partial_match(query, order_id)
    return jsonify(work_names)
