from decimal import Decimal
from typing import Dict, List, Tuple, Union

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required
from werkzeug.wrappers import Response

from app.db import DatabaseManager
from app.utils import MESSAGES, permission_required

users_bp: Blueprint = Blueprint("users", __name__, url_prefix="/users")
db_manager: DatabaseManager = DatabaseManager()


@users_bp.route("", methods=["GET"])
@login_required
@permission_required(["advanced"])
def users_table() -> str:
    user_name: str = request.args.get("user_name")
    user_login: str = request.args.get("user_login")

    args: Dict[str, str] = {
        "user_name": user_name,
        "user_login": user_login,
    }

    filtered_users: List[Tuple[str]] = db_manager.users.get_users(**args)
    if not filtered_users:
        return render_template("control/users/users_table.html")

    page: int = request.args.get("page", 1, int)

    args: Dict[str, Union[str, int]] = {
        "user_name": user_name,
        "user_login": user_login,
        "page": page,
    }

    filtered_users_page: List[Tuple[str]] = db_manager.users.get_users(**args)

    context: Dict[str, Union[int, List[Tuple[str]]]] = {
        "filtered_users": filtered_users,
        "filtered_users_page": filtered_users_page,
        "page": page,
    }
    return render_template("control/users/users_table.html", **context)


@users_bp.route("/add", methods=["GET", "POST"])
@login_required
@permission_required(["advanced"])
def add_user() -> str:
    if request.method == "POST":
        user_name: str = request.form.get("user_name")
        user_department: str = request.form.get("user_department")
        user_login: str = request.form.get("user_login")
        user_password: str = request.form.get("user_password")
        user_permissions_level: str = request.form.get("user_permissions_level")

        if not db_manager.users.is_login_available(login=user_login):
            flash(message=MESSAGES["users"]["user_login_taken"], category="error")
            return render_template("control/users/add_user.html", user_login_error=True)

        is_user_factory_worker: bool = request.form.get("is_user_factory_worker") is not None
        is_user_account_enabled: bool = request.form.get("is_user_account_enabled") is not None

        args: Dict[str, str] = {
            "name": user_name,
            "department": user_department,
            "login": user_login,
            "password": user_password,
            "permissions_level": user_permissions_level,
            "is_user_factory_worker": is_user_factory_worker,
            "is_user_account_enabled": is_user_account_enabled,
        }
        db_manager.users.add_user(**args)

        flash(message=MESSAGES["users"]["user_added"], category="info")
        return render_template("control/users/add_user.html")
    return render_template("control/users/add_user.html")


@users_bp.route("/edit/<int:user_id>", methods=["GET", "POST"])
@login_required
@permission_required(["advanced"])
def edit_user(user_id: int) -> Union[str, Response]:
    user_data: Dict[str, Union[str, int]] = db_manager.users.get_user_data_by_id(user_id)

    context: Dict[str, str] = {
        "user_name": user_data["user_name"],
        "user_department": user_data["user_department"],
        "user_login": user_data["user_login"],
        "user_permissions_level": user_data["user_permissions_level"],
        "is_user_factory_worker": user_data["is_user_factory_worker"],
        "is_user_account_enabled": user_data["is_user_account_enabled"],
    }

    if request.method == "POST":
        user_name: str = request.form.get("user_name")
        user_department: str = request.form.get("user_department")
        user_login: str = request.form.get("user_login")
        user_password: str = request.form.get("user_password")
        user_permissions_level: str = request.form.get("user_permissions_level")
        is_user_factory_worker: bool = request.form.get("is_user_factory_worker") is not None
        is_user_account_enabled: bool = request.form.get("is_user_account_enabled") is not None

        if not db_manager.users.is_login_available(user_login, exclude_id=user_id):
            flash(message=MESSAGES["users"]["user_login_taken"], category="error")
            context_with_error: Dict[str, str] = context.copy()
            context_with_error.update(
                {
                    "user_login": user_login,
                    "user_login_error": True,
                }
            )
            return render_template("control/users/edit_user.html", **context_with_error)

        args: Dict[str, Union[str, bool]] = {
            "user_id": user_id,
            "user_name": user_name,
            "user_department": user_department,
            "user_login": user_login,
            "user_password": user_password,
            "user_permissions_level": user_permissions_level,
            "is_user_factory_worker": is_user_factory_worker,
            "is_user_account_enabled": is_user_account_enabled,
        }
        db_manager.users.update_user(**args)

        flash(message=MESSAGES["users"]["user_updated"], category="info")
        return redirect(url_for("control.users.edit_user", user_id=user_id))
    return render_template("control/users/edit_user.html", **context)


@users_bp.route("/delete/<int:user_id>", methods=["POST"])
@login_required
@permission_required(["advanced"])
def delete_user(user_id: int) -> Response:
    page: int = request.form.get("page", 1, type=int)
    db_manager.users.delete_user(user_id)
    return redirect(url_for("control.users.users_table", page=page))


@users_bp.route("/update_user_status/<int:user_id>", methods=["POST"])
@login_required
@permission_required(["advanced"])
def update_user_status(user_id: int) -> Response:
    data: Dict[str, bool] = request.get_json()
    is_active: bool = data.get("is_active")
    db_manager.users.update_user_status(user_id, is_active)

    payload: Dict[str, Union[str, bool, Dict[str, Union[int, bool]]]] = {
        "success": True,
        "message": "User status updated",
        "data": {
            "user_id": user_id,
            "user_status": "enabled" if is_active else "disabled",
        },
    }
    return jsonify(payload), 200


@users_bp.route("/reset_user_password/<int:user_id>", methods=["POST"])
def reset_user_password(user_id: int) -> Response:
    page: int = request.form.get("page", 1, type=int)
    db_manager.users.reset_user_password(user_id)
    return redirect(url_for("control.users.users_table", page=page))


@users_bp.route("/names", methods=["GET"])
@login_required
def get_user_names() -> Response:
    query: str = request.args.get("query", "")
    user_names: List[str] = db_manager.users.get_user_names_by_partial_match(query)
    return jsonify(user_names)


@users_bp.route("/logins", methods=["GET"])
@login_required
def get_user_logins() -> Response:
    query: str = request.args.get("query", "")
    user_logins: List[str] = db_manager.users.get_user_logins_by_partial_match(query)
    return jsonify(user_logins)


@users_bp.route("/<string:user_login>/name", methods=["GET"])
@login_required
def get_user_name(user_login: str) -> Response:
    user_name: str = db_manager.users.get_user_name_by_login(user_login)
    return jsonify({"user_name": user_name})


@users_bp.route("/<string:user_name>/login", methods=["GET"])
@login_required
def get_user_login(user_name: str) -> Response:
    user_login: str = db_manager.users.get_user_login_by_name(user_name)
    return jsonify({"user_login": user_login})
