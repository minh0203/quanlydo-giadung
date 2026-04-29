from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QInputDialog
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtCore import Qt
from models.product import Product
from models.order import Order


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

    def checkout(self):
        if not self.cart:
            QMessageBox.warning(None, "Cảnh báo", "Giỏ hàng trống. Vui lòng thêm sản phẩm trước khi thanh toán.")
            return

        total = self.calculate_total()

        # Nhập tên khách hàng
        customer_name, ok = QInputDialog.getText(None, "Thông tin khách hàng", "Nhập tên khách hàng:")
        if not ok or not customer_name.strip():
            return

        # Nhập ID nhân viên (có thể lấy từ session sau này)
        employee_id, ok = QInputDialog.getText(None, "Thông tin nhân viên", "Nhập ID nhân viên:")
        if not ok or not employee_id.strip():
            return

        reply = QMessageBox.question(
            None,
            "Xác nhận thanh toán",
            f"Tên khách hàng: {customer_name}\nID nhân viên: {employee_id}\nTổng thanh toán: {self.format_currency(total)}\n\nBạn có muốn thanh toán?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            # Chuẩn bị dữ liệu items cho hóa đơn
            order_items = []
            for item in self.cart:
                order_items.append({
                    "product_id": item["product"].product_id,
                    "product_name": item["product"].name,
                    "quantity": item["quantity"],
                    "unit_price": item["product"].selling_price,
                    "total_price": item["product"].selling_price * item["quantity"]
                })

            # Tạo hóa đơn
            order = Order.create(customer_name.strip(), "", employee_id.strip(), order_items, total)

            # Cập nhật số lượng sản phẩm
            for item in self.cart:
                product = item["product"]
                product.quantity -= item["quantity"]
                product.update()

            self.cart.clear()
            self.refresh_cart_table()
            self.load_products()
            QMessageBox.information(None, "Thành công", f"Đã thanh toán hóa đơn thành công!\nMã hóa đơn: {order.order_number}")
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
