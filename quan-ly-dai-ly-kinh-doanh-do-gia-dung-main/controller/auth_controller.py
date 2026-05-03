from PyQt5.QtWidgets import QMessageBox
from models.employee import Employee


# Biến global để lưu user hiện tại
current_user = None


class LoginAuthController:
    """Controller xử lý logic đăng nhập"""
    
    def __init__(self, view):
        self.view = view
        self.connect_signals()
    
    def connect_signals(self):
        """Kết nối các signal từ view"""
        if hasattr(self.view, 'btnLogin'):
            self.view.btnLogin.clicked.connect(self.login)
        if hasattr(self.view, 'btnRegister'):
            self.view.btnRegister.clicked.connect(self.show_register)
        if hasattr(self.view, 'btnExit'):
            self.view.btnExit.clicked.connect(self.view.close)
        if hasattr(self.view, 'lblForgotPassword'):
            self.view.lblForgotPassword.mousePressEvent = lambda e: self.show_forgot_password()
    
    def login(self):
        """Xử lý đăng nhập"""
        global current_user
        
        username = self.view.txtUsername.text().strip()
        password = self.view.txtPassword.text()
        
        if not username or not password:
            QMessageBox.warning(self.view, "Cảnh báo", "Vui lòng nhập tài khoản và mật khẩu!")
            return
        
        # Tìm employee từ database
        employee = Employee.get_by_username(username)
        
        # Fallback cho admin account test
        if not employee and username == "admin" and password == "admin123":
            QMessageBox.information(self.view, "Thông báo", 
                "Tài khoản admin test được sử dụng. Vui lòng tạo tài khoản thực trong quản lý nhân viên.")
            # Tạo một employee object tạm thời
            from dataclasses import replace
            employee = Employee(
                employee_id="ADM001",
                full_name="Admin (Test)",
                role="Admin",
                username="admin",
                password="admin123",
                status="Đang làm",
                email="admin@system.local"
            )
            current_user = employee
            self.view.accept()
            return
        
        if not employee:
            QMessageBox.warning(self.view, "Lỗi", "Tài khoản không tồn tại!")
            return
        
        # Kiểm tra mật khẩu
        if employee.password != password:
            QMessageBox.warning(self.view, "Lỗi", "Mật khẩu không đúng!")
            return
        
        # Kiểm tra trạng thái nhân viên
        if employee.status != "Đang làm":
            QMessageBox.warning(self.view, "Lỗi", f"Nhân viên này đang ở trạng thái: {employee.status}")
            return
        
        # Lưu user hiện tại vào biến global
        current_user = employee
        self.view.accept()
    
    def show_register(self):
        """Hiển thị màn hình đăng ký"""
        if hasattr(self.view, 'show_register_dialog'):
            self.view.show_register_dialog()
    
    def show_forgot_password(self):
        """Hiển thị dialog quên mật khẩu"""
        if hasattr(self.view, 'show_forgot_password_dialog'):
            self.view.show_forgot_password_dialog()


class RegisterAuthController:
    """Controller xử lý logic đăng ký"""
    
    def __init__(self, view):
        self.view = view
        self.connect_signals()
    
    def connect_signals(self):
        """Kết nối các signal từ view"""
        if hasattr(self.view, 'btnRegister'):
            self.view.btnRegister.clicked.connect(self.register)
        if hasattr(self.view, 'btnCancel'):
            self.view.btnCancel.clicked.connect(self.on_cancel)
        if hasattr(self.view, 'btnLogin'):
            self.view.btnLogin.clicked.connect(self.on_back_to_login)
    
    def register(self):
        """Xử lý đăng ký"""
        username = self.view.txtUsername.text().strip()
        password = self.view.txtPassword.text()
        confirm = self.view.txtConfirmPassword.text()
        
        if not username:
            QMessageBox.warning(self.view, "Lỗi", "Vui lòng nhập tên đăng nhập!")
            return
        if not password:
            QMessageBox.warning(self.view, "Lỗi", "Vui lòng nhập mật khẩu!")
            return
        if password != confirm:
            QMessageBox.warning(self.view, "Lỗi", "Mật khẩu xác nhận không khớp!")
            return
        
        QMessageBox.information(self.view, "Thành công", f"Đăng ký tài khoản '{username}' thành công!")
        self.on_cancel()
    
    def on_cancel(self):
        """Xử lý khi ấn nút Hủy"""
        self.view.reject()
    
    def on_back_to_login(self):
        """Xử lý khi ấn nút 'Đã có tài khoản đăng nhập ngay'"""
        self.view.reject()
