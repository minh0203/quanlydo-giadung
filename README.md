# 🏠 Phần Mềm Quản Lý Kinh Doanh Đồ Gia Dụng

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt-6.6-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![SQLite](https://img.shields.io/badge/SQLite-3-blue.svg)](https://www.sqlite.org/)

## 📋 Tổng quan

Phần mềm quản lý kinh doanh đồ gia dụng là giải pháp toàn diện dành cho các cửa hàng bán lẻ điện máy, đồ gia dụng. Hệ thống giúp quản lý **sản phẩm, khách hàng, hóa đơn, kho hàng và báo cáo doanh thu** một cách chuyên nghiệp và hiệu quả.

### 🎯 Đối tượng sử dụng
- Chủ cửa hàng kinh doanh đồ gia dụng
- Nhân viên bán hàng
- Nhân viên quản lý kho
- Kế toán/Thu ngân

## ✨ Tính năng chính

### 🔐 Quản lý đăng nhập & Phân quyền
- Đăng nhập với tài khoản/nhân khẩu
- Phân quyền: Admin, Nhân viên bán hàng, Kho, Kế toán
- Đổi mật khẩu, quên mật khẩu

### 📦 Quản lý sản phẩm
- Thêm, sửa, xóa sản phẩm
- Tìm kiếm, lọc sản phẩm theo danh mục (Tủ lạnh, Máy giặt, TV, Điều hòa, Bếp từ, Quạt, Máy hút bụi...)
- Quản lý giá nhập, giá bán, số lượng tồn kho
- Hiển thị ảnh sản phẩm
- Cảnh báo sản phẩm sắp hết hàng

### 👥 Quản lý khách hàng
- Thêm, sửa, xóa thông tin khách hàng
- Lịch sử mua hàng
- Quản lý điểm tích lũy / khách hàng thân thiết
- Tìm kiếm theo số điện thoại, tên

### 🧾 Quản lý bán hàng
- Tạo hóa đơn bán hàng trực tiếp
- Tự động tính tiền
- In hóa đơn
### 📥 Quản lý nhập hàng
- Nhập kho từ nhà cung cấp
- Quản lý nhà cung cấp (Thông tin, công nợ)
- Kiểm tra lô hàng, hạn sử dụng (nếu có)

### 📊 Báo cáo & Thống kê
- Báo cáo doanh thu theo ngày/tuần/tháng/năm
- Báo cáo sản phẩm bán chạy nhất
- Báo cáo tồn kho
- Báo cáo công nợ nhà cung cấp
- Biểu đồ trực quan (doanh thu, tồn kho)

### 🔧 Quản lý hệ thống
- Sao lưu & phục hồi dữ liệu
- Nhật ký hoạt động (log)
- Cấu hình cửa hàng (tên, địa chỉ, số điện thoại, logo)
- Quản lý người dùng

## 🛠️ Công nghệ sử dụng

| Công nghệ | Vai trò |
|-----------|---------|
| **Python 3.10+** | Ngôn ngữ lập trình chính |
| **PyQt6** | Xây dựng giao diện đồ họa (GUI) |
| **QtDesigner** | Thiết kế giao diện trực quan kéo-thả |
| **SQLite3** | Cơ sở dữ liệu nhúng (cho phiên bản Desktop) |
