import sys

with open('admin.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

sys.stdout.reconfigure(encoding='utf-8')

for idx in range(1040, min(1090, len(lines))):
    print(f"{idx+1}: {lines[idx]}", end="")
