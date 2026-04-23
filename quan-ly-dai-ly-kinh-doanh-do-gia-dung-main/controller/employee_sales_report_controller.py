from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QComboBox
from PyQt5.QtCore import Qt
import sqlite3
from datetime import datetime, timedelta

class EmployeeSalesReportController:
    """Controller xử lý logic báo cáo bán hàng theo nhân viên"""

    def __init__(self, view):
        self.view = view
        self.db_path = "database/store.db"
        self.setup_connections()

    def setup_connections(self):
        """Thiết lập kết nối các signal"""
        # Kết nối nút tìm kiếm
        if hasattr(self.view, 'btnSearch'):
            self.view.btnSearch.clicked.connect(self.search_sales_report)

        # Kết nối nút xuất báo cáo
        if hasattr(self.view, 'btnExport'):
            self.view.btnExport.clicked.connect(self.export_report)

        # Kết nối nút làm mới
        if hasattr(self.view, 'btnRefresh'):
            self.view.btnRefresh.clicked.connect(self.load_sales_data)

        # Kết nối combobox lọc thời gian
        if hasattr(self.view, 'cbTimeFilter'):
            self.view.cbTimeFilter.currentTextChanged.connect(self.on_time_filter_changed)

        # Tự động tải dữ liệu khi khởi tạo
        self.load_employee_list()
        self.load_sales_data()

    def load_employee_list(self):
        """Tải danh sách nhân viên cho combobox"""
        if not hasattr(self.view, 'cbEmployee'):
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT employee_id, name FROM employees ORDER BY name")
            employees = cursor.fetchall()

            self.view.cbEmployee.clear()
            self.view.cbEmployee.addItem("Tất cả nhân viên", None)
            for emp_id, name in employees:
                self.view.cbEmployee.addItem(f"{name} ({emp_id})", emp_id)

            conn.close()

        except Exception as e:
            QMessageBox.warning(self.view, "Lỗi", f"Không thể tải danh sách nhân viên: {str(e)}")

    def load_sales_data(self, employee_id=None, date_from=None, date_to=None):
        """Tải dữ liệu báo cáo bán hàng"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Query lấy dữ liệu bán hàng theo nhân viên
            query = """
            SELECT
                e.employee_id,
                e.name as employee_name,
                COUNT(o.order_id) as total_orders,
                COALESCE(SUM(o.total_amount), 0) as total_sales,
                AVG(o.total_amount) as avg_order_value,
                MAX(o.order_date) as last_sale_date
            FROM employees e
            LEFT JOIN orders o ON e.employee_id = o.employee_id
            """

            params = []
            conditions = []

            if employee_id:
                conditions.append("e.employee_id = ?")
                params.append(employee_id)

            if date_from and date_to:
                conditions.append("o.order_date BETWEEN ? AND ?")
                params.extend([date_from, date_to])
            elif date_from:
                conditions.append("o.order_date >= ?")
                params.append(date_from)
            elif date_to:
                conditions.append("o.order_date <= ?")
                params.append(date_to)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " GROUP BY e.employee_id, e.name ORDER BY total_sales DESC"

            cursor.execute(query, params)
            results = cursor.fetchall()

            # Hiển thị dữ liệu lên table
            self.display_sales_data(results)

            conn.close()

        except Exception as e:
            QMessageBox.warning(self.view, "Lỗi", f"Không thể tải dữ liệu báo cáo: {str(e)}")

    def display_sales_data(self, data):
        """Hiển thị dữ liệu báo cáo lên table"""
        if not hasattr(self.view, 'tableSales'):
            return

        table = self.view.tableSales
        table.setRowCount(len(data))
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Mã NV", "Tên nhân viên", "Tổng đơn hàng",
            "Tổng doanh thu", "Giá trị TB/đơn", "Ngày bán cuối"
        ])

        for row, item in enumerate(data):
            for col, value in enumerate(item):
                if col == 3 or col == 4:  # Tổng doanh thu và giá trị TB
                    display_value = f"{float(value):,.0f} VNĐ" if value else "0 VNĐ"
                elif col == 5:  # Ngày
                    display_value = value if value else "Chưa có"
                else:
                    display_value = str(value) if value is not None else ""

                table_item = QTableWidgetItem(display_value)
                table_item.setFlags(table_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, col, table_item)

        # Điều chỉnh kích thước cột
        table.resizeColumnsToContents()

    def search_sales_report(self):
        """Tìm kiếm báo cáo bán hàng"""
        employee_id = None
        if hasattr(self.view, 'cbEmployee'):
            employee_id = self.view.cbEmployee.currentData()

        date_from = None
        date_to = None

        if hasattr(self.view, 'dateFrom') and self.view.dateFrom.dateTime().toString("yyyy-MM-dd") != "2000-01-01":
            date_from = self.view.dateFrom.dateTime().toString("yyyy-MM-dd")

        if hasattr(self.view, 'dateTo') and self.view.dateTo.dateTime().toString("yyyy-MM-dd") != "2000-01-01":
            date_to = self.view.dateTo.dateTime().toString("yyyy-MM-dd")

        self.load_sales_data(employee_id, date_from, date_to)

    def on_time_filter_changed(self):
        """Xử lý khi thay đổi bộ lọc thời gian"""
        if not hasattr(self.view, 'cbTimeFilter'):
            return

        filter_type = self.view.cbTimeFilter.currentText()

        if filter_type == "Hôm nay":
            today = datetime.now().strftime("%Y-%m-%d")
            if hasattr(self.view, 'dateFrom'):
                self.view.dateFrom.setDateTime(datetime.strptime(today, "%Y-%m-%d"))
            if hasattr(self.view, 'dateTo'):
                self.view.dateTo.setDateTime(datetime.strptime(today, "%Y-%m-%d"))
        elif filter_type == "Tuần này":
            # Tính toán ngày đầu và cuối tuần
            today = datetime.now()
            start_of_week = today - datetime.timedelta(days=today.weekday())
            end_of_week = start_of_week + datetime.timedelta(days=6)
            if hasattr(self.view, 'dateFrom'):
                self.view.dateFrom.setDateTime(start_of_week)
            if hasattr(self.view, 'dateTo'):
                self.view.dateTo.setDateTime(end_of_week)
        elif filter_type == "Tháng này":
            today = datetime.now()
            start_of_month = today.replace(day=1)
            if hasattr(self.view, 'dateFrom'):
                self.view.dateFrom.setDateTime(start_of_month)
            if hasattr(self.view, 'dateTo'):
                self.view.dateTo.setDateTime(today)

        self.search_sales_report()

    def export_report(self):
        """Xuất báo cáo bán hàng ra file"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            import csv

            filename, _ = QFileDialog.getSaveFileName(
                self.view, "Xuất báo cáo", "employee_sales_report.csv",
                "CSV Files (*.csv);;All Files (*)"
            )

            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Mã NV", "Tên nhân viên", "Tổng đơn hàng", "Tổng doanh thu", "Giá trị TB/đơn", "Ngày bán cuối"])

                    for row in range(self.view.tableSales.rowCount()):
                        row_data = []
                        for col in range(self.view.tableSales.columnCount()):
                            item = self.view.tableSales.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)

                QMessageBox.information(self.view, "Thành công", "Đã xuất báo cáo thành công!")

        except Exception as e:
            QMessageBox.warning(self.view, "Lỗi", f"Không thể xuất báo cáo: {str(e)}")