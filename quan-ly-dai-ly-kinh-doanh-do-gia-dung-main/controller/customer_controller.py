from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QLineEdit, QPushButton, QComboBox, QTextEdit
from PyQt5.QtCore import Qt
from models.customer import Customer
from models.database import Database


class CustomerController:
    """Controller xử lý logic quản lý khách hàng"""

    def __init__(self, view):
        self.view = view
        self.current_customer = None
        self.setup_connections()
        self.load_customers()

    def setup_connections(self):
        """Thiết lập kết nối các signal"""
        # Kết nối nút thêm khách hàng
        if hasattr(self.view, "btnAdd"):
            self.view.btnAdd.clicked.connect(self.show_add_form)

        # Kết nối nút lưu khách hàng
        if hasattr(self.view, "btnSave"):
            self.view.btnSave.clicked.connect(self.save_customer)

        # Kết nối nút cập nhật khách hàng
        if hasattr(self.view, "btnEdit"):
            self.view.btnEdit.clicked.connect(self.edit_customer)

        # Kết nối nút xóa khách hàng
        if hasattr(self.view, "btnDelete"):
            self.view.btnDelete.clicked.connect(self.delete_customer)

        # Kết nối nút làm mới
        if hasattr(self.view, "btnClear"):
            self.view.btnClear.clicked.connect(self.clear_form)

        # Kết nối nút tìm kiếm
        if hasattr(self.view, "btnSearch"):
            self.view.btnSearch.clicked.connect(self.search_customers)

        # Kết nối ô tìm kiếm
        if hasattr(self.view, "txtSearch"):
            self.view.txtSearch.textChanged.connect(self.on_search_text_changed)

        # Kết nối bảng khách hàng
        if hasattr(self.view, "tableCustomers"):
            self.view.tableCustomers.itemSelectionChanged.connect(self.on_customer_selected)

    def load_customers(self):
        """Tải danh sách khách hàng"""
        try:
            customers = Customer.get_all()
            self.display_customers(customers)
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể tải danh sách khách hàng: {str(e)}")

    def display_customers(self, customers):
        """Hiển thị danh sách khách hàng lên bảng"""
        if not hasattr(self.view, "tableCustomers"):
            return

        table = self.view.tableCustomers
        table.setRowCount(len(customers))
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "ID", "Mã KH", "Tên khách hàng", "Điện thoại",
            "Email", "Địa chỉ", "Điểm tích lũy", "Ngày tạo"
        ])

        for row, customer in enumerate(customers):
            table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            table.setItem(row, 1, QTableWidgetItem(customer.customer_id))
            table.setItem(row, 2, QTableWidgetItem(customer.name))
            table.setItem(row, 3, QTableWidgetItem(customer.phone))
            table.setItem(row, 4, QTableWidgetItem(customer.email))
            table.setItem(row, 5, QTableWidgetItem(customer.address))
            table.setItem(row, 6, QTableWidgetItem(str(customer.points)))
            table.setItem(row, 7, QTableWidgetItem(customer.created_date[:10]))  # Hiển thị chỉ ngày

        # Điều chỉnh kích thước cột
        table.resizeColumnsToContents()

    def show_add_form(self):
        """Hiển thị form thêm khách hàng mới"""
        self.clear_form()
        self.current_customer = None
        # Disable mã khách hàng vì tự động tạo
        self.set_field_enabled("txtCustomerCode", False)
        if hasattr(self.view, "btnSave"):
            self.view.btnSave.setEnabled(True)
        if hasattr(self.view, "btnEdit"):
            self.view.btnEdit.setEnabled(False)

    def save_customer(self):
        """Lưu khách hàng (thêm mới hoặc cập nhật)"""
        try:
            # Lấy dữ liệu từ form
            name = self.get_text_field("txtCustomerName")
            phone = self.get_text_field("txtPhone")
            email = self.get_text_field("txtEmail")
            address = self.get_text_field("txtAddress")
            points = self.get_int_field("txtPoints")
            notes = self.get_text_field("txtNotes")

            # Kiểm tra dữ liệu bắt buộc
            if not name:
                QMessageBox.warning(None, "Cảnh báo", "Vui lòng nhập tên khách hàng!")
                return

            if self.current_customer:
                # Cập nhật khách hàng hiện tại
                self.current_customer.name = name
                self.current_customer.phone = phone
                self.current_customer.email = email
                self.current_customer.address = address
                self.current_customer.points = points
                self.current_customer.notes = notes

                self.current_customer.update()
                QMessageBox.information(None, "Thành công", "Đã cập nhật khách hàng thành công!")
            else:
                # Tạo khách hàng mới
                customer = Customer.create(
                    name=name,
                    phone=phone,
                    email=email,
                    address=address,
                    points=points,
                    notes=notes
                )
                QMessageBox.information(None, "Thành công", f"Đã thêm khách hàng thành công! Mã khách hàng: {customer.customer_id}")

            self.clear_form()
            self.load_customers()

        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể lưu khách hàng: {str(e)}")

    def edit_customer(self):
        """Chỉnh sửa khách hàng được chọn"""
        if not self.current_customer:
            QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn khách hàng cần chỉnh sửa!")
            return

        # Enable các field để chỉnh sửa
        self.set_field_enabled("txtCustomerCode", False)  # Không cho sửa mã khách hàng
        if hasattr(self.view, "btnSave"):
            self.view.btnSave.setEnabled(True)
        if hasattr(self.view, "btnEdit"):
            self.view.btnEdit.setEnabled(False)

    def delete_customer(self):
        """Xóa khách hàng"""
        if not self.current_customer:
            QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn khách hàng cần xóa!")
            return

        reply = QMessageBox.question(
            None, "Xác nhận",
            f"Bạn có chắc muốn xóa khách hàng \'{self.current_customer.name}\'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.current_customer.delete()
                QMessageBox.information(None, "Thành công", "Đã xóa khách hàng thành công!")
                self.clear_form()
                self.load_customers()
            except Exception as e:
                QMessageBox.warning(None, "Lỗi", f"Không thể xóa khách hàng: {str(e)}")

    def search_customers(self):
        """Tìm kiếm khách hàng"""
        keyword = self.get_text_field("txtSearch").strip()
        if keyword:
            try:
                customers = Customer.search(keyword)
                self.display_customers(customers)
            except Exception as e:
                QMessageBox.warning(None, "Lỗi", f"Không thể tìm kiếm: {str(e)}")
        else:
            self.load_customers()

    def on_search_text_changed(self):
        """Xử lý khi text tìm kiếm thay đổi"""
        if hasattr(self.view, "txtSearch"):
            if not self.view.txtSearch.text().strip():
                self.load_customers()

    def on_customer_selected(self):
        """Xử lý khi chọn khách hàng từ bảng"""
        if not hasattr(self.view, "tableCustomers"):
            return

        current_row = self.view.tableCustomers.currentRow()
        if current_row >= 0:
            # Column 1 là Mã KH (customer_id), Column 0 là STT
            customer_id = self.view.tableCustomers.item(current_row, 1).text()
            self.current_customer = Customer.get_by_id(customer_id)
            if self.current_customer:
                self.fill_form()

    def fill_form(self):
        """Điền dữ liệu khách hàng vào form"""
        if not self.current_customer:
            return

        self.set_text_field("txtCustomerCode", self.current_customer.customer_id)
        self.set_text_field("txtCustomerName", self.current_customer.name)
        self.set_text_field("txtPhone", self.current_customer.phone)
        self.set_text_field("txtEmail", self.current_customer.email)
        self.set_text_field("txtAddress", self.current_customer.address)
        self.set_text_field("txtPoints", str(self.current_customer.points))
        self.set_text_field("txtNotes", self.current_customer.notes)

        # Disable các nút
        if hasattr(self.view, "btnSave"):
            self.view.btnSave.setEnabled(False)
        if hasattr(self.view, "btnEdit"):
            self.view.btnEdit.setEnabled(True)

    def clear_form(self):
        """Xóa dữ liệu trong form"""
        self.set_text_field("txtCustomerCode", "")
        self.set_text_field("txtCustomerName", "")
        self.set_text_field("txtPhone", "")
        self.set_text_field("txtEmail", "")
        self.set_text_field("txtAddress", "")
        self.set_text_field("txtPoints", "0")
        self.set_text_field("txtNotes", "")

        # Enable các field
        self.set_field_enabled("txtCustomerCode", True)

        # Reset trạng thái nút
        if hasattr(self.view, "btnSave"):
            self.view.btnSave.setEnabled(True)
        if hasattr(self.view, "btnEdit"):
            self.view.btnEdit.setEnabled(False)

        self.current_customer = None

    # Helper methods
    def get_text_field(self, field_name):
        """Lấy text từ field"""
        if hasattr(self.view, field_name):
            field = getattr(self.view, field_name)
            if isinstance(field, QLineEdit):
                return field.text().strip()
            elif isinstance(field, QTextEdit):
                return field.toPlainText().strip()
            elif isinstance(field, QComboBox):
                return field.currentText().strip()
        return ""

    def set_text_field(self, field_name, value):
        """Đặt text cho field"""
        if hasattr(self.view, field_name):
            field = getattr(self.view, field_name)
            if isinstance(field, QLineEdit):
                field.setText(str(value))
            elif isinstance(field, QTextEdit):
                field.setPlainText(str(value))
            elif isinstance(field, QComboBox):
                field.setCurrentText(str(value))

    def get_combo_field(self, field_name):
        """Lấy giá trị từ combo box"""
        if hasattr(self.view, field_name):
            field = getattr(self.view, field_name)
            if isinstance(field, QComboBox):
                return field.currentText().strip()
        return ""

    def set_combo_field(self, field_name, value):
        """Đặt giá trị cho combo box"""
        if hasattr(self.view, field_name):
            field = getattr(self.view, field_name)
            if isinstance(field, QComboBox):
                index = field.findText(str(value))
                if index >= 0:
                    field.setCurrentIndex(index)
                else:
                    field.setCurrentText(str(value))

    def set_field_enabled(self, field_name, enabled):
        """Enable/disable field"""
        if hasattr(self.view, field_name):
            field = getattr(self.view, field_name)
            field.setEnabled(enabled)

    def get_int_field(self, field_name):
        """Lấy giá trị int từ field"""
        text = self.get_text_field(field_name)
        try:
            return int(text) if text else 0
        except ValueError:
            return 0

    def get_float_field(self, field_name):
        """Lấy giá trị float từ field"""
        text = self.get_text_field(field_name)
        try:
            return float(text) if text else 0.0
        except ValueError:
            return 0.0
