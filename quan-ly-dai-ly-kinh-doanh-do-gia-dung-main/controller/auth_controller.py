from PyQt5.QtWidgets import QMessageBox


class AuthController:
    """Controller xử lý logic xác thực (đăng nhập/đăng ký)"""
    
    def __init__(self, view, login_callback=None):
        self.view = view
        self.login_callback = login_callback
        self.connect_signals()
    
    def connect_signals(self):
        """Kết nối các signal từ view"""
        # Kiểm tra loại dialog
        if hasattr(self.view, 'btnLogin'):
            # Login dialog
            self.view.btnLogin.clicked.connect(self.login)
            self.view.btnRegister.clicked.connect(self.open_register)
            self.view.btnExit.clicked.connect(self.view.close)
        elif hasattr(self.view, 'btnRegister'):
            # Register dialog
            self.view.btnRegister.clicked.connect(self.register)
            self.view.btnCancel.clicked.connect(self.view.close)
            self.view.btnLogin.clicked.connect(self.back_to_login)
    
    def login(self):
        """Xử lý đăng nhập"""
        username = self.view.txtUsername.text().strip()
        password = self.view.txtPassword.text()
        
        if username and password:
            # TODO: Kiểm tra database
            if username == "admin" and password == "admin123":
                self.view.accept()
            else:
                QMessageBox.warning(self.view, "Lỗi", "Tài khoản hoặc mật khẩu không đúng!")
        else:
            QMessageBox.warning(self.view, "Cảnh báo", "Vui lòng nhập tài khoản và mật khẩu!")
    
    def open_register(self):
        """Mở màn hình đăng ký"""
        # Import ở đây để tránh vòng import
        from main import RegisterDialog
        self.register_dialog = RegisterDialog(login_callback=self.view.show)
        self.view.hide()
        self.register_dialog.exec()
    
    def register(self):
        """Xử lý đăng ký"""
        username = self.view.txtUsername.text().strip()
        password = self.view.txtPassword.text()
        confirm = self.view.txtConfirmPassword.text()
        full_name = self.view.txtFullName.text().strip()
        
        # Validation
        if not username:
            QMessageBox.warning(self.view, "Lỗi", "Vui lòng nhập tên đăng nhập!")
            return
        
        if not password:
            QMessageBox.warning(self.view, "Lỗi", "Vui lòng nhập mật khẩu!")
            return
        
        if password != confirm:
            QMessageBox.warning(self.view, "Lỗi", "Mật khẩu xác nhận không khớp!")
            return
        
        if not full_name:
            QMessageBox.warning(self.view, "Lỗi", "Vui lòng nhập họ tên!")
            return
        
        # TODO: Lưu vào database
        QMessageBox.information(self.view, "Thành công", f"Đăng ký thành công!\nChào mừng {full_name}!")
        self.back_to_login()
    
    def back_to_login(self):
        """Quay lại màn hình đăng nhập"""
        self.view.close()
        if self.login_callback:
            self.login_callback()