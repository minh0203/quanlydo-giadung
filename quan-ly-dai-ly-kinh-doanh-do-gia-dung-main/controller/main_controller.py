from PyQt5.QtWidgets import QWidget, QMessageBox

# Import UI classes
from ui.employee_management import Ui_EmployeeManagement
from ui.product_management import Ui_ProductManagement
from ui.customer_management import Ui_CustomerManagement
from ui.sale_order import Ui_SaleOrder
from ui.import_goods import Ui_ImportGoods
from ui.report_viewer import Ui_ReportViewer
from ui.shift_schedule import Ui_ShiftSchedule
from ui.attendance import Ui_Attendance
from ui.OrderManagement import Ui_OrderManagement
from ui.WarrantyManagement import Ui_WarrantyManagement
from ui.SupplierManagement import Ui_SupplierManagement
from ui.InventoryReport import Ui_InventoryReport

# Import controllers
from controller.employee_controller import EmployeeController
from controller.product_controller import ProductController
from controller.customer_controller import CustomerController
from controller.sale_controller import SaleController
from controller.import_controller import ImportController
from controller.report_controller import ReportController
from controller.shift_controller import ShiftController
from controller.attendance_controller import AttendanceController
from controller.order_controller import OrderController
from controller.warranty_controller import WarrantyController
from controller.supplier_controller import SupplierController
from controller.inventory_report_controller import InventoryReportController


class MainController:
    """Controller chính xử lý logic ứng dụng"""
    
    def __init__(self, view, current_user):
        self.view = view
        self.current_user = current_user
        self.modules = {}
        self.controllers = {}
        self.setup_modules()
        self.connect_signals()
    
    def setup_modules(self):
        """Thiết lập các module và controller"""
        modules_config = [
            ("employee", Ui_EmployeeManagement, EmployeeController, 0),
            ("product", Ui_ProductManagement, ProductController, 1),
            ("customer", Ui_CustomerManagement, CustomerController, 2),
            ("sale", Ui_SaleOrder, SaleController, 3),
            ("import", Ui_ImportGoods, ImportController, 4),
            ("report", Ui_ReportViewer, ReportController, 5),
            ("shift", Ui_ShiftSchedule, ShiftController, 6),
            ("attendance", Ui_Attendance, AttendanceController, 7),
            ("order", Ui_OrderManagement, OrderController, 8),
            ("warranty", Ui_WarrantyManagement, WarrantyController, 9),
            ("supplier", Ui_SupplierManagement, SupplierController, 10),
            ("inventory_report", Ui_InventoryReport, InventoryReportController, 11),
        ]
        
        for name, ui_class, controller_class, index in modules_config:
            # Tạo widget và UI
            widget = QWidget()
            ui = ui_class()
            ui.setupUi(widget)
            
            # Lưu widget
            self.modules[name] = {"widget": widget, "ui": ui, "index": index}
            
            # Thêm vào stacked widget
            self.view.stacked_widget.addWidget(widget)
            
            # Tạo controller
            try:
                self.controllers[name] = controller_class(ui)
            except:
                # Nếu controller chưa implement, tạo placeholder
                self.controllers[name] = None
    
    def connect_signals(self):
        """Kết nối các signal từ menu"""
        self.view.actionProducts.triggered.connect(lambda: self.show_module("product"))
        self.view.actionCustomers.triggered.connect(lambda: self.show_module("customer"))
        self.view.actionEmployees.triggered.connect(lambda: self.show_module("employee"))
        self.view.actionNewOrder.triggered.connect(lambda: self.show_module("sale"))
        self.view.actionOrderManagement.triggered.connect(lambda: self.show_module("order"))
        self.view.actionWarranty.triggered.connect(lambda: self.show_module("warranty"))
        self.view.actionImportGoods.triggered.connect(lambda: self.show_module("import"))
        self.view.actionSupplierManagement.triggered.connect(lambda: self.show_module("supplier"))
        self.view.actionRevenueReport.triggered.connect(lambda: self.show_module("report"))
        self.view.actionInventoryReport.triggered.connect(lambda: self.show_module("inventory_report"))
        
        # Kết nối các action người dùng
        if hasattr(self.view, 'actionChangePassword'):
            self.view.actionChangePassword.triggered.connect(self.on_change_password)
        if hasattr(self.view, 'actionLogout'):
            self.view.actionLogout.triggered.connect(self.on_logout)
        self.view.actionExit.triggered.connect(self.view.close)
    
    def show_module(self, module_name):
        """Hiển thị module theo tên"""
        if module_name in self.modules:
            index = self.modules[module_name]["index"]
            self.view.stacked_widget.setCurrentIndex(index)
            self.view.statusbar.showMessage(f"📋 {module_name.replace('_', ' ').title()}")
            if module_name == "sale" and self.controllers.get("sale"):
                try:
                    self.controllers["sale"].load_products()
                    self.controllers["sale"].refresh_cart_table()
                except Exception:
                    pass
            elif module_name == "order" and self.controllers.get("order"):
                try:
                    self.controllers["order"].load_orders()
                except Exception:
                    pass
    
    def on_change_password(self):
        """Xử lý đổi mật khẩu"""
        try:
            if hasattr(self.view, 'show_change_password_dialog'):
                self.view.show_change_password_dialog()
        except Exception as e:
            QMessageBox.warning(self.view, "Lỗi", f"Không thể mở dialog: {str(e)}")
    
    def on_logout(self):
        """Xử lý đăng xuất"""
        reply = QMessageBox.question(
            self.view, "Xác nhận",
            f"Bạn có chắc muốn đăng xuất?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Đóng cửa sổ chính và quay lại màn đăng nhập
            self.view.close()
            # Phát tín hiệu để ứng dụng biết cần quay lại login
            if hasattr(self.view, 'logout_signal'):
                self.view.logout_signal.emit()