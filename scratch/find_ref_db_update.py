with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Occurrences of db_update_event:")
for i, line in enumerate(lines, 1):
    if 'db_update_event' in line:
        print(f"Line {i}: {line.strip()}")
