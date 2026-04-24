from typing import Dict

from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.db import db_manager
from app.utils import permission_required

from .employees import employees_bp
from .hours import hours_bp
from .logs import logs_bp
from .orders import orders_bp
from .reports import reports_bp
from .users import users_bp
from .works import works_bp

control_bp: Blueprint = Blueprint("control", __name__, url_prefix="/control")

control_bp.register_blueprint(employees_bp)
control_bp.register_blueprint(hours_bp)
control_bp.register_blueprint(logs_bp)
control_bp.register_blueprint(orders_bp)
control_bp.register_blueprint(reports_bp)
control_bp.register_blueprint(users_bp)
control_bp.register_blueprint(works_bp)


@control_bp.route("", methods=["GET"])
@login_required
@permission_required(["advanced"])
def index() -> str:
    recent_logs = db_manager.logs.get_recent_logs(limit=5)
    context: Dict = {
        "user_name": current_user.name,
        "orders_count": db_manager.orders.get_orders_count(),
        "employees_count": db_manager.employees.get_employees_count(),
        "tasks_count": db_manager.tasks.get_tasks_count(),
        "works_count": db_manager.works.get_works_count(),
        "users_count": db_manager.users.get_users_count(),
        "recent_logs": recent_logs,
    }
    return render_template("control/index.html", **context)