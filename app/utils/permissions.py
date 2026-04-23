from functools import wraps
from typing import List

from flask_login import current_user

from app.utils import MESSAGES


def permission_required(allowed_levels: List[str]) -> callable:
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if current_user.permissions_level not in allowed_levels:
                return MESSAGES["auth"]["access_denied"]
            return function(*args, **kwargs)

        return wrapper

    return decorator
