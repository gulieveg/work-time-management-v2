from flask import Flask

from .errors import handle_error_404
from .logging import create_log
from .messages import EMPLOYEE_CATEGORIES, MESSAGES
from .permissions import permission_required
from .reports import get_report_file
from .template_filters import zip_iterables


def register_error_handlers(app: Flask) -> None:
    handle_error_404(app)


def register_template_filters(app: Flask) -> None:
    app.jinja_env.filters["zip_iterables"] = zip_iterables