from dataclasses import dataclass
from datetime import datetime
from .database import Database


@dataclass
class SaleOrder:
    """Model cho đơn bán hàng"""
    order_id: str
    customer_id: str
    order_date: str
    total_amount: float = 0.0
    vat_amount: float = 0.0
    grand_total: float = 0.0
    notes: str = ""
    status: str = "pending"  # pending, completed, cancelled

    @classmethod
    def create_table(cls, cursor):
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sale_orders (
                order_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                order_date TEXT NOT NULL,
                total_amount REAL DEFAULT 0.0,
                vat_amount REAL DEFAULT 0.0,
                grand_total REAL DEFAULT 0.0,
                notes TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
            """
        )
        # Tạo bảng chi tiết đơn hàng
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sale_order_details (
                detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                quantity INTEGER DEFAULT 0,
                unit_price REAL DEFAULT 0.0,
                total_price REAL DEFAULT 0.0,
                FOREIGN KEY (order_id) REFERENCES sale_orders(order_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
            """
        )

    @classmethod
    def generate_order_id(cls):
        """Tạo mã đơn hàng tự động dạng DH001, DH002, ..."""
        rows = Database.execute(
            "SELECT order_id FROM sale_orders WHERE order_id LIKE 'DH%'",
            fetch_all=True,
        )
        max_num = 0
        for row in rows:
            order_id = row[0]
            if order_id.startswith('DH'):
                try:
                    num = int(order_id[2:])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        new_num = max_num + 1
        return f"DH{new_num:05d}"

    @classmethod
    def create(cls, customer_id, order_date, total_amount, vat_amount, grand_total, notes=""):
        """Tạo đơn hàng mới"""
        order_id = cls.generate_order_id()
        order_date = order_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        Database.execute(
            "INSERT INTO sale_orders (order_id, customer_id, order_date, total_amount, vat_amount, grand_total, notes, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (order_id, customer_id, order_date, total_amount, vat_amount, grand_total, notes, "completed"),
            commit=True,
        )
        return cls(order_id, customer_id, order_date, total_amount, vat_amount, grand_total, notes, "completed")

    @classmethod
    def add_detail(cls, order_id, product_id, quantity, unit_price):
        """Thêm chi tiết sản phẩm vào đơn hàng"""
        total_price = quantity * unit_price
        Database.execute(
            "INSERT INTO sale_order_details (order_id, product_id, quantity, unit_price, total_price) VALUES (?, ?, ?, ?, ?)",
            (order_id, product_id, quantity, unit_price, total_price),
            commit=True,
        )

    @classmethod
    def get_all(cls):
        rows = Database.execute(
            "SELECT order_id, customer_id, order_date, total_amount, vat_amount, grand_total, notes, status FROM sale_orders ORDER BY order_date DESC",
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    @classmethod
    def get_by_id(cls, order_id):
        row = Database.execute(
            "SELECT order_id, customer_id, order_date, total_amount, vat_amount, grand_total, notes, status FROM sale_orders WHERE order_id = ?",
            (order_id,),
            fetch_one=True,
        )
        return cls(*row) if row else None

    @classmethod
    def get_details(cls, order_id):
        """Lấy chi tiết các sản phẩm trong đơn hàng"""
        rows = Database.execute(
            "SELECT detail_id, order_id, product_id, quantity, unit_price, total_price FROM sale_order_details WHERE order_id = ?",
            (order_id,),
            fetch_all=True,
        )
        return rows

    def update(self):
        Database.execute(
            "UPDATE sale_orders SET total_amount = ?, vat_amount = ?, grand_total = ?, notes = ?, status = ? WHERE order_id = ?",
            (self.total_amount, self.vat_amount, self.grand_total, self.notes, self.status, self.order_id),
            commit=True,
        )

    def delete(self):
        # Xóa chi tiết đơn hàng trước
        Database.execute(
            "DELETE FROM sale_order_details WHERE order_id = ?",
            (self.order_id,),
            commit=True,
        )
        # Xóa đơn hàng
        Database.execute(
            "DELETE FROM sale_orders WHERE order_id = ?",
            (self.order_id,),
            commit=True,
        )
