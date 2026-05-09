from .database import Database


class ProductCategory:
    DEFAULT_CATEGORIES = [
        "Tủ lạnh",
        "Máy giặt",
        "TV",
        "Điều hòa",
        "Bếp từ",
        "Quạt",
        "Máy hút bụi",
    ]

    @classmethod
    def create_table(cls, cursor):
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                name TEXT PRIMARY KEY COLLATE NOCASE
            )
            """
        )

        cursor.execute("SELECT name FROM categories LIMIT 1")
        if not cursor.fetchone():
            cursor.executemany(
                "INSERT INTO categories (name) VALUES (?)",
                [(name,) for name in cls.DEFAULT_CATEGORIES],
            )
            cursor.execute(
                "SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category <> ''"
            )
            for row in cursor.fetchall():
                category = row[0]
                if category:
                    cursor.execute(
                        "INSERT OR IGNORE INTO categories (name) VALUES (?)",
                        (category,),
                    )

    @classmethod
    def get_all(cls):
        rows = Database.execute(
            "SELECT name FROM categories ORDER BY name COLLATE NOCASE",
            fetch_all=True,
        )
        categories = [row[0] for row in rows]
        extra_rows = Database.execute(
            "SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category <> '' ORDER BY category COLLATE NOCASE",
            fetch_all=True,
        )
        for row in extra_rows:
            category = row[0]
            if category and category not in categories:
                categories.append(category)
        return categories

    @classmethod
    def exists(cls, name):
        if not name:
            return False
        row = Database.execute(
            "SELECT 1 FROM categories WHERE name = ? COLLATE NOCASE",
            (name,),
            fetch_one=True,
        )
        return bool(row)

    @classmethod
    def create(cls, name):
        if not name:
            return None
        Database.execute(
            "INSERT OR IGNORE INTO categories (name) VALUES (?)",
            (name,),
            commit=True,
        )
        return name

    @classmethod
    def update(cls, old_name, new_name):
        if not old_name or not new_name:
            return
        Database.execute(
            "UPDATE categories SET name = ? WHERE name = ? COLLATE NOCASE",
            (new_name, old_name),
            commit=True,
        )

    @classmethod
    def delete(cls, name):
        if not name:
            return
        Database.execute(
            "DELETE FROM categories WHERE name = ? COLLATE NOCASE",
            (name,),
            commit=True,
        )
