import os
import subprocess

# Tạo thư mục ui nếu chưa có
os.makedirs('ui', exist_ok=True)

# Lấy danh sách file .ui
ui_files = [f for f in os.listdir('ui') if f.endswith('.ui')]

if not ui_files:
    print("❌ Không tìm thấy file .ui trong thư mục ui/")
    print("📌 Hãy copy các file .ui vào thư mục ui/ trước khi chạy!")
    exit()

print(f"🔍 Tìm thấy {len(ui_files)} file UI\n")

for ui_file in ui_files:
    input_path = os.path.join('ui', ui_file)
    output_path = os.path.join('ui', ui_file.replace('.ui', '.py'))
    
    print(f"🔄 Đang convert: {ui_file}")
    
    try:
        subprocess.run(
            ['python', '-m', 'PyQt5.uic.pyuic', '-x', input_path, '-o', output_path],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ Đã tạo: {output_path}\n")
    except Exception as e:
        print(f"❌ Lỗi: {e}\n")

print("🎉 Hoàn tất convert!")
