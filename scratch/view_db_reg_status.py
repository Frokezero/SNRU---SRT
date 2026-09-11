import sys

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

sys.stdout.reconfigure(encoding='utf-8')

for idx, line in enumerate(lines):
    if "def db_update_registration_status" in line:
        for j in range(idx, min(idx + 30, len(lines))):
            print(f"{j+1}: {lines[j]}", end="")
        break
