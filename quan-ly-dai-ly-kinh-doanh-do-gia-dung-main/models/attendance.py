from dataclasses import dataclass
from datetime import datetime
from .database import Database


@dataclass
class Attendance:
    id: int
    employee_id: str
    employee_name: str
    check_in_date: str
    check_in_time: str
    check_out_time: str
    status: str
    note: str
    created_at: str

    @classmethod
    def create_table(cls, cursor):
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='attendance'")
        if cursor.fetchone() is None:
            cursor.execute(
                """
                CREATE TABLE attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id TEXT NOT NULL,
                    employee_name TEXT NOT NULL,
                    check_in_date TEXT NOT NULL,
                    check_in_time TEXT,
                    check_out_time TEXT,
                    status TEXT DEFAULT 'Đúng giờ',
                    note TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )

    @classmethod
    def check_in(cls, employee_id, employee_name):
        check_in_time = datetime.now().strftime("%H:%M:%S")
        check_in_date = datetime.now().strftime("%Y-%m-%d")
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        Database.execute(
            "INSERT INTO attendance (employee_id, employee_name, check_in_date, check_in_time, created_at) VALUES (?, ?, ?, ?, ?)",
            (employee_id, employee_name, check_in_date, check_in_time, created_at),
            commit=True,
        )

    @classmethod
    def check_out(cls, employee_id, check_in_date):
        check_out_time = datetime.now().strftime("%H:%M:%S")
        Database.execute(
            "UPDATE attendance SET check_out_time = ? WHERE employee_id = ? AND check_in_date = ? AND check_out_time IS NULL",
            (check_out_time, employee_id, check_in_date),
            commit=True,
        )

    @classmethod
    def get_by_date(cls, date):
        rows = Database.execute(
            "SELECT id, employee_id, employee_name, check_in_date, check_in_time, check_out_time, status, note, created_at FROM attendance WHERE check_in_date = ? ORDER BY employee_name",
            (date,),
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    @classmethod
    def get_by_employee(cls, employee_id, month, year):
        rows = Database.execute(
            """SELECT id, employee_id, employee_name, check_in_date, check_in_time, check_out_time, status, note, created_at 
               FROM attendance WHERE employee_id = ? AND strftime('%Y-%m', check_in_date) = ? 
               ORDER BY check_in_date""",
            (employee_id, f"{year}-{month:02d}"),
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    def calculate_hours(self):
        if self.check_in_time and self.check_out_time:
            try:
                check_in = datetime.strptime(self.check_in_time, "%H:%M:%S")
                check_out = datetime.strptime(self.check_out_time, "%H:%M:%S")
                delta = check_out - check_in
                return delta.total_seconds() / 3600
            except Exception:
                return 0
        return 0
