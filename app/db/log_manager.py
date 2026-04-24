from datetime import date, time
from typing import Any, Dict, List, Optional, Tuple, Union

from .db_connection import DatabaseConnection


ACTION_LABELS: Dict[str, Dict[str, str]] = {
    "CREATE": {"short": "создан", "full": "создание"},
    "UPDATE": {"short": "обновлён", "full": "обновление"},
    "DELETE": {"short": "удалён", "full": "удаление"},
    "LOGIN": {"short": "вошёл", "full": "вход в систему"},
    "LOGOUT": {"short": "вышел", "full": "выход из системы"},
    "REGISTER": {"short": "зарегистрировался", "full": "регистрация"},
    "RESET_PASSWORD": {"short": "сброшен пароль", "full": "сброс пароля"},
    "DISABLE": {"short": "отключён", "full": "отключение"},
}

ENTITY_LABELS: Dict[str, str] = {
    "user": "пользователь",
    "employee": "сотрудник",
    "order": "заказ",
    "work": "работа",
    "task": "задание",
    "hours": "часы",
}


class LogManager(DatabaseConnection):
    def _get_entity_name(self, entity_type: str, entity_id: int) -> str:
        if entity_type == "employee":
            query = "SELECT name FROM employees WHERE id = ?"
        elif entity_type == "user":
            query = "SELECT name FROM users WHERE id = ?"
        elif entity_type == "order":
            query = "SELECT number FROM orders WHERE id = ?"
        elif entity_type == "work":
            query = "SELECT name FROM works WHERE id = ?"
        elif entity_type == "task":
            query = "SELECT work_name FROM tasks WHERE id = ?"
        else:
            return str(entity_id)

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (entity_id,))
                row = cursor.fetchone()
                return row[0] if row else str(entity_id)

    def get_logs(self) -> List[Dict[str, Any]]:
        query: str = """
            SELECT
                id,
                action,
                entity_id,
                entity_type,
                user_name,
                ip_address,
                platform,
                os_version,
                browser,
                created_date,
                created_time
            FROM logs
            ORDER BY id DESC
        """

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

        logs: List[Dict[str, Any]] = []
        for row in rows:
            log_dict: Dict[str, Any] = dict(zip(columns, row))
            action = log_dict.get("action", "")
            entity_type = log_dict.get("entity_type", "")
            entity_id = log_dict.get("entity_id", 0)

            entity_name = self._get_entity_name(entity_type, entity_id)
            action_label = ACTION_LABELS.get(action, {}).get("short", action.lower())
            entity_label = ENTITY_LABELS.get(entity_type, entity_type)

            log_dict["entity_name"] = entity_name
            log_dict["action_label"] = action_label
            log_dict["entity_label"] = entity_label
            log_dict["short_description"] = f"{action_label} {entity_label}: {entity_name}"
            log_dict["full_description"] = f"{ACTION_LABELS.get(action, {}).get('full', action)} {entity_type}"

            logs.append(log_dict)

        return logs

    def get_recent_logs(self, limit: int = 5) -> List[Dict[str, Any]]:
        query: str = """
            SELECT TOP (?)
                id,
                action,
                entity_id,
                entity_type,
                user_name,
                ip_address,
                platform,
                os_version,
                browser,
                created_date,
                created_time
            FROM logs
            ORDER BY id DESC
        """

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (limit,))
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

        logs: List[Dict[str, Any]] = []
        for row in rows:
            log_dict: Dict[str, Any] = dict(zip(columns, row))
            action = log_dict.get("action", "")
            entity_type = log_dict.get("entity_type", "")
            entity_id = log_dict.get("entity_id", 0)

            entity_name = self._get_entity_name(entity_type, entity_id)
            action_label = ACTION_LABELS.get(action, {}).get("short", action.lower())
            entity_label = ENTITY_LABELS.get(entity_type, entity_type)

            log_dict["entity_name"] = entity_name
            log_dict["action_label"] = action_label
            log_dict["entity_label"] = entity_label
            log_dict["short_description"] = f"{action_label} {entity_label}: {entity_name}"
            log_dict["full_description"] = f"{ACTION_LABELS.get(action, {}).get('full', action)} {entity_type}"

            logs.append(log_dict)

        return logs

    def create_log(
        self,
        action: str,
        entity_id: int,
        entity_type: str,
        user_name: str,
        ip_address: str,
        platform: str,
        os_version: str,
        browser: str,
        browser_version: str,
    ) -> None:
        query: str = """
            INSERT INTO logs (
                action,
                entity_id,
                entity_type,
                user_name,
                ip_address,
                platform,
                os_version,
                browser,
                browser_version
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        action,
                        entity_id,
                        entity_type,
                        user_name,
                        ip_address,
                        platform,
                        os_version,
                        browser,
                        browser_version,
                    ),
                )
                connection.commit()
