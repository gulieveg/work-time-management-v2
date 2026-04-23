from typing import Dict, List, Tuple, Union

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required
from werkzeug.wrappers import Response

from app.db import DatabaseManager
from app.utils import MESSAGES, permission_required

employees_bp: Blueprint = Blueprint("employees", __name__, url_prefix="/employees")
db_manager: DatabaseManager = DatabaseManager()


@employees_bp.route("", methods=["GET"])
@login_required
@permission_required(["advanced"])
def employees_table() -> Response:
    employee_name: str = request.args.get("employee_name")
    personnel_number: str = request.args.get("personnel_number")

    args: Dict[str, str] = {
        "employee_name": employee_name,
        "personnel_number": personnel_number,
    }

    filtered_employees: List[Tuple[str]] = db_manager.employees.get_employees(**args)
    if not filtered_employees:
        return render_template("control/employees/employees_table.html")

    page: int = request.args.get("page", 1, int)

    args: Dict[str, Union[str, int]] = {
        "employee_name": employee_name,
        "personnel_number": personnel_number,
        "page": page,
    }

    filtered_employees_page: List[Tuple[str]] = db_manager.employees.get_employees(**args)

    context: Dict[str, Union[int, List[Tuple[str]]]] = {
        "filtered_employees": filtered_employees,
        "filtered_employees_page": filtered_employees_page,
        "page": page,
    }
    return render_template("control/employees/employees_table.html", **context)


@employees_bp.route("/names", methods=["GET"])
@login_required
def get_employee_names() -> Response:
    query: str = request.args.get("query", "")
    employee_names: List[str] = db_manager.employees.get_employee_names_by_partial_match(query)
    return jsonify(employee_names)


@employees_bp.route("/numbers", methods=["GET"])
@login_required
def get_personnel_numbers() -> Response:
    query: str = request.args.get("query", "")
    personnel_numbers: List[str] = db_manager.employees.get_personnel_numbers_by_partial_match(query)
    return jsonify(personnel_numbers)


@employees_bp.route("/<string:personnel_number>/name", methods=["GET"])
@login_required
def get_employee_name(personnel_number: str) -> Response:
    employee_name: str = db_manager.employees.get_employee_name_by_number(personnel_number)
    return jsonify({"employee_name": employee_name})


@employees_bp.route("/<string:employee_name>/number", methods=["GET"])
@login_required
def get_personnel_number(employee_name: str) -> Response:
    personnel_number: str = db_manager.employees.get_personnel_number_by_name(employee_name)
    return jsonify({"personnel_number": personnel_number})


@employees_bp.route("/add", methods=["GET", "POST"])
@login_required
@permission_required(["advanced"])
def add_employee() -> str:
    if request.method == "POST":
        employee_name: str = request.form.get("employee_name")
        personnel_number: str = request.form.get("personnel_number")
        employee_department: str = request.form.get("employee_department")
        employee_category: str = request.form.get("employee_category")

        if db_manager.employees.employee_exists(personnel_number):
            flash(message=MESSAGES["employees"]["employee_exists"], category="warning")
            return render_template("control/employees/add_employee.html")

        args: Dict[str, str] = {
            "name": employee_name,
            "personnel_number": personnel_number,
            "department": employee_department,
            "category": employee_category,
        }
        db_manager.employees.add_employee(**args)

        flash(message=MESSAGES["employees"]["employee_added"], category="info")
        return render_template("control/employees/add_employee.html")
    return render_template("control/employees/add_employee.html")


@employees_bp.route("/edit/<int:employee_id>", methods=["GET", "POST"])
@login_required
@permission_required(["advanced"])
def edit_employee(employee_id: int) -> Union[str, Response]:
    employee_data: Dict[str, Union[str, int]] = db_manager.employees.get_employee_data_by_id(employee_id)

    context: Dict[str, str] = {
        "employee_name": employee_data["employee_name"],
        "personnel_number": employee_data["personnel_number"],
        "employee_department": employee_data["employee_department"],
        "employee_category": employee_data["employee_category"],
    }

    if request.method == "POST":
        employee_name: str = request.form.get("employee_name")
        personnel_number: str = request.form.get("personnel_number")
        employee_department: str = request.form.get("employee_department")
        employee_category: str = request.form.get("employee_category")

        if db_manager.employees.employee_exists(personnel_number, exclude_id=employee_id):
            flash(message=MESSAGES["employees"]["employee_exists"], category="error")
            context_with_error: Dict[str, str] = context.copy()
            context_with_error.update(
                {
                    "personnel_number": personnel_number,
                    "personnel_number_error": True,
                }
            )
            return render_template("control/employees/edit_employee.html", **context_with_error)

        args: Dict[str, Union[int, str]] = {
            "employee_id": employee_id,
            "employee_name": employee_name,
            "personnel_number": personnel_number,
            "employee_department": employee_department,
            "employee_category": employee_category,
        }
        db_manager.employees.update_employee(**args)

        flash(message=MESSAGES["employees"]["employee_updated"], category="info")
        return redirect(url_for("control.employees.edit_employee", employee_id=employee_id))
    return render_template("control/employees/edit_employee.html", **context)


@employees_bp.route("/delete/<int:employee_id>", methods=["POST"])
@login_required
@permission_required(["advanced"])
def delete_employee(employee_id: int) -> Response:
    page: int = request.form.get("page", 1, type=int)
    db_manager.employees.delete_employee(employee_id)
    return redirect(url_for("control.employees.employees_table", page=page))
