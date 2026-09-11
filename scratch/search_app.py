import sys
import re

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

filepath = r"d:\โฟลเดอร์ใหม่ (6)\1122220\app.py"
query = sys.argv[1] if len(sys.argv) > 1 else "update-status-bulk"

print(f"Searching for '{query}' in {filepath}...")

with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

matches = [m.start() for m in re.finditer(re.escape(query), text)]
print(f"Found {len(matches)} matches:")
for idx in matches[:5]:
    start = max(0, idx - 200)
    end = min(len(text), idx + 1000)
    print(f"--- Match at index {idx} ---")
    print(text[start:end])
    print("----------------------------\n")
