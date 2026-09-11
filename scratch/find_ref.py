with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Occurrences of process_auto_open:")
for i, line in enumerate(lines, 1):
    if 'process_auto_open' in line:
        print(f"Line {i}: {line.strip()}")
