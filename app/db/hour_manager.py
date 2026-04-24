from decimal import Decimal
from typing import Any, List, Tuple

from .db_connection import DatabaseConnection


class HourManager(DatabaseConnection):
    def add_hours(
        self,
        order_name: str,
        order_number: str,
        order_id: int,
        work_name: str,
        spent_hours: Decimal,
    ) -> int:
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                query: str = """
                    INSERT INTO hours (order_name, order_number, work_name, spent_hours)
                    OUTPUT INSERTED.id
                    VALUES (?, ?, ?, ?)
                """
                cursor.execute(query, (order_name.strip(), order_number.strip(), work_name.strip(), spent_hours))
                result = cursor.fetchone()
                hours_id = int(result[0])

                query = """
                    UPDATE works
                    SET spent_hours = ?
                    WHERE order_id = ? AND name = ?
                """
                cursor.execute(query, (spent_hours, order_id, work_name))
            connection.commit()
            return hours_id

    def delete_hours(self, hours_id: int, order_id: int, work_name: str) -> None:
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                query = """
                    UPDATE works
                    SET planned_hours = 0, spent_hours = 0
                    WHERE order_id = ? AND name = ?
                """
                cursor.execute(query, (order_id, work_name.strip()))

                query = "DELETE FROM hours WHERE id = ?"
                cursor.execute(query, (hours_id,))
            connection.commit()

    def get_hours_list(self) -> List[Tuple[Any]]:
        query: str = """
            SELECT id, order_name, order_number, work_name, spent_hours, created_date, created_time
            FROM hours
        """

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                hours_list: List[Tuple[Any]] = cursor.fetchall()
                return hours_list