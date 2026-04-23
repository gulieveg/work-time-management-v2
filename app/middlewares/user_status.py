from typing import Callable, Optional

from flask import Flask, flash, redirect, url_for
from flask_login import current_user, logout_user

from app.db import DatabaseManager
from app.utils import MESSAGES

db_manager: DatabaseManager = DatabaseManager()


def check_user_status(app: Flask) -> Callable:
    @app.before_request
    def wrapper() -> Optional[str]:
        if current_user.is_authenticated:
            user_id: int = current_user.id

            if db_manager.users.is_user_deleted(user_id):
                logout_user()
                flash(message=MESSAGES["users"]["user_deleted"], category="warning")
                return redirect(url_for("auth.login"))

            if db_manager.users.is_user_disabled(user_id):
                logout_user()
                flash(message=MESSAGES["users"]["user_disabled"], category="warning")
                return redirect(url_for("auth.login"))

    return wrapper
