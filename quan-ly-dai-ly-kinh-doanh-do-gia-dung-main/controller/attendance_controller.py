from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QDate, QTime, QDateTime
from datetime import datetime, timedelta
import json
import os


class AttendanceController:
    """Controller xử lý logic điểm danh nhân viên"""

    def __init__(self, view):
        self.view = view
        self.attendance_data = {}  # Lưu dữ liệu điểm danh trong bộ nhớ
        self.load_attendance_data()
        self.connect_signals()
        self.setup_table()
        self.load_employee_list()

    def connect_signals(self):
        """Kết nối các signal từ UI"""
        # Nút điểm danh
        if hasattr(self.view, 'btnCheckIn'):
            self.view.btnCheckIn.clicked.connect(self.check_in)
        if hasattr(self.view, 'btnCheckOut'):
            self.view.btnCheckOut.clicked.connect(self.check_out)

        # Nút làm mới
        if hasattr(self.view, 'btnRefresh'):
            self.view.btnRefresh.clicked.connect(self.refresh_data)

        # Nút xem báo cáo
        if hasattr(self.view, 'btnViewReport'):
            self.view.btnViewReport.clicked.connect(self.view_report)

        # Combobox chọn ngày
        if hasattr(self.view, 'dateEdit'):
            self.view.dateEdit.dateChanged.connect(self.load_attendance_for_date)

    def setup_table(self):
        """Thiết lập bảng điểm danh"""
        if hasattr(self.view, 'tableAttendance'):
            self.view.tableAttendance.setColumnCount(5)
            self.view.tableAttendance.setHorizontalHeaderLabels([
                "Mã NV", "Tên NV", "Check In", "Check Out", "Giờ làm"
            ])

    def load_employee_list(self):
        """Tải danh sách nhân viên (tạm thời dùng dữ liệu mẫu)"""
        # TODO: Lấy từ database
        self.employees = {
            "NV001": "Nguyễn Văn A",
            "NV002": "Trần Thị B",
            "NV003": "Lê Văn C",
            "NV004": "Phạm Thị D",
            "NV005": "Hoàng Văn E"
        }

        # Hiển thị trong combobox nếu có
        if hasattr(self.view, 'comboEmployee'):
            self.view.comboEmployee.clear()
            for emp_id, name in self.employees.items():
                self.view.comboEmployee.addItem(f"{emp_id} - {name}", emp_id)

    def check_in(self):
        """Xử lý check in"""
        if not hasattr(self.view, 'comboEmployee'):
            QMessageBox.warning(self.view, "Lỗi", "Không tìm thấy danh sách nhân viên!")
            return

        emp_id = self.view.comboEmployee.currentData()
        if not emp_id:
            QMessageBox.warning(self.view, "Lỗi", "Vui lòng chọn nhân viên!")
            return

        current_date = QDate.currentDate().toString("yyyy-MM-dd")
        current_time = QTime.currentTime().toString("HH:mm:ss")

        # Kiểm tra đã check in chưa
        if self.is_checked_in_today(emp_id, current_date):
            QMessageBox.warning(self.view, "Cảnh báo", "Nhân viên đã check in hôm nay!")
            return

        # Lưu check in
        if current_date not in self.attendance_data:
            self.attendance_data[current_date] = {}

        if emp_id not in self.attendance_data[current_date]:
            self.attendance_data[current_date][emp_id] = {}

        self.attendance_data[current_date][emp_id]['check_in'] = current_time
        self.save_attendance_data()

        QMessageBox.information(self.view, "Thành công",
                               f"Check in thành công cho {self.employees[emp_id]} lúc {current_time}")
        self.refresh_data()

    def check_out(self):
        """Xử lý check out"""
        if not hasattr(self.view, 'comboEmployee'):
            QMessageBox.warning(self.view, "Lỗi", "Không tìm thấy danh sách nhân viên!")
            return

        emp_id = self.view.comboEmployee.currentData()
        if not emp_id:
            QMessageBox.warning(self.view, "Lỗi", "Vui lòng chọn nhân viên!")
            return

        current_date = QDate.currentDate().toString("yyyy-MM-dd")
        current_time = QTime.currentTime().toString("HH:mm:ss")

        # Kiểm tra đã check in chưa
        if not self.is_checked_in_today(emp_id, current_date):
            QMessageBox.warning(self.view, "Cảnh báo", "Nhân viên chưa check in hôm nay!")
            return

        # Kiểm tra đã check out chưa
        if self.is_checked_out_today(emp_id, current_date):
            QMessageBox.warning(self.view, "Cảnh báo", "Nhân viên đã check out hôm nay!")
            return

        # Lưu check out
        self.attendance_data[current_date][emp_id]['check_out'] = current_time
        self.save_attendance_data()

        # Tính giờ làm việc
        check_in_time = self.attendance_data[current_date][emp_id]['check_in']
        work_hours = self.calculate_work_hours(check_in_time, current_time)

        QMessageBox.information(self.view, "Thành công",
                               f"Check out thành công cho {self.employees[emp_id]} lúc {current_time}\n"
                               f"Giờ làm việc: {work_hours:.2f} giờ")
        self.refresh_data()

    def is_checked_in_today(self, emp_id, date):
        """Kiểm tra nhân viên đã check in hôm nay chưa"""
        return (date in self.attendance_data and
                emp_id in self.attendance_data[date] and
                'check_in' in self.attendance_data[date][emp_id])

    def is_checked_out_today(self, emp_id, date):
        """Kiểm tra nhân viên đã check out hôm nay chưa"""
        return (date in self.attendance_data and
                emp_id in self.attendance_data[date] and
                'check_out' in self.attendance_data[date][emp_id])

    def calculate_work_hours(self, check_in_time, check_out_time):
        """Tính số giờ làm việc"""
        try:
            check_in = datetime.strptime(check_in_time, "%H:%M:%S")
            check_out = datetime.strptime(check_out_time, "%H:%M:%S")

            # Tính thời gian làm việc (bao gồm nghỉ trưa nếu cần)
            duration = check_out - check_in

            # Trừ giờ nghỉ trưa (12:00 - 13:00)
            lunch_break = timedelta(hours=1)
            if duration > lunch_break:
                duration = duration - lunch_break

            return duration.total_seconds() / 3600  # Chuyển sang giờ
        except:
            return 0

    def refresh_data(self):
        """Làm mới dữ liệu hiển thị"""
        current_date = QDate.currentDate().toString("yyyy-MM-dd")
        self.load_attendance_for_date(QDate.fromString(current_date, "yyyy-MM-dd"))

    def load_attendance_for_date(self, date):
        """Tải dữ liệu điểm danh cho ngày cụ thể"""
        date_str = date.toString("yyyy-MM-dd")

        if hasattr(self.view, 'tableAttendance'):
            self.view.tableAttendance.setRowCount(0)

            if date_str in self.attendance_data:
                row = 0
                for emp_id, data in self.attendance_data[date_str].items():
                    self.view.tableAttendance.insertRow(row)

                    # Mã NV
                    self.view.tableAttendance.setItem(row, 0, QTableWidgetItem(emp_id))

                    # Tên NV
                    emp_name = self.employees.get(emp_id, "Unknown")
                    self.view.tableAttendance.setItem(row, 1, QTableWidgetItem(emp_name))

                    # Check In
                    check_in = data.get('check_in', '')
                    self.view.tableAttendance.setItem(row, 2, QTableWidgetItem(check_in))

                    # Check Out
                    check_out = data.get('check_out', '')
                    self.view.tableAttendance.setItem(row, 3, QTableWidgetItem(check_out))

                    # Giờ làm
                    if check_in and check_out:
                        work_hours = self.calculate_work_hours(check_in, check_out)
                        self.view.tableAttendance.setItem(row, 4, QTableWidgetItem(f"{work_hours:.2f}"))
                    else:
                        self.view.tableAttendance.setItem(row, 4, QTableWidgetItem(""))

                    row += 1

    def view_report(self):
        """Xem báo cáo điểm danh"""
        # TODO: Implement báo cáo chi tiết
        QMessageBox.information(self.view, "Báo cáo", "Tính năng báo cáo đang phát triển...")

    def load_attendance_data(self):
        """Tải dữ liệu điểm danh từ file"""
        try:
            if os.path.exists('attendance_data.json'):
                with open('attendance_data.json', 'r', encoding='utf-8') as f:
                    self.attendance_data = json.load(f)
        except:
            self.attendance_data = {}

    def save_attendance_data(self):
        """Lưu dữ liệu điểm danh vào file"""
        try:
            with open('attendance_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.attendance_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            QMessageBox.warning(self.view, "Lỗi", f"Không thể lưu dữ liệu: {str(e)}")