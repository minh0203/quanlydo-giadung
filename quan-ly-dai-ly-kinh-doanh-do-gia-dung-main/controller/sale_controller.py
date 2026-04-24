from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QSpinBox, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
from models.product import Product
from models.customer import Customer
from models.sale_order import SaleOrder
from models.database import Database
from datetime import datetime


class SaleController:
    """Controller xử lý logic bán hàng"""
    
    VAT_RATE = 0.10  # 10% VAT
    
    def __init__(self, view):
        self.view = view
        self.cart_items = []  # Lưu items trong giỏ hàng (product_id, quantity, unit_price)
        self.setup_connections()
        self.load_products()
        self.update_cart_display()

    def setup_connections(self):
        """Thiết lập kết nối các signal"""
        # Kết nối nút tìm kiếm sản phẩm
        if hasattr(self.view, "btnSearchProduct"):
            self.view.btnSearchProduct.clicked.connect(self.search_products)
        
        # Kết nối ô tìm kiếm sản phẩm
        if hasattr(self.view, "txtProductSearch"):
            self.view.txtProductSearch.textChanged.connect(self.on_search_text_changed)
        
        # Kết nối nút thêm vào giỏ hàng
        if hasattr(self.view, "btnAddToCart"):
            self.view.btnAddToCart.clicked.connect(self.add_to_cart)
        
        # Kết nối nút xóa khỏi giỏ hàng
        if hasattr(self.view, "btnRemoveFromCart"):
            self.view.btnRemoveFromCart.clicked.connect(self.remove_from_cart)
        
        # Kết nối nút xóa giỏ hàng
        if hasattr(self.view, "btnClearCart"):
            self.view.btnClearCart.clicked.connect(self.clear_cart)
        
        # Kết nối nút thanh toán
        if hasattr(self.view, "btnCheckout"):
            self.view.btnCheckout.clicked.connect(self.checkout)
        
        # Kết nối bảng giỏ hàng để cập nhật khi thay đổi quantity
        if hasattr(self.view, "tableCart"):
            self.view.tableCart.itemChanged.connect(self.on_cart_item_changed)

    def load_products(self):
        """Tải danh sách sản phẩm"""
        try:
            products = Product.get_all()
            self.display_products(products)
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể tải danh sách sản phẩm: {str(e)}")

    def display_products(self, products):
        """Hiển thị danh sách sản phẩm lên bảng"""
        if not hasattr(self.view, "tableProducts"):
            return

        table = self.view.tableProducts
        table.setRowCount(len(products))
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "Mã SP", "Tên sản phẩm", "Giá bán", "Số lượng", "Đơn vị"
        ])

        for row, product in enumerate(products):
            table.setItem(row, 0, QTableWidgetItem(product.product_id))
            table.setItem(row, 1, QTableWidgetItem(product.name))
            table.setItem(row, 2, QTableWidgetItem(f"{product.selling_price:,.0f}"))
            table.setItem(row, 3, QTableWidgetItem(str(product.quantity)))
            table.setItem(row, 4, QTableWidgetItem(product.unit))

        # Điều chỉnh kích thước cột
        table.resizeColumnsToContents()

    def search_products(self):
        """Tìm kiếm sản phẩm"""
        if not hasattr(self.view, "txtProductSearch"):
            return
        
        keyword = self.view.txtProductSearch.text().strip()
        if not keyword:
            self.load_products()
            return
        
        try:
            products = Product.search(keyword)
            self.display_products(products)
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Lỗi tìm kiếm: {str(e)}")

    def on_search_text_changed(self):
        """Xử lý khi text tìm kiếm thay đổi"""
        self.search_products()

    def add_to_cart(self):
        """Thêm sản phẩm được chọn vào giỏ hàng"""
        if not hasattr(self.view, "tableProducts"):
            QMessageBox.warning(None, "Cảnh báo", "Không tìm thấy bảng sản phẩm")
            return
        
        table = self.view.tableProducts
        selected_rows = table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn sản phẩm!")
            return
        
        # Mở dialog nhập số lượng
        for index in selected_rows:
            row = index.row()
            product_id = table.item(row, 0).text()
            product_name = table.item(row, 1).text()
            price_text = table.item(row, 2).text().replace(",", "")
            try:
                unit_price = float(price_text)
            except:
                unit_price = 0
            
            # Tạo dialog nhập số lượng
            quantity = self.show_quantity_dialog(product_name)
            if quantity and quantity > 0:
                # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
                existing_item = None
                for item in self.cart_items:
                    if item[0] == product_id:
                        existing_item = item
                        break
                
                if existing_item:
                    # Cập nhật số lượng
                    self.cart_items[self.cart_items.index(existing_item)] = (
                        product_id, 
                        existing_item[1] + quantity, 
                        unit_price
                    )
                else:
                    # Thêm sản phẩm mới
                    self.cart_items.append((product_id, quantity, unit_price))
                
                self.update_cart_display()

    def show_quantity_dialog(self, product_name):
        """Hiển thị dialog nhập số lượng"""
        dialog = QDialog(self.view)
        dialog.setWindowTitle("Nhập số lượng")
        dialog.setGeometry(100, 100, 300, 150)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Sản phẩm: {product_name}"))
        layout.addWidget(QLabel("Số lượng:"))
        
        spinbox = QSpinBox()
        spinbox.setMinimum(1)
        spinbox.setMaximum(10000)
        spinbox.setValue(1)
        layout.addWidget(spinbox)
        
        button_layout = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Hủy")
        button_layout.addWidget(btn_ok)
        button_layout.addWidget(btn_cancel)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        result = None
        def on_ok():
            nonlocal result
            result = spinbox.value()
            dialog.accept()
        
        btn_ok.clicked.connect(on_ok)
        btn_cancel.clicked.connect(dialog.reject)
        
        dialog.exec_()
        return result

    def remove_from_cart(self):
        """Xóa sản phẩm được chọn khỏi giỏ hàng"""
        if not hasattr(self.view, "tableCart"):
            return
        
        table = self.view.tableCart
        selected_rows = table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn sản phẩm trong giỏ hàng!")
            return
        
        for index in sorted(selected_rows, reverse=True):
            row = index.row()
            if row < len(self.cart_items):
                self.cart_items.pop(row)
        
        self.update_cart_display()

    def clear_cart(self):
        """Xóa toàn bộ giỏ hàng"""
        if not self.cart_items:
            QMessageBox.information(None, "Thông báo", "Giỏ hàng đã trống!")
            return
        
        reply = QMessageBox.question(None, "Xác nhận", "Bạn có chắc muốn xóa toàn bộ giỏ hàng?")
        if reply == QMessageBox.Yes:
            self.cart_items = []
            self.update_cart_display()

    def on_cart_item_changed(self, item):
        """Xử lý khi item trong giỏ hàng thay đổi"""
        if not hasattr(self.view, "tableCart"):
            return
        
        table = self.view.tableCart
        row = table.row(item)
        col = table.column(item)
        
        # Cập nhật số lượng nếu thay đổi cột quantity (cột 2)
        if col == 2 and row < len(self.cart_items):
            try:
                new_quantity = int(item.text())
                if new_quantity <= 0:
                    raise ValueError("Số lượng phải lớn hơn 0")
                
                product_id, _, unit_price = self.cart_items[row]
                self.cart_items[row] = (product_id, new_quantity, unit_price)
                self.update_cart_display()
            except ValueError as e:
                QMessageBox.warning(None, "Lỗi", f"Số lượng không hợp lệ: {str(e)}")
                self.update_cart_display()

    def update_cart_display(self):
        """Cập nhật hiển thị giỏ hàng"""
        if not hasattr(self.view, "tableCart"):
            return
        
        table = self.view.tableCart
        table.setRowCount(len(self.cart_items))
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels([
            "Mã SP", "Số lượng", "Đơn giá", "Thành tiền"
        ])

        total_amount = 0
        for row, (product_id, quantity, unit_price) in enumerate(self.cart_items):
            line_total = quantity * unit_price
            total_amount += line_total
            
            table.setItem(row, 0, QTableWidgetItem(product_id))
            
            qty_item = QTableWidgetItem(str(quantity))
            qty_item.setFlags(qty_item.flags() | Qt.ItemIsEditable)
            table.setItem(row, 2, qty_item)
            
            table.setItem(row, 1, QTableWidgetItem(f"{unit_price:,.0f}"))
            table.setItem(row, 3, QTableWidgetItem(f"{line_total:,.0f}"))

        # Điều chỉnh kích thước cột
        table.resizeColumnsToContents()
        
        # Cập nhật tổng tiền
        self.update_totals(total_amount)

    def update_totals(self, total_amount):
        """Cập nhật tổng tiền, VAT và tổng cộng"""
        vat_amount = total_amount * self.VAT_RATE
        grand_total = total_amount + vat_amount
        
        if hasattr(self.view, "lblTotal"):
            self.view.lblTotal.setText(f"{total_amount:,.0f} VNĐ")
        
        if hasattr(self.view, "lblVAT"):
            self.view.lblVAT.setText(f"{vat_amount:,.0f} VNĐ")
        
        if hasattr(self.view, "lblGrandTotal"):
            self.view.lblGrandTotal.setText(f"{grand_total:,.0f} VNĐ")
        
        # Lưu giá trị để dùng trong checkout
        self.current_total = total_amount
        self.current_vat = vat_amount
        self.current_grand_total = grand_total

    def checkout(self):
        """Thanh toán và lưu đơn hàng"""
        if not self.cart_items:
            QMessageBox.warning(None, "Cảnh báo", "Giỏ hàng trống! Vui lòng thêm sản phẩm.")
            return
        
        # Mở dialog chọn khách hàng
        customer = self.show_customer_selection_dialog()
        if not customer:
            return
        
        try:
            # Tạo đơn hàng
            order = SaleOrder.create(
                customer_id=customer.customer_id,
                order_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                total_amount=self.current_total,
                vat_amount=self.current_vat,
                grand_total=self.current_grand_total,
                notes=""
            )
            
            # Thêm chi tiết đơn hàng
            for product_id, quantity, unit_price in self.cart_items:
                SaleOrder.add_detail(order.order_id, product_id, quantity, unit_price)
                
                # Cập nhật số lượng sản phẩm trong kho
                product = Product.get_by_id(product_id)
                if product:
                    product.quantity -= quantity
                    product.update()
            
            QMessageBox.information(None, "Thành công", f"Đã lưu đơn hàng thành công!\nMã đơn hàng: {order.order_id}")
            
            # Xóa giỏ hàng
            self.cart_items = []
            self.update_cart_display()
            self.load_products()
            
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể lưu đơn hàng: {str(e)}")

    def show_customer_selection_dialog(self):
        """Hiển thị dialog chọn khách hàng"""
        try:
            customers = Customer.get_all()
            if not customers:
                QMessageBox.warning(None, "Cảnh báo", "Không có khách hàng nào! Vui lòng thêm khách hàng trước.")
                return None
            
            dialog = QDialog(self.view)
            dialog.setWindowTitle("Chọn khách hàng")
            dialog.setGeometry(100, 100, 500, 400)
            
            layout = QVBoxLayout()
            layout.addWidget(QLabel("Chọn khách hàng:"))
            
            # Tạo bảng chọn khách hàng
            from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
            table = QTableWidget()
            table.setRowCount(len(customers))
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["Mã KH", "Tên khách hàng", "Điện thoại"])
            
            for row, customer in enumerate(customers):
                table.setItem(row, 0, QTableWidgetItem(customer.customer_id))
                table.setItem(row, 1, QTableWidgetItem(customer.name))
                table.setItem(row, 2, QTableWidgetItem(customer.phone))
            
            table.resizeColumnsToContents()
            layout.addWidget(table)
            
            button_layout = QHBoxLayout()
            btn_ok = QPushButton("Chọn")
            btn_cancel = QPushButton("Hủy")
            button_layout.addWidget(btn_ok)
            button_layout.addWidget(btn_cancel)
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            
            selected_customer = None
            def on_ok():
                nonlocal selected_customer
                selected_rows = table.selectionModel().selectedRows()
                if not selected_rows:
                    QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn khách hàng!")
                    return
                row = selected_rows[0].row()
                selected_customer = customers[row]
                dialog.accept()
            
            btn_ok.clicked.connect(on_ok)
            btn_cancel.clicked.connect(dialog.reject)
            
            dialog.exec_()
            return selected_customer
            
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Lỗi khi lấy danh sách khách hàng: {str(e)}")
            return None
