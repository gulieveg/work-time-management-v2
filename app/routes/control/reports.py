from datetime import datetime
from decimal import Decimal
from io import BytesIO
from typing import Dict, List, Union

from flask import Blueprint, render_template, request, send_file
from flask_login import login_required

from app.db import DatabaseManager
from app.utils import get_report_file, permission_required

Tasks = List[Dict[str, Union[str, Decimal]]]
Data = List[List[Union[str, Decimal]]]

reports_bp: Blueprint = Blueprint("reports", __name__, url_prefix="/reports")
db_manager: DatabaseManager = DatabaseManager()


@reports_bp.route("", methods=["GET"])
@login_required
@permission_required(["advanced"])
def reports() -> str:
    start_date: str = request.args.get("start_date")
    end_date: str = request.args.get("end_date")

    if start_date:
        start_date: Union[str, datetime] = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        end_date: Union[str, datetime] = datetime.strptime(end_date, "%Y-%m-%d")

    if request.args.get("export"):
        tasks: Tasks = db_manager.tasks.get_tasks(start_date=start_date, end_date=end_date)

        tasks_data: Data = db_manager.tasks.get_tasks_data(tasks=tasks)
        employees_data: Data = db_manager.employees.get_employees_data(tasks=tasks)
        basic_orders_data: Data = db_manager.orders.get_basic_orders_data(
            tasks=tasks,
            start_date=start_date,
            end_date=end_date,
            extended=True,
        )
        detailed_orders_data: Data = db_manager.orders.get_detailed_orders_data(tasks=tasks)

        file: BytesIO = get_report_file(
            tasks_data=tasks_data,
            employees_data=employees_data,
            basic_orders_data=basic_orders_data,
            detailed_orders_data=detailed_orders_data,
        )
        timestamp: str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return send_file(file, download_name=f"{timestamp}.xlsx", as_attachment=True)

    return render_template("control/reports/get_report_file.html")
