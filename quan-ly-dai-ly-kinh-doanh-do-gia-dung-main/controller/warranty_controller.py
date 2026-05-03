from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QPushButton, QLineEdit, QComboBox, QTextEdit
from PyQt5.QtCore import Qt, QDate

from models.warranty import Warranty
from models.product import Product


class WarrantyController:
    """Controller xử lý logic quản lý bảo hành"""

    def __init__(self, view):
        self.view = view
        self.current_warranty = None
        self.setup_connections()
        self.reset_filters()
        self.load_products()
        self.load_warranties()

    def setup_connections(self):
        if hasattr(self.view, "btnSearch"):
            self.view.btnSearch.clicked.connect(self.search_warranties)
        if hasattr(self.view, "btnReset"):
            self.view.btnReset.clicked.connect(self.reset_filters)
        if hasattr(self.view, "btnRegister"):
            self.view.btnRegister.clicked.connect(self.show_register_form)
        if hasattr(self.view, "btnSave"):
            self.view.btnSave.clicked.connect(self.save_warranty)
        if hasattr(self.view, "btnRepair"):
            self.view.btnRepair.clicked.connect(self.repair_warranty)
        if hasattr(self.view, "btnComplete"):
            self.view.btnComplete.clicked.connect(self.complete_warranty)
        if hasattr(self.view, "btnPrint"):
            self.view.btnPrint.clicked.connect(self.print_warranty)
        if hasattr(self.view, "btnClear"):
            self.view.btnClear.clicked.connect(self.clear_form)
        if hasattr(self.view, "tableWarranties"):
            self.view.tableWarranties.itemSelectionChanged.connect(self.on_warranty_selected)

    def load_products(self):
        try:
            products = Product.get_all()
            if hasattr(self.view, "cboProduct") and products:
                self.view.cboProduct.clear()
                for product in products:
                    self.view.cboProduct.addItem(product.name)
        except Exception:
            pass

    def load_warranties(self):
        try:
            warranties = Warranty.get_all()
            self.display_warranties(warranties)
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể tải danh sách bảo hành: {str(e)}")

    def display_warranties(self, warranties):
        if not hasattr(self.view, "tableWarranties"):
            return

        table = self.view.tableWarranties
        table.setRowCount(len(warranties))
        table.setColumnCount(10)
        table.setHorizontalHeaderLabels([
            "Mã BH",
            "Ngày tiếp nhận",
            "Sản phẩm",
            "Serial/Mã SP",
            "Khách hàng",
            "SĐT",
            "Mã hóa đơn",
            "Lỗi",
            "Trạng thái",
            "Thao tác"
        ])

        for row, warranty in enumerate(warranties):
            table.setItem(row, 0, QTableWidgetItem(warranty.warranty_code))
            table.setItem(row, 1, QTableWidgetItem(warranty.created_at[:10]))
            table.setItem(row, 2, QTableWidgetItem(warranty.product))
            table.setItem(row, 3, QTableWidgetItem(warranty.serial))
            table.setItem(row, 4, QTableWidgetItem(warranty.customer_name))
            table.setItem(row, 5, QTableWidgetItem(warranty.phone))
            table.setItem(row, 6, QTableWidgetItem(warranty.order_id or ""))
            table.setItem(row, 7, QTableWidgetItem(warranty.error_description))
            table.setItem(row, 8, QTableWidgetItem(warranty.status))

            button = QPushButton("Xem")
            button.clicked.connect(lambda checked, code=warranty.warranty_code: self.load_warranty_by_code(code))
            table.setCellWidget(row, 9, button)

        table.resizeColumnsToContents()

    def load_warranty_by_code(self, warranty_code):
        try:
            warranty = Warranty.get_by_code(warranty_code)
            if warranty:
                self.current_warranty = warranty
                self.fill_form()
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể tải phiếu bảo hành: {str(e)}")

    def show_register_form(self):
        self.clear_form()
        self.current_warranty = None
        if hasattr(self.view, "btnSave"):
            self.view.btnSave.setEnabled(True)
        if hasattr(self.view, "btnRepair"):
            self.view.btnRepair.setEnabled(False)
        if hasattr(self.view, "btnComplete"):
            self.view.btnComplete.setEnabled(False)

    def save_warranty(self):
        try:
            product = self.get_combo_field("cboProduct")
            serial = self.get_text_field("txtSerial")
            customer_name = self.get_text_field("txtCustomerName")
            phone = self.get_text_field("txtPhone")
            purchase_date = self.get_date_field("datePurchase")
            expiry_date = self.get_date_field("dateExpiry")
            error_description = self.get_text_field("txtError")
            note = self.get_text_field("txtNote")

            if not product:
                QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn sản phẩm!")
                return
            if not serial:
                QMessageBox.warning(None, "Cảnh báo", "Vui lòng nhập Serial/Mã sản phẩm!")
                return
            if not customer_name:
                QMessageBox.warning(None, "Cảnh báo", "Vui lòng nhập tên khách hàng!")
                return

            if self.current_warranty:
                self.current_warranty.product = product
                self.current_warranty.serial = serial
                self.current_warranty.customer_name = customer_name
                self.current_warranty.phone = phone
                self.current_warranty.purchase_date = purchase_date
                self.current_warranty.expiry_date = expiry_date
                self.current_warranty.error_description = error_description
                self.current_warranty.note = note
                self.current_warranty.update()
                QMessageBox.information(None, "Thành công", "Đã cập nhật phiếu bảo hành thành công!")
            else:
                warranty = Warranty.create(
                    product=product,
                    serial=serial,
                    customer_name=customer_name,
                    phone=phone,
                    purchase_date=purchase_date,
                    expiry_date=expiry_date,
                    error_description=error_description,
                    note=note,
                )
                QMessageBox.information(None, "Thành công", f"Đã tạo phiếu bảo hành {warranty.warranty_code} thành công!")

            self.clear_form()
            self.load_warranties()

        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể lưu phiếu bảo hành: {str(e)}")

    def repair_warranty(self):
        if not self.current_warranty:
            QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn phiếu bảo hành để cập nhật sửa chữa!")
            return

        try:
            self.current_warranty.update_status("Đã sửa xong")
            QMessageBox.information(None, "Thành công", "Đã đánh dấu phiếu bảo hành là 'Đã sửa xong'!")
            self.load_warranties()
            self.fill_form()
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể cập nhật trạng thái sửa chữa: {str(e)}")

    def complete_warranty(self):
        if not self.current_warranty:
            QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn phiếu bảo hành để hoàn thành!")
            return

        try:
            self.current_warranty.update_status("Đã trả hàng")
            QMessageBox.information(None, "Thành công", "Đã đánh dấu phiếu bảo hành là 'Đã trả hàng'!")
            self.load_warranties()
            self.fill_form()
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể cập nhật trạng thái hoàn thành: {str(e)}")

    def print_warranty(self):
        if not self.current_warranty:
            QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn phiếu bảo hành để in!")
            return

        detail = (
            f"Mã BH: {self.current_warranty.warranty_code}\n"
            f"Ngày tiếp nhận: {self.current_warranty.created_at}\n"
            f"Sản phẩm: {self.current_warranty.product}\n"
            f"Serial/Mã SP: {self.current_warranty.serial}\n"
            f"Khách hàng: {self.current_warranty.customer_name}\n"
            f"SĐT: {self.current_warranty.phone}\n"
            f"Ngày mua: {self.current_warranty.purchase_date}\n"
            f"Hết hạn BH: {self.current_warranty.expiry_date}\n"
            f"Lỗi: {self.current_warranty.error_description}\n"
            f"Ghi chú: {self.current_warranty.note}\n"
            f"Trạng thái: {self.current_warranty.status}"
        )
        QMessageBox.information(None, "Phiếu bảo hành", detail)

    def clear_form(self):
        self.set_combo_field("cboProduct", "")
        self.set_text_field("txtSerial", "")
        self.set_text_field("txtCustomerName", "")
        self.set_text_field("txtPhone", "")
        self.set_date_field("datePurchase", QDate.currentDate())
        self.set_date_field("dateExpiry", QDate.currentDate())
        self.set_text_field("txtError", "")
        self.set_text_field("txtNote", "")

        if hasattr(self.view, "btnRepair"):
            self.view.btnRepair.setEnabled(False)
        if hasattr(self.view, "btnComplete"):
            self.view.btnComplete.setEnabled(False)
        if hasattr(self.view, "btnSave"):
            self.view.btnSave.setEnabled(True)

        self.current_warranty = None

    def reset_filters(self):
        self.set_text_field("txtWarrantyCode", "")
        self.set_text_field("txtCustomer", "")
        self.set_combo_field("cboStatus", "Tất cả")
        if hasattr(self.view, "dateFrom"):
            self.view.dateFrom.setDate(QDate(2000, 1, 1))
        if hasattr(self.view, "dateTo"):
            self.view.dateTo.setDate(QDate.currentDate())
        self.load_warranties()

    def search_warranties(self):
        try:
            warranty_code = self.get_text_field("txtWarrantyCode")
            customer = self.get_text_field("txtCustomer")
            status = self.get_combo_field("cboStatus")
            if status == "Tất cả":
                status = ""
            date_from = self.get_date_field("dateFrom")
            date_to = self.get_date_field("dateTo")

            warranties = Warranty.search_by_filters(
                warranty_code=warranty_code,
                customer=customer,
                status=status,
                date_from=date_from,
                date_to=date_to,
            )
            self.display_warranties(warranties)
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể tìm kiếm phiếu bảo hành: {str(e)}")

    def on_warranty_selected(self):
        if not hasattr(self.view, "tableWarranties"):
            return

        row = self.view.tableWarranties.currentRow()
        if row < 0:
            return

        item = self.view.tableWarranties.item(row, 0)
        if item:
            warranty_code = item.text()
            self.load_warranty_by_code(warranty_code)

    def fill_form(self):
        if not self.current_warranty:
            return

        self.set_combo_field("cboProduct", self.current_warranty.product)
        self.set_text_field("txtSerial", self.current_warranty.serial)
        self.set_text_field("txtCustomerName", self.current_warranty.customer_name)
        self.set_text_field("txtPhone", self.current_warranty.phone)
        self.set_date_field("datePurchase", self.parse_date(self.current_warranty.purchase_date))
        self.set_date_field("dateExpiry", self.parse_date(self.current_warranty.expiry_date))
        self.set_text_field("txtError", self.current_warranty.error_description)
        self.set_text_field("txtNote", self.current_warranty.note)

        if hasattr(self.view, "btnRepair"):
            self.view.btnRepair.setEnabled(True)
        if hasattr(self.view, "btnComplete"):
            self.view.btnComplete.setEnabled(True)

    def parse_date(self, value):
        if not value:
            return QDate.currentDate()
        date = QDate.fromString(value, "yyyy-MM-dd")
        if not date.isValid():
            date = QDate.fromString(value, "dd/MM/yyyy")
        return date if date.isValid() else QDate.currentDate()

    def get_date_field(self, field_name):
        if hasattr(self.view, field_name):
            field = getattr(self.view, field_name)
            if hasattr(field, "date"):
                return field.date().toString("yyyy-MM-dd")
        return ""

    def set_date_field(self, field_name, date_value):
        if hasattr(self.view, field_name):
            field = getattr(self.view, field_name)
            if hasattr(field, "setDate"):
                field.setDate(date_value)

    def get_text_field(self, field_name):
        if hasattr(self.view, field_name):
            field = getattr(self.view, field_name)
            if isinstance(field, QLineEdit):
                return field.text().strip()
            if isinstance(field, QTextEdit):
                return field.toPlainText().strip()
            if isinstance(field, QComboBox):
                return field.currentText().strip()
        return ""

    def set_text_field(self, field_name, value):
        if hasattr(self.view, field_name):
            field = getattr(self.view, field_name)
            if isinstance(field, QLineEdit):
                field.setText(str(value))
            if isinstance(field, QTextEdit):
                field.setPlainText(str(value))
            if isinstance(field, QComboBox):
                field.setCurrentText(str(value))

    def get_combo_field(self, field_name):
        if hasattr(self.view, field_name):
            field = getattr(self.view, field_name)
            if isinstance(field, QComboBox):
                return field.currentText().strip()
        return ""

    def set_combo_field(self, field_name, value):
        if hasattr(self.view, field_name):
            field = getattr(self.view, field_name)
            if isinstance(field, QComboBox):
                index = field.findText(str(value))
                if index >= 0:
                    field.setCurrentIndex(index)
                else:
                    field.setCurrentText(str(value))

    def set_field_enabled(self, field_name, enabled):
        if hasattr(self.view, field_name):
            getattr(self.view, field_name).setEnabled(enabled)
