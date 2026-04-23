from datetime import datetime, timedelta
from decimal import Decimal
from io import BytesIO
from typing import Dict, List, Tuple, Union

from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for
from flask_login import login_required
from werkzeug.wrappers import Response

from app.db import DatabaseManager
from app.utils import MESSAGES, get_report_file, permission_required

Tasks = List[Dict[str, Union[str, Decimal]]]
Data = List[List[Union[str, Decimal]]]
GroupedData = Dict[str, Dict[str, Union[str, Dict[str, Decimal]]]]

tasks_bp: Blueprint = Blueprint("tasks", __name__, url_prefix="/tasks")
db_manager: DatabaseManager = DatabaseManager()


@tasks_bp.route("/", methods=["GET"])
@login_required
def index() -> Union[str, Response]:
    today: str = datetime.today().strftime("%Y-%m-%d")
    week_start: str = (datetime.today() - timedelta(days=datetime.today().weekday())).strftime("%Y-%m-%d")
    month_start: str = datetime.today().replace(day=1).strftime("%Y-%m-%d")

    stats_day: Dict[str, Dict[str, Decimal]] = db_manager.tasks.get_stats_by_department(today, today)
    stats_week: Dict[str, Dict[str, Decimal]] = db_manager.tasks.get_stats_by_department(week_start, today)
    stats_month: Dict[str, Dict[str, Decimal]] = db_manager.tasks.get_stats_by_department(month_start, today)

    departments: List[str] = db_manager.employees.get_departments()

    context: Dict[str, Union[str, Dict, List[str]]] = {
        "stats_day": stats_day,
        "stats_week": stats_week,
        "stats_month": stats_month,
        "departments": departments,
        "today": today,
        "week_start": week_start,
        "month_start": month_start,
    }
    return render_template("index.html", **context)


@tasks_bp.route("/table", methods=["GET"])
@login_required
def tasks_table() -> Union[str, Response]:
    start_date: str = request.args.get("start_date")
    end_date: str = request.args.get("end_date")

    default_date: str = datetime.today().strftime("%Y-%m-%d")

    if not start_date and not end_date:
        start_date = end_date = default_date

    args: Dict[str, Union[str, List[str]]] = {
        "departments": request.args.getlist("departments[]"),
        "start_date": start_date,
        "end_date": end_date,
        "employee_data": request.args.get("employee_data"),
        "order_number": request.args.get("order_number"),
        "work_name": request.args.get("work_name"),
        "order_name": request.args.get("order_name"),
    }

    tasks: Tasks = db_manager.tasks.get_tasks(**args)
    departments: List[str] = db_manager.employees.get_departments()

    if request.args.get("export"):
        tasks_data: Tasks = db_manager.tasks.get_tasks_data(tasks=tasks)
        basic_orders_data: Data = db_manager.orders.get_basic_orders_data(tasks=tasks)
        file: BytesIO = get_report_file(tasks_data=tasks_data, basic_orders_data=basic_orders_data)
        timestamp: str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return send_file(file, download_name=f"{timestamp}.xlsx", as_attachment=True)

    context: Dict[str, Union[str, Tasks]] = {
        "tasks": tasks,
        "departments": departments,
        "default_date": default_date,
    }
    return render_template("tasks/tasks_table.html", **context)


@tasks_bp.route("/add", methods=["GET", "POST"])
@login_required
@permission_required(["advanced", "standard"])
def add_task() -> Union[str, Response]:
    if request.method == "POST":
        employee_data: str = request.form.get("employee_data")
        operation_date: str = request.form.get("operation_date")
        order_names: List[str] = request.form.getlist("order_name[]")
        order_numbers: List[str] = request.form.getlist("order_number[]")

        if not operation_date:
            operation_date: str = datetime.now().strftime("%Y-%m-%d")

        employee_details: Tuple[str, str] = db_manager.employees.get_employee_details(employee_data)
        employee_name, personnel_number = employee_details

        employee_department: str = db_manager.employees.get_employee_department(personnel_number)
        employee_category: str = db_manager.employees.get_employee_category(personnel_number)

        grouped_data: GroupedData = {
            order_number: {
                "order_name": order_name,
                "works": {
                    work_name.split("][")[1].rstrip("]"): Decimal(spent_hours)
                    for work_name, spent_hours in request.form.items()
                    if spent_hours and work_name.startswith(f"work_hours[{order_number}]")
                },
            }
            for order_number, order_name in zip(order_numbers, order_names)
        }

        total_spent_hours: Decimal = Decimal(0)

        for order_data in grouped_data.values():
            for spent_hours in order_data["works"].values():
                if spent_hours < Decimal(0):
                    flash(message=MESSAGES["tasks"]["hours_less_than_zero"], category="error")
                    return render_template("tasks/add_task.html")
                total_spent_hours += spent_hours

        if total_spent_hours > Decimal(12.25):
            flash(message=MESSAGES["tasks"]["hours_exceed_limit"], category="error")
            return render_template("tasks/add_task.html")

        for order_number, order_data in grouped_data.items():
            for work_name, spent_hours in order_data["works"].items():
                args: Dict[str, Union[str, Decimal]] = {
                    "employee_name": employee_name,
                    "personnel_number": personnel_number,
                    "department": employee_department,
                    "work_name": work_name,
                    "hours": spent_hours,
                    "order_number": order_number,
                    "order_name": order_data["order_name"],
                    "operation_date": operation_date,
                    "employee_category": employee_category,
                }
                db_manager.tasks.add_task(**args)
        flash(message="Задания успешно добавлены.", category="info")
        return redirect(url_for("tasks.add_task"))
    return render_template("tasks/add_task.html")


