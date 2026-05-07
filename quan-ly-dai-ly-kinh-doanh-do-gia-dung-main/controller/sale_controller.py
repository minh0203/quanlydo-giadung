from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QInputDialog, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtCore import Qt, QDate
from models.product import Product
from models.order import Order
from models.customer import Customer
from models.warranty import Warranty


class SaleController:
    """Controller xử lý logic bán hàng"""

    def __init__(self, view, current_user=None):
        self.view = view
        self.current_user = current_user
        self.cart = []
        self.selected_product = None
        self.setup_connections()
        self.load_products()
        self.refresh_cart_table()
        self.set_default_employee()

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

        if hasattr(self.view, "txtCustomerName"):
            self.view.txtCustomerName.textChanged.connect(self.update_payment_summary)
            self.view.txtCustomerName.editingFinished.connect(self.on_customer_name_entered)
        if hasattr(self.view, "txtPaidAmount"):
            self.view.txtPaidAmount.textChanged.connect(self.update_payment_summary)
        if hasattr(self.view, "txtOldDebtPayment"):
            self.view.txtOldDebtPayment.textChanged.connect(self.update_payment_summary)

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

    def set_default_employee(self):
        if self.current_user and hasattr(self.view, "txtEmployeeId"):
            self.view.txtEmployeeId.setText(self.current_user.employee_id)

    def get_currency_value(self, text):
        if not text:
            return 0.0
        try:
            cleaned = text.replace(",", "").replace("VNĐ", "").replace(" ", "").strip()
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0

    def get_paid_amount(self):
        if not hasattr(self.view, "txtPaidAmount"):
            return 0.0
        return self.get_currency_value(self.view.txtPaidAmount.text())

    def get_old_debt_payment(self):
        if not hasattr(self.view, "txtOldDebtPayment"):
            return 0.0
        return self.get_currency_value(self.view.txtOldDebtPayment.text())

    def update_payment_summary(self):
        total = self.calculate_total()
        vat = total * 0.10
        grand_total = total + vat
        paid_amount = self.get_paid_amount()
        debt = max(0.0, grand_total - paid_amount)

        if hasattr(self.view, "lblPaid"):
            self.view.lblPaid.setText(self.format_currency(paid_amount))
        if hasattr(self.view, "lblDebt"):
            self.view.lblDebt.setText(self.format_currency(debt))

        status = "Chưa thanh toán"
        if grand_total == 0:
            status = "Chưa thanh toán"
        elif paid_amount >= grand_total:
            status = "Đã thanh toán hết"
        else:
            status = "Còn nợ"

        if hasattr(self.view, "lblPaymentStatus"):
            self.view.lblPaymentStatus.setText(status)

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
        self.update_payment_summary()

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

    def select_customer(self, customer_name, customer_phone=""):
        """Chọn khách hàng khi có nhiều khách cùng tên
        Trả về (customer, customer_phone) hoặc (None, "")"""
        customers = Customer.get_all_by_name(customer_name)

        if customer_phone:
            exact_customer = next((c for c in customers if c.phone == customer_phone), None)
            if exact_customer:
                return exact_customer, exact_customer.phone

        if len(customers) == 0:
            if customer_phone:
                all_customers = Customer.search(customer_phone)
                for c in all_customers:
                    if c.phone == customer_phone:
                        return c, c.phone

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
                    all_customers = Customer.search(phone)
                    for c in all_customers:
                        if c.phone == phone:
                            return c, phone
            return None, ""

        elif len(customers) == 1:
            customer = customers[0]
            return customer, customer.phone or customer_phone

        else:
            if customer_phone:
                exact_customer = next((c for c in customers if c.phone == customer_phone), None)
                if exact_customer:
                    return exact_customer, exact_customer.phone

            dialog = QDialog(None)
            dialog.setWindowTitle("Chọn khách hàng")
            dialog.setGeometry(100, 100, 500, 300)

            layout = QVBoxLayout()
            layout.addWidget(QLabel(f"Có {len(customers)} khách hàng tên '{customer_name}'.\nVui lòng chọn khách hàng:"))

            selected_customer = [None]

            def select(customer):
                selected_customer[0] = customer
                dialog.accept()

            for customer in customers:
                btn_text = f"{customer.name} - SĐT: {customer.phone if customer.phone else 'Không có'}"
                btn = QPushButton(btn_text)
                btn.clicked.connect(lambda checked, c=customer: select(c))
                layout.addWidget(btn)

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

    def set_customer_code(self, customer):
        if hasattr(self.view, "txtCustomerCode"):
            self.view.txtCustomerCode.setText(customer.customer_id if customer else "")

    def on_customer_name_entered(self):
        if not hasattr(self.view, "txtCustomerName") or not hasattr(self.view, "txtCustomerPhone"):
            return

        customer_name = self.view.txtCustomerName.text().strip()
        if not customer_name:
            return

        customer_phone = self.view.txtCustomerPhone.text().strip()
        customers = Customer.get_all_by_name(customer_name)
        if not customers:
            self.set_customer_code(None)
            return

        if len(customers) == 1:
            if not customer_phone and customers[0].phone:
                self.view.txtCustomerPhone.setText(customers[0].phone)
            self.set_customer_code(customers[0])
            return

        if len(customers) > 1 and not customer_phone:
            customer, phone = self.select_customer(customer_name)
            if customer:
                self.view.txtCustomerName.setText(customer.name)
                self.view.txtCustomerPhone.setText(phone or "")
                self.set_customer_code(customer)
            else:
                self.set_customer_code(None)

    def checkout(self):
        if not self.cart:
            QMessageBox.warning(None, "Cảnh báo", "Giỏ hàng trống. Vui lòng thêm sản phẩm trước khi thanh toán.")
            return

        if not hasattr(self.view, "txtCustomerName") or not hasattr(self.view, "txtEmployeeId"):
            QMessageBox.warning(None, "Lỗi", "Thiết lập thanh toán chưa đầy đủ.")
            return

        customer_name = self.view.txtCustomerName.text().strip()
        customer_phone = self.view.txtCustomerPhone.text().strip() if hasattr(self.view, "txtCustomerPhone") else ""
        employee_id = self.view.txtEmployeeId.text().strip()
        amount_paid = self.get_paid_amount()
        amount_paid_for_old_debt = self.get_old_debt_payment()
        total = self.calculate_total()

        if not customer_name:
            QMessageBox.warning(None, "Cảnh báo", "Vui lòng nhập tên khách hàng.")
            return
        if not employee_id:
            QMessageBox.warning(None, "Cảnh báo", "Vui lòng nhập ID nhân viên.")
            return
        if amount_paid < 0 or amount_paid_for_old_debt < 0:
            QMessageBox.warning(None, "Lỗi", "Số tiền phải lớn hơn hoặc bằng 0.")
            return

        customer, customer_phone_from_selection = self.select_customer(customer_name, customer_phone)
        if customer:
            self.set_customer_code(customer)
        if customer is None and not customer_phone:
            reply = QMessageBox.question(
                None,
                "Tạo khách hàng mới",
                f"Khách hàng '{customer_name}' không tồn tại.\n\nBạn có muốn tạo khách hàng mới không?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                phone, ok = QInputDialog.getText(None, "Tạo khách hàng mới", "Nhập SĐT khách hàng (hoặc để trống):")
                if ok:
                    phone = phone.strip() if phone else ""
                    Customer.create(customer_name, phone)
                    customer_phone = phone
                else:
                    return
            else:
                return
        elif customer is not None and not customer_phone:
            customer_phone = customer_phone_from_selection

        old_debt = Order.get_customer_debt(customer_name)
        if old_debt <= 0:
            amount_paid_for_old_debt = 0.0
        elif amount_paid_for_old_debt > old_debt:
            QMessageBox.warning(None, "Lỗi", f"Số tiền thanh toán nợ cũ không thể vượt quá {self.format_currency(old_debt)}")
            return

        vat = total * 0.10
        grand_total = total + vat
        debt_current_order = max(0.0, grand_total - amount_paid)

        info_message = f"Tên khách hàng: {customer_name}\n"
        if customer_phone:
            info_message += f"SĐT: {customer_phone}\n"
        if old_debt > 0:
            info_message += f"Nợ cũ: {self.format_currency(old_debt)}\n"
        info_message += f"Tổng hóa đơn: {self.format_currency(total)}\n"
        info_message += f"Thuế VAT (10%): {self.format_currency(vat)}\n"
        info_message += f"Thành tiền: {self.format_currency(grand_total)}"

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
            if amount_paid_for_old_debt > 0:
                unpaid_orders = Order.get_unpaid_orders(customer_name)
                remaining_payment = amount_paid_for_old_debt
                for order in unpaid_orders:
                    if remaining_payment <= 0:
                        break
                    current_debt = order.total_amount - order.paid_amount
                    if remaining_payment >= current_debt:
                        order.update_paid_amount(order.total_amount)
                        remaining_payment -= current_debt
                    else:
                        order.update_paid_amount(order.paid_amount + remaining_payment)
                        remaining_payment = 0

            order_items = []
            for item in self.cart:
                order_items.append({
                    "product_id": item["product"].product_id,
                    "product_name": item["product"].name,
                    "quantity": item["quantity"],
                    "unit_price": item["product"].selling_price,
                    "total_price": item["product"].selling_price * item["quantity"]
                })

            order = Order.create(customer_name, customer_phone, employee_id, order_items, grand_total, amount_paid)

            for item in self.cart:
                product = item["product"]
                product.quantity -= item["quantity"]
                product.update()

            purchase_date = QDate.currentDate().toString("yyyy-MM-dd")
            for item in self.cart:
                product = item["product"]
                try:
                    expiry_date = QDate.currentDate().addMonths(product.warranty_months).toString("yyyy-MM-dd")
                    Warranty.create(
                        product=product.name,
                        serial=product.product_id,
                        customer_name=customer_name,
                        phone=customer_phone or "",
                        purchase_date=purchase_date,
                        expiry_date=expiry_date,
                        error_description="",
                        note=f"Tạo từ đơn hàng {order.order_number}",
                        status="Còn bảo hành",
                        order_id=order.order_number
                    )
                except Exception as warranty_error:
                    print(f"Cảnh báo: Không thể tạo bảo hành cho {product.name}: {str(warranty_error)}")

            self.cart.clear()
            self.refresh_cart_table()
            self.load_products()
            if hasattr(self.view, "txtCustomerName"):
                self.view.txtCustomerName.clear()
            if hasattr(self.view, "txtCustomerPhone"):
                self.view.txtCustomerPhone.clear()
            if hasattr(self.view, "txtCustomerCode"):
                self.view.txtCustomerCode.clear()
            if hasattr(self.view, "txtPaidAmount"):
                self.view.txtPaidAmount.clear()
            if hasattr(self.view, "txtOldDebtPayment"):
                self.view.txtOldDebtPayment.clear()
            self.set_default_employee()

            message = f"Đã tạo hóa đơn thành công!\nMã hóa đơn: {order.order_number}\n\n"
            message += f"Tổng: {self.format_currency(total)}\n"
            message += f"Thuế VAT (10%): {self.format_currency(vat)}\n"
            message += f"Thành tiền: {self.format_currency(grand_total)}\n"
            message += f"Đã trả: {self.format_currency(amount_paid)}\n"
            if debt_current_order > 0:
                message += f"Nợ: {self.format_currency(debt_current_order)}"
                status = "Còn nợ"
            else:
                message += "Trạng thái: Đã thanh toán hết"
                status = "Đã thanh toán hết"
            if amount_paid_for_old_debt > 0:
                message += f"\n\nCũng thanh toán nợ cũ: {self.format_currency(amount_paid_for_old_debt)}"
                if status == "Còn nợ":
                    status = "Thanh toán nợ cũ một phần"
            message += f"\n\n✓ Phiếu bảo hành đã được tạo tự động!"
            QMessageBox.information(None, "Thành công", message)
            self.display_payment_summary(amount_paid, debt_current_order, status)
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Thanh toán không thành công: {str(e)}")

    def calculate_total(self):
        return sum(item["product"].selling_price * item["quantity"] for item in self.cart)

    def display_payment_summary(self, amount_paid, debt_current_order, status):
        if hasattr(self.view, "lblPaid"):
            self.view.lblPaid.setText(self.format_currency(amount_paid))
        if hasattr(self.view, "lblDebt"):
            self.view.lblDebt.setText(self.format_currency(debt_current_order))
        if hasattr(self.view, "lblPaymentStatus"):
            self.view.lblPaymentStatus.setText(status)

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
