from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QLineEdit, QPushButton, QComboBox, QTextEdit
from PyQt5.QtCore import Qt
from models.product import Product
from models.database import Database


class ProductController:
    """Controller xử lý logic quản lý sản phẩm"""

    def __init__(self, view):
        self.view = view
        self.current_product = None
        self.setup_connections()
        self.load_products()

    def setup_connections(self):
        """Thiết lập kết nối các signal"""
        # Kết nối nút thêm sản phẩm
        if hasattr(self.view, "btnAdd"):
            self.view.btnAdd.clicked.connect(self.show_add_form)

        # Kết nối nút lưu sản phẩm
        if hasattr(self.view, "btnSave"):
            self.view.btnSave.clicked.connect(self.save_product)

        # Kết nối nút cập nhật sản phẩm
        if hasattr(self.view, "btnEdit"):
            self.view.btnEdit.clicked.connect(self.edit_product)

        # Kết nối nút xóa sản phẩm
        if hasattr(self.view, "btnDelete"):
            self.view.btnDelete.clicked.connect(self.delete_product)

        # Kết nối nút làm mới
        if hasattr(self.view, "btnClear"):
            self.view.btnClear.clicked.connect(self.clear_form)

        # Kết nối nút tìm kiếm
        if hasattr(self.view, "btnSearch"):
            self.view.btnSearch.clicked.connect(self.search_products)

        # Kết nối ô tìm kiếm
        if hasattr(self.view, "txtSearch"):
            self.view.txtSearch.textChanged.connect(self.on_search_text_changed)

        # Kết nối bảng sản phẩm
        if hasattr(self.view, "tableProducts"):
            self.view.tableProducts.itemSelectionChanged.connect(self.on_product_selected)

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
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "Mã SP", "Tên sản phẩm", "Danh mục", "Thương hiệu",
            "Giá mua", "Giá bán", "Số lượng", "Đơn vị"
        ])

        for row, product in enumerate(products):
            table.setItem(row, 0, QTableWidgetItem(product.product_id))
            table.setItem(row, 1, QTableWidgetItem(product.name))
            table.setItem(row, 2, QTableWidgetItem(product.category))
            table.setItem(row, 3, QTableWidgetItem(product.brand))
            table.setItem(row, 4, QTableWidgetItem(f"{product.purchase_price:,.0f} VNĐ"))
            table.setItem(row, 5, QTableWidgetItem(f"{product.selling_price:,.0f} VNĐ"))
            table.setItem(row, 6, QTableWidgetItem(str(product.quantity)))
            table.setItem(row, 7, QTableWidgetItem(product.unit))

        # Điều chỉnh kích thước cột
        table.resizeColumnsToContents()

    def show_add_form(self):
        """Hiển thị form thêm sản phẩm mới"""
        self.clear_form()
        self.current_product = None
        # Disable mã sản phẩm vì tự động tạo
        self.set_field_enabled("txtProductCode", False)
        if hasattr(self.view, "btnSave"):
            self.view.btnSave.setEnabled(True)
        if hasattr(self.view, "btnEdit"):
            self.view.btnEdit.setEnabled(False)

    def save_product(self):
        """Lưu sản phẩm (thêm mới hoặc cập nhật)"""
        try:
            # Lấy dữ liệu từ form
            name = self.get_text_field("txtProductName")
            category = self.get_combo_field("cboProductCategory")
            brand = self.get_text_field("txtBrand")
            purchase_price = self.get_float_field("txtPurchasePrice")
            selling_price = self.get_float_field("txtSellingPrice")
            quantity = self.get_int_field("txtQuantity")
            unit = self.get_combo_field("cboUnit")
            description = self.get_text_field("txtDescription")

            # Kiểm tra dữ liệu bắt buộc
            if not name:
                QMessageBox.warning(None, "Cảnh báo", "Vui lòng nhập tên sản phẩm!")
                return

            if self.current_product:
                # Cập nhật sản phẩm hiện tại
                self.current_product.name = name
                self.current_product.category = category
                self.current_product.brand = brand
                self.current_product.purchase_price = purchase_price
                self.current_product.selling_price = selling_price
                self.current_product.quantity = quantity
                self.current_product.unit = unit
                self.current_product.description = description

                self.current_product.update()
                QMessageBox.information(None, "Thành công", "Đã cập nhật sản phẩm thành công!")
            else:
                # Tạo sản phẩm mới
                product = Product.create(
                    name=name,
                    category=category,
                    brand=brand,
                    purchase_price=purchase_price,
                    selling_price=selling_price,
                    quantity=quantity,
                    unit=unit,
                    description=description
                )
                QMessageBox.information(None, "Thành công", f"Đã thêm sản phẩm thành công! Mã sản phẩm: {product.product_id}")

            self.clear_form()
            self.load_products()

        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể lưu sản phẩm: {str(e)}")

    def edit_product(self):
        """Chỉnh sửa sản phẩm được chọn"""
        if not self.current_product:
            QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn sản phẩm cần chỉnh sửa!")
            return

        # Enable các field để chỉnh sửa
        self.set_field_enabled("txtProductCode", False)  # Không cho sửa mã sản phẩm
        if hasattr(self.view, "btnSave"):
            self.view.btnSave.setEnabled(True)
        if hasattr(self.view, "btnEdit"):
            self.view.btnEdit.setEnabled(False)

    def delete_product(self):
        """Xóa sản phẩm"""
        if not self.current_product:
            QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn sản phẩm cần xóa!")
            return

        reply = QMessageBox.question(
            None, "Xác nhận",
            f"Bạn có chắc muốn xóa sản phẩm \'{self.current_product.name}\'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.current_product.delete()
                QMessageBox.information(None, "Thành công", "Đã xóa sản phẩm thành công!")
                self.clear_form()
                self.load_products()
            except Exception as e:
                QMessageBox.warning(None, "Lỗi", f"Không thể xóa sản phẩm: {str(e)}")

    def search_products(self):
        """Tìm kiếm sản phẩm"""
        keyword = self.get_text_field("txtSearch").strip()
        if keyword:
            try:
                products = Product.search(keyword)
                self.display_products(products)
            except Exception as e:
                QMessageBox.warning(None, "Lỗi", f"Không thể tìm kiếm: {str(e)}")
        else:
            self.load_products()

    def on_search_text_changed(self):
        """Xử lý khi text tìm kiếm thay đổi"""
        if hasattr(self.view, "txtSearch"):
            if not self.view.txtSearch.text().strip():
                self.load_products()

    def on_product_selected(self):
        """Xử lý khi chọn sản phẩm từ bảng"""
        if not hasattr(self.view, "tableProducts"):
            return

        current_row = self.view.tableProducts.currentRow()
        if current_row >= 0:
            product_id = self.view.tableProducts.item(current_row, 0).text()
            self.current_product = Product.get_by_id(product_id)
            if self.current_product:
                self.fill_form()

    def fill_form(self):
        """Điền dữ liệu sản phẩm vào form"""
        if not self.current_product:
            return

        self.set_text_field("txtProductCode", self.current_product.product_id)
        self.set_text_field("txtProductName", self.current_product.name)
        self.set_combo_field("cboProductCategory", self.current_product.category)
        self.set_text_field("txtBrand", self.current_product.brand)
        self.set_text_field("txtPurchasePrice", str(self.current_product.purchase_price))
        self.set_text_field("txtSellingPrice", str(self.current_product.selling_price))
        self.set_text_field("txtQuantity", str(self.current_product.quantity))
        self.set_combo_field("cboUnit", self.current_product.unit)
        self.set_text_field("txtDescription", self.current_product.description)

        # Disable các nút
        if hasattr(self.view, "btnSave"):
            self.view.btnSave.setEnabled(False)
        if hasattr(self.view, "btnEdit"):
            self.view.btnEdit.setEnabled(True)

    def clear_form(self):
        """Xóa dữ liệu trong form"""
        self.set_text_field("txtProductCode", "")
        self.set_text_field("txtProductName", "")
        self.set_combo_field("cboProductCategory", "")
        self.set_text_field("txtBrand", "")
        self.set_text_field("txtPurchasePrice", "0.0")
        self.set_text_field("txtSellingPrice", "0.0")
        self.set_text_field("txtQuantity", "0")
        self.set_combo_field("cboUnit", "Cái")
        self.set_text_field("txtDescription", "")

        # Enable các field
        self.set_field_enabled("txtProductCode", True)

        # Reset trạng thái nút
        if hasattr(self.view, "btnSave"):
            self.view.btnSave.setEnabled(True)
        if hasattr(self.view, "btnEdit"):
            self.view.btnEdit.setEnabled(False)

        self.current_product = None

    # Helper methods
    def get_text_field(self, field_name):
        """Lấy text từ field"""
        if hasattr(self.view, field_name):
            field = getattr(self.view, field_name)
            if isinstance(field, QLineEdit):
                return field.text().strip()
            elif isinstance(field, QTextEdit):
                return field.toPlainText().strip()
            elif isinstance(field, QComboBox):
                return field.currentText().strip()
        return ""

    def set_text_field(self, field_name, value):
        """Đặt text cho field"""
        if hasattr(self.view, field_name):
            field = getattr(self.view, field_name)
            if isinstance(field, QLineEdit):
                field.setText(str(value))
            elif isinstance(field, QTextEdit):
                field.setPlainText(str(value))
            elif isinstance(field, QComboBox):
                field.setCurrentText(str(value))

    def get_combo_field(self, field_name):
        """Lấy giá trị từ combo box"""
        if hasattr(self.view, field_name):
            field = getattr(self.view, field_name)
            if isinstance(field, QComboBox):
                return field.currentText().strip()
        return ""

    def set_combo_field(self, field_name, value):
        """Đặt giá trị cho combo box"""
        if hasattr(self.view, field_name):
            field = getattr(self.view, field_name)
            if isinstance(field, QComboBox):
                index = field.findText(str(value))
                if index >= 0:
                    field.setCurrentIndex(index)
                else:
                    field.setCurrentText(str(value))

    def set_field_enabled(self, field_name, enabled):
        """Enable/disable field"""
        if hasattr(self.view, field_name):
            field = getattr(self.view, field_name)
            field.setEnabled(enabled)

    def get_int_field(self, field_name):
        """Lấy giá trị int từ field"""
        text = self.get_text_field(field_name)
        try:
            return int(text) if text else 0
        except ValueError:
            return 0

    def get_float_field(self, field_name):
        """Lấy giá trị float từ field"""
        text = self.get_text_field(field_name)
        try:
            return float(text) if text else 0.0
        except ValueError:
            return 0.0
