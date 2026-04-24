from dataclasses import dataclass
from datetime import datetime
from .database import Database


@dataclass
class Employee:
    employee_id: str
    full_name: str
    gender: str = "Nam"  # Nam, Nữ, Khác
    birth_date: str = ""
    phone: str = ""
    email: str = ""
    identity_card: str = ""
    address: str = ""
    hire_date: str = ""
    role: str = "Sale"  # Admin, Sale, Warehouse, Accountant
    base_salary: float = 0.0
    commission_rate: float = 0.0  # Phần trăm
    username: str = ""
    password: str = ""
    status: str = "Đang làm"  # Đang làm, Tạm nghỉ, Đã nghỉ
    note: str = ""
    created_date: str = ""

    @classmethod
    def create_table(cls, cursor):
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS employees (
                employee_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                gender TEXT DEFAULT 'Nam',
                birth_date TEXT,
                phone TEXT,
                email TEXT,
                identity_card TEXT,
                address TEXT,
                hire_date TEXT,
                role TEXT DEFAULT 'Sale',
                base_salary REAL DEFAULT 0.0,
                commission_rate REAL DEFAULT 0.0,
                username TEXT,
                password TEXT,
                status TEXT DEFAULT 'Đang làm',
                note TEXT,
                created_date TEXT
            )
            """
        )

    @classmethod
    def generate_employee_id(cls):
        """Tạo mã nhân viên tự động dạng NV001, NV002, ..."""
        rows = Database.execute(
            "SELECT employee_id FROM employees WHERE employee_id LIKE 'NV%'",
            fetch_all=True,
        )
        max_num = 0
        for row in rows:
            employee_id = row[0]
            if employee_id.startswith('NV'):
                try:
                    num = int(employee_id[2:])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        new_num = max_num + 1
        return f"NV{new_num:03d}"

    @classmethod
    def create(cls, full_name, gender="Nam", birth_date="", phone="", email="", 
               identity_card="", address="", hire_date="", role="Sale", 
               base_salary=0.0, commission_rate=0.0, username="", password="", 
               status="Đang làm", note=""):
        employee_id = cls.generate_employee_id()
        created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        Database.execute(
            """INSERT INTO employees 
               (employee_id, full_name, gender, birth_date, phone, email, identity_card, address, 
                hire_date, role, base_salary, commission_rate, username, password, status, note, created_date) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (employee_id, full_name, gender, birth_date, phone, email, identity_card, address, 
             hire_date, role, base_salary, commission_rate, username, password, status, note, created_date),
            commit=True,
        )
        return cls(employee_id, full_name, gender, birth_date, phone, email, identity_card, address,
                   hire_date, role, base_salary, commission_rate, username, password, status, note, created_date)

    @classmethod
    def get_all(cls):
        rows = Database.execute(
            """SELECT employee_id, full_name, gender, birth_date, phone, email, identity_card, address, 
                      hire_date, role, base_salary, commission_rate, username, password, status, note, created_date 
               FROM employees ORDER BY full_name""",
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    @classmethod
    def get_by_id(cls, employee_id):
        row = Database.execute(
            """SELECT employee_id, full_name, gender, birth_date, phone, email, identity_card, address, 
                      hire_date, role, base_salary, commission_rate, username, password, status, note, created_date 
               FROM employees WHERE employee_id = ?""",
            (employee_id,),
            fetch_one=True,
        )
        return cls(*row) if row else None

    @classmethod
    def search(cls, keyword):
        keyword = f"%{keyword.lower()}%"
        rows = Database.execute(
            """SELECT employee_id, full_name, gender, birth_date, phone, email, identity_card, address, 
                      hire_date, role, base_salary, commission_rate, username, password, status, note, created_date 
               FROM employees 
               WHERE LOWER(full_name) LIKE ? OR LOWER(phone) LIKE ? OR LOWER(email) LIKE ? 
                  OR employee_id LIKE ? OR LOWER(username) LIKE ?
               ORDER BY full_name""",
            (keyword, keyword, keyword, keyword, keyword),
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    @classmethod
    def filter_by_role(cls, role):
        """Lọc nhân viên theo vai trò"""
        if role == "Tất cả":
            return cls.get_all()
        rows = Database.execute(
            """SELECT employee_id, full_name, gender, birth_date, phone, email, identity_card, address, 
                      hire_date, role, base_salary, commission_rate, username, password, status, note, created_date 
               FROM employees WHERE role = ? ORDER BY full_name""",
            (role,),
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    @classmethod
    def filter_by_status(cls, status):
        """Lọc nhân viên theo trạng thái"""
        if status == "Tất cả":
            return cls.get_all()
        rows = Database.execute(
            """SELECT employee_id, full_name, gender, birth_date, phone, email, identity_card, address, 
                      hire_date, role, base_salary, commission_rate, username, password, status, note, created_date 
               FROM employees WHERE status = ? ORDER BY full_name""",
            (status,),
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    def update(self):
        Database.execute(
            """UPDATE employees 
               SET full_name = ?, gender = ?, birth_date = ?, phone = ?, email = ?, 
                   identity_card = ?, address = ?, hire_date = ?, role = ?, base_salary = ?, 
                   commission_rate = ?, username = ?, password = ?, status = ?, note = ?
               WHERE employee_id = ?""",
            (self.full_name, self.gender, self.birth_date, self.phone, self.email, 
             self.identity_card, self.address, self.hire_date, self.role, self.base_salary,
             self.commission_rate, self.username, self.password, self.status, self.note, self.employee_id),
            commit=True,
        )

    def delete(self):
        Database.execute(
            "DELETE FROM employees WHERE employee_id = ?",
            (self.employee_id,),
            commit=True,
        )
