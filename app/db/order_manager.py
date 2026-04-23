from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Union

from .db_connection import DatabaseConnection
from .work_manager import WorkManager

Tasks = List[Dict[str, Union[str, Decimal]]]
Data = List[List[Union[str, Decimal]]]

work_manager: WorkManager = WorkManager()


class OrderManager(DatabaseConnection):
    def add_order(self, order_number: str, order_name: str) -> int:
        query: str = "INSERT INTO orders (number, name) OUTPUT INSERTED.id VALUES (?, ?)"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (order_number.strip(), order_name.strip()))
                order_id: int = cursor.fetchone()[0]
                connection.commit()
        return order_id

    def order_exists(self, order_number: str, exclude_id: Optional[int] = None) -> bool:
        query: str = "SELECT * FROM orders WHERE number = ?"

        params: List[str] = [order_number.strip()]

        if exclude_id is not None:
            query += " AND id <> ?"
            params.append(exclude_id)

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, tuple(params))
                record: Optional[Tuple[str]] = cursor.fetchone()
                return record is not None

    def get_order_names_by_partial_match(self, query: str) -> List[str]:
        query_string: str = "SELECT name FROM orders WHERE name LIKE ?"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_string, ("%" + query + "%",))
                order_names: List[str] = [data[0] for data in cursor.fetchall()]
                return order_names

    def get_order_numbers_by_partial_match(self, query: str) -> List[str]:
        query_string: str = "SELECT number FROM orders WHERE number LIKE ?"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_string, ("%" + query + "%",))
                order_numbers: List[str] = [data[0] for data in cursor.fetchall()]
                return order_numbers

    def get_order_number_by_name(self, order_name: str) -> Optional[str]:
        query: str = "SELECT number FROM orders WHERE name = ?"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (order_name.strip(),))

                res: Optional[Tuple[str]] = cursor.fetchone()
                if res:
                    return res[0]

    def get_order_name_by_number(self, order_number: str) -> Optional[str]:
        query: str = "SELECT name FROM orders WHERE number = ?"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (order_number.strip(),))

                res: Optional[Tuple[str]] = cursor.fetchone()
                if res:
                    return res[0]

    def get_order_id_by_number(self, order_number: str) -> Optional[int]:
        query: str = "SELECT id FROM orders WHERE number = ?"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (order_number.strip(),))

                res: Optional[Tuple[str]] = cursor.fetchone()
                if res:
                    return res[0]

    def get_order_data_by_id(self, order_id: int) -> Optional[Dict[str, Union[str, int]]]:
        query: str = "SELECT id, number, name FROM orders WHERE id = ?"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (order_id,))

                order_data: Optional[Tuple[str]] = cursor.fetchone()
                if order_data:
                    return {
                        "id": order_data[0],
                        "order_number": order_data[1],
                        "order_name": order_data[2],
                    }

    def delete_order(self, order_id: str) -> None:
        query: str = "DELETE FROM orders WHERE id = ?"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (order_id,))
                connection.commit()

    def update_order(self, order_id: int, order_number: str, order_name: str) -> None:
        query: str = "UPDATE orders SET number = ?, name = ? WHERE id = ?"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (order_number.strip(), order_name.strip(), order_id))
                connection.commit()

    def get_orders(
        self,
        order_number: Optional[str] = None,
        order_name: Optional[str] = None,
        page: Optional[int] = None,
    ) -> List[Tuple[str]]:
        query: str = "SELECT id, number, name FROM orders"

        conditions: List[str] = []
        params: List[str] = []

        if order_number:
            conditions.append("number = ?")
            params.append(order_number.strip())
        if order_name:
            conditions.append("name = ?")
            params.append(order_name.strip())

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                if page:
                    page_size: int = 9
                    offset: int = (page - 1) * page_size
                    params.append(offset)
                    params.append(page_size)
                    query += """
                        ORDER BY id
                        OFFSET ? ROWS
                        FETCH NEXT ? ROWS ONLY
                    """
                cursor.execute(query, (tuple(params)))
                orders: List[Tuple[str]] = cursor.fetchall()
                return orders

    def get_orders_count(self) -> int:
        query: str = "SELECT COUNT(*) FROM orders"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchone()[0]

    def get_spent_hours_for_2025(self) -> Dict[str, Decimal]:
        query: str = "SELECT order_number, spent_hours FROM hours"

        spent_hours_by_order: Dict[str, Decimal] = defaultdict(Decimal)

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                for order_number, spent_hours in cursor.fetchall():
                    spent_hours_by_order[order_number] = spent_hours
                return spent_hours_by_order

    def get_planned_hours_for_order(self, order_number: str) -> Decimal:
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                query: str = "SELECT id FROM orders WHERE number = ?"
                cursor.execute(query, (order_number.strip(),))
                order_id: int = cursor.fetchone()[0]

                query: str = "SELECT SUM(planned_hours) FROM works WHERE order_id = ?"
                cursor.execute(query, (order_id,))
                return cursor.fetchone()[0]

    def get_planned_hours_per_order(self, order_numbers: Tuple[str]) -> List:
        if not order_numbers:
            return []

        placeholders: str = ",".join("?" for _ in order_numbers)

        query: str = f"""
            SELECT
                orders.number,
                orders.name,
                COALESCE(SUM(works.planned_hours), 0) AS planned_hours
            FROM orders
            LEFT JOIN works ON works.order_id = orders.id
            WHERE orders.number IN ({placeholders})
            GROUP BY orders.number, orders.name
            ORDER BY orders.number
        """

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, order_numbers)
                return cursor.fetchall()

    def get_basic_orders_data(
        self,
        tasks: Tasks,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        extended: bool = False,
    ) -> Data:
        """
        Returns orders data including planned, spent, and remaining hours.

        This function calculates the total spent hours per order based on the provided tasks,
        optionally includes spent hours for the year 2025, if the specified date range requires it.

        Args:
            tasks (Tasks): List of task records, each containing employee details,
                order information, and work metrics.
            start_date (datetime): The start date for selecting tasks from the database.
            end_date (datetime): The end date for selecting tasks from the database.

        Returns:
            orders_data (Data): List of lists, where each inner list contains the data for one specific order,
                including its number, name, planned hours, spent hours, and remaining hours.
                The final inner list in the outer list contains the totals for planned hours, spent hours,
                and remaining hours calculated across all orders in the dataset.
        """

        def period_contains_2025(start_date: datetime, end_date: datetime) -> bool:
            """
            Checks if the given period contains any date in the year 2025.

            Args:
                start_date (datetime, optional): The start of the period.
                end_date (datetime, optional): The end of the period.

            Returns:
                bool: True if the period includes any date in 2025, False otherwise.
            """
            lower_bound: datetime = datetime(2024, 12, 31)
            upper_bound: datetime = datetime(2026, 1, 1)

            if not start_date and not end_date:
                return True
            elif not start_date and end_date and end_date > lower_bound:
                return True
            elif start_date and end_date and lower_bound < start_date < upper_bound and end_date >= start_date:
                return True
            elif start_date and lower_bound < start_date < upper_bound and not end_date:
                return True
            return False

        spent_hours_per_order: Dict[str, Decimal] = defaultdict(Decimal)

        for task in tasks:
            spent_hours_per_order[task["order_number"]] += task["hours"]

        if extended and period_contains_2025(start_date, end_date):
            spent_hours_for_2025: Dict[str, Decimal] = self.get_spent_hours_for_2025()

            for order_number, spent_hours in spent_hours_for_2025.items():
                spent_hours_per_order[order_number] += spent_hours

        orders_data: Data = []

        order_numbers: Tuple[str] = tuple(spent_hours_per_order.keys())

        if order_numbers:
            planned_hours_per_order: List = self.get_planned_hours_per_order(order_numbers=order_numbers)

            for order_number, order_name, planned_hours in planned_hours_per_order:
                spent_hours: Decimal = spent_hours_per_order[order_number]
                remaining_hours: Decimal = planned_hours - spent_hours
                orders_data.append(
                    [
                        order_number,
                        order_name,
                        planned_hours,
                        spent_hours,
                        remaining_hours,
                    ]
                )

        planned_hours, spent_hours, remaining_hours = Decimal(0), Decimal(0), Decimal(0)

        for order_data in orders_data:
            planned_hours += order_data[2]
            spent_hours += order_data[3]
            remaining_hours += order_data[4]

        orders_data.append(["Итого", "", planned_hours, spent_hours, remaining_hours])
        return orders_data

    def get_detailed_orders_data(self, tasks: Tasks) -> Data:
        """
        Returns order data with detailed information by types of work.

        This function extends the basic orders data by providing information on work types
        associated with each order. For each order it displays list of work types with their planned,
        spent and remaining hours.

        The function calculates spent hours of work types from the provided tasks for each order and
        displays all associated work types with their corresponding planned, spent and remaining hours.

        This provides detailed view of hour distribution across different work types within each order.

        Args:
            tasks (Tasks): List of task records, each containing employee details,
                order information, and work metrics.

        Returns:
            orders_data (Data): List of lists, where each inner list contains the data for one specific order,
                including its number, name, work name, planned hours, spent hours, and remaining hours.
        """

        spent_hours_per_work: Dict[str, Decimal] = defaultdict(Decimal)

        for task in tasks:
            key: Tuple[str, str] = (
                task["order_number"],
                task["work_name"],
            )
            spent_hours_per_work[key] += task["hours"]

        order_numbers, work_names = [], []

        for order_number, work_name in spent_hours_per_work.keys():
            order_numbers.append(order_number)
            work_names.append(work_name)

        orders_data: Data = []

        if order_numbers and work_names:
            planned_hours_per_work: List = work_manager.get_planned_hours_per_work(
                order_numbers=order_numbers,
                work_names=work_names,
            )

            for order_number, order_name, work_name, planned_hours in planned_hours_per_work:
                spent_hours: Decimal = spent_hours_per_work[(order_number, work_name)]
                remaining_hours: Decimal = planned_hours - spent_hours
                orders_data.append(
                    [
                        order_number,
                        order_name,
                        work_name,
                        planned_hours,
                        spent_hours,
                        remaining_hours,
                    ]
                )
            return orders_data
