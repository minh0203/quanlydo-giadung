from datetime import datetime

from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QPushButton, QDialog, QVBoxLayout, QLabel, QInputDialog, QFileDialog
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtCore import Qt, QDate

from models.product import Product
from models.supplier import Supplier
from models.import_order import ImportOrder


class ImportController:
    """Controller xử lý logic nhập hàng"""

    def __init__(self, view):
        self.view = view
        self.import_items = []
        self.selected_product = None
        self.suppliers = []
        self.supplier_map = {}
        
        # Khởi tạo database nếu chưa có
        self.ensure_default_suppliers()
        
        self.setup_connections()
        self.reset_form()
        self.load_suppliers()

    def ensure_default_suppliers(self):
        """Đảm bảo có ít nhất 1 supplier trong database"""
        try:
            suppliers = Supplier.get_all()
            if not suppliers or len(suppliers) == 0:
                print("Creating default suppliers...")
                default_suppliers = [
                    {"name": "Nhà cung cấp A", "phone": "0123456789", "email": "ncc_a@example.com", "address": "Hà Nội"},
                    {"name": "Nhà cung cấp B", "phone": "0987654321", "email": "ncc_b@example.com", "address": "TP.HCM"},
                ]
                for sup_data in default_suppliers:
                    Supplier.create(
                        name=sup_data["name"],
                        phone=sup_data.get("phone", ""),
                        email=sup_data.get("email", ""),
                        address=sup_data.get("address", "")
                    )
                print(f"✓ Created {len(default_suppliers)} default suppliers")
        except Exception as e:
            print(f"⚠️ Error ensuring default suppliers: {str(e)}")

    def setup_connections(self):
        """Kết nối các signal từ UI"""
        try:
            if hasattr(self.view, "btnSearchProduct"):
                self.view.btnSearchProduct.clicked.connect(self.search_product)
            if hasattr(self.view, "btnAddProduct"):
                self.view.btnAddProduct.clicked.connect(self.add_product_to_import)
            if hasattr(self.view, "btnClearCart"):
                self.view.btnClearCart.clicked.connect(self.clear_import_items)
            if hasattr(self.view, "btnSaveImport"):
                self.view.btnSaveImport.clicked.connect(self.save_import)
            if hasattr(self.view, "btnPrintImport"):
                self.view.btnPrintImport.clicked.connect(self.print_import)
            if hasattr(self.view, "btnAddSupplier"):
                self.view.btnAddSupplier.clicked.connect(self.add_supplier)
            if hasattr(self.view, "tableImportItems"):
                self.view.tableImportItems.setSelectionBehavior(QAbstractItemView.SelectRows)
                self.view.tableImportItems.setEditTriggers(QAbstractItemView.NoEditTriggers)
                self.view.tableImportItems.setAlternatingRowColors(True)
            print("✓ ImportController: All signal connections successful")
        except Exception as e:
            print(f"⚠️ ImportController: Error setting up connections: {str(e)}")

    def reset_form(self):
        self.import_items = []
        self.selected_product = None
        
        # Reset form fields một cách an toàn
        if hasattr(self.view, "txtProductSearch"):
            self.view.txtProductSearch.setText("")
        if hasattr(self.view, "txtQuantity"):
            self.view.txtQuantity.setText("1")
        if hasattr(self.view, "txtPrice"):
            self.view.txtPrice.setText("")
        if hasattr(self.view, "lblTotalAmount"):
            self.view.lblTotalAmount.setText("0 VNĐ")
        if hasattr(self.view, "dateImportDate"):
            self.view.dateImportDate.setDate(QDate.currentDate())
        if hasattr(self.view, "cboPaymentStatus"):
            self.view.cboPaymentStatus.setCurrentIndex(0)  # Set "Chưa thanh toán"
        
        self.update_import_code()
        self.display_import_items()

    def update_import_code(self):
        code = datetime.now().strftime("PN%Y%m%d%H%M%S")
        if hasattr(self.view, "txtImportCode"):
            self.view.txtImportCode.setText(code)

    def load_suppliers(self):
        if not hasattr(self.view, "cboSupplier"):
            print("❌ ImportController: cboSupplier not found in UI")
            return
        try:
            self.suppliers = Supplier.get_all()
            self.supplier_map = {supplier.name: supplier for supplier in self.suppliers}
            self.view.cboSupplier.clear()
            self.view.cboSupplier.addItem("")
            
            if not self.suppliers:
                print("⚠️ ImportController: No suppliers found in database")
                self.view.cboSupplier.addItem("(Chưa có NCC - Vui lòng thêm)")
            else:
                for supplier in self.suppliers:
                    self.view.cboSupplier.addItem(supplier.name)
                print(f"✓ ImportController: Loaded {len(self.suppliers)} suppliers")
        except Exception as e:
            print(f"❌ ImportController Error loading suppliers: {str(e)}")
            self.view.cboSupplier.clear()
            self.view.cboSupplier.addItem("")
            self.view.cboSupplier.addItem("(Lỗi tải NCC)")
            self.suppliers = []
            self.supplier_map = {}

    def add_supplier(self):
        if not hasattr(self.view, "cboSupplier"):
            return
        name, ok = QInputDialog.getText(None, "Thêm nhà cung cấp", "Nhập tên nhà cung cấp:")
        if not ok or not name.strip():
            return
        name = name.strip()
        existing = next((s for s in self.suppliers if s.name.lower() == name.lower()), None)
        if existing:
            QMessageBox.information(None, "Thông báo", "Nhà cung cấp đã tồn tại.")
            self.view.cboSupplier.setCurrentText(existing.name)
            return
        supplier = Supplier.create(name)
        self.load_suppliers()
        self.view.cboSupplier.setCurrentText(supplier.name)
        QMessageBox.information(None, "Thành công", f"Đã tạo nhà cung cấp mới: {supplier.name}")

    def search_product(self):
        if not hasattr(self.view, "txtProductSearch"):
            return
        keyword = self.view.txtProductSearch.text().strip()
        if not keyword:
            QMessageBox.warning(None, "Cảnh báo", "Vui lòng nhập mã hoặc tên sản phẩm để tìm.")
            return

        product = Product.get_by_id(keyword)
        if product:
            self.selected_product = product
            QMessageBox.information(None, "Sản phẩm tìm thấy", f"Đã chọn sản phẩm: {product.name}")
            return

        products = Product.search(keyword)
        if not products:
            QMessageBox.warning(None, "Không tìm thấy", "Không tìm thấy sản phẩm phù hợp.")
            self.selected_product = None
            return

        if len(products) == 1:
            self.selected_product = products[0]
            QMessageBox.information(None, "Sản phẩm tìm thấy", f"Đã chọn sản phẩm: {products[0].name}")
            return

        dialog = QDialog(None)
        dialog.setWindowTitle("Chọn sản phẩm")
        dialog.setMinimumWidth(500)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"Có {len(products)} sản phẩm trùng khớp. Vui lòng chọn:"))

        selected = [None]

        def select(product):
            selected[0] = product
            dialog.accept()

        for product in products:
            btn = QPushButton(f"{product.product_id} - {product.name}")
            btn.clicked.connect(lambda checked, p=product: select(p))
            layout.addWidget(btn)

        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(dialog.reject)
        layout.addWidget(cancel_btn)

        if dialog.exec_() == QDialog.Accepted and selected[0]:
            self.selected_product = selected[0]
            QMessageBox.information(None, "Sản phẩm đã chọn", f"Đã chọn: {self.selected_product.name}")
        else:
            self.selected_product = None

    def add_product_to_import(self):
        if not self.selected_product:
            QMessageBox.warning(None, "Cảnh báo", "Vui lòng tìm và chọn sản phẩm trước khi thêm vào phiếu.")
            return

        try:
            quantity = int(self.view.txtQuantity.text().strip())
        except Exception:
            QMessageBox.warning(None, "Lỗi", "Số lượng phải là số nguyên dương.")
            return

        if quantity <= 0:
            QMessageBox.warning(None, "Lỗi", "Số lượng phải lớn hơn 0.")
            return

        price_text = self.view.txtPrice.text().strip().replace("VNĐ", "").replace(",", "")
        try:
            import_price = float(price_text) if price_text else self.selected_product.purchase_price
        except Exception:
            QMessageBox.warning(None, "Lỗi", "Giá nhập không hợp lệ.")
            return

        item = next((item for item in self.import_items if item["product"].product_id == self.selected_product.product_id and item["price"] == import_price), None)
        if item:
            item["quantity"] += quantity
        else:
            self.import_items.append({
                "product": self.selected_product,
                "quantity": quantity,
                "price": import_price,
            })

        self.display_import_items()
        self.view.txtQuantity.setText("1")
        self.view.txtPrice.setText("")
        self.view.txtProductSearch.setText("")
        self.selected_product = None

    def display_import_items(self):
        if not hasattr(self.view, "tableImportItems"):
            return

        table = self.view.tableImportItems
        table.setRowCount(len(self.import_items))
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "ID", "Mã SP", "Tên sản phẩm", "Số lượng", "Giá nhập", "Thành tiền", "Thao tác"
        ])

        total = 0
        for row, item in enumerate(self.import_items):
            product = item["product"]
            quantity = item["quantity"]
            price = item["price"]
            total_price = quantity * price
            total += total_price

            table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            table.setItem(row, 1, QTableWidgetItem(product.product_id))
            table.setItem(row, 2, QTableWidgetItem(product.name))
            table.setItem(row, 3, QTableWidgetItem(str(quantity)))
            table.setItem(row, 4, QTableWidgetItem(f"{price:,.0f} VNĐ"))
            table.setItem(row, 5, QTableWidgetItem(f"{total_price:,.0f} VNĐ"))

            btn_remove = QPushButton("Xóa")
            btn_remove.clicked.connect(lambda checked, r=row: self.remove_import_item(r))
            table.setCellWidget(row, 6, btn_remove)

        self.view.lblTotalAmount.setText(f"{total:,.0f} VNĐ")
        table.resizeColumnsToContents()

    def remove_import_item(self, row):
        if 0 <= row < len(self.import_items):
            self.import_items.pop(row)
            self.display_import_items()

    def clear_import_items(self):
        if not self.import_items:
            QMessageBox.information(None, "Thông báo", "Giỏ nhập đang trống.")
            return
        reply = QMessageBox.question(None, "Xác nhận", "Bạn có chắc muốn xóa toàn bộ giỏ nhập?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.import_items.clear()
            self.display_import_items()

    def save_import(self):
        if not self.import_items:
            QMessageBox.warning(None, "Cảnh báo", "Không có sản phẩm nào trong phiếu nhập.")
            return

        if not hasattr(self.view, "cboSupplier"):
            QMessageBox.warning(None, "Lỗi", "Không tìm thấy điều khiển nhà cung cấp.")
            return

        supplier_name = self.view.cboSupplier.currentText().strip()
        if not supplier_name:
            QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn nhà cung cấp.")
            return

        supplier = self.supplier_map.get(supplier_name)
        if not supplier:
            QMessageBox.warning(None, "Lỗi", "Nhà cung cấp chọn không hợp lệ.")
            return

        payment_status = self.view.cboPaymentStatus.currentText() if hasattr(self.view, "cboPaymentStatus") else "Chưa thanh toán"
        import_date = self.view.dateImportDate.date().toString("yyyy-MM-dd")
        total_text = self.view.lblTotalAmount.text().replace(" VNĐ", "").replace(",", "")
        try:
            total_amount = float(total_text)
        except Exception:
            total_amount = 0.0

        items = []
        for item in self.import_items:
            items.append({
                "product_id": item["product"].product_id,
                "product_name": item["product"].name,
                "quantity": item["quantity"],
                "unit_price": item["price"],
                "total_price": item["quantity"] * item["price"],
            })

        try:
            import_order = ImportOrder.create(
                supplier_id=supplier.supplier_id,
                supplier_name=supplier.name,
                import_date=import_date,
                payment_status=payment_status,
                total_amount=total_amount,
                note="",
                items=items,
            )

            for item in self.import_items:
                product = item["product"]
                product.quantity += item["quantity"]
                if item["price"] > 0:
                    product.purchase_price = item["price"]
                product.update()

            QMessageBox.information(None, "Thành công", f"Lưu phiếu nhập {import_order.import_number} thành công!\nTổng: {self.view.lblTotalAmount.text()}")
            self.reset_form()
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể lưu phiếu nhập: {str(e)}")

    def print_import(self):
        if not self.import_items:
            QMessageBox.warning(None, "Cảnh báo", "Không có phiếu nhập để in.")
            return

        supplier_name = self.view.cboSupplier.currentText() if hasattr(self.view, "cboSupplier") else ""
        lines = [
            f"Phiếu nhập: {self.view.txtImportCode.text()}",
            f"Ngày nhập: {self.view.dateImportDate.date().toString('yyyy-MM-dd')}",
            f"Nhà cung cấp: {supplier_name}",
            "",
        ]
        for item in self.import_items:
            lines.append(f"{item['product'].product_id} - {item['product'].name} x{item['quantity']} @ {item['price']:,.0f} = {item['quantity'] * item['price']:,.0f} VNĐ")
        lines.append("")
        lines.append(f"Tổng: {self.view.lblTotalAmount.text()}")
        QMessageBox.information(None, "Phiếu nhập", "\n".join(lines))
