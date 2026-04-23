from .db_connection import DatabaseConnection
from .employee_manager import EmployeeManager
from .hour_manager import HourManager
from .log_manager import LogManager
from .order_manager import OrderManager
from .task_manager import TaskManager
from .user_manager import UserManager
from .work_manager import WorkManager


class DatabaseManager(DatabaseConnection):
    def __init__(self):
        self.employees: EmployeeManager = EmployeeManager()
        self.hours: HourManager = HourManager()
        self.logs: LogManager = LogManager()
        self.orders: OrderManager = OrderManager()
        self.tasks: TaskManager = TaskManager()
        self.users: UserManager = UserManager()
        self.works: WorkManager = WorkManager()
