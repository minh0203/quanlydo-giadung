from dataclasses import dataclass
from datetime import datetime
from .database import Database


@dataclass
class Employee:
    """Model cho nhân viên"""
    employee_id: str
    full_name: str
    gender: str = "Nam"
    birth_date: str = ""
    phone: str = ""
    email: str = ""
    identity_card: str = ""
    address: str = ""
    hire_date: str = ""
    role: str = "Sale"  # Admin, Sale, Warehouse, Accountant, Manager
    base_salary: float = 0.0
    commission_rate: float = 0.0
    username: str = ""
    password: str = ""
    status: str = "Đang làm"  # Đang làm, Tạm nghỉ, Đã nghỉ
    note: str = ""
    avatar: str = ""
    created_at: str = ""
    updated_at: str = ""

    VALID_ROLES = ["Admin", "Sale", "Warehouse", "Accountant", "Manager"]
    VALID_STATUSES = ["Đang làm", "Tạm nghỉ", "Đã nghỉ"]
    VALID_GENDERS = ["Nam", "Nữ", "Khác"]

    @classmethod
    def create_table(cls, cursor):
        """Tạo bảng nhân viên"""
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS employees (
                employee_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                gender TEXT DEFAULT 'Nam',
                birth_date TEXT,
                phone TEXT,
                email TEXT,
                identity_card TEXT UNIQUE,
                address TEXT,
                hire_date TEXT,
                role TEXT DEFAULT 'Sale',
                base_salary REAL DEFAULT 0.0,
                commission_rate REAL DEFAULT 0.0,
                username TEXT UNIQUE,
                password TEXT,
                status TEXT DEFAULT 'Đang làm',
                note TEXT,
                avatar TEXT,
                created_at TEXT,
                updated_at TEXT
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
               status="Đang làm", note="", avatar=""):
        """Tạo nhân viên mới"""
        employee_id = cls.generate_employee_id()
        now = datetime.now().isoformat()
        
        Database.execute(
            """INSERT INTO employees 
               (employee_id, full_name, gender, birth_date, phone, email,
                identity_card, address, hire_date, role, base_salary,
                commission_rate, username, password, status, note, avatar,
                created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (employee_id, full_name, gender, birth_date, phone, email,
             identity_card, address, hire_date, role, base_salary,
             commission_rate, username, password, status, note, avatar,
             now, now),
            commit=True,
        )
        return cls(employee_id, full_name, gender, birth_date, phone, email,
                   identity_card, address, hire_date, role, base_salary,
                   commission_rate, username, password, status, note, avatar, now, now)

    @classmethod
    def get_all(cls):
        """Lấy tất cả nhân viên"""
        rows = Database.execute(
            """SELECT employee_id, full_name, gender, birth_date, phone, email,
                      identity_card, address, hire_date, role, base_salary,
                      commission_rate, username, password, status, note, avatar,
                      created_at, updated_at FROM employees ORDER BY full_name""",
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    @classmethod
    def get_by_id(cls, employee_id):
        """Lấy nhân viên theo ID"""
        row = Database.execute(
            """SELECT employee_id, full_name, gender, birth_date, phone, email,
                      identity_card, address, hire_date, role, base_salary,
                      commission_rate, username, password, status, note, avatar,
                      created_at, updated_at FROM employees WHERE employee_id = ?""",
            (employee_id,),
            fetch_one=True,
        )
        return cls(*row) if row else None

    @classmethod
    def search(cls, keyword):
        """Tìm kiếm nhân viên"""
        keyword = f"%{keyword.lower()}%"
        rows = Database.execute(
            """SELECT employee_id, full_name, gender, birth_date, phone, email,
                      identity_card, address, hire_date, role, base_salary,
                      commission_rate, username, password, status, note, avatar,
                      created_at, updated_at FROM employees
               WHERE LOWER(full_name) LIKE ? OR LOWER(email) LIKE ? 
                     OR LOWER(phone) LIKE ? OR employee_id LIKE ?
               ORDER BY full_name""",
            (keyword, keyword, keyword, keyword),
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    @classmethod
    def filter_by_role(cls, role):
        """Lọc nhân viên theo chức vụ"""
        rows = Database.execute(
            """SELECT employee_id, full_name, gender, birth_date, phone, email,
                      identity_card, address, hire_date, role, base_salary,
                      commission_rate, username, password, status, note, avatar,
                      created_at, updated_at FROM employees WHERE role = ?
               ORDER BY full_name""",
            (role,),
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    @classmethod
    def filter_by_status(cls, status):
        """Lọc nhân viên theo tình trạng"""
        rows = Database.execute(
            """SELECT employee_id, full_name, gender, birth_date, phone, email,
                      identity_card, address, hire_date, role, base_salary,
                      commission_rate, username, password, status, note, avatar,
                      created_at, updated_at FROM employees WHERE status = ?
               ORDER BY full_name""",
            (status,),
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    @classmethod
    def check_duplicate_email(cls, email, exclude_id=None):
        """Kiểm tra email đã tồn tại"""
        if not email:
            return False
        query = "SELECT COUNT(*) FROM employees WHERE email = ?"
        params = [email]
        if exclude_id:
            query += " AND employee_id != ?"
            params.append(exclude_id)
        result = Database.execute(query, params, fetch_one=True)
        return result[0] > 0 if result else False

    @classmethod
    def check_duplicate_identity_card(cls, identity_card, exclude_id=None):
        """Kiểm tra CCCD đã tồn tại"""
        if not identity_card:
            return False
        query = "SELECT COUNT(*) FROM employees WHERE identity_card = ?"
        params = [identity_card]
        if exclude_id:
            query += " AND employee_id != ?"
            params.append(exclude_id)
        result = Database.execute(query, params, fetch_one=True)
        return result[0] > 0 if result else False

    @classmethod
    def check_duplicate_username(cls, username, exclude_id=None):
        """Kiểm tra username đã tồn tại"""
        if not username:
            return False
        query = "SELECT COUNT(*) FROM employees WHERE username = ?"
        params = [username]
        if exclude_id:
            query += " AND employee_id != ?"
            params.append(exclude_id)
        result = Database.execute(query, params, fetch_one=True)
        return result[0] > 0 if result else False

    def update(self):
        """Cập nhật nhân viên"""
        self.updated_at = datetime.now().isoformat()
        Database.execute(
            """UPDATE employees SET
                   full_name = ?, gender = ?, birth_date = ?, phone = ?, email = ?,
                   identity_card = ?, address = ?, hire_date = ?, role = ?,
                   base_salary = ?, commission_rate = ?, username = ?, password = ?,
                   status = ?, note = ?, avatar = ?, updated_at = ?
               WHERE employee_id = ?""",
            (self.full_name, self.gender, self.birth_date, self.phone, self.email,
             self.identity_card, self.address, self.hire_date, self.role,
             self.base_salary, self.commission_rate, self.username, self.password,
             self.status, self.note, self.avatar, self.updated_at, self.employee_id),
            commit=True,
        )

    def delete(self):
        """Xóa nhân viên"""
        Database.execute(
            "DELETE FROM employees WHERE employee_id = ?",
            (self.employee_id,),
            commit=True,
        )

    def get_age(self):
        """Tính tuổi nhân viên"""
        if not self.birth_date:
            return None
        try:
            birth = datetime.fromisoformat(self.birth_date)
            today = datetime.now()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            return age
        except:
            return None

    def get_working_days(self):
        """Tính số ngày làm việc"""
        if not self.hire_date:
            return 0
        try:
            hire = datetime.fromisoformat(self.hire_date)
            today = datetime.now()
            delta = today - hire
            return delta.days
        except:
            return 0
