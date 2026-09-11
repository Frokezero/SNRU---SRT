import sys
import re

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

filepath = r"d:\โฟลเดอร์ใหม่ (6)\1122220\admin.html"
query = sys.argv[1] if len(sys.argv) > 1 else "latitude"
case_insensitive = True

print(f"Searching for '{query}' in {filepath}...")

with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

matches = []
for idx, line in enumerate(lines):
    match = False
    if case_insensitive:
        if query.lower() in line.lower():
            match = True
    else:
        if query in line:
            match = True
    if match:
        matches.append((idx + 1, line.strip()))

print(f"Found {len(matches)} matches:")
for line_num, content in matches[:50]:
    print(f"L{line_num}: {content}")
