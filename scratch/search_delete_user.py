import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

filepath = r"d:\โฟลเดอร์ใหม่ (6)\1122220\app.py"
with open(filepath, "r", encoding="utf-8") as f:
    code = f.read()

idx = code.find("def admin_delete_user")
if idx != -1:
    print(code[idx:idx+1500])
else:
    print("admin_delete_user not found")
