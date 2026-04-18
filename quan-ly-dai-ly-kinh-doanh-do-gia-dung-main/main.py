# main.py
import sys
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QDialog, QMessageBox, QLabel, QGroupBox
from PyQt5.QtCore import Qt

# Import các giao diện đã convert
from ui.login import Ui_LoginDialog
from ui.register import Ui_RegisterDialog
from ui.main_window import Ui_MainWindow
from ui.employee_management import Ui_EmployeeManagement
from ui.product_management import Ui_ProductManagement
from ui.customer_management import Ui_CustomerManagement
from ui.sale_order import Ui_SaleOrder
from ui.import_goods import Ui_ImportGoods
from ui.report_viewer import Ui_ReportViewer
from ui.shift_schedule import Ui_ShiftSchedule
from ui.salary_calculation import Ui_SalaryCalculation
from ui.attendance import Ui_Attendance

from PyQt5.QtWidgets import QTableWidgetItem


class LoginDialog(QDialog, Ui_LoginDialog):
    """Cửa sổ đăng nhập"""
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        font = QFont()
        font.setPointSize(18)
        self.txtUsername.setFont(font)
        self.txtPassword.setFont(font)
        
        # Kết nối nút bấm
        self.btnLogin.clicked.connect(self.login)
        self.btnRegister.clicked.connect(self.show_register)
        self.btnExit.clicked.connect(self.close)
        
        # Demo: tự động điền thông tin test
        self.txtUsername.setText("admin")
        self.txtPassword.setText("admin123")
    
    def login(self):
        if self.txtUsername.text() and self.txtPassword.text():
            self.accept()
        else:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập tài khoản và mật khẩu!")
    
    def show_register(self):
        """Hiển thị cửa sổ đăng ký"""
        register_dialog = RegisterDialog()
        if register_dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Thành công", "Đăng ký tài khoản thành công! Vui lòng đăng nhập.")
            # Có thể tự động điền username vừa đăng ký
            self.txtUsername.setText(register_dialog.registered_username)


class RegisterDialog(QDialog, Ui_RegisterDialog):
    """Cửa sổ đăng ký"""
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.registered_username = ""

        font = QFont()
        font.setPointSize(18)
        self.txtUsername.setFont(font)
        self.txtEmail.setFont(font)
        self.txtPassword.setFont(font)
        self.txtConfirmPassword.setFont(font)
        
        # Kết nối nút bấm
        self.btnRegister.clicked.connect(self.register)
        self.btnBack.clicked.connect(self.reject)
    
    def register(self):
        """Xử lý đăng ký tài khoản"""
        username = self.txtUsername.text().strip()
        email = self.txtEmail.text().strip()
        password = self.txtPassword.text()
        confirm_password = self.txtConfirmPassword.text()
        
        # Validation
        if not username:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập tên đăng nhập!")
            return
        
        if not email:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập email!")
            return
        
        if not password:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập mật khẩu!")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "Cảnh báo", "Mật khẩu xác nhận không khớp!")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Cảnh báo", "Mật khẩu phải có ít nhất 6 ký tự!")
            return
        
        # Kiểm tra email hợp lệ (đơn giản)
        if "@" not in email or "." not in email:
            QMessageBox.warning(self, "Cảnh báo", "Email không hợp lệ!")
            return
        
        # TODO: Lưu tài khoản vào database/file
        # Hiện tại chỉ lưu vào biến để demo
        self.registered_username = username
        
        QMessageBox.information(self, "Thành công", f"Đăng ký tài khoản '{username}' thành công!")
        self.accept()


