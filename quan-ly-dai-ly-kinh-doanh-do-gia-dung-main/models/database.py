import sqlite3
import os


class Database:
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "store.db")

    @staticmethod
    def connect():
        os.makedirs(os.path.dirname(Database.DB_PATH), exist_ok=True)
        return sqlite3.connect(Database.DB_PATH)

    @classmethod
    def execute(cls, query, params=None, fetch_one=False, fetch_all=False, commit=False):
        conn = cls.connect()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        result = None
        if commit:
            conn.commit()
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result

    @classmethod
    def execute_many(cls, query, params_list, commit=False):
        conn = cls.connect()
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        if commit:
            conn.commit()
        cursor.close()
        conn.close()
        return True

    @classmethod
    def initialize_schema(cls):
        from .product import Product
        from .customer import Customer
        from .employee import Employee
        from .sale_order import SaleOrder
        conn = cls.connect()
        cursor = conn.cursor()
        Product.create_table(cursor)
        Customer.create_table(cursor)
        Employee.create_table(cursor)
        SaleOrder.create_table(cursor)
        conn.commit()
        cursor.close()
        conn.close()