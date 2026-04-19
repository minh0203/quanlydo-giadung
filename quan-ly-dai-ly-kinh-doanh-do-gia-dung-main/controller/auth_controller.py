from PyQt5.QtWidgets import QMessageBox


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
    
    def login(self):
        """Xử lý đăng nhập"""
        username = self.view.txtUsername.text().strip()
        password = self.view.txtPassword.text()
        
        if username and password:
            if username == "admin" and password == "admin123":
                self.view.accept()
            else:
                QMessageBox.warning(self.view, "Lỗi", "Tài khoản hoặc mật khẩu không đúng!")
        else:
            QMessageBox.warning(self.view, "Cảnh báo", "Vui lòng nhập tài khoản và mật khẩu!")
    
    def show_register(self):
        """Hiển thị màn hình đăng ký"""
        if hasattr(self.view, 'show_register_dialog'):
            self.view.show_register_dialog()


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