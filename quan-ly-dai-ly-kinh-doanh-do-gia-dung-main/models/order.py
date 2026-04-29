from dataclasses import dataclass
from datetime import datetime
from .database import Database


@dataclass
class Order:
    order_number: str
    created_at: str
    customer_name: str
    customer_phone: str
    total_amount: float
    paid_amount: float
    status: str = "Đã thanh toán"
    employee_id: str = ""
    order_date: str = ""
    items: list = None  # List of order items

    @classmethod
    def create_table(cls, cursor):
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'")
        if cursor.fetchone() is None:
            cursor.execute(
                """
                CREATE TABLE orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_number TEXT UNIQUE NOT NULL,
                    customer_name TEXT,
                    customer_phone TEXT,
                    employee_id TEXT,
                    order_date TEXT,
                    total_amount REAL NOT NULL DEFAULT 0,
                    paid_amount REAL NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'Đã thanh toán',
                    created_at TEXT NOT NULL
                )
                """
            )
        else:
            existing_columns = [row[1] for row in cursor.execute("PRAGMA table_info(orders)").fetchall()]
            if "order_number" not in existing_columns:
                cursor.execute("ALTER TABLE orders ADD COLUMN order_number TEXT")
            if "customer_phone" not in existing_columns:
                cursor.execute("ALTER TABLE orders ADD COLUMN customer_phone TEXT")
            if "employee_id" not in existing_columns:
                cursor.execute("ALTER TABLE orders ADD COLUMN employee_id TEXT")
            if "order_date" not in existing_columns:
                cursor.execute("ALTER TABLE orders ADD COLUMN order_date TEXT")
            if "paid_amount" not in existing_columns:
                cursor.execute("ALTER TABLE orders ADD COLUMN paid_amount REAL NOT NULL DEFAULT 0")
            if "status" not in existing_columns:
                cursor.execute("ALTER TABLE orders ADD COLUMN status TEXT DEFAULT 'Đã thanh toán'")
            if "created_at" not in existing_columns:
                cursor.execute("ALTER TABLE orders ADD COLUMN created_at TEXT")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='order_items'")
        if cursor.fetchone() is None:
            cursor.execute(
                """
                CREATE TABLE order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT NOT NULL,
                    product_id TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    total_price REAL NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders (order_number)
                )
                """
            )

    @classmethod
    def generate_order_id(cls):
        """Tạo mã đơn hàng tự động dạng HD001, HD002, ..."""
        rows = Database.execute(
            "SELECT order_number FROM orders WHERE order_number LIKE 'HD%'",
            fetch_all=True,
        )
        max_num = 0
        for row in rows:
            order_number = row[0]
            if order_number and order_number.startswith('HD'):
                try:
                    num = int(order_number[2:])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        new_num = max_num + 1
        return f"HD{new_num:03d}"

    @classmethod
    def create(cls, customer_name, customer_phone, employee_id, items, total_amount):
        order_number = cls.generate_order_id()
        order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        created_at = order_date

        Database.execute(
            "INSERT INTO orders (order_number, customer_name, customer_phone, employee_id, order_date, total_amount, paid_amount, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (order_number, customer_name, customer_phone, employee_id, order_date, total_amount, total_amount, "Đã thanh toán", created_at),
            commit=True,
        )

        for item in items:
            Database.execute(
                "INSERT INTO order_items (order_id, product_id, product_name, quantity, unit_price, total_price) VALUES (?, ?, ?, ?, ?, ?)",
                (order_number, item["product_id"], item["product_name"], item["quantity"], item["unit_price"], item["total_price"]),
                commit=True,
            )

        return cls(order_number, created_at, customer_name, customer_phone, total_amount, total_amount, "Đã thanh toán", employee_id, order_date, items)

    @classmethod
    def get_all(cls):
        rows = Database.execute(
            "SELECT order_number, created_at, customer_name, customer_phone, total_amount, paid_amount, status, order_date, employee_id FROM orders ORDER BY created_at DESC",
            fetch_all=True,
        )
        orders = []
        for row in rows:
            order = cls(*row)
            items = Database.execute(
                "SELECT product_id, product_name, quantity, unit_price, total_price FROM order_items WHERE order_id = ?",
                (order.order_number,),
                fetch_all=True,
            )
            order.items = [{"product_id": item[0], "product_name": item[1], "quantity": item[2], "unit_price": item[3], "total_price": item[4]} for item in items]
            orders.append(order)
        return orders

    @classmethod
    def get_by_id(cls, order_number):
        row = Database.execute(
            "SELECT order_number, created_at, customer_name, customer_phone, total_amount, paid_amount, status, order_date, employee_id FROM orders WHERE order_number = ?",
            (order_number,),
            fetch_one=True,
        )
        if not row:
            return None

        order = cls(*row)
        items = Database.execute(
            "SELECT product_id, product_name, quantity, unit_price, total_price FROM order_items WHERE order_id = ?",
            (order.order_number,),
            fetch_all=True,
        )
        order.items = [{"product_id": item[0], "product_name": item[1], "quantity": item[2], "unit_price": item[3], "total_price": item[4]} for item in items]
        return order

    def update_status(self, status):
        Database.execute(
            "UPDATE orders SET status = ? WHERE order_number = ?",
            (status, self.order_number),
            commit=True,
        )
        self.status = status

    @classmethod
    def search_by_filters(cls, order_number="", customer_name="", status="", date_from="", date_to=""):
        """Tìm kiếm hóa đơn theo các tiêu chí"""
        query = "SELECT order_number, created_at, customer_name, customer_phone, total_amount, paid_amount, status, order_date, employee_id FROM orders WHERE 1=1"
        params = []
        
        if order_number:
            query += " AND order_number LIKE ?"
            params.append(f"%{order_number}%")
        
        if customer_name:
            query += " AND (customer_name LIKE ? OR customer_phone LIKE ?)"
            params.append(f"%{customer_name}%")
            params.append(f"%{customer_name}%")
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if date_from:
            query += " AND DATE(created_at) >= DATE(?)"
            params.append(date_from)
        
        if date_to:
            query += " AND DATE(created_at) <= DATE(?)"
            params.append(date_to)
        
        query += " ORDER BY created_at DESC"
        
        rows = Database.execute(query, params, fetch_all=True)
        orders = []
        for row in rows:
            order = cls(*row)
            items = Database.execute(
                "SELECT product_id, product_name, quantity, unit_price, total_price FROM order_items WHERE order_id = ?",
                (order.order_number,),
                fetch_all=True,
            )
            order.items = [{"product_id": item[0], "product_name": item[1], "quantity": item[2], "unit_price": item[3], "total_price": item[4]} for item in items]
            orders.append(order)
        return orders