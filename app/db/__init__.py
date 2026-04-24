from app.db.db_manager import DatabaseManager

db_manager: DatabaseManager = DatabaseManager()

__all__ = ["DatabaseManager", "db_manager"]