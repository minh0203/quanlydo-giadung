from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QDate, QTime, QDateTime
from datetime import datetime, timedelta
from models.attendance import Attendance
from models.employee import Employee


class AttendanceController:
    """Controller xử lý logic điểm danh nhân viên"""

    def __init__(self, view):
        self.view = view
        self.employees = {}
        self.connect_signals()
        self.setup_table()
        self.load_employee_list()
        self.refresh_data()

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
        """Tải danh sách nhân viên từ database"""
        try:
            employees = Employee.get_all()
            self.employees = {emp.employee_id: emp.full_name for emp in employees}
            
            if not self.employees:
                print("Cảnh báo: Không có nhân viên nào trong database")
                return

            # Hiển thị trong combobox nếu có
            if hasattr(self.view, 'comboEmployee'):
                self.view.comboEmployee.clear()
                for emp_id, name in self.employees.items():
                    self.view.comboEmployee.addItem(f"{emp_id} - {name}", emp_id)
        except Exception as e:
            print(f"Lỗi tải danh sách nhân viên: {e}")
            self.employees = {}

    def check_in(self):
        """Xử lý check in"""
        if not hasattr(self.view, 'comboEmployee'):
            QMessageBox.warning(self.view, "Lỗi", "Không tìm thấy danh sách nhân viên!")
            return

        emp_id = self.view.comboEmployee.currentData()
        if not emp_id:
            QMessageBox.warning(self.view, "Lỗi", "Vui lòng chọn nhân viên!")
            return

        # Kiểm tra đã check in chưa
        existing = Attendance.get_by_date(current_date)
        if any(a.employee_id == emp_id and a.check_in_time for a in existing):
            QMessageBox.warning(self.view, "Cảnh báo", "Nhân viên đã check in hôm nay!")
            return

        try:
            emp_name = self.employees.get(emp_id, emp_id)
            Attendance.check_in(emp_id, emp_name)
            current_time = QTime.currentTime().toString("HH:mm:ss")
            QMessageBox.information(self.view, "Thành công",
                                   f"Check in thành công cho {emp_name} lúc {current_time}")
            self.refresh_data()
        except Exception as e:
            QMessageBox.warning(self.view, "Lỗi", f"Không thể check in: {str(e)}"ation(self.view, "Thành công",
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
        
        # Kiểm tra đã check in chưa
        existing = Attendance.get_by_date(current_date)
        record = next((a for a in existing if a.employee_id == emp_id), None)
        
        if not record or not record.check_in_time:
            QMessageBox.warning(self.view, "Cảnh báo", "Nhân viên chưa check in hôm nay!")
            return

        if record.check_out_time:
            QMessageBox.warning(self.view, "Cảnh báo", "Nhân viên đã check out hôm nay!")
            return

        try:
            Attendance.check_out(emp_id, current_date)
            current_time = QTime.currentTime().toString("HH:mm:ss")
            work_hours = record.calculate_hours()
            emp_name = self.employees.get(emp_id, emp_id)
            QMessageBox.information(self.view, "Thành công",
                                   f"Check out thành công cho {emp_name} lúc {current_time}\n"
                                   f"Giờ làm việc: {work_hours:.2f} giờ")
            self.refresh_data()
        except Exception as e:
            QMessageBox.warning(self.view, "Lỗi", f"Không thể check out: {str(e)}"lf.attendance_data and
                emp_id in self.attendance_data[date] and
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
                    self.view.tableAttendance.se từ database"""
        date_str = date.toString("yyyy-MM-dd")

        if hasattr(self.view, 'tableAttendance'):
            self.view.tableAttendance.setRowCount(0)
            
            try:
                records = Attendance.get_by_date(date_str)
                for row, record in enumerate(records):
                    self.view.tableAttendance.insertRow(row)

                    # Mã NV
                    self.view.tableAttendance.setItem(row, 0, QTableWidgetItem(record.employee_id))

                    # Tên NV
                    self.view.tableAttendance.setItem(row, 1, QTableWidgetItem(record.employee_name))

                    # Check In
                    check_in = record.check_in_time or ''
                    self.view.tableAttendance.setItem(row, 2, QTableWidgetItem(check_in))

                    # Check Out
                    check_out = record.check_out_time or ''
                    self.view.tableAttendance.setItem(row, 3, QTableWidgetItem(check_out))

                    # Giờ làm
                    if check_in and check_out:
                        work_hours = record.calculate_hours()
                        self.view.tableAttendance.setItem(row, 4, QTableWidgetItem(f"{work_hours:.2f}"))
                    else:
                        self.view.tableAttendance.setItem(row, 4, QTableWidgetItem(""))
            except Exception as e:
                print(f"Lỗi tải dữ liệu điểm danh: {e}")endance_data = json.load(f)
        except:
            self.attendance_data = {}

    def save_attendance_data(self):
        """Lưu dữ liệu điểm danh vào file"""
        try:
            with open('attendance_data.json', 'w', encoding='utf-8') as f:
