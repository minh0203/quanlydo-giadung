from dataclasses import dataclass
from datetime import datetime
from .database import Database


@dataclass
class Salary:
    salary_id: str
    employee_id: str
    employee_name: str
    month: int
    year: int
    base_salary: float
    commission: float = 0.0
    allowance: float = 0.0
    deduction: float = 0.0
    gross_salary: float = 0.0
    net_salary: float = 0.0
    status: str = "Nháp"
    approved_by: str = ""
    paid_date: str = ""
    note: str = ""
    created_at: str = ""

    @classmethod
    def create_table(cls, cursor):
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='salaries'")
        if cursor.fetchone() is None:
            cursor.execute(
                """
                CREATE TABLE salaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    salary_id TEXT UNIQUE NOT NULL,
                    employee_id TEXT NOT NULL,
                    employee_name TEXT NOT NULL,
                    month INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    base_salary REAL DEFAULT 0,
                    commission REAL DEFAULT 0,
                    allowance REAL DEFAULT 0,
                    deduction REAL DEFAULT 0,
                    gross_salary REAL DEFAULT 0,
                    net_salary REAL DEFAULT 0,
                    status TEXT DEFAULT 'Nháp',
                    approved_by TEXT,
                    paid_date TEXT,
                    note TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )

    @classmethod
    def generate_salary_id(cls):
        rows = Database.execute(
            "SELECT salary_id FROM salaries WHERE salary_id LIKE 'LG%' ORDER BY salary_id DESC",
            fetch_all=True,
        )
        max_num = 0
        for row in rows:
            salary_id = row[0]
            if salary_id and salary_id.startswith('LG'):
                try:
                    num = int(salary_id[2:])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        return f"LG{max_num + 1:05d}"

    @classmethod
    def create(cls, employee_id, employee_name, month, year, base_salary, commission=0, allowance=0, deduction=0):
        salary_id = cls.generate_salary_id()
        gross_salary = base_salary + commission + allowance
        net_salary = gross_salary - deduction
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        Database.execute(
            """INSERT INTO salaries 
               (salary_id, employee_id, employee_name, month, year, base_salary, 
                commission, allowance, deduction, gross_salary, net_salary, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (salary_id, employee_id, employee_name, month, year, base_salary,
             commission, allowance, deduction, gross_salary, net_salary, "Nháp", created_at),
            commit=True,
        )
        return cls(salary_id, employee_id, employee_name, month, year, base_salary,
                   commission, allowance, deduction, gross_salary, net_salary, "Nháp", "", "", "", created_at)

    @classmethod
    def get_all(cls):
        rows = Database.execute(
            """SELECT salary_id, employee_id, employee_name, month, year, base_salary, 
                      commission, allowance, deduction, gross_salary, net_salary, 
                      status, approved_by, paid_date, note, created_at FROM salaries 
               ORDER BY created_at DESC""",
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    @classmethod
    def get_by_month_year(cls, month, year):
        rows = Database.execute(
            """SELECT salary_id, employee_id, employee_name, month, year, base_salary, 
                      commission, allowance, deduction, gross_salary, net_salary, 
                      status, approved_by, paid_date, note, created_at FROM salaries 
               WHERE month = ? AND year = ? ORDER BY employee_name""",
            (month, year),
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    @classmethod
    def get_by_employee(cls, employee_id, month, year):
        row = Database.execute(
            """SELECT salary_id, employee_id, employee_name, month, year, base_salary, 
                      commission, allowance, deduction, gross_salary, net_salary, 
                      status, approved_by, paid_date, note, created_at FROM salaries 
               WHERE employee_id = ? AND month = ? AND year = ?""",
            (employee_id, month, year),
            fetch_one=True,
        )
        return cls(*row) if row else None

    def update(self):
        Database.execute(
            """UPDATE salaries SET commission = ?, allowance = ?, deduction = ?, 
                      gross_salary = ?, net_salary = ?, note = ? WHERE salary_id = ?""",
            (self.commission, self.allowance, self.deduction,
             self.gross_salary, self.net_salary, self.note, self.salary_id),
            commit=True,
        )

    def approve(self, approved_by):
        Database.execute(
            "UPDATE salaries SET status = ?, approved_by = ? WHERE salary_id = ?",
            ("Phê duyệt", approved_by, self.salary_id),
            commit=True,
        )
        self.status = "Phê duyệt"
        self.approved_by = approved_by

    def pay(self):
        Database.execute(
            "UPDATE salaries SET status = ?, paid_date = ? WHERE salary_id = ?",
            ("Đã thanh toán", datetime.now().strftime("%Y-%m-%d"), self.salary_id),
            commit=True,
        )
        self.status = "Đã thanh toán"
        self.paid_date = datetime.now().strftime("%Y-%m-%d")
