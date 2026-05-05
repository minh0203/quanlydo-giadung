import csv

from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QDialog, QVBoxLayout, QLabel, QPushButton, QFileDialog
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtCore import Qt

from models.supplier import Supplier


class SupplierController:
    """Controller xử lý logic quản lý nhà cung cấp"""

    def __init__(self, view):
        self.view = view
        self.current_supplier = None
        self.suppliers = []
        self.setup_connections()
        self.load_suppliers()
        self.clear_form()

    def setup_connections(self):
        if hasattr(self.view, "btnSearch"):
            self.view.btnSearch.clicked.connect(self.search_suppliers)
        if hasattr(self.view, "txtSearch"):
            self.view.txtSearch.textChanged.connect(self.search_suppliers)
        if hasattr(self.view, "btnAdd"):
            self.view.btnAdd.clicked.connect(self.clear_form)
        if hasattr(self.view, "btnSave"):
            self.view.btnSave.clicked.connect(self.save_supplier)
        if hasattr(self.view, "btnUpdate"):
            self.view.btnUpdate.clicked.connect(self.update_supplier)
        if hasattr(self.view, "btnClear"):
            self.view.btnClear.clicked.connect(self.clear_form)
        if hasattr(self.view, "btnEdit"):
            self.view.btnEdit.clicked.connect(self.edit_selected_supplier)
        if hasattr(self.view, "btnDelete"):
            self.view.btnDelete.clicked.connect(self.delete_selected_supplier)
        if hasattr(self.view, "btnImport"):
            self.view.btnImport.clicked.connect(self.import_suppliers)
        if hasattr(self.view, "btnExport"):
            self.view.btnExport.clicked.connect(self.export_suppliers)
        if hasattr(self.view, "tableSuppliers"):
            self.view.tableSuppliers.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.view.tableSuppliers.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.view.tableSuppliers.setAlternatingRowColors(True)
            self.view.tableSuppliers.itemSelectionChanged.connect(self.on_supplier_selected)

    def load_suppliers(self):
        self.suppliers = Supplier.get_all()
        self.display_suppliers(self.suppliers)

    def search_suppliers(self):
        keyword = self.view.txtSearch.text().strip() if hasattr(self.view, "txtSearch") else ""
        if keyword:
            results = Supplier.search(keyword)
        else:
            results = Supplier.get_all()
        self.display_suppliers(results)

    def display_suppliers(self, suppliers):
        if not hasattr(self.view, "tableSuppliers"):
            return

        table = self.view.tableSuppliers
        table.setRowCount(len(suppliers))
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "Mã NCC", "Tên nhà cung cấp", "SĐT", "Email", "Địa chỉ", "Mã số thuế", "Công nợ", "Trạng thái"
        ])

        total_debt = 0.0
        for row, supplier in enumerate(suppliers):
            table.setItem(row, 0, QTableWidgetItem(supplier.supplier_id))
            table.setItem(row, 1, QTableWidgetItem(supplier.name))
            table.setItem(row, 2, QTableWidgetItem(supplier.phone))
            table.setItem(row, 3, QTableWidgetItem(supplier.email))
            table.setItem(row, 4, QTableWidgetItem(supplier.address))
            table.setItem(row, 5, QTableWidgetItem(supplier.tax_code))
            table.setItem(row, 6, QTableWidgetItem(f"{supplier.debt:,.0f} VNĐ"))
            table.setItem(row, 7, QTableWidgetItem(supplier.status))
            total_debt += supplier.debt

        table.resizeColumnsToContents()
        if hasattr(self.view, "lblTotalDebt"):
            self.view.lblTotalDebt.setText(f"Tổng nợ hiện tại: {total_debt:,.0f} VNĐ")

    def on_supplier_selected(self):
        if not hasattr(self.view, "tableSuppliers"):
            return
        row = self.view.tableSuppliers.currentRow()
        if row < 0:
            return
        supplier_id = self.view.tableSuppliers.item(row, 0).text()
        self.load_supplier_by_id(supplier_id)

    def edit_selected_supplier(self):
        if not hasattr(self.view, "tableSuppliers"):
            return
        row = self.view.tableSuppliers.currentRow()
        if row < 0:
            QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn nhà cung cấp để sửa.")
            return
        supplier_id = self.view.tableSuppliers.item(row, 0).text()
        self.load_supplier_by_id(supplier_id)

    def load_supplier_by_id(self, supplier_id):
        supplier = Supplier.get_by_id(supplier_id)
        if not supplier:
            QMessageBox.warning(None, "Lỗi", "Không tìm thấy nhà cung cấp.")
            return
        self.current_supplier = supplier
        self.fill_form()

    def fill_form(self):
        if not self.current_supplier:
            return
        self.view.txtSupplierCode.setText(self.current_supplier.supplier_id)
        self.view.txtSupplierName.setText(self.current_supplier.name)
        self.view.txtPhone.setText(self.current_supplier.phone)
        self.view.txtEmail.setText(self.current_supplier.email)
        self.view.txtAddress.setText(self.current_supplier.address)
        self.view.txtTaxCode.setText(self.current_supplier.tax_code)
        self.view.txtContactPerson.setText(self.current_supplier.contact_person)
        self.view.txtBankAccount.setText(self.current_supplier.bank_account)
        self.view.txtBankName.setText(self.current_supplier.bank_name)
        self.view.txtDebt.setText(str(self.current_supplier.debt))
        self.view.cboSupplierStatus.setCurrentText(self.current_supplier.status)
        self.view.txtNote.setPlainText(self.current_supplier.note)

    def clear_form(self):
        self.current_supplier = None
        if hasattr(self.view, "txtSupplierCode"):
            self.view.txtSupplierCode.clear()
        if hasattr(self.view, "txtSupplierName"):
            self.view.txtSupplierName.clear()
        if hasattr(self.view, "txtPhone"):
            self.view.txtPhone.clear()
        if hasattr(self.view, "txtEmail"):
            self.view.txtEmail.clear()
        if hasattr(self.view, "txtAddress"):
            self.view.txtAddress.clear()
        if hasattr(self.view, "txtTaxCode"):
            self.view.txtTaxCode.clear()
        if hasattr(self.view, "txtContactPerson"):
            self.view.txtContactPerson.clear()
        if hasattr(self.view, "txtBankAccount"):
            self.view.txtBankAccount.clear()
        if hasattr(self.view, "txtBankName"):
            self.view.txtBankName.clear()
        if hasattr(self.view, "txtDebt"):
            self.view.txtDebt.setText("0")
        if hasattr(self.view, "cboSupplierStatus"):
            self.view.cboSupplierStatus.setCurrentIndex(0)
        if hasattr(self.view, "txtNote"):
            self.view.txtNote.clear()
        self.load_suppliers()

    def save_supplier(self):
        name = self.view.txtSupplierName.text().strip() if hasattr(self.view, "txtSupplierName") else ""
        if not name:
            QMessageBox.warning(None, "Cảnh báo", "Vui lòng nhập tên nhà cung cấp.")
            return
        phone = self.view.txtPhone.text().strip() if hasattr(self.view, "txtPhone") else ""
        email = self.view.txtEmail.text().strip() if hasattr(self.view, "txtEmail") else ""
        address = self.view.txtAddress.text().strip() if hasattr(self.view, "txtAddress") else ""
        tax_code = self.view.txtTaxCode.text().strip() if hasattr(self.view, "txtTaxCode") else ""
        contact_person = self.view.txtContactPerson.text().strip() if hasattr(self.view, "txtContactPerson") else ""
        bank_account = self.view.txtBankAccount.text().strip() if hasattr(self.view, "txtBankAccount") else ""
        bank_name = self.view.txtBankName.text().strip() if hasattr(self.view, "txtBankName") else ""
        debt_text = self.view.txtDebt.text().strip() if hasattr(self.view, "txtDebt") else "0"
        try:
            debt = float(debt_text.replace(",", ""))
        except Exception:
            debt = 0.0
        status = self.view.cboSupplierStatus.currentText() if hasattr(self.view, "cboSupplierStatus") else "Đang hợp tác"
        note = self.view.txtNote.toPlainText().strip() if hasattr(self.view, "txtNote") else ""

        try:
            # Check duplicate supplier by name
            existing = Supplier.get_by_name(name)
            if existing:
                QMessageBox.warning(None, "Cảnh báo", "Nhà cung cấp này đã tồn tại. Vui lòng kiểm tra lại.")
                return

            Supplier.create(name, phone, email, address, tax_code, contact_person, bank_account, bank_name, debt, status, note)
            QMessageBox.information(None, "Thành công", "Đã thêm nhà cung cấp thành công.")
            self.clear_form()
            self.load_suppliers()
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể thêm nhà cung cấp: {str(e)}")

    def update_supplier(self):
        if not self.current_supplier:
            QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn nhà cung cấp để cập nhật.")
            return
        name = self.view.txtSupplierName.text().strip()
        self.current_supplier.name = name
        self.current_supplier.phone = self.view.txtPhone.text().strip()
        self.current_supplier.email = self.view.txtEmail.text().strip()
        self.current_supplier.address = self.view.txtAddress.text().strip()
        self.current_supplier.tax_code = self.view.txtTaxCode.text().strip()
        self.current_supplier.contact_person = self.view.txtContactPerson.text().strip()
        self.current_supplier.bank_account = self.view.txtBankAccount.text().strip()
        self.current_supplier.bank_name = self.view.txtBankName.text().strip()
        debt_text = self.view.txtDebt.text().strip() if hasattr(self.view, "txtDebt") else "0"
        try:
            self.current_supplier.debt = float(debt_text.replace(",", ""))
        except Exception:
            self.current_supplier.debt = 0.0
        self.current_supplier.status = self.view.cboSupplierStatus.currentText() if hasattr(self.view, "cboSupplierStatus") else self.current_supplier.status
        self.current_supplier.note = self.view.txtNote.toPlainText().strip() if hasattr(self.view, "txtNote") else ""

        existing = Supplier.get_by_name(name)
        if existing and existing.supplier_id != self.current_supplier.supplier_id:
            QMessageBox.warning(None, "Cảnh báo", "Tên nhà cung cấp này đã tồn tại. Vui lòng chọn tên khác.")
            return

        try:
            self.current_supplier.update()
            QMessageBox.information(None, "Thành công", "Đã cập nhật nhà cung cấp thành công.")
            self.load_suppliers()
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể cập nhật nhà cung cấp: {str(e)}")

    def delete_selected_supplier(self):
        if not self.current_supplier:
            QMessageBox.warning(None, "Cảnh báo", "Vui lòng chọn nhà cung cấp để xóa.")
            return
        reply = QMessageBox.question(None, "Xác nhận", f"Bạn có chắc muốn xóa nhà cung cấp {self.current_supplier.name}?", QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        try:
            self.current_supplier.delete()
            QMessageBox.information(None, "Thành công", "Đã xóa nhà cung cấp.")
            self.clear_form()
            self.load_suppliers()
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể xóa nhà cung cấp: {str(e)}")

    def import_suppliers(self):
        path, _ = QFileDialog.getOpenFileName(None, "Nhập danh sách nhà cung cấp", "", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                count = 0
                for row in reader:
                    name = row.get('name') or row.get('Tên nhà cung cấp')
                    if not name:
                        continue
                    phone = row.get('phone') or row.get('SĐT') or ""
                    email = row.get('email') or ""
                    address = row.get('address') or ""
                    tax_code = row.get('tax_code') or row.get('Mã số thuế') or ""
                    contact_person = row.get('contact_person') or row.get('Người liên hệ') or ""
                    bank_account = row.get('bank_account') or ""
                    bank_name = row.get('bank_name') or ""
                    debt_text = row.get('debt') or "0"
                    try:
                        debt = float(debt_text.replace(',', ''))
                    except Exception:
                        debt = 0.0
                    status = row.get('status') or "Đang hợp tác"
                    note = row.get('note') or ""
                    Supplier.create(name, phone, email, address, tax_code, contact_person, bank_account, bank_name, debt, status, note)
                    count += 1
            QMessageBox.information(None, "Thành công", f"Đã nhập {count} nhà cung cấp từ file.")
            self.load_suppliers()
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể nhập file: {str(e)}")

    def export_suppliers(self):
        path, _ = QFileDialog.getSaveFileName(None, "Xuất danh sách nhà cung cấp", "suppliers.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['supplier_id', 'name', 'phone', 'email', 'address', 'tax_code', 'contact_person', 'bank_account', 'bank_name', 'debt', 'status', 'note', 'created_at']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for supplier in self.suppliers:
                    writer.writerow({
                        'supplier_id': supplier.supplier_id,
                        'name': supplier.name,
                        'phone': supplier.phone,
                        'email': supplier.email,
                        'address': supplier.address,
                        'tax_code': supplier.tax_code,
                        'contact_person': supplier.contact_person,
                        'bank_account': supplier.bank_account,
                        'bank_name': supplier.bank_name,
                        'debt': supplier.debt,
                        'status': supplier.status,
                        'note': supplier.note,
                        'created_at': supplier.created_at,
                    })
            QMessageBox.information(None, "Thành công", "Đã xuất danh sách nhà cung cấp.")
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể xuất file: {str(e)}")

