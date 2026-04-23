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
                description TEXT
            )
            """
        )

    @classmethod
    def create(cls, product_id, name, category="", brand="", purchase_price=0.0, selling_price=0.0, quantity=0, unit="Cái", description=""):
        Database.execute(
            "INSERT INTO products (product_id, name, category, brand, purchase_price, selling_price, quantity, unit, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (product_id, name, category, brand, purchase_price, selling_price, quantity, unit, description),
            commit=True,
        )
        return cls(product_id, name, category, brand, purchase_price, selling_price, quantity, unit, description)

    @classmethod
    def get_all(cls):
        rows = Database.execute(
            "SELECT product_id, name, category, brand, purchase_price, selling_price, quantity, unit, description FROM products ORDER BY name",
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    @classmethod
    def get_by_id(cls, product_id):
        row = Database.execute(
            "SELECT product_id, name, category, brand, purchase_price, selling_price, quantity, unit, description FROM products WHERE product_id = ?",
            (product_id,),
            fetch_one=True,
        )
        return cls(*row) if row else None

    @classmethod
    def search(cls, keyword):
        keyword = f"%{keyword.lower()}%"
        rows = Database.execute(
            "SELECT product_id, name, category, brand, purchase_price, selling_price, quantity, unit, description FROM products WHERE LOWER(name) LIKE ? OR LOWER(category) LIKE ? OR LOWER(brand) LIKE ? OR product_id LIKE ? ORDER BY name",
            (keyword, keyword, keyword, keyword),
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    def update(self):
        Database.execute(
            "UPDATE products SET name = ?, category = ?, brand = ?, purchase_price = ?, selling_price = ?, quantity = ?, unit = ?, description = ? WHERE product_id = ?",
            (self.name, self.category, self.brand, self.purchase_price, self.selling_price, self.quantity, self.unit, self.description, self.product_id),
            commit=True,
        )

    def delete(self):
        Database.execute(
            "DELETE FROM products WHERE product_id = ?",
            (self.product_id,),
            commit=True,
        )