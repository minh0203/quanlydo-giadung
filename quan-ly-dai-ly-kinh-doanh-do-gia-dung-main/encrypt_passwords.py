#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script mã hóa tất cả mật khẩu trong database từ plain text sang bcrypt
"""
import sys
import os

# Thêm thư mục hiện tại vào path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import Database
from utils.password_utils import PasswordUtils


def encrypt_all_passwords():
    """Mã hóa tất cả mật khẩu trong bảng employees"""
    
    try:
        # Lấy tất cả employees
        rows = Database.execute(
            "SELECT employee_id, username, password FROM employees",
            fetch_all=True
        )
        
        if not rows:
            print("❌ Không có nhân viên nào trong database!")
            return False
        
        print(f"📋 Tìm thấy {len(rows)} nhân viên")
        print("-" * 60)
        
        # Chuẩn bị dữ liệu cập nhật
        updates = []
        for employee_id, username, password in rows:
            # Bỏ qua nếu mật khẩu trống
            if not password or password.strip() == "":
                print(f"⏭️  Bỏ qua {employee_id} ({username}): mật khẩu trống")
                continue
            
            # Kiểm tra xem mật khẩu đã mã hóa hay chưa (bcrypt hashes bắt đầu bằng $2a$, $2b$, $2x$, $2y$)
            if password.startswith("$2"):
                print(f"✅ Đã mã hóa: {employee_id} ({username}): {password[:20]}...")
                continue
            
            # Mã hóa mật khẩu
            hashed_password = PasswordUtils.hash_password(password)
            updates.append((hashed_password, employee_id))
            print(f"🔐 Mã hóa: {employee_id} ({username})")
            print(f"   Mật khẩu cũ: {password}")
            print(f"   Mật khẩu mới: {hashed_password[:30]}...")
        
        if not updates:
            print("\n⚠️  Tất cả mật khẩu đã mã hóa hoặc trống!")
            return True
        
        print("-" * 60)
        print(f"\n📝 Cập nhật {len(updates)} mật khẩu...")
        
        # Cập nhật database
        Database.execute_many(
            "UPDATE employees SET password = ? WHERE employee_id = ?",
            updates,
            commit=True
        )
        
        print(f"✅ Mã hóa thành công {len(updates)} mật khẩu!")
        return True
        
    except ImportError as e:
        print(f"❌ Lỗi import: {e}")
        print("💡 Vui lòng cài đặt bcrypt trước: pip install bcrypt")
        return False
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🔐 SCRIPT MÃ HÓA MẬT KHẨU - PASSWORD ENCRYPTION")
    print("=" * 60)
    print()
    
    success = encrypt_all_passwords()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Hoàn thành!")
    else:
        print("❌ Thất bại!")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
