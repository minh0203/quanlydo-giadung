from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QDate, QTime
from models.attendance import Attendance
from models.employee import Employee


class AttendanceController:
    """Controller xử lý logic điểm danh"""

    def __init__(self, view):
        self.view = view
        self.employees = {}  # {id: name}

        self.connect_signals()
        self.setup_table()
        self.load_employee_list()
        self.refresh_data()

    # ================= SIGNAL =================
    def connect_signals(self):
        if hasattr(self.view, 'btnCheckIn'):
            self.view.btnCheckIn.clicked.connect(self.check_in)

        if hasattr(self.view, 'btnCheckOut'):
            self.view.btnCheckOut.clicked.connect(self.check_out)

        if hasattr(self.view, 'btnRefresh'):
            self.view.btnRefresh.clicked.connect(self.refresh_data)

        if hasattr(self.view, 'dateEdit'):
            self.view.dateEdit.dateChanged.connect(self.load_attendance_for_date)

    # ================= UI =================
    def setup_table(self):
        if hasattr(self.view, 'tableAttendance'):
            self.view.tableAttendance.setColumnCount(5)
            self.view.tableAttendance.setHorizontalHeaderLabels([
                "Mã NV", "Tên NV", "Check In", "Check Out", "Giờ làm"
            ])

    # ================= DATA =================
    def load_employee_list(self):
        try:
            employees = Employee.get_all()
            self.employees = {e.employee_id: e.full_name for e in employees}

            if hasattr(self.view, 'comboEmployee'):
                self.view.comboEmployee.clear()
                for emp_id, name in self.employees.items():
                    self.view.comboEmployee.addItem(f"{emp_id} - {name}", emp_id)

        except Exception as e:
            QMessageBox.warning(self.view, "Lỗi", f"Lỗi tải nhân viên: {e}")

    # ================= CHECK IN =================
    def check_in(self):
        if not hasattr(self.view, 'comboEmployee'):
            return

        emp_id = self.view.comboEmployee.currentData()
        if not emp_id:
            QMessageBox.warning(self.view, "Lỗi", "Vui lòng chọn nhân viên")
            return

        current_date = QDate.currentDate().toString("yyyy-MM-dd")

        try:
            # kiểm tra đã check in chưa
            records = Attendance.get_by_date(current_date)
            for r in records:
                if r.employee_id == emp_id and r.check_in_time:
                    QMessageBox.warning(self.view, "Cảnh báo", "Đã check in hôm nay")
                    return

            emp_name = self.employees.get(emp_id, emp_id)
            Attendance.check_in(emp_id, emp_name)

            current_time = QTime.currentTime().toString("HH:mm:ss")

            QMessageBox.information(
                self.view,
                "Thành công",
                f"{emp_name} đã check in lúc {current_time}"
            )

            self.refresh_data()

        except Exception as e:
            QMessageBox.warning(self.view, "Lỗi", str(e))

    # ================= CHECK OUT =================
    def check_out(self):
        if not hasattr(self.view, 'comboEmployee'):
            return

        emp_id = self.view.comboEmployee.currentData()
        if not emp_id:
            QMessageBox.warning(self.view, "Lỗi", "Vui lòng chọn nhân viên")
            return

        current_date = QDate.currentDate().toString("yyyy-MM-dd")

        try:
            records = Attendance.get_by_date(current_date)
            record = next((r for r in records if r.employee_id == emp_id), None)

            if not record or not record.check_in_time:
                QMessageBox.warning(self.view, "Cảnh báo", "Chưa check in")
                return

            if record.check_out_time:
                QMessageBox.warning(self.view, "Cảnh báo", "Đã check out")
                return

            Attendance.check_out(emp_id, current_date)

            work_hours = record.calculate_hours()
            current_time = QTime.currentTime().toString("HH:mm:ss")
            emp_name = self.employees.get(emp_id, emp_id)

            QMessageBox.information(
                self.view,
                "Thành công",
                f"{emp_name} đã check out lúc {current_time}\nGiờ làm: {work_hours:.2f}h"
            )

            self.refresh_data()

        except Exception as e:
            QMessageBox.warning(self.view, "Lỗi", str(e))

    # ================= LOAD DATA =================
    def refresh_data(self):
        self.load_attendance_for_date(QDate.currentDate())

    def load_attendance_for_date(self, date):
        if not hasattr(self.view, 'tableAttendance'):
            return

        self.view.tableAttendance.setRowCount(0)

        date_str = date.toString("yyyy-MM-dd")

        try:
            records = Attendance.get_by_date(date_str)

            for row, record in enumerate(records):
                self.view.tableAttendance.insertRow(row)

                self.view.tableAttendance.setItem(row, 0,
                    QTableWidgetItem(str(record.employee_id)))

                self.view.tableAttendance.setItem(row, 1,
                    QTableWidgetItem(record.employee_name))

                self.view.tableAttendance.setItem(row, 2,
                    QTableWidgetItem(record.check_in_time or ""))

                self.view.tableAttendance.setItem(row, 3,
                    QTableWidgetItem(record.check_out_time or ""))

                if record.check_in_time and record.check_out_time:
                    hours = record.calculate_hours()
                    self.view.tableAttendance.setItem(row, 4,
                        QTableWidgetItem(f"{hours:.2f}"))
                else:
                    self.view.tableAttendance.setItem(row, 4,
                        QTableWidgetItem(""))

        except Exception as e:
            QMessageBox.warning(self.view, "Lỗi", f"Lỗi tải dữ liệu: {e}")