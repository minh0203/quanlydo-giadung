import csv
from datetime import datetime

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QFileDialog, QWidget, QVBoxLayout

from models.order import Order
from models.product import Product


class BarChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chart_data = []
        self.title = ""
        self.setMinimumHeight(320)

    def set_data(self, chart_data, title=""):
        self.chart_data = chart_data
        self.title = title
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        painter.fillRect(rect, QColor("#ffffff"))
        painter.setRenderHint(QPainter.Antialiasing)

        if not self.chart_data:
            painter.setPen(QPen(QColor("#555555")))
            painter.setFont(QFont("Arial", 12))
            painter.drawText(rect, Qt.AlignCenter, "Không có dữ liệu biểu đồ")
            return

        margin = 40
        bottom_margin = 60
        chart_rect = QRect(
            rect.left() + margin,
            rect.top() + margin + 20,
            rect.width() - 2 * margin,
            rect.height() - 2 * margin - bottom_margin
        )
        painter.setPen(QPen(QColor("#333333"), 2))
        painter.drawRect(chart_rect)

        max_value = max(value for _, value in self.chart_data)
        if max_value == 0:
            max_value = 1

        bar_width = int(chart_rect.width() / (len(self.chart_data) * 1.5))
        spacing = int(bar_width / 2)
        x = chart_rect.left() + spacing
        base_y = chart_rect.bottom() - 10

        colors = [QColor("#4caf50"), QColor("#2196f3"), QColor("#ff9800"), QColor("#9c27b0"), QColor("#f44336")]
        for index, (label, value) in enumerate(self.chart_data):
            bar_height = int((value / max_value) * (chart_rect.height() - 40))
            bar_top = base_y - bar_height
            bar_rect = QRect(x, bar_top, bar_width, bar_height)
            painter.setBrush(colors[index % len(colors)])
            painter.setPen(Qt.NoPen)
            painter.drawRect(bar_rect)

            painter.setPen(QPen(QColor("#333333")))
            painter.setFont(QFont("Arial", 9))
            label_rect = QRect(x - 10, chart_rect.bottom() + 6, bar_width + 20, 40)
            painter.drawText(label_rect, Qt.AlignHCenter | Qt.TextWordWrap, label)

            value_text = f"{value:,.0f}"
            painter.drawText(QRect(x, bar_top - 20, bar_width, 18), Qt.AlignHCenter | Qt.AlignVCenter, value_text)
            x += bar_width + spacing

        if self.title:
            painter.setPen(QPen(QColor("#111111")))
            painter.setFont(QFont("Arial", 11, QFont.Bold))
            painter.drawText(QRect(rect.left(), rect.top() + 4, rect.width(), 20), Qt.AlignCenter, self.title)


