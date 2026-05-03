from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
import sqlite3
from datetime import datetime

class InventoryReportController:
    """Controller xử lý logic báo cáo tồn kho"""

    def __init__(self, view):
        self.view = view
        self.db_path = "database/store.db"
        self.setup_connections()

    def setup_connections(self):
        """Thiết lập kết nối các signal"""
        # Kết nối nút tìm kiếm
        if hasattr(self.view, 'btnSearch'):
            self.view.btnSearch.clicked.connect(self.search_inventory)

        # Kết nối nút xuất báo cáo
        if hasattr(self.view, 'btnExport'):
            self.view.btnExport.clicked.connect(self.export_report)

        # Kết nối nút làm mới
        if hasattr(self.view, 'btnRefresh'):
            self.view.btnRefresh.clicked.connect(self.load_inventory_data)

        # Tự động tải dữ liệu khi khởi tạo
        self.load_inventory_data()

    def load_inventory_data(self):
        """Tải dữ liệu tồn kho từ database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Query lấy thông tin tồn kho
            query = """
            SELECT
                p.product_id,
                p.name,
                p.category,
                COALESCE(SUM(CASE WHEN t.type = 'import' THEN t.quantity ELSE 0 END), 0) -
                COALESCE(SUM(CASE WHEN t.type = 'export' THEN t.quantity ELSE 0 END), 0) as stock_quantity,
                p.price,
                p.supplier_id
            FROM products p
            LEFT JOIN transactions t ON p.product_id = t.product_id
            GROUP BY p.product_id, p.name, p.category, p.price, p.supplier_id
            ORDER BY p.name
            """

            cursor.execute(query)
            results = cursor.fetchall()

            # Hiển thị dữ liệu lên table
            self.display_inventory_data(results)

            conn.close()

        except Exception as e:
            QMessageBox.warning(self.view, "Lỗi", f"Không thể tải dữ liệu tồn kho: {str(e)}")

    def display_inventory_data(self, data):
        """Hiển thị dữ liệu tồn kho lên table"""
        if not hasattr(self.view, 'tableInventory'):
            return

        table = self.view.tableInventory
        table.setRowCount(len(data))
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Mã sản phẩm", "Tên sản phẩm", "Danh mục",
            "Số lượng tồn", "Giá", "Nhà cung cấp"
        ])

        for row, item in enumerate(data):
            for col, value in enumerate(item):
                table_item = QTableWidgetItem(str(value) if value is not None else "")
                table_item.setFlags(table_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, col, table_item)

        # Điều chỉnh kích thước cột
        table.resizeColumnsToContents()

    def search_inventory(self):
        """Tìm kiếm sản phẩm trong tồn kho"""
        if not hasattr(self.view, 'txtSearch'):
            return

        search_text = self.view.txtSearch.text().strip().lower()

        if not search_text:
            self.load_inventory_data()
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = """
            SELECT
                p.product_id,
                p.name,
                p.category,
                COALESCE(SUM(CASE WHEN t.type = 'import' THEN t.quantity ELSE 0 END), 0) -
                COALESCE(SUM(CASE WHEN t.type = 'export' THEN t.quantity ELSE 0 END), 0) as stock_quantity,
                p.price,
                p.supplier_id
            FROM products p
            LEFT JOIN transactions t ON p.product_id = t.product_id
            WHERE LOWER(p.name) LIKE ? OR LOWER(p.category) LIKE ? OR p.product_id LIKE ?
            GROUP BY p.product_id, p.name, p.category, p.price, p.supplier_id
            ORDER BY p.name
            """

            cursor.execute(query, (f'%{search_text}%', f'%{search_text}%', f'%{search_text}%'))
            results = cursor.fetchall()

            self.display_inventory_data(results)
            conn.close()

        except Exception as e:
            QMessageBox.warning(self.view, "Lỗi", f"Không thể tìm kiếm: {str(e)}")

    def export_report(self):
        """Xuất báo cáo tồn kho ra file"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            import csv

            filename, _ = QFileDialog.getSaveFileName(
                self.view, "Xuất báo cáo", "inventory_report.csv",
                "CSV Files (*.csv);;All Files (*)"
            )

            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Mã sản phẩm", "Tên sản phẩm", "Danh mục", "Số lượng tồn", "Giá", "Nhà cung cấp"])

                    for row in range(self.view.tableInventory.rowCount()):
                        row_data = []
                        for col in range(self.view.tableInventory.columnCount()):
                            item = self.view.tableInventory.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)

                QMessageBox.information(self.view, "Thành công", "Đã xuất báo cáo thành công!")

        except Exception as e:
            QMessageBox.warning(self.view, "Lỗi", f"Không thể xuất báo cáo: {str(e)}")
