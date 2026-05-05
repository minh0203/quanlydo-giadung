from datetime import datetime

from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QPushButton, QDialog, QVBoxLayout, QLabel, QInputDialog, QFileDialog, QWidget, QHBoxLayout, QLineEdit, QDialogButtonBox
from PyQt5.QtWidgets import QAbstractItemView, QTableWidget
from PyQt5 import QtWidgets
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
            
            # Payment amount connection
            if hasattr(self.view, "txtPaidAmount"):
                self.view.txtPaidAmount.textChanged.connect(self.calculate_remaining_debt)
            
            # History tab connections
            if hasattr(self.view, "btnSearchHistory"):
                self.view.btnSearchHistory.clicked.connect(self.search_import_history)
            if hasattr(self.view, "btnRefreshHistory"):
                self.view.btnRefreshHistory.clicked.connect(self.load_import_history)
            if hasattr(self.view, "btnViewDetail"):
                self.view.btnViewDetail.clicked.connect(self.view_import_detail)
            if hasattr(self.view, "btnDeleteImport"):
                self.view.btnDeleteImport.clicked.connect(self.delete_import)
            if hasattr(self.view, "cboFilterStatus"):
                self.view.cboFilterStatus.currentTextChanged.connect(self.search_import_history)
            if hasattr(self.view, "tableHistoryImports"):
                self.view.tableHistoryImports.setSelectionBehavior(QAbstractItemView.SelectRows)
                self.view.tableHistoryImports.setEditTriggers(QAbstractItemView.NoEditTriggers)
                self.view.tableHistoryImports.setAlternatingRowColors(True)
            
            # Load history on first load
            self.load_import_history()
            
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
        if hasattr(self.view, "txtPaidAmount"):
            self.view.txtPaidAmount.setText("")
        if hasattr(self.view, "lblRemainingDebtValue"):
            self.view.lblRemainingDebtValue.setText("0 VNĐ")
        
        self.update_import_code()
        self.display_import_items()

    def calculate_remaining_debt(self):
        """Tính toán số tiền còn nợ dựa trên tổng tiền và số tiền đã thanh toán"""
        try:
            if not hasattr(self.view, "lblTotalAmount") or not hasattr(self.view, "txtPaidAmount") or not hasattr(self.view, "lblRemainingDebtValue"):
                return
            
            total_text = self.view.lblTotalAmount.text().replace(" VNĐ", "").replace(",", "")
            paid_text = self.view.txtPaidAmount.text().strip().replace(",", "")
            
            total_amount = float(total_text) if total_text else 0.0
            paid_amount = float(paid_text) if paid_text else 0.0
            
            remaining_debt = max(0, total_amount - paid_amount)
            
            self.view.lblRemainingDebtValue.setText(f"{remaining_debt:,.0f} VNĐ")
            
            # Auto-update payment status based on payment amount
            if hasattr(self.view, "cboPaymentStatus"):
                if paid_amount == 0:
                    self.view.cboPaymentStatus.setCurrentIndex(0)  # Chưa thanh toán
                elif paid_amount >= total_amount:
                    self.view.cboPaymentStatus.setCurrentIndex(1)  # Đã thanh toán
                else:
                    self.view.cboPaymentStatus.setCurrentIndex(2)  # Thanh toán một phần
                    
        except Exception as e:
            print(f"⚠️ Error calculating remaining debt: {str(e)}")
            if hasattr(self.view, "lblRemainingDebtValue"):
                self.view.lblRemainingDebtValue.setText("0 VNĐ")

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

        # Get payment information
        paid_text = self.view.txtPaidAmount.text().strip().replace(",", "") if hasattr(self.view, "txtPaidAmount") else ""
        try:
            paid_amount = float(paid_text) if paid_text else 0.0
        except Exception:
            paid_amount = 0.0

        remaining_debt = max(0, total_amount - paid_amount)

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
                paid_amount=paid_amount,
                remaining_debt=remaining_debt,
                note="",
                items=items,
            )

            # Cập nhật số tiền nợ của nhà cung cấp nếu có nợ
            if remaining_debt > 0:
                supplier.update_debt(remaining_debt)

            for item in self.import_items:
                product = item["product"]
                product.quantity += item["quantity"]
                if item["price"] > 0:
                    product.purchase_price = item["price"]
                product.update()

            QMessageBox.information(None, "Thành công", f"Lưu phiếu nhập {import_order.import_number} thành công!\nTổng: {self.view.lblTotalAmount.text()}\nĐã thanh toán: {paid_amount:,.0f} VNĐ\nCòn nợ: {remaining_debt:,.0f} VNĐ")
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

    # ============== HISTORY TAB METHODS ==============
    
    def load_import_history(self):
        """Tải lịch sử nhập hàng từ database"""
        try:
            all_imports = ImportOrder.get_all()
            self.current_imports = all_imports
            self.display_import_history(all_imports)
            print(f"✓ Loaded {len(all_imports)} import orders")
        except Exception as e:
            print(f"❌ Error loading import history: {str(e)}")
            QMessageBox.warning(None, "Lỗi", f"Không thể tải lịch sử nhập: {str(e)}")

    def display_import_history(self, imports):
        """Hiển thị lịch sử nhập hàng trong bảng"""
        if not hasattr(self.view, "tableHistoryImports"):
            return
        
        table = self.view.tableHistoryImports
        table.setRowCount(len(imports))
        table.setColumnCount(9)
        table.setHorizontalHeaderLabels([
            "ID", "Mã phiếu", "Ngày nhập", "NCC", "Số lượng SP", "Tổng tiền", "Số tiền nợ", "Thanh toán", "Thao tác"
        ])
        
        for row, import_order in enumerate(imports):
            # Calculate total items
            total_items = sum([item.get("quantity", 0) for item in (import_order.items or [])])
            
            table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            table.setItem(row, 1, QTableWidgetItem(import_order.import_number))
            table.setItem(row, 2, QTableWidgetItem(import_order.import_date))
            table.setItem(row, 3, QTableWidgetItem(import_order.supplier_name))
            table.setItem(row, 4, QTableWidgetItem(str(total_items)))
            table.setItem(row, 5, QTableWidgetItem(f"{import_order.total_amount:,.0f} VNĐ"))
            table.setItem(row, 6, QTableWidgetItem(f"{import_order.remaining_debt:,.0f} VNĐ"))
            table.setItem(row, 7, QTableWidgetItem(import_order.payment_status))
            
            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            
            # View detail button
            btn_view = QPushButton("👁️ Chi tiết")
            btn_view.clicked.connect(lambda checked, imp=import_order: self.view_import_detail(imp))
            action_layout.addWidget(btn_view)
            
            # Pay debt button (only if there's remaining debt)
            if import_order.remaining_debt > 0:
                btn_pay = QPushButton("💰 Thanh toán")
                btn_pay.clicked.connect(lambda checked, imp=import_order: self.show_payment_dialog(imp))
                action_layout.addWidget(btn_pay)
            
            table.setCellWidget(row, 8, action_widget)
        
        table.resizeColumnsToContents()

    def search_import_history(self):
        """Tìm kiếm và lọc lịch sử nhập"""
        try:
            search_text = ""
            filter_status = "Tất cả"
            
            if hasattr(self.view, "txtSearchHistory"):
                search_text = self.view.txtSearchHistory.text().strip()
            
            if hasattr(self.view, "cboFilterStatus"):
                filter_status = self.view.cboFilterStatus.currentText()
            
            all_imports = self.current_imports if hasattr(self, 'current_imports') else ImportOrder.get_all()
            
            # Filter by payment status
            if filter_status != "Tất cả":
                all_imports = [imp for imp in all_imports if imp.payment_status == filter_status]
            
            # Filter by search text
            if search_text:
                search_lower = search_text.lower()
                all_imports = [
                    imp for imp in all_imports 
                    if (search_lower in imp.import_number.lower() or 
                        search_lower in imp.supplier_name.lower())
                ]
            
            self.display_import_history(all_imports)
            print(f"✓ Found {len(all_imports)} matching imports")
        except Exception as e:
            print(f"❌ Error searching imports: {str(e)}")
            QMessageBox.warning(None, "Lỗi", f"Lỗi tìm kiếm: {str(e)}")

    def view_import_detail(self, import_order=None):
        """Xem chi tiết phiếu nhập"""
        try:
            if import_order is None:
                # Get selected row from table
                if not hasattr(self.view, "tableHistoryImports"):
                    QMessageBox.warning(None, "Cảnh báo", "Chưa chọn phiếu nhập.")
                    return
                
                row = self.view.tableHistoryImports.currentRow()
                if row < 0:
                    QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn một phiếu nhập để xem chi tiết.")
                    return
                
                # Get import_number from table
                import_number = self.view.tableHistoryImports.item(row, 1).text()
                import_order = ImportOrder.get_by_id(import_number)
            
            if not import_order:
                QMessageBox.warning(None, "Lỗi", "Không tìm thấy phiếu nhập.")
                return
            
            # Create detail dialog
            dialog = QDialog(None)
            dialog.setWindowTitle(f"Chi tiết phiếu nhập: {import_order.import_number}")
            dialog.setMinimumSize(700, 500)
            layout = QVBoxLayout(dialog)
            
            # Import info
            info_text = f"""
Mã phiếu nhập: {import_order.import_number}
Ngày nhập: {import_order.import_date}
Nhà cung cấp: {import_order.supplier_name}
Trạng thái thanh toán: {import_order.payment_status}
Tổng tiền: {import_order.total_amount:,.0f} VNĐ
Đã thanh toán: {import_order.paid_amount:,.0f} VNĐ
Còn nợ: {import_order.remaining_debt:,.0f} VNĐ
Ghi chú: {import_order.note if import_order.note else 'Không có'}
            """
            
            info_label = QLabel(info_text)
            layout.addWidget(info_label)
            
            # Items table
            items_table = QtWidgets.QTableWidget()
            items_table.setColumnCount(5)
            items_table.setHorizontalHeaderLabels(["Mã SP", "Tên sản phẩm", "Số lượng", "Giá nhập", "Thành tiền"])
            items_table.setRowCount(len(import_order.items) if import_order.items else 0)
            
            if import_order.items:
                for row, item in enumerate(import_order.items):
                    items_table.setItem(row, 0, QTableWidgetItem(item.get("product_id", "")))
                    items_table.setItem(row, 1, QTableWidgetItem(item.get("product_name", "")))
                    items_table.setItem(row, 2, QTableWidgetItem(str(item.get("quantity", 0))))
                    items_table.setItem(row, 3, QTableWidgetItem(f"{item.get('unit_price', 0):,.0f} VNĐ"))
                    items_table.setItem(row, 4, QTableWidgetItem(f"{item.get('total_price', 0):,.0f} VNĐ"))
            
            items_table.resizeColumnsToContents()
            layout.addWidget(items_table)
            
            # Close button
            close_btn = QtWidgets.QPushButton("Đóng")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            
            dialog.exec_()
        except Exception as e:
            print(f"❌ Error viewing import detail: {str(e)}")
            QMessageBox.warning(None, "Lỗi", f"Không thể xem chi tiết: {str(e)}")

    def pay_import_debt(self, import_order, payment_amount):
        """Thanh toán nợ cho phiếu nhập"""
        try:
            if payment_amount <= 0:
                QMessageBox.warning(None, "Cảnh báo", "Số tiền thanh toán phải lớn hơn 0.")
                return
            
            if payment_amount > import_order.remaining_debt:
                QMessageBox.warning(None, "Cảnh báo", f"Số tiền thanh toán không được vượt quá số tiền nợ ({import_order.remaining_debt:,.0f} VNĐ).")
                return
            
            # Cập nhật import order
            new_paid_amount = import_order.paid_amount + payment_amount
            new_remaining_debt = import_order.remaining_debt - payment_amount
            
            if new_remaining_debt == 0:
                new_payment_status = "Đã thanh toán"
            else:
                new_payment_status = "Thanh toán một phần"
            
            ImportOrder.update_payment(
                import_order.import_number,
                new_paid_amount,
                new_remaining_debt,
                new_payment_status
            )
            
            # Cập nhật debt của supplier (giảm nợ)
            supplier = Supplier.get_by_id(import_order.supplier_id)
            if supplier:
                supplier.update_debt(-payment_amount)  # Giảm nợ
            
            QMessageBox.information(
                None, 
                "Thành công", 
                f"Thanh toán thành công!\nSố tiền: {payment_amount:,.0f} VNĐ\nCòn nợ: {new_remaining_debt:,.0f} VNĐ"
            )
            
            # Refresh history
            self.load_import_history()
            
        except Exception as e:
            print(f"❌ Error paying import debt: {str(e)}")
            QMessageBox.warning(None, "Lỗi", f"Không thể thanh toán: {str(e)}")

    def show_payment_dialog(self, import_order):
        """Hiển thị dialog thanh toán nợ"""
        try:
            dialog = QDialog(None)
            dialog.setWindowTitle(f"Thanh toán nợ - Phiếu nhập {import_order.import_number}")
            dialog.setMinimumWidth(400)
            layout = QVBoxLayout(dialog)
            
            # Info labels
            info_text = f"""
Phiếu nhập: {import_order.import_number}
Nhà cung cấp: {import_order.supplier_name}
Tổng tiền: {import_order.total_amount:,.0f} VNĐ
Đã thanh toán: {import_order.paid_amount:,.0f} VNĐ
Còn nợ: {import_order.remaining_debt:,.0f} VNĐ
            """
            
            info_label = QLabel(info_text)
            layout.addWidget(info_label)
            
            # Payment amount input
            payment_label = QLabel("Số tiền thanh toán:")
            layout.addWidget(payment_label)
            
            txt_payment = QLineEdit()
            txt_payment.setPlaceholderText(f"Nhập số tiền (tối đa {import_order.remaining_debt:,.0f} VNĐ)")
            layout.addWidget(txt_payment)
            
            # Buttons
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(lambda: self.process_payment(dialog, import_order, txt_payment))
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            dialog.exec_()
            
        except Exception as e:
            print(f"❌ Error showing payment dialog: {str(e)}")
            QMessageBox.warning(None, "Lỗi", f"Không thể mở dialog thanh toán: {str(e)}")

    def process_payment(self, dialog, import_order, txt_payment):
        """Xử lý thanh toán từ dialog"""
        try:
            payment_text = txt_payment.text().strip()
            if not payment_text:
                QMessageBox.warning(dialog, "Cảnh báo", "Vui lòng nhập số tiền thanh toán.")
                return
            
            try:
                payment_amount = float(payment_text.replace(',', '').replace(' VNĐ', ''))
            except ValueError:
                QMessageBox.warning(dialog, "Cảnh báo", "Số tiền không hợp lệ.")
                return
            
            self.pay_import_debt(import_order, payment_amount)
            dialog.accept()
            
        except Exception as e:
            print(f"❌ Error processing payment: {str(e)}")
            QMessageBox.warning(dialog, "Lỗi", f"Không thể xử lý thanh toán: {str(e)}")

    def delete_import(self):
        """Xóa phiếu nhập"""
        try:
            if not hasattr(self.view, "tableHistoryImports"):
                QMessageBox.warning(None, "Cảnh báo", "Không tìm thấy bảng lịch sử.")
                return
            
            row = self.view.tableHistoryImports.currentRow()
            if row < 0:
                QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn một phiếu nhập để xóa.")
                return
            
            import_number = self.view.tableHistoryImports.item(row, 1).text()
            
            reply = QMessageBox.question(
                None, 
                "Xác nhận xóa",
                f"Bạn có chắc muốn xóa phiếu nhập {import_number}?\n\nHành động này không thể hoàn tác!",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # Get import order info before deleting
            import_order = ImportOrder.get_by_id(import_number)
            if not import_order:
                QMessageBox.warning(None, "Lỗi", "Không tìm thấy phiếu nhập.")
                return
            
            # If there's remaining debt, reduce supplier's debt
            if import_order.remaining_debt > 0:
                supplier = Supplier.get_by_id(import_order.supplier_id)
                if supplier:
                    supplier.update_debt(-import_order.remaining_debt)  # Reduce debt
            
            # Delete the import order
            from models.database import Database
            Database.execute(
                "DELETE FROM import_items WHERE import_number = ?",
                (import_number,),
                commit=True
            )
            Database.execute(
                "DELETE FROM import_orders WHERE import_number = ?",
                (import_number,),
                commit=True
            )
            
            QMessageBox.information(None, "Thành công", f"Đã xóa phiếu nhập {import_number}.")
            self.load_import_history()
        except Exception as e:
            print(f"❌ Error deleting import: {str(e)}")
            QMessageBox.warning(None, "Lỗi", f"Không thể xóa phiếu nhập: {str(e)}")
