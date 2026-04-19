# main.py (phiên bản đơn giản - không cần controller)
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget, QDialog, QMessageBox
from PyQt5.QtCore import Qt

# Import UI
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


class RegisterDialog(QDialog, Ui_RegisterDialog):
    """Màn hình đăng ký đơn giản"""
    def __init__(self, parent=None, login_callback=None):
        super().__init__(parent)
        self.setupUi(self)
        self.login_callback = login_callback
        
        # Kết nối sự kiện
        self.btnRegister.clicked.connect(self.register)
        self.btnCancel.clicked.connect(self.close)
        self.btnLogin.clicked.connect(self.back_to_login)
    
    def register(self):
        """Xử lý đăng ký đơn giản"""
        username = self.txtUsername.text().strip()
        password = self.txtPassword.text()
        confirm = self.txtConfirmPassword.text()
        full_name = self.txtFullName.text().strip()
        
        # Kiểm tra đơn giản
        if not username:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên đăng nhập!")
            return
        
        if not password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mật khẩu!")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu xác nhận không khớp!")
            return
        
        if not full_name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập họ tên!")
            return
        
        # TODO: Lưu vào database sau
        QMessageBox.information(self, "Thành công", f"Đăng ký thành công!\nChào mừng {full_name}!")
        self.back_to_login()
    
    def back_to_login(self):
        """Quay lại màn hình đăng nhập"""
        self.close()
        if self.login_callback:
            self.login_callback()


class LoginDialog(QDialog, Ui_LoginDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Kết nối sự kiện
        self.btnLogin.clicked.connect(self.login)
        self.btnRegister.clicked.connect(self.open_register)
        self.btnExit.clicked.connect(self.close)
        
        # Demo: tự động điền thông tin test
        self.txtUsername.setText("admin")
        self.txtPassword.setText("admin123")
    
    def login(self):
        """Xử lý đăng nhập"""
        username = self.txtUsername.text().strip()
        password = self.txtPassword.text()
        
        if username and password:
            self.accept()
        else:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập tài khoản và mật khẩu!")
    
    def open_register(self):
        """Mở màn hình đăng ký"""
        self.register_dialog = RegisterDialog(login_callback=self.show)
        self.hide()
        self.register_dialog.exec()
    
    def show(self):
        """Hiển thị lại màn hình login"""
        super().show()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Tạo stacked widget
        self.stacked_widget = QStackedWidget()
        self.centralwidget.layout().addWidget(self.stacked_widget)
        
        # Tạo và thêm các module
        modules_list = [
            ("employee", Ui_EmployeeManagement),
            ("product", Ui_ProductManagement),
            ("customer", Ui_CustomerManagement),
            ("sale", Ui_SaleOrder),
            ("import", Ui_ImportGoods),
            ("report", Ui_ReportViewer),
            ("shift", Ui_ShiftSchedule),
            ("salary", Ui_SalaryCalculation),
            ("attendance", Ui_Attendance),
        ]
        
        for idx, (name, ui_class) in enumerate(modules_list):
            widget = QWidget()
            ui = ui_class()
            ui.setupUi(widget)
            self.stacked_widget.addWidget(widget)
        
        # Kết nối menu
        self.actionProducts.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.actionCustomers.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        self.actionEmployees.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.actionNewOrder.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        self.actionImportGoods.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(4))
        self.actionRevenueReport.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(5))
        self.actionExit.triggered.connect(self.close)
        
        # Hiển thị module mặc định (sản phẩm)
        self.stacked_widget.setCurrentIndex(1)
        self.statusbar.showMessage("✅ Hệ thống sẵn sàng")


def main():
    app = QApplication(sys.argv)
    login = LoginDialog()
    
    if login.exec() == QDialog.Accepted:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit()


if __name__ == "__main__":
    main()