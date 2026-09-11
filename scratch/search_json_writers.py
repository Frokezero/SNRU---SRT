with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("=== json.dump or json.dumps writing to files in app.py ===")
for i, line in enumerate(content.splitlines(), 1):
    if 'json.dump' in line or 'open(' in line:
        if any(keyword in line for keyword in ['w', 'write', 'USER_FILE', 'DATA_FILE', 'PARTICIPATIONS_FILE', 'REGISTRATIONS_FILE']):
            print(f"Line {i}: {line.strip()}")
