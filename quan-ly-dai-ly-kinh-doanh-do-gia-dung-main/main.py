# main.py - Chỉ chạy app, logic xử lý ở controller
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QDesktopWidget
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

# Import UI
from ui.login import Ui_LoginDialog
from ui.register import Ui_RegisterDialog
from ui.main_window import Ui_MainWindow

# Import Controller
from controller.auth_controller import LoginAuthController, RegisterAuthController, current_user
from controller.main_controller import MainController

# Import Database
from models.database import Database
from models.employee import Employee


class ChangePasswordDialog(QDialog):
    """Dialog đổi/quên mật khẩu"""
    def __init__(self, parent=None, is_forgot=False):
        super().__init__(parent)
        self.is_forgot = is_forgot
        self.setModal(True)
        self.setup_ui()
        self.center_on_screen()
    
    def center_on_screen(self):
        """Đặt dialog ở giữa màn hình"""
        if self.parent():
            # Nếu có parent, center trên parent
            parent_geometry = self.parent().frameGeometry()
            center_point = parent_geometry.center()
            self.move(center_point.x() - self.width() // 2, center_point.y() - self.height() // 2)
        else:
            # Nếu không có parent, center trên màn hình
            center = QDesktopWidget().availableGeometry().center()
            self.move(center.x() - self.width() // 2, center.y() - self.height() // 2)
    
    def setup_ui(self):
        """Thiết lập giao diện"""
        self.setWindowTitle("Quên mật khẩu" if self.is_forgot else "Đổi mật khẩu")
        self.setGeometry(100, 100, 450, 250 if self.is_forgot else 220)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
            QLabel {
                font-weight: bold;
                color: #2c3e50;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #dcdfe6;
                border-radius: 6px;
                background-color: white;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
                background-color: #f9f9f9;
            }
            QPushButton {
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton#btnOK {
                background-color: #27ae60;
                color: white;
            }
            QPushButton#btnOK:hover {
                background-color: #2ecc71;
            }
            QPushButton#btnCancel {
                background-color: #95a5a6;
                color: white;
            }
            QPushButton#btnCancel:hover {
                background-color: #7f8c8d;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)
        
        # Grid layout cho fields
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 2)
        
        row = 0
        
        if self.is_forgot:
            # Quên mật khẩu
            grid.addWidget(QLabel("Tên đăng nhập:"), row, 0)
            self.txtUsername = QLineEdit()
            self.txtUsername.setPlaceholderText("Nhập tên đăng nhập")
            grid.addWidget(self.txtUsername, row, 1)
            row += 1
            
            grid.addWidget(QLabel("Email:"), row, 0)
            self.txtEmail = QLineEdit()
            self.txtEmail.setPlaceholderText("Nhập email đã đăng ký")
            grid.addWidget(self.txtEmail, row, 1)
            row += 1
            
            grid.addWidget(QLabel("Mật khẩu mới:"), row, 0)
            self.txtNewPassword = QLineEdit()
            self.txtNewPassword.setPlaceholderText("Tối thiểu 6 ký tự")
            self.txtNewPassword.setEchoMode(QLineEdit.Password)
            grid.addWidget(self.txtNewPassword, row, 1)
            row += 1
            
            grid.addWidget(QLabel("Xác nhận:"), row, 0)
            self.txtConfirmPassword = QLineEdit()
            self.txtConfirmPassword.setPlaceholderText("Xác nhận mật khẩu")
            self.txtConfirmPassword.setEchoMode(QLineEdit.Password)
            grid.addWidget(self.txtConfirmPassword, row, 1)
        else:
            # Đổi mật khẩu
            grid.addWidget(QLabel("Mật khẩu hiện tại:"), row, 0)
            self.txtOldPassword = QLineEdit()
            self.txtOldPassword.setPlaceholderText("Nhập mật khẩu hiện tại")
            self.txtOldPassword.setEchoMode(QLineEdit.Password)
            grid.addWidget(self.txtOldPassword, row, 1)
            row += 1
            
            grid.addWidget(QLabel("Mật khẩu mới:"), row, 0)
            self.txtNewPassword = QLineEdit()
            self.txtNewPassword.setPlaceholderText("Tối thiểu 6 ký tự")
            self.txtNewPassword.setEchoMode(QLineEdit.Password)
            grid.addWidget(self.txtNewPassword, row, 1)
            row += 1
            
            grid.addWidget(QLabel("Xác nhận:"), row, 0)
            self.txtConfirmPassword = QLineEdit()
            self.txtConfirmPassword.setPlaceholderText("Xác nhận mật khẩu")
            self.txtConfirmPassword.setEchoMode(QLineEdit.Password)
            grid.addWidget(self.txtConfirmPassword, row, 1)
        
        main_layout.addLayout(grid)
        main_layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btnOK = QPushButton("OK")
        self.btnOK.setObjectName("btnOK")
        self.btnOK.setMinimumWidth(100)
        self.btnCancel = QPushButton("Hủy")
        self.btnCancel.setObjectName("btnCancel")
        self.btnCancel.setMinimumWidth(100)
        btn_layout.addWidget(self.btnOK)
        btn_layout.addWidget(self.btnCancel)
        
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)
        
        # Connect signals
        self.btnOK.clicked.connect(self.on_ok)
        self.btnCancel.clicked.connect(self.reject)
    
    def on_ok(self):
        """Xử lý OK"""
        if self.is_forgot:
            self.handle_forgot_password()
        else:
            self.handle_change_password()
    
    def handle_change_password(self):
        """Xử lý đổi mật khẩu"""
        import controller.auth_controller as auth_module
        current_user = auth_module.current_user
        
        if not current_user:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy thông tin người dùng!")
            return
        
        old_password = self.txtOldPassword.text()
        new_password = self.txtNewPassword.text()
        confirm_password = self.txtConfirmPassword.text()
        
        if not old_password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mật khẩu hiện tại!")
            return
        
        if current_user.password != old_password:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu hiện tại không đúng!")
            return
        
        if len(new_password) < 6:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu mới phải ít nhất 6 ký tự!")
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu xác nhận không khớp!")
            return
        
        # Cập nhật mật khẩu
        try:
            current_user.update_password(new_password)
            QMessageBox.information(self, "Thành công", "Đã đổi mật khẩu thành công!")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể đổi mật khẩu: {str(e)}")
    
    def handle_forgot_password(self):
        """Xử lý quên mật khẩu"""
        username = self.txtUsername.text().strip()
        email = self.txtEmail.text().strip()
        new_password = self.txtNewPassword.text()
        confirm_password = self.txtConfirmPassword.text()
        
        if not username:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên đăng nhập!")
            return
        
        if not email:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập email!")
            return
        
        if len(new_password) < 6:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu mới phải ít nhất 6 ký tự!")
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu xác nhận không khớp!")
            return
        
        # Tìm employee
        employee = Employee.get_by_username(username)
        if not employee:
            QMessageBox.warning(self, "Lỗi", "Tài khoản không tồn tại!")
            return
        
        if employee.email != email:
            QMessageBox.warning(self, "Lỗi", "Email không khớp với tài khoản!")
            return
        
        # Cập nhật mật khẩu
        try:
            employee.update_password(new_password)
            QMessageBox.information(self, "Thành công", "Đã reset mật khẩu thành công! Vui lòng đăng nhập lại.")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể reset mật khẩu: {str(e)}")


