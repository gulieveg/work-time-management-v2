from flask_login import UserMixin


class User(UserMixin):
    def __init__(
        self,
        user_id: int,
        user_name: str,
        user_department: str,
        user_login: str,
        user_permissions_level: str,
        is_user_factory_worker: bool,
        is_user_account_enabled: bool,
        is_user_admin: bool,
    ) -> None:
        self.id: int = user_id
        self.name: str = user_name
        self.department: str = user_department
        self.login: str = user_login
        self.permissions_level: str = user_permissions_level
        self.is_factory_worker: bool = is_user_factory_worker
        self.is_account_enabled: bool = is_user_account_enabled
        self.is_admin: bool = is_user_admin
