# main.py - Chỉ chạy app, logic xử lý ở controller
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget, QDialog
from PyQt5.QtCore import Qt

# Import UI
from ui.login import Ui_LoginDialog
from ui.register import Ui_RegisterDialog
from ui.main_window import Ui_MainWindow

# Import Controller
from controller.auth_controller import AuthController
from controller.main_controller import MainController


class RegisterDialog(QDialog, Ui_RegisterDialog):
    """Màn hình đăng ký - logic xử lý ở controller"""
    def __init__(self, parent=None, login_callback=None):
        super().__init__(parent)
        self.setupUi(self)
        # Khởi tạo controller
        self.controller = AuthController(self, login_callback)


class LoginDialog(QDialog, Ui_LoginDialog):
    """Màn hình đăng nhập - logic xử lý ở controller"""
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # Khởi tạo controller
        self.controller = AuthController(self)
        
        # Demo: tự động điền thông tin test
        self.txtUsername.setText("admin")
        self.txtPassword.setText("admin123")


class MainWindow(QMainWindow, Ui_MainWindow):
    """Cửa sổ chính - logic xử lý ở controller"""
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Tạo stacked widget
        self.stacked_widget = QStackedWidget()
        self.centralwidget.layout().addWidget(self.stacked_widget)
        
        # Khởi tạo controller (controller sẽ setup các module)
        self.controller = MainController(self)
        
        # Hiển thị module mặc định
        self.stacked_widget.setCurrentIndex(1)  # Product
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