@tasks_bp.route("/edit/<int:task_id>", methods=["GET", "POST"])
@login_required
@permission_required(["advanced", "standard"])
def edit_task(task_id: int) -> Union[str, Response]:
    task_data: Dict[str, Union[str, Decimal]] = db_manager.tasks.get_task_data_by_id(task_id)

    context: Dict[str, Union[str, Decimal]] = {
        "employee_name": task_data["employee_name"],
        "personnel_number": task_data["personnel_number"],
        "operation_date": task_data["operation_date"],
        "hours": task_data["hours"],
        "order_name": task_data["order_name"],
        "order_number": task_data["order_number"],
        "work_name": task_data["work_name"],
    }

    if request.method == "POST":
        employee_data: str = request.form.get("employee_data")
        operation_date: str = request.form.get("operation_date")
        hours: str = request.form.get("hours")
        order_name: str = request.form.get("order_name")
        order_number: str = request.form.get("order_number")
        work_name: str = request.form.get("work_name")

        employee_details: Tuple[str, str] = db_manager.employees.get_employee_details(employee_data)

        if employee_details is None:
            flash(message=MESSAGES["employees"]["invalid_employee_format"], category="warning")
            context: Dict[str, str] = {
                "operation_date": operation_date,
                "hours": hours,
                "order_name": order_name,
                "order_number": order_number,
                "work_name": work_name,
            }
            return render_template("tasks/edit_task.html", **context)

        employee_name, personnel_number = employee_details

        if not db_manager.employees.employee_exists(personnel_number):
            flash(message=MESSAGES["employees"]["employee_not_found"], category="warning")
            context: Dict[str, str] = {
                "employee_name": employee_name,
                "personnel_number": personnel_number,
                "operation_date": operation_date,
                "hours": hours,
                "order_name": order_name,
                "order_number": order_number,
                "work_name": work_name,
            }
            return render_template("tasks/edit_task.html", **context)

        free_hours: Decimal = db_manager.employees.get_employee_free_hours(personnel_number, operation_date)

        if Decimal(hours) > free_hours + context["hours"]:
            free_hours: Decimal = free_hours + context["hours"]
            message: str = MESSAGES["employees"]["exceeded_hours"].format(employee_data, free_hours)
            flash(message=message, category="warning")
            context: Dict[str, str] = {
                "employee_name": employee_name,
                "personnel_number": personnel_number,
                "operation_date": operation_date,
                "hours": hours,
                "order_name": order_name,
                "order_number": order_number,
                "work_name": work_name,
            }
            return render_template("tasks/edit_task.html", **context)

        args: Dict[str, Union[str, Decimal]] = {
            "task_id": task_id,
            "employee_name": employee_name,
            "personnel_number": personnel_number,
            "hours": Decimal(hours),
            "order_name": order_name,
            "order_number": order_number,
            "operation_date": operation_date,
            "work_name": work_name,
        }
        db_manager.tasks.update_task(**args)

        params: Dict[str, str] = {
            "departments[]": request.args.getlist("departments[]"),
            "start_date": request.args.get("start_date"),
            "end_date": request.args.get("end_date"),
            "employee_data": request.args.get("employee_data"),
            "order_number": request.args.get("order_number"),
            "work_name": request.args.get("work_name"),
            "order_name": request.args.get("order_name"),
        }
        return redirect(url_for("tasks.tasks_table", **params))
    return render_template("tasks/edit_task.html", **context)


@tasks_bp.route("/delete/<int:task_id>", methods=["POST"])
@login_required
@permission_required(["advanced", "standard"])
def delete_task(task_id: str) -> Response:
    params: Dict[str, str] = {
        "departments[]": request.form.getlist("departments[]"),
        "start_date": request.form.get("start_date"),
        "end_date": request.form.get("end_date"),
        "employee_data": request.form.get("employee_data"),
        "order_number": request.form.get("order_number"),
        "work_name": request.form.get("work_name"),
        "order_name": request.form.get("order_name"),
    }
    db_manager.tasks.delete_task(task_id)
    return redirect(url_for("tasks.tasks_table", **params))
