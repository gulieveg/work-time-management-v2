from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Union

from app.utils import EMPLOYEE_CATEGORIES

from .db_connection import DatabaseConnection
from .employee_manager import EmployeeManager

Tasks = List[Dict[str, Union[str, Decimal]]]
Data = List[List[Union[str, Decimal]]]
employee_manager: EmployeeManager = EmployeeManager()


class TaskManager(DatabaseConnection):
    def add_task(
        self,
        employee_name: str,
        personnel_number: str,
        department: str,
        work_name: str,
        hours: Decimal,
        order_number: str,
        order_name: str,
        operation_date: str,
        employee_category: str,
    ) -> int:
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                query: str = """
                    INSERT INTO tasks (
                        employee_name,
                        personnel_number,
                        department,
                        work_name,
                        hours,
                        order_number,
                        order_name,
                        operation_date,
                        employee_category
                    )
                    OUTPUT INSERTED.id
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(
                    query,
                    (
                        employee_name.strip(),
                        personnel_number.strip(),
                        department.strip(),
                        work_name.strip(),
                        hours,
                        order_number.strip(),
                        order_name.strip(),
                        operation_date,
                        employee_category.strip(),
                    ),
                )

                task_id: int = cursor.fetchone()[0]

                query: str = """
                    UPDATE works
                    SET works.spent_hours = works.spent_hours + ?
                    FROM works
                    JOIN orders ON works.order_id = orders.id
                    WHERE works.name = ? AND orders.number = ?
                """
                cursor.execute(query, (hours, work_name, order_number))
            connection.commit()
        return task_id

    def delete_task(self, task_id: int) -> None:
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                query: str = "SELECT order_number, work_name, hours FROM tasks WHERE id = ?"
                cursor.execute(query, (task_id,))
                order_number, work_name, hours = cursor.fetchone()

                query: str = "DELETE FROM tasks WHERE id = ?"
                cursor.execute(query, (task_id,))

                query: str = """
                    UPDATE works
                    SET spent_hours = spent_hours - ?
                    FROM works
                    JOIN orders ON works.order_id = orders.id
                    WHERE works.name = ? AND orders.number = ?
                """
                cursor.execute(query, (hours, work_name, order_number))
            connection.commit()

    def get_task_data_by_id(self, task_id: int) -> Optional[Dict[str, Union[str, Decimal]]]:
        query: str = """
            SELECT
                id,
                employee_name,
                personnel_number,
                department,
                work_name,
                hours,
                order_number,
                order_name,
                operation_date
            FROM tasks WHERE id = ?
        """

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (task_id,))

                task_data: Optional[Tuple[str]] = cursor.fetchone()
                if task_data:
                    return {
                        "id": task_data[0],
                        "employee_name": task_data[1],
                        "personnel_number": task_data[2],
                        "department": task_data[3],
                        "work_name": task_data[4],
                        "hours": task_data[5],
                        "order_number": task_data[6],
                        "order_name": task_data[7],
                        "operation_date": task_data[8].strftime("%Y-%m-%d"),
                    }

    def get_tasks(
        self,
        departments: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        employee_data: Optional[str] = None,
        order_number: Optional[str] = None,
        work_name: Optional[str] = None,
        order_name: Optional[str] = None,
    ) -> Tasks:
        base_query: str = """
            SELECT
                id,
                employee_name,
                personnel_number,
                department,
                work_name,
                hours,
                order_number,
                order_name,
                operation_date,
                employee_category
            FROM tasks
        """

        if departments:
            departments: List[str] = list(filter(None, departments))
            placeholders: str = ",".join(["?"] * len(departments))
            query: str = f"{base_query} WHERE department IN ({placeholders})"
            params: List[str] = departments
        else:
            query: str = f"{base_query} WHERE 1 = 1"
            params: List[str] = []

        if start_date:
            query += " AND operation_date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND operation_date <= ?"
            params.append(end_date)

        if employee_data:
            employee_details: Optional[Tuple[str, str]] = employee_manager.get_employee_details(employee_data)
            if employee_details is None:
                query += " AND employee_name = ?"
                params.append(employee_data)
            else:
                _, personnel_number = employee_details
                query += " AND personnel_number = ?"
                params.append(personnel_number)

        if order_number:
            query += " AND order_number = ?"
            params.append(order_number.strip())

        if work_name:
            query += " AND work_name = ?"
            params.append(work_name.strip())

        if order_name:
            query += " AND order_name = ?"
            params.append(order_name.strip())

        query += " ORDER BY employee_name, personnel_number, operation_date"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, tuple(params))

                tasks: List[Dict[str, str]] = [
                    {
                        "id": task[0],
                        "employee_name": task[1],
                        "personnel_number": task[2],
                        "department": task[3],
                        "work_name": task[4],
                        "hours": task[5],
                        "order_number": task[6],
                        "order_name": task[7],
                        "operation_date": task[8].strftime("%Y-%m-%d"),
                        "employee_category": task[9],
                    }
                    for task in cursor.fetchall()
                ]
                return tasks

    def update_task(
        self,
        task_id: int,
        employee_name: str,
        personnel_number: str,
        hours: Decimal,
        order_name: str,
        order_number: str,
        operation_date: str,
        work_name: str,
    ) -> None:
        department: str = employee_manager.get_employee_department(personnel_number)

        query: str = """
            UPDATE tasks
            SET
                employee_name = ?,
                personnel_number = ?,
                department = ?,
                work_name = ?,
                hours = ?,
                order_number = ?,
                order_name = ?,
                operation_date = ?
            WHERE id = ?
        """

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        employee_name.strip(),
                        personnel_number.strip(),
                        department.strip(),
                        work_name.strip(),
                        hours,
                        order_number.strip(),
                        order_name.strip(),
                        operation_date,
                        task_id,
                    ),
                )
                connection.commit()

    def get_tasks_count(self) -> int:
        query: str = "SELECT COUNT(*) FROM tasks"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchone()[0]

    def get_tasks_data(self, tasks: Tasks) -> Data:
        """
        Converts tasks object into list of lists for report generation.

        Args:
            tasks (Tasks): List of task records, each containing employee details,
                order information, and work metrics.

        Returns:
            tasks_data (Data): List of lists, where each inner list contains the data for one specific task.
        """
        tasks_data: Data = [
            [
                task["employee_name"],
                task["personnel_number"],
                EMPLOYEE_CATEGORIES[task["employee_category"]],
                task["department"],
                task["order_number"],
                task["order_name"],
                task["work_name"],
                task["hours"],
                task["operation_date"],
            ]
            for task in tasks
        ]
        return tasks_data

    def get_stats_by_department(self, start_date: str, end_date: str) -> Dict[str, Dict[str, Decimal]]:
        query: str = """
            SELECT
                department,
                COUNT(*) as task_count,
                SUM(hours) as total_hours
            FROM tasks
            WHERE operation_date >= ? AND operation_date <= ?
            GROUP BY department
        """

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (start_date, end_date))
                results: List[Tuple[str, int, Decimal]] = cursor.fetchall()
                return {
                    row[0]: {
                        "task_count": row[1],
                        "total_hours": row[2] if row[2] else Decimal(0)
                    }
                    for row in results
                }
