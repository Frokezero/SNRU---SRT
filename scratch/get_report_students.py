import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

filepath = r"d:\โฟลเดอร์ใหม่ (6)\1122220\app.py"
with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

start_pattern = "@app.route('/api/admin/reports/students'"
idx = text.find(start_pattern)
if idx != -1:
    print("--- FOUND get_student_report ---")
    print(text[idx:idx+2500])
else:
    print("Not found get_student_report")
