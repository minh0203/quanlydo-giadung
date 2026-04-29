from dataclasses import dataclass
from datetime import datetime
from .database import Database


@dataclass
class Customer:
    customer_id: str
    name: str
    phone: str = ""
    email: str = ""
    address: str = ""
    points: int = 0
    notes: str = ""
    created_date: str = ""

    @classmethod
    def create_table(cls, cursor):
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                points INTEGER DEFAULT 0,
                notes TEXT,
                created_date TEXT
            )
            """
        )

    @classmethod
    def generate_customer_id(cls):
        """Tạo mã khách hàng tự động dạng KH001, KH002, ..."""
        rows = Database.execute(
            "SELECT customer_id FROM customers WHERE customer_id LIKE 'KH%'",
            fetch_all=True,
        )
        max_num = 0
        for row in rows:
            customer_id = row[0]
            if customer_id.startswith('KH'):
                try:
                    num = int(customer_id[2:])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        new_num = max_num + 1
        return f"KH{new_num:03d}"

    @classmethod
    def create(cls, name, phone="", email="", address="", points=0, notes=""):
        customer_id = cls.generate_customer_id()
        created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        Database.execute(
            "INSERT INTO customers (customer_id, name, phone, email, address, points, notes, created_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (customer_id, name, phone, email, address, points, notes, created_date),
            commit=True,
        )
        return cls(customer_id, name, phone, email, address, points, notes, created_date)

    @classmethod
    def get_all(cls):
        rows = Database.execute(
            "SELECT customer_id, name, phone, email, address, points, notes, created_date FROM customers ORDER BY name",
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    @classmethod
    def get_by_id(cls, customer_id):
        row = Database.execute(
            "SELECT customer_id, name, phone, email, address, points, notes, created_date FROM customers WHERE customer_id = ?",
            (customer_id,),
            fetch_one=True,
        )
        return cls(*row) if row else None

    @classmethod
    def get_by_name(cls, name):
        """Tìm khách hàng theo tên (trả về khách hàng đầu tiên tìm được)"""
        row = Database.execute(
            "SELECT customer_id, name, phone, email, address, points, notes, created_date FROM customers WHERE LOWER(name) = LOWER(?)",
            (name,),
            fetch_one=True,
        )
        return cls(*row) if row else None

    @classmethod
    def get_all_by_name(cls, name):
        """Tìm tất cả khách hàng có tên giống nhau"""
        rows = Database.execute(
            "SELECT customer_id, name, phone, email, address, points, notes, created_date FROM customers WHERE LOWER(name) = LOWER(?) ORDER BY phone",
            (name,),
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    @classmethod
    def search(cls, keyword):
        keyword = f"%{keyword.lower()}%"
        rows = Database.execute(
            "SELECT customer_id, name, phone, email, address, points, notes, created_date FROM customers WHERE LOWER(name) LIKE ? OR LOWER(phone) LIKE ? OR LOWER(email) LIKE ? OR customer_id LIKE ? ORDER BY name",
            (keyword, keyword, keyword, keyword),
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    def update(self):
        Database.execute(
            "UPDATE customers SET name = ?, phone = ?, email = ?, address = ?, points = ?, notes = ? WHERE customer_id = ?",
            (self.name, self.phone, self.email, self.address, self.points, self.notes, self.customer_id),
            commit=True,
        )

    def delete(self):
        Database.execute(
            "DELETE FROM customers WHERE customer_id = ?",
            (self.customer_id,),
            commit=True,
        )
