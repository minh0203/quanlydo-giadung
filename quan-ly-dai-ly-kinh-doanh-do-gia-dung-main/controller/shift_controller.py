import calendar
import csv
from datetime import datetime

from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QFileDialog
from PyQt5.QtWidgets import QAbstractItemView

from models.employee import Employee
from models.shift_schedule import ShiftScheduleEntry


class ShiftController:
    """Controller xử lý logic lịch làm việc"""

    SHIFTS = ["", "Sáng", "Chiều", "Tối", "Nghỉ"]

    def __init__(self, view):
        self.view = view
        self.employees = []
        self.current_year_month = self.get_year_month()
        self.setup_connections()
        self.load_employees()
        self.load_schedule()

    def setup_connections(self):
        if hasattr(self.view, "btnLoadSchedule"):
            self.view.btnLoadSchedule.clicked.connect(self.load_schedule)
        if hasattr(self.view, "btnSaveSchedule"):
            self.view.btnSaveSchedule.clicked.connect(self.save_schedule)
        if hasattr(self.view, "btnClearSchedule"):
            self.view.btnClearSchedule.clicked.connect(self.clear_schedule)
        if hasattr(self.view, "btnCopyWeek"):
            self.view.btnCopyWeek.clicked.connect(self.copy_week)
        if hasattr(self.view, "btnExportSchedule"):
            self.view.btnExportSchedule.clicked.connect(self.export_schedule)
        if hasattr(self.view, "btnViewEmployeeSchedule"):
            self.view.btnViewEmployeeSchedule.clicked.connect(self.view_employee_schedule)
        if hasattr(self.view, "dateMonth"):
            self.view.dateMonth.dateChanged.connect(self.on_month_changed)
        if hasattr(self.view, "tableSchedule"):
            self.view.tableSchedule.setSelectionBehavior(QAbstractItemView.SelectItems)
            self.view.tableSchedule.setEditTriggers(QAbstractItemView.DoubleClicked)

    def get_year_month(self):
        if hasattr(self.view, "dateMonth"):
            date = self.view.dateMonth.date()
            return f"{date.year():04d}-{date.month():02d}"
        return datetime.now().strftime("%Y-%m")

    def on_month_changed(self):
        self.current_year_month = self.get_year_month()
        self.load_schedule()

    def load_employees(self):
        self.employees = Employee.get_all()
        if not self.employees:
            default_staff = [
                {"full_name": "Nguyễn Văn A", "role": "Sale"},
                {"full_name": "Trần Thị B", "role": "Warehouse"},
                {"full_name": "Lê Văn C", "role": "Manager"},
            ]
            for staff in default_staff:
                Employee.create(full_name=staff["full_name"], role=staff["role"])
            self.employees = Employee.get_all()

        if hasattr(self.view, "cboEmployee"):
            self.view.cboEmployee.clear()
            self.view.cboEmployee.addItem("")
            for employee in self.employees:
                self.view.cboEmployee.addItem(f"{employee.employee_id} - {employee.full_name}")

    def build_schedule_table(self, schedule_entries=None):
        if not hasattr(self.view, "tableSchedule"):
            return

        days = calendar.monthrange(int(self.current_year_month[:4]), int(self.current_year_month[5:]))[1]
        table = self.view.tableSchedule
        table.clear()
        table.setRowCount(len(self.employees))
        table.setColumnCount(days + 1)
        headers = ["Nhân viên"] + [f"{day}" for day in range(1, days + 1)]
        table.setHorizontalHeaderLabels(headers)

        schedule_map = {}
        if schedule_entries:
            for entry in schedule_entries:
                schedule_map[(entry.employee_id, entry.day)] = entry.shift_code

        for row, employee in enumerate(self.employees):
            table.setItem(row, 0, QTableWidgetItem(employee.full_name))
            for day in range(1, days + 1):
                shift_code = schedule_map.get((employee.employee_id, day), "")
                table.setItem(row, day, QTableWidgetItem(shift_code))

        table.resizeColumnsToContents()

    def load_schedule(self):
        self.current_year_month = self.get_year_month()
        entries = ShiftScheduleEntry.get_by_month(self.current_year_month)
        self.build_schedule_table(entries)
        if not entries and self.employees:
            QMessageBox.information(None, "Thông báo", f"Chưa có lịch cho {self.current_year_month}. Vui lòng tạo mới.")

    def save_schedule(self):
        if not self.employees:
            QMessageBox.warning(None, "Cảnh báo", "Không có nhân viên để lưu lịch.")
            return
        if not hasattr(self.view, "tableSchedule"):
            return

        table = self.view.tableSchedule
        entries = []
        for row, employee in enumerate(self.employees):
            for col in range(1, table.columnCount()):
                item = table.item(row, col)
                shift_code = item.text().strip() if item else ""
                if shift_code:
                    entries.append({
                        "employee_id": employee.employee_id,
                        "employee_name": employee.full_name,
                        "day": col,
                        "shift_code": shift_code,
                    })

        ShiftScheduleEntry.save_month(self.current_year_month, entries)
        QMessageBox.information(None, "Thành công", "Đã lưu lịch phân ca thành công.")

    def clear_schedule(self):
        if not hasattr(self.view, "tableSchedule"):
            return
        table = self.view.tableSchedule
        for row in range(table.rowCount()):
            for col in range(1, table.columnCount()):
                table.setItem(row, col, QTableWidgetItem(""))

    def copy_week(self):
        if not hasattr(self.view, "tableSchedule"):
            return
        table = self.view.tableSchedule
        days = table.columnCount() - 1
        if days <= 7:
            QMessageBox.warning(None, "Cảnh báo", "Không đủ ngày để copy tuần.")
            return

        for row in range(table.rowCount()):
            for col in range(1, days + 1):
                if col > 7:
                    source_item = table.item(row, col - 7)
                    source_text = source_item.text() if source_item else ""
                    table.setItem(row, col, QTableWidgetItem(source_text))
        QMessageBox.information(None, "Thành công", "Đã copy lịch tuần vào phần còn lại của tháng.")

    def view_employee_schedule(self):
        if not hasattr(self.view, "cboEmployee") or not hasattr(self.view, "tableEmployeeSchedule"):
            return
        selected = self.view.cboEmployee.currentText().strip()
        if not selected:
            QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn nhân viên.")
            return
        employee_id = selected.split(" - ")[0]
        entries = ShiftScheduleEntry.get_employee_schedule(employee_id, self.current_year_month)
        table = self.view.tableEmployeeSchedule
        table.clear()
        table.setRowCount(len(entries))
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Ngày", "Ca"])
        for row, entry in enumerate(entries):
            table.setItem(row, 0, QTableWidgetItem(str(entry.day)))
            table.setItem(row, 1, QTableWidgetItem(entry.shift_code))
        table.resizeColumnsToContents()

    def export_schedule(self):
        if not hasattr(self.view, "tableSchedule"):
            return
        path, _ = QFileDialog.getSaveFileName(None, "Xuất lịch phân ca", "shift_schedule.csv", "CSV Files (*.csv)")
        if not path:
            return
        table = self.view.tableSchedule
        rows = []
        headers = [table.horizontalHeaderItem(col).text() for col in range(table.columnCount())]
        rows.append(headers)
        for row in range(table.rowCount()):
            row_data = []
            for col in range(table.columnCount()):
                item = table.item(row, col)
                row_data.append(item.text() if item else "")
            rows.append(row_data)
        try:
            with open(path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(rows)
            QMessageBox.information(None, "Thành công", "Đã xuất lịch phân ca ra file CSV.")
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể xuất file: {str(e)}")