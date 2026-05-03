from dataclasses import dataclass
from datetime import datetime
from .database import Database


@dataclass
class Supplier:
    supplier_id: str
    name: str
    phone: str = ""
    email: str = ""
    address: str = ""
    tax_code: str = ""
    contact_person: str = ""
    bank_account: str = ""
    bank_name: str = ""
    debt: float = 0.0
    status: str = "Đang hợp tác"
    note: str = ""
    created_at: str = ""

    @classmethod
    def create_table(cls, cursor):
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='suppliers'")
        if cursor.fetchone() is None:
            cursor.execute(
                """
                CREATE TABLE suppliers (
                    supplier_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    tax_code TEXT,
                    contact_person TEXT,
                    bank_account TEXT,
                    bank_name TEXT,
                    debt REAL DEFAULT 0,
                    status TEXT DEFAULT 'Đang hợp tác',
                    note TEXT,
                    created_at TEXT
                )
                """
            )

    @classmethod
    def generate_supplier_id(cls):
        rows = Database.execute(
            "SELECT supplier_id FROM suppliers WHERE supplier_id LIKE 'NCC%'",
            fetch_all=True,
        )
        max_num = 0
        for row in rows:
            supplier_id = row[0]
            if supplier_id and supplier_id.startswith('NCC'):
                try:
                    num = int(supplier_id[3:])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        return f"NCC{max_num + 1:03d}"

    @classmethod
    def create(cls, name, phone="", email="", address="", tax_code="", contact_person="", bank_account="", bank_name="", debt=0.0, status="Đang hợp tác", note=""):
        supplier_id = cls.generate_supplier_id()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        Database.execute(
            "INSERT INTO suppliers (supplier_id, name, phone, email, address, tax_code, contact_person, bank_account, bank_name, debt, status, note, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (supplier_id, name, phone, email, address, tax_code, contact_person, bank_account, bank_name, debt, status, note, created_at),
            commit=True,
        )
        return cls(supplier_id, name, phone, email, address, tax_code, contact_person, bank_account, bank_name, debt, status, note, created_at)

    @classmethod
    def get_all(cls):
        rows = Database.execute(
            "SELECT supplier_id, name, phone, email, address, tax_code, contact_person, bank_account, bank_name, debt, status, note, created_at FROM suppliers ORDER BY name",
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    @classmethod
    def get_by_id(cls, supplier_id):
        row = Database.execute(
            "SELECT supplier_id, name, phone, email, address, tax_code, contact_person, bank_account, bank_name, debt, status, note, created_at FROM suppliers WHERE supplier_id = ?",
            (supplier_id,),
            fetch_one=True,
        )
        return cls(*row) if row else None

    @classmethod
    def search(cls, keyword):
        keyword = f"%{keyword.lower()}%"
        rows = Database.execute(
            "SELECT supplier_id, name, phone, email, address, tax_code, contact_person, bank_account, bank_name, debt, status, note, created_at FROM suppliers WHERE LOWER(name) LIKE ? OR LOWER(phone) LIKE ? OR LOWER(email) LIKE ? OR LOWER(address) LIKE ? OR LOWER(tax_code) LIKE ? OR supplier_id LIKE ? ORDER BY name",
            (keyword, keyword, keyword, keyword, keyword, keyword),
            fetch_all=True,
        )
        return [cls(*row) for row in rows]

    def update(self):
        Database.execute(
            "UPDATE suppliers SET name = ?, phone = ?, email = ?, address = ?, tax_code = ?, contact_person = ?, bank_account = ?, bank_name = ?, debt = ?, status = ?, note = ? WHERE supplier_id = ?",
            (self.name, self.phone, self.email, self.address, self.tax_code, self.contact_person, self.bank_account, self.bank_name, self.debt, self.status, self.note, self.supplier_id),
            commit=True,
        )

    def delete(self):
        Database.execute(
            "DELETE FROM suppliers WHERE supplier_id = ?",
            (self.supplier_id,),
            commit=True,
        )
