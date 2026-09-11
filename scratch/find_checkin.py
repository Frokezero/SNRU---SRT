import re

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Searching for checkin routes in app.py:")
for idx, line in enumerate(lines, 1):
    if '/api/student/checkin' in line or 'def check_in' in line or 'def checkin' in line:
        print(f"Line {idx}: {line.strip()}")
