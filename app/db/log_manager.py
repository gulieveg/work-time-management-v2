from typing import List, Tuple, Union

from .db_connection import DatabaseConnection


class LogManager(DatabaseConnection):
    def get_logs(self) -> List[Tuple[str]]:
        query: str = "SELECT * FROM logs"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                logs: List[Tuple[Union[str, int]]] = cursor.fetchall()
                return logs

    def get_recent_logs(self, limit: int = 5) -> List[Tuple[str]]:
        query: str = f"""
            SELECT TOP {limit} * FROM logs
            ORDER BY id DESC
        """

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                logs: List[Tuple[Union[str, int]]] = cursor.fetchall()
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