class RegisterDialog(QDialog, Ui_RegisterDialog):
    """Màn hình đăng ký - logic xử lý ở controller"""
    def __init__(self, parent=None, login_callback=None):
        super().__init__(parent)
        self.setupUi(self)
        self.login_callback = login_callback
        # Khởi tạo controller
        self.controller = RegisterAuthController(self)


class LoginDialog(QDialog, Ui_LoginDialog):
    """Màn hình đăng nhập - logic xử lý ở controller"""
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # Khởi tạo controller
        self.controller = LoginAuthController(self)
    
    def show_register_dialog(self):
        """Hiển thị dialog đăng ký"""
        print("DEBUG: Showing register dialog...")
        register_dialog = RegisterDialog(self)
        register_dialog.exec()
        print("DEBUG: Register dialog closed")
    
    def show_forgot_password_dialog(self):
        """Hiển thị dialog quên mật khẩu"""
        dialog = ChangePasswordDialog(self, is_forgot=True)
        dialog.exec()


class MainWindow(QMainWindow, Ui_MainWindow):
    """Cửa sổ chính - logic xử lý ở controller"""
    def __init__(self, current_user):
        super().__init__()
        self.setupUi(self)
        self.current_user = current_user
        
        # Khởi tạo database
        Database.initialize_schema()
        
        # Tạo stacked widget
        self.stacked_widget = QStackedWidget()
        self.centralwidget.layout().addWidget(self.stacked_widget)
        
        # Khởi tạo controller (controller sẽ setup các module)
        self.controller = MainController(self, current_user)
        
        # Hiển thị module mặc định
        self.stacked_widget.setCurrentIndex(1)  # Product
        self.update_status_bar()
    
    def update_status_bar(self):
        """Cập nhật status bar với thông tin user"""
        if self.current_user:
            user_info = f"👤 {self.current_user.full_name} | {self.current_user.role}"
            self.statusbar.showMessage(user_info)
    
    def show_change_password_dialog(self):
        """Hiển thị dialog đổi mật khẩu"""
        dialog = ChangePasswordDialog(self, is_forgot=False)
        dialog.exec()


def main():
    app = QApplication(sys.argv)
    login = LoginDialog()
    
    if login.exec() == QDialog.Accepted:
        import controller.auth_controller as auth_module
        current_user_obj = auth_module.current_user
        
        if current_user_obj:
            window = MainWindow(current_user_obj)
            window.show()
            sys.exit(app.exec())
        else:
            QMessageBox.warning(None, "Lỗi", "Không thể lấy thông tin người dùng!")
            sys.exit()
    else:
        sys.exit()


if __name__ == "__main__":
    main()