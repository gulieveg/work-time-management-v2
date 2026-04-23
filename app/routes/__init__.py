from flask import Flask

from .auth import auth_bp
from .control import control_bp
from .employees import employees_bp
from .help import help_bp
from .orders import orders_bp
from .tasks import tasks_bp


def register_routes(app: Flask) -> None:
    app.register_blueprint(control_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(help_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(tasks_bp)
