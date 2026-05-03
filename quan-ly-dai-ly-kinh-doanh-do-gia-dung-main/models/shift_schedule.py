from dataclasses import dataclass
from datetime import datetime
from .database import Database


@dataclass
class ShiftScheduleEntry:
    id: int
    year_month: str
    employee_id: str
    employee_name: str
    day: int
    shift_code: str
    created_at: str

    @classmethod
    def create_table(cls, cursor):
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shift_schedules'")
        if cursor.fetchone() is None:
            cursor.execute(
                """
                CREATE TABLE shift_schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    year_month TEXT NOT NULL,
                    employee_id TEXT NOT NULL,
                    employee_name TEXT NOT NULL,
                    day INTEGER NOT NULL,
                    shift_code TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    @classmethod
    def get_by_month(cls, year_month):
        rows = Database.execute(
            "SELECT id, year_month, employee_id, employee_name, day, shift_code, created_at FROM shift_schedules WHERE year_month = ? ORDER BY employee_name, day",
            (year_month,),
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    @classmethod
    def save_month(cls, year_month, entries):
        Database.execute(
            "DELETE FROM shift_schedules WHERE year_month = ?",
            (year_month,),
            commit=True,
        )
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for entry in entries:
            Database.execute(
                "INSERT INTO shift_schedules (year_month, employee_id, employee_name, day, shift_code, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    year_month,
                    entry["employee_id"],
                    entry["employee_name"],
                    entry["day"],
                    entry["shift_code"],
                    now,
                ),
                commit=True,
            )

    @classmethod
    def get_employee_schedule(cls, employee_id, year_month):
        rows = Database.execute(
            "SELECT id, year_month, employee_id, employee_name, day, shift_code, created_at FROM shift_schedules WHERE year_month = ? AND employee_id = ? ORDER BY day",
            (year_month, employee_id),
            fetch_all=True,
        )
        return [cls(*row) for row in rows]
