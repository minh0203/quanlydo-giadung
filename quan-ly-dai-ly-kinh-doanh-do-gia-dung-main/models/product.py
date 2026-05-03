from dataclasses import dataclass
from .database import Database


@dataclass
class Product:
    product_id: str
    name: str
    category: str = ""
    brand: str = ""
    purchase_price: float = 0.0
    selling_price: float = 0.0
    quantity: int = 0
    unit: str = "Cái"
    description: str = ""
    warranty_months: int = 12

    @classmethod
    def create_table(cls, cursor):
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                product_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                brand TEXT,
                purchase_price REAL DEFAULT 0.0,
                selling_price REAL DEFAULT 0.0,
                quantity INTEGER DEFAULT 0,
                unit TEXT DEFAULT 'Cái',
                description TEXT,
                warranty_months INTEGER DEFAULT 12
            )
            """
        )
        
        # Thêm cột warranty_months nếu chưa tồn tại
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]
        if "warranty_months" not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN warranty_months INTEGER DEFAULT 12")

    @classmethod
    def generate_product_id(cls):
        """Tạo mã sản phẩm tự động dạng SP001, SP002, ..."""
        rows = Database.execute(
            "SELECT product_id FROM products WHERE product_id LIKE 'SP%'",
            fetch_all=True,
        )
        max_num = 0
        for row in rows:
            product_id = row[0]
            if product_id.startswith('SP'):
                try:
                    num = int(product_id[2:])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        new_num = max_num + 1
        return f"SP{new_num:03d}"

    @classmethod
    def create(cls, name, category="", brand="", purchase_price=0.0, selling_price=0.0, quantity=0, unit="Cái", description="", warranty_months=12):
        product_id = cls.generate_product_id()
        Database.execute(
            "INSERT INTO products (product_id, name, category, brand, purchase_price, selling_price, quantity, unit, description, warranty_months) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (product_id, name, category, brand, purchase_price, selling_price, quantity, unit, description, warranty_months),
            commit=True,
        )
        return cls(product_id, name, category, brand, purchase_price, selling_price, quantity, unit, description, warranty_months)

    @classmethod
    def get_all(cls):
        rows = Database.execute(
            "SELECT product_id, name, category, brand, purchase_price, selling_price, quantity, unit, description, warranty_months FROM products ORDER BY name",
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    @classmethod
    def get_by_id(cls, product_id):
        row = Database.execute(
            "SELECT product_id, name, category, brand, purchase_price, selling_price, quantity, unit, description, warranty_months FROM products WHERE product_id = ?",
            (product_id,),
            fetch_one=True,
        )
        return cls(*row) if row else None

    @classmethod
    def search(cls, keyword):
        keyword = f"%{keyword.lower()}%"
        rows = Database.execute(
            "SELECT product_id, name, category, brand, purchase_price, selling_price, quantity, unit, description, warranty_months FROM products WHERE LOWER(name) LIKE ? OR LOWER(category) LIKE ? OR LOWER(brand) LIKE ? OR product_id LIKE ? ORDER BY name",
            (keyword, keyword, keyword, keyword),
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    def update(self):
        Database.execute(
            "UPDATE products SET name = ?, category = ?, brand = ?, purchase_price = ?, selling_price = ?, quantity = ?, unit = ?, description = ?, warranty_months = ? WHERE product_id = ?",
            (self.name, self.category, self.brand, self.purchase_price, self.selling_price, self.quantity, self.unit, self.description, self.warranty_months, self.product_id),
            commit=True,
        )

    def delete(self):
        Database.execute(
            "DELETE FROM products WHERE product_id = ?",
            (self.product_id,),
            commit=True,
        )