class MainWindow(QMainWindow, Ui_MainWindow):
    """Cửa sổ chính"""
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Khởi tạo stacked widget
        self.stacked_widget = QStackedWidget()
        self.centralwidget.layout().addWidget(self.stacked_widget)
        
        # Tạo các module
        self.create_modules()
        
        # Kết nối menu
        self.connect_menu()
        
        # Hiển thị module mặc định
        self.show_module(0)
        
        self.statusbar.showMessage("✅ Hệ thống sẵn sàng")
    
    def create_modules(self):
        """Tạo các module giao diện"""
        modules = [
            ("home", None),                      # index 0 - Trang chủ
            ("employee", Ui_EmployeeManagement),   # index 1
            ("product", Ui_ProductManagement),    # index 2
            ("customer", Ui_CustomerManagement),  # index 3
            ("sale", Ui_SaleOrder),               # index 4
            ("import", Ui_ImportGoods),           # index 5
            ("report", Ui_ReportViewer),          # index 6
            ("shift", Ui_ShiftSchedule),          # index 7
            ("salary", Ui_SalaryCalculation),     # index 8
            ("attendance", Ui_Attendance),        # index 9
        ]
        
        self.module_widgets = {}
        
        for name, ui_class in modules:
            widget = QWidget()
            ui = None
            if ui_class:
                ui = ui_class()
                ui.setupUi(widget)
            else:
                # Trang chủ đơn giản
                layout = QVBoxLayout(widget)
                title = QLabel("🏠 TRANG CHỦ")
                title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; text-align: center;")
                title.setAlignment(Qt.AlignCenter)
                layout.addWidget(title)
                
                # Thêm thông tin tổng quan
                info_layout = QVBoxLayout()
                info_layout.addWidget(QLabel("📊 Tổng quan hệ thống:"))
                info_layout.addWidget(QLabel("• Sản phẩm: 50+ loại"))
                info_layout.addWidget(QLabel("• Khách hàng: 200+"))
                info_layout.addWidget(QLabel("• Nhân viên: 15+"))
                info_layout.addWidget(QLabel("• Doanh thu tháng: 500M VNĐ"))
                
                info_group = QGroupBox("Thống kê nhanh")
                info_group.setLayout(info_layout)
                layout.addWidget(info_group)
                
                layout.addStretch()
            
            self.stacked_widget.addWidget(widget)
            self.module_widgets[name] = {"widget": widget, "ui": ui}
            if name == "product" and ui is not None:
                if hasattr(ui, 'btnAdd'):
                    ui.btnAdd.clicked.connect(self.add_product)
                if hasattr(ui, 'btnEdit'):
                    ui.btnEdit.clicked.connect(self.edit_product)
                if hasattr(ui, 'btnDelete'):
                    ui.btnDelete.clicked.connect(self.delete_product)
                if hasattr(ui, 'tableProducts'):
                    ui.tableProducts.itemSelectionChanged.connect(self.load_selected_product)
            elif name == "customer" and ui is not None:
                if hasattr(ui, 'btnAdd'):
                    ui.btnAdd.clicked.connect(self.add_customer)
                if hasattr(ui, 'btnEditCustomer'):
                    ui.btnEditCustomer.clicked.connect(self.edit_customer)
                if hasattr(ui, 'btnDelete'):
                    ui.btnDelete.clicked.connect(self.delete_customer)
                if hasattr(ui, 'tableCustomers'):
                    ui.tableCustomers.itemSelectionChanged.connect(self.load_selected_customer)
        
        # Thêm dữ liệu mẫu
        self.add_sample_data()
    
    def add_sample_data(self):
        """Thêm dữ liệu mẫu cho các bảng"""
        
        # Dữ liệu nhân viên
        if "employee" in self.module_widgets:
            ui = self.module_widgets["employee"]["ui"]
            if hasattr(ui, 'tableEmployees'):
                data = [
                    ["1", "NV001", "Nguyễn Văn A", "Nam", "0987654321", "nva@email.com", "Admin", "Đang làm", "10,000,000"],
                    ["2", "NV002", "Trần Thị B", "Nữ", "0987654322", "ttb@email.com", "Sale", "Đang làm", "8,000,000"],
                    ["3", "NV003", "Lê Văn C", "Nam", "0987654323", "lvc@email.com", "Kho", "Đang làm", "7,000,000"],
                ]
                ui.tableEmployees.setRowCount(len(data))
                for row, row_data in enumerate(data):
                    for col, value in enumerate(row_data):
                        ui.tableEmployees.setItem(row, col, QTableWidgetItem(value))
        
        # Dữ liệu sản phẩm
        if "product" in self.module_widgets:
            ui = self.module_widgets["product"]["ui"]
            if hasattr(ui, 'tableProducts'):
                data = [
                    ["1", "SP001", "Tủ lạnh Samsung 200L", "Tủ lạnh", "8,500,000", "15", "Còn hàng"],
                    ["2", "SP002", "Máy giặt Panasonic", "Máy giặt", "6,500,000", "10", "Còn hàng"],
                    ["3", "SP003", "TV Sony 55 inch", "TV", "12,500,000", "5", "Còn hàng"],
                ]
                ui.tableProducts.setRowCount(len(data))
                for row, row_data in enumerate(data):
                    for col, value in enumerate(row_data):
                        ui.tableProducts.setItem(row, col, QTableWidgetItem(value))
        
        # Dữ liệu khách hàng
        if "customer" in self.module_widgets:
            ui = self.module_widgets["customer"]["ui"]
            if hasattr(ui, 'tableCustomers'):
                data = [
                    ["1", "KH001", "Nguyễn Văn Khách", "0900000001", "khach1@email.com", "Hà Nội", "150"],
                    ["2", "KH002", "Trần Thị Mua", "0900000002", "mua2@email.com", "HCM", "320"],
                ]
                ui.tableCustomers.setRowCount(len(data))
                for row, row_data in enumerate(data):
                    for col, value in enumerate(row_data):
                        ui.tableCustomers.setItem(row, col, QTableWidgetItem(value))
        
        # Dữ liệu giỏ hàng
        if "sale" in self.module_widgets:
            ui = self.module_widgets["sale"]["ui"]
            if hasattr(ui, 'tableCart'):
                data = [
                    ["1", "SP001", "Tủ lạnh Samsung", "1", "8,500,000", "8,500,000"],
                    ["2", "SP002", "Máy giặt Panasonic", "2", "6,500,000", "13,000,000"],
                ]
                ui.tableCart.setRowCount(len(data))
                for row, row_data in enumerate(data):
                    for col, value in enumerate(row_data):
                        ui.tableCart.setItem(row, col, QTableWidgetItem(value))
                
                if hasattr(ui, 'lblTotal'):
                    ui.lblTotal.setText("21,500,000 VNĐ")
                if hasattr(ui, 'lblGrandTotal'):
                    ui.lblGrandTotal.setText("23,650,000 VNĐ")
    
    def connect_menu(self):
        """Kết nối menu và toolbar"""
        # Menu Quản lý
        if hasattr(self, 'actionHome'):
            self.actionHome.triggered.connect(lambda: self.show_module(0))
        if hasattr(self, 'actionProducts'):
            self.actionProducts.triggered.connect(lambda: self.show_module(2))
        if hasattr(self, 'actionCustomers'):
            self.actionCustomers.triggered.connect(lambda: self.show_module(3))
        if hasattr(self, 'actionEmployees'):
            self.actionEmployees.triggered.connect(lambda: self.show_module(1))
        
        # Menu Bán hàng
        if hasattr(self, 'actionNewOrder'):
            self.actionNewOrder.triggered.connect(lambda: self.show_module(4))
        
        # Menu Nhập hàng
        if hasattr(self, 'actionImportGoods'):
            self.actionImportGoods.triggered.connect(lambda: self.show_module(5))
        
        # Menu Báo cáo
        if hasattr(self, 'actionRevenueReport'):
            self.actionRevenueReport.triggered.connect(lambda: self.show_module(6))
        
        # Menu Hệ thống
        if hasattr(self, 'actionExit'):
            self.actionExit.triggered.connect(self.close)
        
        # Toolbar
        toolbar_actions = [
            ('actionHome', 0),
            ('actionProducts', 2),
            ('actionCustomers', 3),
            ('actionEmployees', 1),
            ('actionNewOrder', 4),
            ('actionRevenueReport', 6),
        ]
        
        for action_name, index in toolbar_actions:
            if hasattr(self, action_name):
                getattr(self, action_name).triggered.connect(lambda x, i=index: self.show_module(i))
    
    def show_module(self, index):
        """Hiển thị module theo index"""
        if 0 <= index < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(index)
            module_names = ["Trang chủ", "Nhân viên", "Sản phẩm", "Khách hàng", "Bán hàng", "Nhập hàng", "Báo cáo", "Phân ca", "Lương", "Chấm công"]
            if index < len(module_names):
                self.statusbar.showMessage(f"Đang hiển thị: {module_names[index]}")

    def add_product(self):
        ui = self.module_widgets.get("product", {}).get("ui")
        if not ui or not hasattr(ui, 'tableProducts') or not hasattr(ui, 'btnAdd'):
            return

        product_code = ui.txtProductCode.text().strip()
        product_name = ui.txtProductName.text().strip()
        category = ui.cboAddCategory.currentText()
        price = ui.txtPrice.text().strip()
        stock_text = ui.txtStock.text().strip()
        status = ui.cboStatus.currentText()

        if not product_code:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập mã sản phẩm!")
            return
        if not product_name:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập tên sản phẩm!")
            return
        if not price:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập giá bán!")
            return
        if not stock_text.isdigit():
            QMessageBox.warning(self, "Cảnh báo", "Tồn kho phải là số nguyên!")
            return

        stock = int(stock_text)
        row = ui.tableProducts.rowCount()
        ui.tableProducts.insertRow(row)
        ui.tableProducts.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        ui.tableProducts.setItem(row, 1, QTableWidgetItem(product_code))
        ui.tableProducts.setItem(row, 2, QTableWidgetItem(product_name))
        ui.tableProducts.setItem(row, 3, QTableWidgetItem(category))
        ui.tableProducts.setItem(row, 4, QTableWidgetItem(price))
        ui.tableProducts.setItem(row, 5, QTableWidgetItem(str(stock)))
        ui.tableProducts.setItem(row, 6, QTableWidgetItem(status))

        ui.txtProductCode.clear()
        ui.txtProductName.clear()
        ui.txtPrice.clear()
        ui.txtStock.clear()
        ui.cboAddCategory.setCurrentIndex(0)
        ui.cboStatus.setCurrentIndex(0)

    def load_selected_product(self):
        ui = self.module_widgets.get("product", {}).get("ui")
        if not ui or not hasattr(ui, 'tableProducts'):
            return

        row = ui.tableProducts.currentRow()
        if row < 0:
            return

        def safe_text(col):
            item = ui.tableProducts.item(row, col)
            return item.text() if item else ""

        ui.txtProductCode.setText(safe_text(1))
        ui.txtProductName.setText(safe_text(2))
        category = safe_text(3)
        index = ui.cboAddCategory.findText(category)
        ui.cboAddCategory.setCurrentIndex(index if index >= 0 else 0)
        ui.txtPrice.setText(safe_text(4))
        ui.txtStock.setText(safe_text(5))
        status = safe_text(6)
        index = ui.cboStatus.findText(status)
        ui.cboStatus.setCurrentIndex(index if index >= 0 else 0)

    def edit_product(self):
        ui = self.module_widgets.get("product", {}).get("ui")
        if not ui or not hasattr(ui, 'tableProducts'):
            return

        row = ui.tableProducts.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn sản phẩm cần sửa!")
            return

        product_code = ui.txtProductCode.text().strip()
        product_name = ui.txtProductName.text().strip()
        category = ui.cboAddCategory.currentText()
        price = ui.txtPrice.text().strip()
        stock_text = ui.txtStock.text().strip()
        status = ui.cboStatus.currentText()

        if not product_code:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập mã sản phẩm!")
            return
        if not product_name:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập tên sản phẩm!")
            return
        if not price:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập giá bán!")
            return
        if not stock_text.isdigit():
            QMessageBox.warning(self, "Cảnh báo", "Tồn kho phải là số nguyên!")
            return

        ui.tableProducts.setItem(row, 1, QTableWidgetItem(product_code))
        ui.tableProducts.setItem(row, 2, QTableWidgetItem(product_name))
        ui.tableProducts.setItem(row, 3, QTableWidgetItem(category))
        ui.tableProducts.setItem(row, 4, QTableWidgetItem(price))
        ui.tableProducts.setItem(row, 5, QTableWidgetItem(stock_text))
        ui.tableProducts.setItem(row, 6, QTableWidgetItem(status))

    def delete_product(self):
        ui = self.module_widgets.get("product", {}).get("ui")
        if not ui or not hasattr(ui, 'tableProducts'):
            return

        row = ui.tableProducts.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn sản phẩm cần xóa!")
            return

        ui.tableProducts.removeRow(row)
        for i in range(ui.tableProducts.rowCount()):
            ui.tableProducts.setItem(i, 0, QTableWidgetItem(str(i + 1)))

        ui.txtProductCode.clear()
        ui.txtProductName.clear()
        ui.txtPrice.clear()
        ui.txtStock.clear()
        ui.cboAddCategory.setCurrentIndex(0)
        ui.cboStatus.setCurrentIndex(0)

    def add_customer(self):
        """Thêm khách hàng mới"""
        ui = self.module_widgets.get("customer", {}).get("ui")
        if not ui or not hasattr(ui, 'tableCustomers'):
            return

        customer_code = ui.txtCustomerCode.text().strip()
        customer_name = ui.txtCustomerName.text().strip()
        phone = ui.txtPhone.text().strip()
        email = ui.txtEmail.text().strip()
        address = ui.txtAddress.text().strip()

        if not customer_code:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập mã khách hàng!")
            return
        if not customer_name:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập tên khách hàng!")
            return
        if not phone:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập số điện thoại!")
            return
        if not email:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập email!")
            return

        row = ui.tableCustomers.rowCount()
        ui.tableCustomers.insertRow(row)
        ui.tableCustomers.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        ui.tableCustomers.setItem(row, 1, QTableWidgetItem(customer_code))
        ui.tableCustomers.setItem(row, 2, QTableWidgetItem(customer_name))
        ui.tableCustomers.setItem(row, 3, QTableWidgetItem(phone))
        ui.tableCustomers.setItem(row, 4, QTableWidgetItem(email))
        ui.tableCustomers.setItem(row, 5, QTableWidgetItem(address))
        ui.tableCustomers.setItem(row, 6, QTableWidgetItem("0"))  # Điểm tích lũy mặc định

        QMessageBox.information(self, "Thành công", "Thêm khách hàng thành công!")

    def load_selected_customer(self):
        """Tải thông tin khách hàng được chọn"""
        ui = self.module_widgets.get("customer", {}).get("ui")
        if not ui or not hasattr(ui, 'tableCustomers'):
            return

        row = ui.tableCustomers.currentRow()
        if row < 0:
            return

        def safe_text(col):
            item = ui.tableCustomers.item(row, col)
            return item.text() if item else ""

        ui.txtCustomerCode.setText(safe_text(1))
        ui.txtCustomerName.setText(safe_text(2))
        ui.txtPhone.setText(safe_text(3))
        ui.txtEmail.setText(safe_text(4))
        ui.txtAddress.setText(safe_text(5))

    def edit_customer(self):
        """Cập nhật thông tin khách hàng"""
        ui = self.module_widgets.get("customer", {}).get("ui")
        if not ui or not hasattr(ui, 'tableCustomers'):
            return

        row = ui.tableCustomers.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn khách hàng cần cập nhật!")
            return

        customer_code = ui.txtCustomerCode.text().strip()
        customer_name = ui.txtCustomerName.text().strip()
        phone = ui.txtPhone.text().strip()
        email = ui.txtEmail.text().strip()
        address = ui.txtAddress.text().strip()

        if not customer_code:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập mã khách hàng!")
            return
        if not customer_name:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập tên khách hàng!")
            return
        if not phone:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập số điện thoại!")
            return
        if not email:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập email!")
            return

        ui.tableCustomers.setItem(row, 1, QTableWidgetItem(customer_code))
        ui.tableCustomers.setItem(row, 2, QTableWidgetItem(customer_name))
        ui.tableCustomers.setItem(row, 3, QTableWidgetItem(phone))
        ui.tableCustomers.setItem(row, 4, QTableWidgetItem(email))
        ui.tableCustomers.setItem(row, 5, QTableWidgetItem(address))

        QMessageBox.information(self, "Thành công", "Cập nhật khách hàng thành công!")

    def delete_customer(self):
        """Xóa khách hàng"""
        ui = self.module_widgets.get("customer", {}).get("ui")
        if not ui or not hasattr(ui, 'tableCustomers'):
            return

        row = ui.tableCustomers.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn khách hàng cần xóa!")
            return

        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc chắn muốn xóa khách hàng này?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            ui.tableCustomers.removeRow(row)
            for i in range(ui.tableCustomers.rowCount()):
                ui.tableCustomers.setItem(i, 0, QTableWidgetItem(str(i + 1)))

            QMessageBox.information(self, "Thành công", "Xóa khách hàng thành công!")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Hiển thị đăng nhập
    login = LoginDialog()
    
    if login.exec() == QDialog.DialogCode.Accepted:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit()


if __name__ == "__main__":
    main()