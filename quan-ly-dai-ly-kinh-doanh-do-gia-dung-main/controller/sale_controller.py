from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QInputDialog, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtCore import Qt
from models.product import Product
from models.order import Order
from models.customer import Customer


class SaleController:
    """Controller xử lý logic bán hàng"""

    def __init__(self, view):
        self.view = view
        self.cart = []
        self.selected_product = None
        self.setup_connections()
        self.load_products()
        self.refresh_cart_table()

    def setup_connections(self):
        if hasattr(self.view, "btnSearchProduct"):
            self.view.btnSearchProduct.clicked.connect(self.search_products)

        if hasattr(self.view, "txtProductSearch"):
            self.view.txtProductSearch.textChanged.connect(self.search_products)

        if hasattr(self.view, "tableProducts"):
            self.view.tableProducts.itemSelectionChanged.connect(self.on_product_selected)
            self.view.tableProducts.cellDoubleClicked.connect(self.on_product_double_clicked)
            self.view.tableProducts.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.view.tableProducts.setSelectionMode(QAbstractItemView.SingleSelection)
            self.view.tableProducts.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.view.tableProducts.setAlternatingRowColors(True)
            self.view.tableProducts.setShowGrid(True)

        if hasattr(self.view, "tableCart"):
            self.view.tableCart.itemSelectionChanged.connect(self.on_cart_selected)
            self.view.tableCart.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.view.tableCart.setSelectionMode(QAbstractItemView.SingleSelection)
            self.view.tableCart.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.view.tableCart.setAlternatingRowColors(True)
            self.view.tableCart.setShowGrid(True)

        if hasattr(self.view, "btnAddToCart"):
            self.view.btnAddToCart.clicked.connect(self.add_to_cart)

        if hasattr(self.view, "btnRemoveFromCart"):
            self.view.btnRemoveFromCart.clicked.connect(self.remove_from_cart)

        if hasattr(self.view, "btnClearCart"):
            self.view.btnClearCart.clicked.connect(self.clear_cart)

        if hasattr(self.view, "btnCheckout"):
            self.view.btnCheckout.clicked.connect(self.checkout)

    def load_products(self):
        try:
            products = Product.get_all()
            self.display_products(products)
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể tải sản phẩm: {str(e)}")

    def search_products(self):
        if not hasattr(self.view, "txtProductSearch"):
            self.load_products()
            return

        keyword = self.view.txtProductSearch.text().strip()
        try:
            if keyword:
                products = Product.search(keyword)
            else:
                products = Product.get_all()
            self.display_products(products)
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể tìm kiếm sản phẩm: {str(e)}")

    def display_products(self, products):
        if not hasattr(self.view, "tableProducts"):
            return

        table = self.view.tableProducts
        table.clear()
        table.setRowCount(len(products))
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Mã SP", "Tên sản phẩm", "Giá bán", "Số lượng tồn", "Đơn vị", "Thương hiệu"
        ])

        for row, product in enumerate(products):
            table.setItem(row, 0, QTableWidgetItem(product.product_id))
            table.setItem(row, 1, QTableWidgetItem(product.name))
            table.setItem(row, 2, QTableWidgetItem(self.format_currency(product.selling_price)))
            table.setItem(row, 3, QTableWidgetItem(str(product.quantity)))
            table.setItem(row, 4, QTableWidgetItem(product.unit))
            table.setItem(row, 5, QTableWidgetItem(product.brand))

        table.resizeColumnsToContents()
        self.selected_product = None

    def on_product_selected(self):
        if not hasattr(self.view, "tableProducts"):
            return

        current_row = self.view.tableProducts.currentRow()
        self.selected_product = None
        if current_row >= 0:
            product_id = self.view.tableProducts.item(current_row, 0).text()
            self.selected_product = Product.get_by_id(product_id)

    def on_cart_selected(self):
        if not hasattr(self.view, "tableCart"):
            return
        self.view.tableCart.currentRow()

    def on_product_double_clicked(self, row, column):
        self.on_product_selected()
        self.add_to_cart()

    def add_to_cart(self):
        if not self.selected_product:
            QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn sản phẩm để thêm vào giỏ.")
            return

        if self.selected_product.quantity <= 0:
            QMessageBox.warning(None, "Cảnh báo", "Sản phẩm đã hết hàng.")
            return

        quantity, ok = QInputDialog.getInt(
            None,
            "Số lượng",
            f"Nhập số lượng cho sản phẩm {self.selected_product.name}:",
            1,
            1,
            self.selected_product.quantity,
            1,
        )
        if not ok:
            return

        cart_item = next((item for item in self.cart if item["product"].product_id == self.selected_product.product_id), None)
        if cart_item:
            cart_item["quantity"] += quantity
        else:
            self.cart.append({"product": self.selected_product, "quantity": quantity})

        self.refresh_cart_table()

    def refresh_cart_table(self):
        if not hasattr(self.view, "tableCart"):
            return

        table = self.view.tableCart
        table.clear()
        table.setRowCount(len(self.cart))
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "Mã SP", "Tên sản phẩm", "Đơn giá", "Số lượng", "Thành tiền"
        ])

        for row, item in enumerate(self.cart):
            product = item["product"]
            quantity = item["quantity"]
            total_price = product.selling_price * quantity

            table.setItem(row, 0, QTableWidgetItem(product.product_id))
            table.setItem(row, 1, QTableWidgetItem(product.name))
            price_item = QTableWidgetItem(self.format_currency(product.selling_price))
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 2, price_item)
            qty_item = QTableWidgetItem(str(quantity))
            qty_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 3, qty_item)
            total_item = QTableWidgetItem(self.format_currency(total_price))
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 4, total_item)

        table.resizeColumnsToContents()
        self.update_totals()

    def remove_from_cart(self):
        if not hasattr(self.view, "tableCart"):
            return

        current_row = self.view.tableCart.currentRow()
        if current_row < 0 or current_row >= len(self.cart):
            QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn mục trong giỏ để xóa.")
            return

        self.cart.pop(current_row)
        self.refresh_cart_table()

    def clear_cart(self):
        if not self.cart:
            QMessageBox.information(None, "Thông báo", "Giỏ hàng đang trống.")
            return

        reply = QMessageBox.question(
            None,
            "Xác nhận",
            "Bạn có chắc muốn xóa toàn bộ giỏ hàng?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.cart.clear()
            self.refresh_cart_table()

    def select_customer(self, customer_name):
        """Chọn khách hàng khi có nhiều khách cùng tên
        Trả về (customer, customer_phone) hoặc (None, "")"""
        customers = Customer.get_all_by_name(customer_name)
        
        if len(customers) == 0:
            # Không tìm thấy khách hàng, hỏi có nhập SĐT không
            reply = QMessageBox.question(
                None,
                "Khách hàng không tồn tại",
                f"Không tìm thấy khách hàng tên '{customer_name}'.\n\nBạn có muốn nhập SĐT để tìm khách hàng không?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                phone, ok = QInputDialog.getText(None, "Tìm khách hàng", "Nhập SĐT khách hàng:")
                if ok and phone.strip():
                    phone = phone.strip()
                    # Tìm khách hàng theo SĐT
                    all_customers = Customer.search(phone)
                    for c in all_customers:
                        if c.phone == phone:
                            return c, phone
            return None, ""
        
        elif len(customers) == 1:
            # Chỉ có một khách hàng cùng tên
            customer = customers[0]
            return customer, customer.phone
        
        else:
            # Có nhiều khách hàng cùng tên, hỏi người dùng chọn
            dialog = QDialog(None)
            dialog.setWindowTitle("Chọn khách hàng")
            dialog.setGeometry(100, 100, 500, 300)
            
            layout = QVBoxLayout()
            layout.addWidget(QLabel(f"Có {len(customers)} khách hàng tên '{customer_name}'.\nVui lòng chọn khách hàng:"))
            
            # Tạo button cho mỗi khách hàng
            buttons = []
            selected_customer = [None]  # Sử dụng list để lưu giữ giá trị trong scope
            
            def select(customer):
                selected_customer[0] = customer
                dialog.accept()
            
            for customer in customers:
                btn_text = f"{customer.name} - SĐT: {customer.phone if customer.phone else 'Không có'}"
                btn = QPushButton(btn_text)
                btn.clicked.connect(lambda checked, c=customer: select(c))
                buttons.append(btn)
                layout.addWidget(btn)
            
            # Button Hủy
            btn_cancel = QPushButton("Hủy")
            btn_cancel.clicked.connect(dialog.reject)
            layout.addWidget(btn_cancel)
            
            dialog.setLayout(layout)
            result = dialog.exec_()
            
            if result == QDialog.Accepted and selected_customer[0]:
                customer = selected_customer[0]
                return customer, customer.phone
            else:
                return None, ""

    def checkout(self):
        if not self.cart:
            QMessageBox.warning(None, "Cảnh báo", "Giỏ hàng trống. Vui lòng thêm sản phẩm trước khi thanh toán.")
            return

        total = self.calculate_total()

        # Nhập tên khách hàng
        customer_name, ok = QInputDialog.getText(None, "Thông tin khách hàng", "Nhập tên khách hàng:")
        if not ok or not customer_name.strip():
            return

        customer_name = customer_name.strip()
        
        # Tìm và chọn khách hàng (xử lý trường hợp có nhiều khách cùng tên)
        customer, customer_phone = self.select_customer(customer_name)
        if customer is None and not customer_phone:
            # Nếu không tìm thấy, hỏi có tạo khách hàng mới không
            reply = QMessageBox.question(
                None,
                "Tạo khách hàng mới",
                f"Khách hàng '{customer_name}' không tồn tại.\n\nBạn có muốn tạo khách hàng mới không?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                phone, ok = QInputDialog.getText(None, "Tạo khách hàng mới", "Nhập SĐT khách hàng (hoặc để trống):")
                if ok:
                    phone = phone.strip() if ok else ""
                    Customer.create(customer_name, phone)
                    customer_phone = phone
                else:
                    return
            else:
                return
        
        # Tính nợ cũ của khách hàng
        old_debt = Order.get_customer_debt(customer_name)
        
        # Hiển thị thông tin khách hàng và nợ cũ
        info_message = f"Tên khách hàng: {customer_name}\n"
        if customer_phone:
            info_message += f"SĐT: {customer_phone}\n"
        if old_debt > 0:
            info_message += f"Nợ cũ: {self.format_currency(old_debt)}\n"
        info_message += f"Tổng hóa đơn hiện tại: {self.format_currency(total)}"
        
        # Nhập ID nhân viên
        employee_id, ok = QInputDialog.getText(None, "Thông tin nhân viên", "Nhập ID nhân viên:")
        if not ok or not employee_id.strip():
            return

        employee_id = employee_id.strip()
        
        # Xử lý thanh toán nợ cũ
        amount_paid_for_old_debt = 0
        if old_debt > 0:
            reply = QMessageBox.question(
                None,
                "Thanh toán nợ cũ",
                f"{info_message}\n\nKhách hàng có nợ: {self.format_currency(old_debt)}\n\nBạn có muốn khách hàng thanh toán nợ cũ không?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                # Hỏi số tiền thanh toán cho nợ cũ
                amount_str, ok = QInputDialog.getText(None, "Thanh toán nợ cũ", f"Nhập số tiền thanh toán nợ cũ (tối đa {self.format_currency(old_debt)}):")
                if ok and amount_str.strip():
                    try:
                        amount_paid_for_old_debt = float(amount_str.replace(" VNĐ", "").replace(",", ""))
                        if amount_paid_for_old_debt > old_debt:
                            QMessageBox.warning(None, "Lỗi", f"Số tiền không thể vượt quá nợ cũ: {self.format_currency(old_debt)}")
                            return
                        if amount_paid_for_old_debt < 0:
                            QMessageBox.warning(None, "Lỗi", "Số tiền phải lớn hơn 0")
                            return
                    except ValueError:
                        QMessageBox.warning(None, "Lỗi", "Vui lòng nhập số tiền hợp lệ")
                        return
        
        # Nhập số tiền trả cho hóa đơn hiện tại
        amount_paid_str, ok = QInputDialog.getText(
            None, 
            "Thanh toán hóa đơn hiện tại", 
            f"Nhập số tiền khách hàng trả (Tổng: {self.format_currency(total)}):"
        )
        if not ok or not amount_paid_str.strip():
            return
        
        try:
            amount_paid = float(amount_paid_str.replace(" VNĐ", "").replace(",", ""))
            if amount_paid < 0:
                QMessageBox.warning(None, "Lỗi", "Số tiền phải lớn hơn hoặc bằng 0")
                return
        except ValueError:
            QMessageBox.warning(None, "Lỗi", "Vui lòng nhập số tiền hợp lệ")
            return
        
        # Tính nợ mới từ hóa đơn hiện tại
        debt_current_order = max(0, total - amount_paid)
        
        # Xác nhận thanh toán
        confirm_message = f"Xác nhận thanh toán:\n\n{info_message}"
        confirm_message += f"\nSố tiền khách trả: {self.format_currency(amount_paid)}"
        if debt_current_order > 0:
            confirm_message += f"\nNợ từ hóa đơn này: {self.format_currency(debt_current_order)}"
        if amount_paid_for_old_debt > 0:
            confirm_message += f"\nThanh toán nợ cũ: {self.format_currency(amount_paid_for_old_debt)}"
        confirm_message += f"\n\nBạn có muốn tiếp tục?"
        
        reply = QMessageBox.question(
            None,
            "Xác nhận thanh toán",
            confirm_message,
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            # Thanh toán nợ cũ nếu có
            if amount_paid_for_old_debt > 0:
                unpaid_orders = Order.get_unpaid_orders(customer_name)
                remaining_payment = amount_paid_for_old_debt
                
                for order in unpaid_orders:
                    if remaining_payment <= 0:
                        break
                    current_debt = order.total_amount - order.paid_amount
                    if remaining_payment >= current_debt:
                        # Thanh toán hết hóa đơn này
                        order.update_paid_amount(order.total_amount)
                        remaining_payment -= current_debt
                    else:
                        # Thanh toán một phần hóa đơn này
                        order.update_paid_amount(order.paid_amount + remaining_payment)
                        remaining_payment = 0
            
            # Chuẩn bị dữ liệu items cho hóa đơn mới
            order_items = []
            for item in self.cart:
                order_items.append({
                    "product_id": item["product"].product_id,
                    "product_name": item["product"].name,
                    "quantity": item["quantity"],
                    "unit_price": item["product"].selling_price,
                    "total_price": item["product"].selling_price * item["quantity"]
                })

            # Tạo hóa đơn mới với số tiền đã thanh toán
            order = Order.create(customer_name, customer_phone, employee_id, order_items, total, amount_paid)

            # Cập nhật số lượng sản phẩm
            for item in self.cart:
                product = item["product"]
                product.quantity -= item["quantity"]
                product.update()

            self.cart.clear()
            self.refresh_cart_table()
            self.load_products()
            
            # Thông báo kết quả
            message = f"Đã tạo hóa đơn thành công!\nMã hóa đơn: {order.order_number}\n\n"
            message += f"Tổng: {self.format_currency(total)}\n"
            message += f"Đã trả: {self.format_currency(amount_paid)}\n"
            if debt_current_order > 0:
                message += f"Nợ: {self.format_currency(debt_current_order)}"
            else:
                message += "Trạng thái: Đã thanh toán hết"
            if amount_paid_for_old_debt > 0:
                message += f"\n\nCũng thanh toán nợ cũ: {self.format_currency(amount_paid_for_old_debt)}"
            QMessageBox.information(None, "Thành công", message)
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Thanh toán không thành công: {str(e)}")

    def calculate_total(self):
        return sum(item["product"].selling_price * item["quantity"] for item in self.cart)

    def update_totals(self):
        total = self.calculate_total()
        vat = total * 0.10
        grand_total = total + vat

        if hasattr(self.view, "lblTotal"):
            self.view.lblTotal.setText(self.format_currency(total))
        if hasattr(self.view, "lblVAT"):
            self.view.lblVAT.setText(self.format_currency(vat))
        if hasattr(self.view, "lblGrandTotal"):
            self.view.lblGrandTotal.setText(self.format_currency(grand_total))

    @staticmethod
    def format_currency(value):
        return f"{value:,.0f} VNĐ"
