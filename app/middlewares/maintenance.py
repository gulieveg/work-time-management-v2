from typing import Callable, Optional, Tuple

from flask import Flask, render_template, request


def check_maintenance(app: Flask) -> Callable:
    @app.before_request
    def wrapper() -> Optional[str]:
        MAINTENANCE_MODE = app.config.get("MAINTENANCE_MODE", False)

        excluded_routes: Tuple[str] = ("/static", "/logout")

        if MAINTENANCE_MODE:
            if request.path != "/" and not request.path.startswith(excluded_routes):
                return render_template("maintenance/maintenance.html"), 503

    return wrapper
