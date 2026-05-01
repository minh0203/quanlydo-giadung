from dataclasses import dataclass
from datetime import datetime
from .database import Database


@dataclass
class ImportOrder:
    import_number: str
    supplier_id: str
    supplier_name: str
    import_date: str
    payment_status: str
    total_amount: float
    note: str = ""
    created_at: str = ""
    items: list = None

    @classmethod
    def create_table(cls, cursor):
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='import_orders'")
        if cursor.fetchone() is None:
            cursor.execute(
                """
                CREATE TABLE import_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    import_number TEXT UNIQUE NOT NULL,
                    supplier_id TEXT,
                    supplier_name TEXT,
                    import_date TEXT,
                    payment_status TEXT,
                    total_amount REAL NOT NULL DEFAULT 0,
                    note TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='import_items'")
        if cursor.fetchone() is None:
            cursor.execute(
                """
                CREATE TABLE import_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    import_number TEXT NOT NULL,
                    product_id TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    total_price REAL NOT NULL,
                    FOREIGN KEY (import_number) REFERENCES import_orders (import_number)
                )
                """
            )

    @classmethod
    def generate_import_number(cls):
        rows = Database.execute(
            "SELECT import_number FROM import_orders WHERE import_number LIKE 'PN%'",
            fetch_all=True,
        )
        max_num = 0
        for row in rows:
            num_text = row[0]
            if num_text and num_text.startswith('PN'):
                try:
                    num = int(num_text[2:])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        return f"PN{max_num + 1:03d}"

    @classmethod
    def create(cls, supplier_id, supplier_name, import_date, payment_status, total_amount, note, items):
        import_number = cls.generate_import_number()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        Database.execute(
            "INSERT INTO import_orders (import_number, supplier_id, supplier_name, import_date, payment_status, total_amount, note, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (import_number, supplier_id, supplier_name, import_date, payment_status, total_amount, note, created_at),
            commit=True,
        )

        for item in items:
            Database.execute(
                "INSERT INTO import_items (import_number, product_id, product_name, quantity, unit_price, total_price) VALUES (?, ?, ?, ?, ?, ?)",
                (import_number, item["product_id"], item["product_name"], item["quantity"], item["unit_price"], item["total_price"]),
                commit=True,
            )

        return cls(import_number, supplier_id, supplier_name, import_date, payment_status, total_amount, note, created_at, items)

    @classmethod
    def get_all(cls):
        rows = Database.execute(
            "SELECT import_number, supplier_id, supplier_name, import_date, payment_status, total_amount, note, created_at FROM import_orders ORDER BY created_at DESC",
            fetch_all=True,
        )
        orders = []
        for row in rows:
            import_order = cls(*row, items=[])
            items = Database.execute(
                "SELECT product_id, product_name, quantity, unit_price, total_price FROM import_items WHERE import_number = ?",
                (import_order.import_number,),
                fetch_all=True,
            )
            import_order.items = [
                {"product_id": item[0], "product_name": item[1], "quantity": item[2], "unit_price": item[3], "total_price": item[4]}
                for item in items
            ]
            orders.append(import_order)
        return orders

    @classmethod
    def get_by_id(cls, import_number):
        row = Database.execute(
            "SELECT import_number, supplier_id, supplier_name, import_date, payment_status, total_amount, note, created_at FROM import_orders WHERE import_number = ?",
            (import_number,),
            fetch_one=True,
        )
        if not row:
            return None
        import_order = cls(*row, items=[])
        items = Database.execute(
            "SELECT product_id, product_name, quantity, unit_price, total_price FROM import_items WHERE import_number = ?",
            (import_number,),
            fetch_all=True,
        )
        import_order.items = [
            {"product_id": item[0], "product_name": item[1], "quantity": item[2], "unit_price": item[3], "total_price": item[4]}
            for item in items
        ]
        return import_order

    @classmethod
    def search(cls, keyword):
        keyword = f"%{keyword.lower()}%"
        rows = Database.execute(
            "SELECT import_number, supplier_id, supplier_name, import_date, payment_status, total_amount, note, created_at FROM import_orders WHERE LOWER(import_number) LIKE ? OR LOWER(supplier_name) LIKE ? OR LOWER(payment_status) LIKE ? ORDER BY created_at DESC",
            (keyword, keyword, keyword),
            fetch_all=True,
        )
        orders = []
        for row in rows:
            import_order = cls(*row, items=[])
            items = Database.execute(
                "SELECT product_id, product_name, quantity, unit_price, total_price FROM import_items WHERE import_number = ?",
                (import_order.import_number,),
                fetch_all=True,
            )
            import_order.items = [
                {"product_id": item[0], "product_name": item[1], "quantity": item[2], "unit_price": item[3], "total_price": item[4]}
                for item in items
            ]
            orders.append(import_order)
        return orders
