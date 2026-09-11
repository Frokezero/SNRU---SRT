import sys

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Set output encoding to UTF-8 for the console
sys.stdout.reconfigure(encoding='utf-8')

for idx in range(2489, min(2530, len(lines))):
    print(f"{idx+1}: {lines[idx]}", end="")
