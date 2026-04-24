from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple, Union

from .db_connection import DatabaseConnection

DEFAULT_PAGE_SIZE: int = 10


class WorkManager(DatabaseConnection):
    def add_work(self, order_id: str, work_name: str, planned_hours: Decimal) -> int:
        query: str = """
            INSERT INTO works (order_id, name, planned_hours)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?)
        """

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (order_id, work_name.strip(), planned_hours))
                result = cursor.fetchone()
                connection.commit()
                return int(result[0])

    def update_work(self, work_id: int, work_name: str, planned_hours: Decimal) -> None:
        query: str = "UPDATE works SET name = ?, planned_hours = ? WHERE id = ?"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (work_name.strip(), planned_hours, work_id))
                connection.commit()

    def delete_work(self, work_id: int) -> None:
        query: str = "DELETE FROM works WHERE id = ?"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (work_id,))
                connection.commit()

    def work_exists(self, order_id: int, work_name: str, exclude_id: Optional[int] = None) -> bool:
        query: str = """
            SELECT *
            FROM works
            WHERE order_id = ? AND name = ?
        """

        params: List[str] = [order_id, work_name.strip()]

        if exclude_id is not None:
            query += " AND id <> ?"
            params.append(exclude_id)

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, tuple(params))
                record: Optional[Tuple[str]] = cursor.fetchone()
                return record is not None

    def get_works(
        self,
        order_id: Optional[int] = None,
        order_number: Optional[str] = None,
        work_name: Optional[str] = None,
        page: Optional[int] = None,
    ) -> List[Tuple[Any]]:
        query: str = """
            SELECT
                works.id,
                orders.number,
                works.name,
                works.planned_hours,
                works.spent_hours,
                works.remaining_hours
            FROM works
            JOIN orders ON works.order_id = orders.id
        """

        conditions: List[str] = []
        params: List[Any] = []

        if order_id:
            conditions.append("works.order_id = ?")
            params.append(order_id)
        elif order_number:
            conditions.append("orders.number = ?")
            params.append(order_number.strip())

        if work_name:
            conditions.append("works.name = ?")
            params.append(work_name.strip())

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                if page:
                    offset: int = (page - 1) * DEFAULT_PAGE_SIZE
                    query += """
                        ORDER BY works.id
                        OFFSET ? ROWS
                        FETCH NEXT ? ROWS ONLY
                    """
                    params.append(offset)
                    params.append(DEFAULT_PAGE_SIZE)

                cursor.execute(query, tuple(params))
                works: List[Tuple[Any]] = cursor.fetchall()
                return works

    def get_work_data_by_id(self, work_id: int) -> Optional[Dict[str, Union[str, int]]]:
        query: str = """
            SELECT id, order_id, name, planned_hours, spent_hours, remaining_hours
            FROM works
            WHERE id = ?
        """

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (work_id,))

                work_data: Optional[Tuple[str]] = cursor.fetchone()
                if work_data:
                    return {
                        "id": work_data[0],
                        "order_id": work_data[1],
                        "work_name": work_data[2],
                        "planned_hours": work_data[3],
                        "spent_hours": work_data[4],
                        "remaining_hours": work_data[5],
                    }

    def get_works_for_order_by_number(self, order_number: str) -> List[Dict[str, Union[str, Decimal]]]:
        query: str = """
            SELECT
                works.id,
                works.name,
                works.planned_hours,
                works.spent_hours,
                works.remaining_hours
            FROM works
            JOIN orders ON works.order_id = orders.id
            WHERE orders.number = ?
        """

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (order_number.strip(),))

                works: List[Dict[str, Union[str, Decimal]]] = [
                    {
                        "work_id": work_data[0],
                        "work_name": work_data[1],
                        "planned_hours": work_data[2],
                        "spent_hours": work_data[3],
                        "remaining_hours": work_data[4],
                    }
                    for work_data in cursor.fetchall()
                ]
                return works

    def get_work_names_by_partial_match(self, query: str, order_id: int) -> List[str]:

        query_string: str = "SELECT name FROM works WHERE name LIKE ? AND order_id = ?"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_string, ("%" + query + "%", order_id))
                work_names: List[str] = [data[0] for data in cursor.fetchall()]
                return work_names

    def get_planned_hours_per_work(self, order_numbers: List[str], work_names: List[str]) -> List[Tuple[Any, ...]]:
        if not order_numbers or not work_names:
            return []

        pairs: List[Tuple[str, str]] = list(zip(order_numbers, work_names))

        placeholders: str = ",".join(["(?, ?)" for _ in pairs])

        query: str = f"""
            SELECT
                orders.number,
                orders.name,
                works.name,
                works.planned_hours
            FROM orders
            INNER JOIN works ON orders.id = works.order_id
            INNER JOIN (VALUES {placeholders}) AS filters(order_number, work_name)
            ON orders.number = filters.order_number AND works.name = filters.work_name
            ORDER BY orders.number, works.name
        """

        params: List[str] = [item for pair in pairs for item in pair]

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    def get_works_count(self) -> int:
        query: str = "SELECT COUNT(*) FROM works"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchone()[0]
