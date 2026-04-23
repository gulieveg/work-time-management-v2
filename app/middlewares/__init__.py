from flask import Flask

from .maintenance import check_maintenance
from .user_status import check_user_status


def register_middlewares(app: Flask) -> None:
    check_maintenance(app)
    check_user_status(app)
