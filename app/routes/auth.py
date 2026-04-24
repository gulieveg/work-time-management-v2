from typing import Dict, Union

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug.wrappers import Response

from app.db import db_manager
from app.models import User
from app.utils import MESSAGES, create_log

auth_bp: Blueprint = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login() -> Union[str, Response]:
    if current_user.is_authenticated:
        return redirect(url_for("tasks.index"))

    if request.method == "POST":
        login: str = request.form["login"]
        password: str = request.form["password"]

        if not db_manager.users.authenticate_user(login=login, password=password):
            flash(message=MESSAGES["auth"]["invalid_credentials"], category="error")
            return render_template("auth/login.html", login=login, password=password)

        user_data: Dict[str, Union[str, int]] = db_manager.users.get_user_data_by_login(login)
        user: User = User(**user_data)
        login_user(user)
        create_log("LOGIN", user_data["user_id"], "user", user_data["user_name"])

        session.permanent = True

        next_page: str = request.args.get("next")
        if not next_page or next_page.startswith("/"):
            return redirect(next_page or url_for("tasks.index"))
    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout() -> Response:
    user_name = current_user.name
    user_id = current_user.id
    logout_user()
    create_log("LOGOUT", user_id, "user", user_name)
    flash(message=MESSAGES["auth"]["logout_success"], category="info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register() -> Union[str, Response]:
    if current_user.is_authenticated:
        return redirect(url_for("tasks.index"))

    if request.method == "POST":
        login: str = request.form["login"]
        password: str = request.form["password"]
        password_confirm: str = request.form["password_confirm"]

        context: Dict[str, str] = {
            "login": login,
            "password": password,
            "password_confirm": password_confirm,
        }

        if not db_manager.users.is_user_existing(login=login):
            flash(MESSAGES["auth"]["registration_denied"], category="warning")
            return render_template("auth/register.html", **context)

        if not db_manager.users.is_user_enabled(login=login):
            flash(MESSAGES["auth"]["account_inactive"], category="warning")
            return render_template("auth/register.html", **context)

        if db_manager.users.is_user_registered(login=login):
            flash(MESSAGES["auth"]["user_already_registered"], category="warning")
            return render_template("auth/register.html", **context)

        if password != password_confirm:
            flash(MESSAGES["auth"]["passwords_do_not_match"], category="warning")
            return render_template("auth/register.html", **context)

        db_manager.users.register_user(login=login, password=password)
        user_data = db_manager.users.get_user_data_by_login(login)
        create_log("REGISTER", user_data["user_id"], "user", user_data["user_name"])
        flash(MESSAGES["auth"]["registration_success"], category="info")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html")