class ReportController:
    """Controller xử lý logic báo cáo"""

    def __init__(self, view):
        self.view = view
        self.current_report = ""
        self.chart_widget = None
        self.setup_connections()
        self.initialize_filters()
        self.initialize_chart()

    def setup_connections(self):
        if hasattr(self.view, "btnViewReport"):
            self.view.btnViewReport.clicked.connect(self.view_report)
        if hasattr(self.view, "btnExportExcel"):
            self.view.btnExportExcel.clicked.connect(self.export_report)
        if hasattr(self.view, "btnPrintReport"):
            self.view.btnPrintReport.clicked.connect(self.print_report)

    def initialize_filters(self):
        if hasattr(self.view, "dateFrom") and hasattr(self.view, "dateTo"):
            today = datetime.today()
            self.view.dateFrom.setDate(self.view.dateFrom.date().fromString(f"{today.year}-{today.month:02d}-01", "yyyy-M-d"))
            self.view.dateTo.setDate(self.view.dateTo.date().fromString(today.strftime("%Y-%m-%d"), "yyyy-MM-dd"))

    def initialize_chart(self):
        if hasattr(self.view, "chartContainer"):
            layout = QVBoxLayout(self.view.chartContainer)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            self.chart_widget = BarChartWidget(self.view.chartContainer)
            layout.addWidget(self.chart_widget)

    def view_report(self):
        date_from = self.get_date(self.view.dateFrom) if hasattr(self.view, "dateFrom") else ""
        date_to = self.get_date(self.view.dateTo) if hasattr(self.view, "dateTo") else ""
        self.current_report = "📈 Báo cáo doanh thu"
        self.show_revenue_report(date_from, date_to)

    def get_date(self, date_widget):
        return date_widget.date().toString("yyyy-MM-dd")

    def show_revenue_report(self, date_from, date_to):
        orders = Order.search_by_filters(date_from=date_from, date_to=date_to)
        table = self.view.tableReport
        headers = ["Mã đơn", "Ngày", "Khách hàng", "Tổng tiền", "Đã thanh toán", "Trạng thái"]
        table.setColumnCount(len(headers))
        table.setRowCount(len(orders))
        table.setHorizontalHeaderLabels(headers)

        total_revenue = 0
        total_orders = len(orders)
        total_paid = 0
        product_totals = {}
        for row, order in enumerate(orders):
            order_date = order.order_date or order.created_at
            table.setItem(row, 0, QTableWidgetItem(order.order_number))
            table.setItem(row, 1, QTableWidgetItem(order_date))
            table.setItem(row, 2, QTableWidgetItem(order.customer_name or "Khách lẻ"))
            table.setItem(row, 3, QTableWidgetItem(f"{order.total_amount:,.0f} VNĐ"))
            table.setItem(row, 4, QTableWidgetItem(f"{order.paid_amount:,.0f} VNĐ"))
            table.setItem(row, 5, QTableWidgetItem(order.status))
            total_revenue += order.total_amount
            total_paid += order.paid_amount

            for item in order.items or []:
                product_name = item.get("product_name", "Không xác định")
                stats = product_totals.setdefault(product_name, {"quantity": 0, "sales": 0})
                stats["quantity"] += item.get("quantity", 0)
                stats["sales"] += item.get("total_price", 0)

        top_product_name = "--"
        top_products = []
        if product_totals:
            sorted_products = sorted(product_totals.items(), key=lambda x: x[1]["sales"], reverse=True)
            top_product_name = sorted_products[0][0]
            top_products = [(name, stats["sales"]) for name, stats in sorted_products[:5]]

        self.update_summary(total_revenue, total_orders, total_revenue / total_orders if total_orders else 0, top_product_name)
        self.view.lblChart.setText(f"Doanh thu từ {date_from} đến {date_to}: {total_revenue:,.0f} VNĐ")
        if self.chart_widget:
            self.chart_widget.set_data(top_products, "Top 5 sản phẩm theo doanh thu")
        table.resizeColumnsToContents()

    def show_inventory_report(self):
        products = Product.get_all()
        table = self.view.tableReport
        headers = ["Mã SP", "Tên sản phẩm", "Số lượng", "Giá vốn", "Giá bán", "Giá trị tồn kho"]
        table.setColumnCount(len(headers))
        table.setRowCount(len(products))
        table.setHorizontalHeaderLabels(headers)

        total_value = 0
        for row, product in enumerate(products):
            value = product.quantity * product.purchase_price
            table.setItem(row, 0, QTableWidgetItem(product.product_id))
            table.setItem(row, 1, QTableWidgetItem(product.name))
            table.setItem(row, 2, QTableWidgetItem(str(product.quantity)))
            table.setItem(row, 3, QTableWidgetItem(f"{product.purchase_price:,.0f} VNĐ"))
            table.setItem(row, 4, QTableWidgetItem(f"{product.sale_price:,.0f} VNĐ" if hasattr(product, 'sale_price') else "0 VNĐ"))
            table.setItem(row, 5, QTableWidgetItem(f"{value:,.0f} VNĐ"))
            total_value += value

        self.update_summary(total_value, len(products), total_value / len(products) if products else 0, "--")
        self.view.lblChart.setText(f"Giá trị tồn kho: {total_value:,.0f} VNĐ")
        table.resizeColumnsToContents()

    def show_top_products_report(self, date_from, date_to):
        orders = Order.search_by_filters(date_from=date_from, date_to=date_to)
        product_totals = {}
        for order in orders:
            for item in order.items or []:
                key = item["product_name"]
                product_totals.setdefault(key, {"quantity": 0, "sales": 0})
                product_totals[key]["quantity"] += item["quantity"]
                product_totals[key]["sales"] += item["total_price"]

        top_products = sorted(product_totals.items(), key=lambda x: x[1]["quantity"], reverse=True)
        table = self.view.tableReport
        headers = ["Sản phẩm", "Số lượng bán", "Doanh thu"]
        table.setColumnCount(len(headers))
        table.setRowCount(len(top_products))
        table.setHorizontalHeaderLabels(headers)

        total_qty = 0
        total_sales = 0
        for row, (name, stats) in enumerate(top_products):
            table.setItem(row, 0, QTableWidgetItem(name))
            table.setItem(row, 1, QTableWidgetItem(str(stats["quantity"])))
            table.setItem(row, 2, QTableWidgetItem(f"{stats["sales"]:,.0f} VNĐ"))
            total_qty += stats["quantity"]
            total_sales += stats["sales"]

        top_product_name = top_products[0][0] if top_products else "--"
        self.update_summary(total_sales, len(top_products), total_sales / len(top_products) if top_products else 0, top_product_name)
        self.view.lblChart.setText(f"Top sản phẩm: {top_product_name}")
        table.resizeColumnsToContents()

    def show_customer_report(self, date_from, date_to):
        orders = Order.search_by_filters(date_from=date_from, date_to=date_to)
        customer_totals = {}
        for order in orders:
            key = order.customer_name or "Khách lẻ"
            customer_totals.setdefault(key, {"orders": 0, "revenue": 0})
            customer_totals[key]["orders"] += 1
            customer_totals[key]["revenue"] += order.total_amount

        customers = sorted(customer_totals.items(), key=lambda x: x[1]["revenue"], reverse=True)
        table = self.view.tableReport
        headers = ["Khách hàng", "Số đơn", "Doanh thu"]
        table.setColumnCount(len(headers))
        table.setRowCount(len(customers))
        table.setHorizontalHeaderLabels(headers)

        total_orders = 0
        total_revenue = 0
        for row, (name, stats) in enumerate(customers):
            table.setItem(row, 0, QTableWidgetItem(name))
            table.setItem(row, 1, QTableWidgetItem(str(stats["orders"])))
            table.setItem(row, 2, QTableWidgetItem(f"{stats["revenue"]:,.0f} VNĐ"))
            total_orders += stats["orders"]
            total_revenue += stats["revenue"]

        top_customer = customers[0][0] if customers else "--"
        self.update_summary(total_revenue, total_orders, total_revenue / total_orders if total_orders else 0, top_customer)
        self.view.lblChart.setText(f"Khách hàng hàng đầu: {top_customer}")
        table.resizeColumnsToContents()

    def update_summary(self, total, count, average, top):
        if hasattr(self.view, "lblTotalRevenueValue"):
            self.view.lblTotalRevenueValue.setText(f"{total:,.0f} VNĐ")
        if hasattr(self.view, "lblTotalOrdersValue"):
            self.view.lblTotalOrdersValue.setText(str(count))
        if hasattr(self.view, "lblAvgOrderValueValue"):
            self.view.lblAvgOrderValueValue.setText(f"{average:,.0f} VNĐ")
        if hasattr(self.view, "lblTopProductValue"):
            self.view.lblTopProductValue.setText(top)

    def export_report(self):
        if not hasattr(self.view, "tableReport"):
            return
        path, _ = QFileDialog.getSaveFileName(None, "Xuất báo cáo", "report.csv", "CSV Files (*.csv)")
        if not path:
            return
        table = self.view.tableReport
        try:
            with open(path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                headers = [table.horizontalHeaderItem(col).text() for col in range(table.columnCount())]
                writer.writerow(headers)
                for row in range(table.rowCount()):
                    row_data = [table.item(row, col).text() if table.item(row, col) else "" for col in range(table.columnCount())]
                    writer.writerow(row_data)
            QMessageBox.information(None, "Thành công", "Đã xuất báo cáo ra file CSV.")
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể xuất file: {str(e)}")

    def print_report(self):
        summary = []
        if hasattr(self.view, "lblTotalRevenueValue"):
            summary.append(f"Tổng: {self.view.lblTotalRevenueValue.text()}")
        if hasattr(self.view, "lblTotalOrdersValue"):
            summary.append(f"Số dòng: {self.view.lblTotalOrdersValue.text()}")
        if hasattr(self.view, "lblAvgOrderValueValue"):
            summary.append(f"Trung bình: {self.view.lblAvgOrderValueValue.text()}")
        if hasattr(self.view, "lblTopProductValue"):
            summary.append(f"Top: {self.view.lblTopProductValue.text()}")
        QMessageBox.information(None, "Báo cáo", "\n".join(summary))
