from dataclasses import dataclass
from datetime import datetime
from .database import Database


@dataclass
class Salary:
    """Model cho bảng lương"""
    salary_id: str
    employee_id: str
    month: int
    year: int
    base_salary: float = 0.0
    overtime_hours: float = 0.0
    overtime_salary: float = 0.0
    bonus: float = 0.0
    deduction: float = 0.0
    gross_salary: float = 0.0
    net_salary: float = 0.0
    status: str = "Nháp"  # Nháp, Phê duyệt, Đã thanh toán
    note: str = ""
    created_at: str = ""
    updated_at: str = ""

    VALID_STATUSES = ["Nháp", "Phê duyệt", "Đã thanh toán"]

    @classmethod
    def create_table(cls, cursor):
        """Tạo bảng lương"""
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS salaries (
                salary_id TEXT PRIMARY KEY,
                employee_id TEXT NOT NULL,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                base_salary REAL DEFAULT 0.0,
                overtime_hours REAL DEFAULT 0.0,
                overtime_salary REAL DEFAULT 0.0,
                bonus REAL DEFAULT 0.0,
                deduction REAL DEFAULT 0.0,
                gross_salary REAL DEFAULT 0.0,
                net_salary REAL DEFAULT 0.0,
                status TEXT DEFAULT 'Nháp',
                note TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
            )
            """
        )

    @classmethod
    def generate_salary_id(cls):
        """Tạo mã bảng lương tự động"""
        rows = Database.execute(
            "SELECT salary_id FROM salaries WHERE salary_id LIKE 'SAL%'",
            fetch_all=True,
        )
        max_num = 0
        for row in rows:
            salary_id = row[0]
            if salary_id.startswith('SAL'):
                try:
                    num = int(salary_id[3:])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        new_num = max_num + 1
        return f"SAL{new_num:05d}"

    @classmethod
    def create(cls, employee_id, month, year, base_salary, overtime_hours=0, bonus=0, deduction=0):
        """Tạo bảng lương mới"""
        salary_id = cls.generate_salary_id()
        now = datetime.now().isoformat()
        
        # Tính lương tăng ca (1.5x lương giờ)
        hourly_rate = base_salary / 160  # 160 giờ/tháng
        overtime_salary = overtime_hours * hourly_rate * 1.5
        
        # Tính lương bruto
        gross_salary = base_salary + overtime_salary + bonus - deduction
        
        # Tính lương ròng (giả sử 10% thuế)
        net_salary = gross_salary * 0.9
        
        Database.execute(
            """INSERT INTO salaries 
               (salary_id, employee_id, month, year, base_salary, overtime_hours,
                overtime_salary, bonus, deduction, gross_salary, net_salary,
                status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (salary_id, employee_id, month, year, base_salary, overtime_hours,
             overtime_salary, bonus, deduction, gross_salary, net_salary,
             "Nháp", now, now),
            commit=True,
        )
        return cls(salary_id, employee_id, month, year, base_salary, overtime_hours,
                   overtime_salary, bonus, deduction, gross_salary, net_salary, "Nháp", "", now, now)

    @classmethod
    def get_all(cls):
        """Lấy tất cả bảng lương"""
        rows = Database.execute(
            """SELECT salary_id, employee_id, month, year, base_salary, overtime_hours,
                      overtime_salary, bonus, deduction, gross_salary, net_salary,
                      status, note, created_at, updated_at FROM salaries
               ORDER BY year DESC, month DESC""",
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    @classmethod
    def get_by_id(cls, salary_id):
        """Lấy bảng lương theo ID"""
        row = Database.execute(
            """SELECT salary_id, employee_id, month, year, base_salary, overtime_hours,
                      overtime_salary, bonus, deduction, gross_salary, net_salary,
                      status, note, created_at, updated_at FROM salaries WHERE salary_id = ?""",
            (salary_id,),
            fetch_one=True,
        )
        return cls(*row) if row else None

    @classmethod
    def get_by_employee(cls, employee_id):
        """Lấy bảng lương của nhân viên"""
        rows = Database.execute(
            """SELECT salary_id, employee_id, month, year, base_salary, overtime_hours,
                      overtime_salary, bonus, deduction, gross_salary, net_salary,
                      status, note, created_at, updated_at FROM salaries
               WHERE employee_id = ? ORDER BY year DESC, month DESC""",
            (employee_id,),
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    @classmethod
    def get_by_month(cls, month, year):
        """Lấy bảng lương theo tháng/năm"""
        rows = Database.execute(
            """SELECT salary_id, employee_id, month, year, base_salary, overtime_hours,
                      overtime_salary, bonus, deduction, gross_salary, net_salary,
                      status, note, created_at, updated_at FROM salaries
               WHERE month = ? AND year = ? ORDER BY employee_id""",
            (month, year),
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    def update(self):
        """Cập nhật bảng lương"""
        self.updated_at = datetime.now().isoformat()
        Database.execute(
            """UPDATE salaries SET
                   employee_id = ?, month = ?, year = ?, base_salary = ?,
                   overtime_hours = ?, overtime_salary = ?, bonus = ?, deduction = ?,
                   gross_salary = ?, net_salary = ?, status = ?, note = ?,
                   updated_at = ?
               WHERE salary_id = ?""",
            (self.employee_id, self.month, self.year, self.base_salary,
             self.overtime_hours, self.overtime_salary, self.bonus, self.deduction,
             self.gross_salary, self.net_salary, self.status, self.note,
             self.updated_at, self.salary_id),
            commit=True,
        )

    def delete(self):
        """Xóa bảng lương"""
        Database.execute(
            "DELETE FROM salaries WHERE salary_id = ?",
            (self.salary_id,),
            commit=True,
        )

    def approve(self):
        """Phê duyệt bảng lương"""
        if self.status == "Nháp":
            self.status = "Phê duyệt"
            self.update()
            return True
        return False

    def pay(self):
        """Thanh toán bảng lương"""
        if self.status == "Phê duyệt":
            self.status = "Đã thanh toán"
            self.update()
            return True
        return False

    def calculate_gross_salary(self):
        """Tính lương bruto"""
        return self.base_salary + self.overtime_salary + self.bonus - self.deduction

    def calculate_net_salary(self):
        """Tính lương ròng (9% bảo hiểm + 1% thuế)"""
        insurance = self.base_salary * 0.09
        return self.calculate_gross_salary() - insurance
