import sys

filepath = r"d:\โฟลเดอร์ใหม่ (6)\1122220\app.py"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "admin_reset_password" in line:
        start_line = max(1, idx - 10)
        end_line = min(len(lines), idx + 10)
        print(f"Lines {start_line} to {end_line}:")
        for i in range(start_line - 1, end_line):
            print(f"{i + 1}: {lines[i]}", end="")
        break
