import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

filepath = r"d:\โฟลเดอร์ใหม่ (6)\1122220\app.py"
query = sys.argv[1] if len(sys.argv) > 1 else "/api/admin/reports/attendance"

print(f"Finding line numbers for '{query}'...")

with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

found = False
for i, line in enumerate(lines):
    if query in line:
        found = True
        print(f"Match found at line {i+1}:")
        start = max(0, i - 10)
        end = min(len(lines), i + 150)
        for j in range(start, end):
            print(f"{j+1}: {lines[j]}", end="")
        print("-" * 50)

if not found:
    print("No match found.")
