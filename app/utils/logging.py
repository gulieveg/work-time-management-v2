from flask import request
from flask_login import current_user


def create_log(action: str, entity_id: int, entity_type: str, user_name: str = None) -> None:
    from app.db import db_manager
    user_agent = request.user_agent
    db_manager.logs.create_log(
        action=action,
        entity_id=entity_id,
        entity_type=entity_type,
        user_name=user_name or current_user.name,
        ip_address=request.remote_addr or "unknown",
        platform=user_agent.platform or "unknown",
        os_version=user_agent.browser or "unknown",
        browser=user_agent.string[:50] if user_agent.string else "unknown",
        browser_version="",
    )