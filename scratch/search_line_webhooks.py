import re

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Searching for LINE webhook or callback in app.py:")
for idx, line in enumerate(lines, 1):
    if 'webhook' in line.lower() or 'callback' in line.lower() or 'line' in line.lower():
        if '@app.route' in line or 'def ' in line:
            print(f"Line {idx}: {line.strip()}")
