from typing import List, Tuple

from flask import Blueprint, render_template, request
from flask_login import login_required
from werkzeug.wrappers import Response

from app.db import DatabaseManager
from app.utils import permission_required

logs_bp: Blueprint = Blueprint("logs", __name__, url_prefix="/logs")
db_manager: DatabaseManager = DatabaseManager()


@logs_bp.route("", methods=["GET"])
@login_required
@permission_required(["advanced"])
def logs_table() -> Response:
    logs: List[Tuple[str]] = db_manager.logs.get_logs()
    return render_template("control/logs/logs_table.html", logs=logs)
