from dataclasses import dataclass
from datetime import datetime
from .database import Database


@dataclass
class Warranty:
    warranty_code: str
    created_at: str
    product: str
    serial: str
    customer_name: str
    phone: str
    purchase_date: str
    expiry_date: str
    error_description: str
    note: str
    status: str = "Đang bảo hành"
    order_id: str = ""  # Liên kết với mã hóa đơn

    @classmethod
    def create_table(cls, cursor):
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='warranties'")
        if cursor.fetchone() is None:
            cursor.execute(
                """
                CREATE TABLE warranties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    warranty_code TEXT UNIQUE NOT NULL,
                    created_at TEXT NOT NULL,
                    product TEXT,
                    serial TEXT,
                    customer_name TEXT,
                    phone TEXT,
                    purchase_date TEXT,
                    expiry_date TEXT,
                    error_description TEXT,
                    note TEXT,
                    status TEXT NOT NULL DEFAULT 'Đang bảo hành',
                    order_id TEXT
                )
                """
            )
        else:
            existing_columns = [row[1] for row in cursor.execute("PRAGMA table_info(warranties)").fetchall()]
            if "created_at" not in existing_columns:
                cursor.execute("ALTER TABLE warranties ADD COLUMN created_at TEXT")
            if "product" not in existing_columns:
                cursor.execute("ALTER TABLE warranties ADD COLUMN product TEXT")
            if "serial" not in existing_columns:
                cursor.execute("ALTER TABLE warranties ADD COLUMN serial TEXT")
            if "customer_name" not in existing_columns:
                cursor.execute("ALTER TABLE warranties ADD COLUMN customer_name TEXT")
            if "phone" not in existing_columns:
                cursor.execute("ALTER TABLE warranties ADD COLUMN phone TEXT")
            if "purchase_date" not in existing_columns:
                cursor.execute("ALTER TABLE warranties ADD COLUMN purchase_date TEXT")
            if "expiry_date" not in existing_columns:
                cursor.execute("ALTER TABLE warranties ADD COLUMN expiry_date TEXT")
            if "error_description" not in existing_columns:
                cursor.execute("ALTER TABLE warranties ADD COLUMN error_description TEXT")
            if "note" not in existing_columns:
                cursor.execute("ALTER TABLE warranties ADD COLUMN note TEXT")
            if "status" not in existing_columns:
                cursor.execute("ALTER TABLE warranties ADD COLUMN status TEXT NOT NULL DEFAULT 'Đang bảo hành'")
            if "order_id" not in existing_columns:
                cursor.execute("ALTER TABLE warranties ADD COLUMN order_id TEXT")

    @classmethod
    def generate_warranty_code(cls):
        rows = Database.execute(
            "SELECT warranty_code FROM warranties WHERE warranty_code LIKE 'BH%'",
            fetch_all=True,
        )
        max_num = 0
        for row in rows:
            code = row[0]
            if code and code.startswith("BH"):
                try:
                    num = int(code[2:])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        return f"BH{max_num + 1:03d}"

    @classmethod
    def create(cls, product, serial, customer_name, phone, purchase_date, expiry_date, error_description, note, status="Đang bảo hành", order_id=""):
        warranty_code = cls.generate_warranty_code()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        Database.execute(
            "INSERT INTO warranties (warranty_code, created_at, product, serial, customer_name, phone, purchase_date, expiry_date, error_description, note, status, order_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (warranty_code, created_at, product, serial, customer_name, phone, purchase_date, expiry_date, error_description, note, status, order_id),
            commit=True,
        )
        return cls(warranty_code, created_at, product, serial, customer_name, phone, purchase_date, expiry_date, error_description, note, status, order_id)

    @classmethod
    def get_all(cls):
        rows = Database.execute(
            "SELECT warranty_code, created_at, product, serial, customer_name, phone, purchase_date, expiry_date, error_description, note, status, order_id FROM warranties ORDER BY created_at DESC",
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    @classmethod
    def get_by_order_id(cls, order_id):
        rows = Database.execute(
            "SELECT warranty_code, created_at, product, serial, customer_name, phone, purchase_date, expiry_date, error_description, note, status, order_id FROM warranties WHERE order_id = ? ORDER BY created_at DESC",
            (order_id,),
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    @classmethod
    def get_by_code(cls, warranty_code):
        row = Database.execute(
            "SELECT warranty_code, created_at, product, serial, customer_name, phone, purchase_date, expiry_date, error_description, note, status, order_id FROM warranties WHERE warranty_code = ?",
            (warranty_code,),
            fetch_one=True,
        )
        if not row:
            return None
        return cls(*row)

    def update(self):
        Database.execute(
            "UPDATE warranties SET product = ?, serial = ?, customer_name = ?, phone = ?, purchase_date = ?, expiry_date = ?, error_description = ?, note = ?, status = ?, order_id = ? WHERE warranty_code = ?",
            (self.product, self.serial, self.customer_name, self.phone, self.purchase_date, self.expiry_date, self.error_description, self.note, self.status, self.order_id, self.warranty_code),
            commit=True,
        )

    def update_status(self, status):
        Database.execute(
            "UPDATE warranties SET status = ? WHERE warranty_code = ?",
            (status, self.warranty_code),
            commit=True,
        )
        self.status = status

    @classmethod
    def search_by_filters(cls, warranty_code="", customer="", status="", date_from="", date_to=""):
        query = "SELECT warranty_code, created_at, product, serial, customer_name, phone, purchase_date, expiry_date, error_description, note, status, order_id FROM warranties WHERE 1=1"
        params = []

        if warranty_code:
            query += " AND warranty_code LIKE ?"
            params.append(f"%{warranty_code}%")

        if customer:
            query += " AND (customer_name LIKE ? OR phone LIKE ?)"
            params.append(f"%{customer}%")
            params.append(f"%{customer}%")

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
        return [cls(*row) for row in rows]
