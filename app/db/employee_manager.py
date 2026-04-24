import re
from collections import defaultdict
from decimal import Decimal
from typing import Dict, List, Match, Optional, Tuple, Union

from app.utils import EMPLOYEE_CATEGORIES

from .db_connection import DatabaseConnection

DEFAULT_PAGE_SIZE: int = 10
DEFAULT_HOURS_PER_DAY: Decimal = Decimal("12.25")

Tasks = List[Dict[str, Union[str, Decimal]]]
Data = List[List[Union[str, Decimal]]]


class EmployeeManager(DatabaseConnection):
    def add_employee(self, name: str, personnel_number: str, department: str, category: str) -> int:
        query: str = """
            INSERT INTO employees (name, personnel_number, department, category)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?)
        """

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (name.strip(), personnel_number.strip(), department.strip(), category.strip()))
                result = cursor.fetchone()
                connection.commit()
                return int(result[0])

    def update_employee(
        self,
        employee_id: int,
        employee_name: str,
        personnel_number: str,
        employee_department: str,
        employee_category: str,
    ) -> None:
        query: str = """
            UPDATE employees
            SET
                name = ?,
                personnel_number = ?,
                department = ?,
                category = ?
            WHERE id = ?
        """

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        employee_name.strip(),
                        personnel_number.strip(),
                        employee_department.strip(),
                        employee_category.strip(),
                        employee_id,
                    ),
                )
                connection.commit()

    def delete_employee(self, employee_id: int) -> None:
        query: str = "DELETE FROM employees WHERE id = ?"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (employee_id,))
                connection.commit()

    def get_employee_used_hours(self, personnel_number: str, operation_date: str) -> Decimal:
        query: str = """
            SELECT SUM(hours)
            FROM tasks
            WHERE personnel_number = ? and operation_date = ?
        """

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (personnel_number.strip(), operation_date))
                used_hours: Decimal = cursor.fetchone()[0]

                if used_hours is None:
                    used_hours: Decimal = Decimal(0)
                return used_hours

    def get_employee_free_hours(self, personnel_number: str, operation_date: str) -> Decimal:
        used_hours: Decimal = self.get_employee_used_hours(personnel_number.strip(), operation_date)
        return DEFAULT_HOURS_PER_DAY - used_hours

    def get_employee_department(self, personnel_number: str) -> Optional[str]:
        query: str = "SELECT department FROM employees WHERE personnel_number = ?"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (personnel_number.strip(),))

                res: Optional[Tuple[str]] = cursor.fetchone()
                if res:
                    return res[0]

    def get_employee_category(self, personnel_number: str) -> Optional[str]:
        query: str = "SELECT category FROM employees WHERE personnel_number = ?"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (personnel_number.strip(),))

                res: Optional[Tuple[str]] = cursor.fetchone()
                if res:
                    return res[0]

    def get_employees_by_partial_match(self, query: str) -> List[str]:
        query_string: str = """
            SELECT name, personnel_number
            FROM employees
            WHERE name LIKE ? OR personnel_number LIKE ?
        """

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_string, ("%" + query + "%", "%" + query + "%"))
                employees = [f"{name} ({personnel_number})" for name, personnel_number in cursor.fetchall()]
                return employees

    def employee_exists(self, personnel_number: str, exclude_id: Optional[int] = None) -> bool:
        query: str = "SELECT * FROM employees WHERE personnel_number = ?"

        params: List[str] = [personnel_number.strip()]

        if exclude_id is not None:
            query += " AND id <> ?"
            params.append(exclude_id)

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, tuple(params))
                record: Optional[Tuple[str]] = cursor.fetchone()
                return record is not None

    def get_employee_details(self, employee_data: str) -> Optional[Tuple[str, str]]:
        pattern: str = "(?P<employee_name>[\\w\\s]+)\\s\\((?P<personnel_number>\\d+)\\)"
        matched: Match[str] = re.fullmatch(pattern=pattern, string=employee_data)
        if matched is None:
            return None
        return matched.group("employee_name"), matched.group("personnel_number")

    def get_employees_count(self) -> int:
        query: str = "SELECT COUNT(*) FROM employees"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchone()[0]

    def get_departments(self) -> List[str]:
        query: str = "SELECT name FROM departments"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)

                departments: List[str] = []
                for data in cursor.fetchall():
                    if data[0] not in departments:
                        departments.append(data[0])
                return departments

    def get_employees(
        self,
        employee_name: Optional[str] = None,
        personnel_number: Optional[str] = None,
        page: Optional[int] = None,
    ) -> List[str]:
        query: str = """
            SELECT id, name, personnel_number, department, category
            FROM employees
        """

        conditions: List[str] = []
        params: List[str] = []

        if employee_name:
            conditions.append("name = ?")
            params.append(employee_name.strip())
        if personnel_number:
            conditions.append("personnel_number = ?")
            params.append(personnel_number.strip())

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                if page:
                    offset: int = (page - 1) * DEFAULT_PAGE_SIZE
                    params.append(offset)
                    params.append(DEFAULT_PAGE_SIZE)
                    query += """
                        ORDER BY id
                        OFFSET ? ROWS
                        FETCH NEXT ? ROWS ONLY
                    """

                cursor.execute(query, tuple(params))
                employees: List[Tuple[str]] = cursor.fetchall()
                return employees

    def get_employee_names_by_partial_match(self, query: str) -> List[str]:
        query_string: str = "SELECT name FROM employees WHERE name LIKE ?"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_string, ("%" + query + "%",))
                employee_names: List[str] = [data[0] for data in cursor.fetchall()]
                return employee_names

    def get_personnel_numbers_by_partial_match(self, query: str) -> List[str]:
        query_string: str = "SELECT personnel_number FROM employees WHERE personnel_number LIKE ?"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query_string, ("%" + query + "%",))
                personnel_numbers: List[str] = [data[0] for data in cursor.fetchall()]
                return personnel_numbers

    def get_employee_name_by_number(self, personnel_number: str) -> Optional[str]:
        query: str = "SELECT name FROM employees WHERE personnel_number = ?"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (personnel_number.strip(),))

                row: Optional[Tuple[str]] = cursor.fetchone()
                return row and row[0]

    def get_personnel_number_by_name(self, employee_name: str) -> Optional[str]:
        query: str = "SELECT personnel_number FROM employees WHERE name = ?"

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (employee_name.strip(),))

                row: Optional[Tuple[str]] = cursor.fetchone()
                return row and row[0]

    def get_employee_data_by_id(self, employee_id: int) -> Optional[Dict[str, Union[str, int]]]:
        query: str = """
            SELECT id, name, personnel_number, department, category
            FROM employees
            WHERE id = ?
        """

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (employee_id,))

                employee_data: Optional[Tuple[str]] = cursor.fetchone()
                if employee_data:
                    return {
                        "employee_id": employee_data[0],
                        "employee_name": employee_data[1],
                        "personnel_number": employee_data[2],
                        "employee_department": employee_data[3],
                        "employee_category": employee_data[4],
                    }

    def get_employees_data(self, tasks: Tasks) -> Data:
        """
        Groups tasks by employee and date, aggregating hours for report generation.

        Creates unique key from employee details and date to aggregate hours,
        then formats the result with translated category names.

        Args:
            tasks (Tasks): List of task records, each containing employee details,
                order information, and work metrics.

        Returns:
            employees_data (Data):  List of lists, where each inner list contains the data for one specific employee
                on specific date.
        """

        spent_hours_per_employee: Dict[Tuple[str, ...], Decimal] = defaultdict(Decimal)

        for task in tasks:
            key: Tuple[str, ...] = (
                task["employee_name"],
                task["personnel_number"],
                task["employee_category"],
                task["department"],
                task["operation_date"],
            )
            spent_hours_per_employee[key] += task["hours"]

        employees_data: Data = [
            [
                employee_details[0],
                employee_details[1],
                EMPLOYEE_CATEGORIES[employee_details[2]],
                employee_details[3],
                operation_date,
                spent_hours,
            ]
            for (*employee_details, operation_date), spent_hours in spent_hours_per_employee.items()
        ]
        return employees_data
