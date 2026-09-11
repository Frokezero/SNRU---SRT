import re

with open('admin.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Search for "ผู้จอง"
matches = []
for i, line in enumerate(content.splitlines(), 1):
    if "ผู้จอง" in line or "Export" in line or "api/admin" in line or "registrations" in line:
        matches.append((i, line))

print(f"Total matches: {len(matches)}")
for line_num, text in matches[:50]:
    print(f"Line {line_num}: {text[:120]}")
