with open('app.py.bak', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

print("=== JSON Save operations in app.py.bak ===")
for i, line in enumerate(content.splitlines(), 1):
    if any(keyword in line for keyword in ['save_users', 'save_events', 'save_participations', 'save_registrations', 'json.dump']):
        print(f"Line {i}: {line.strip()}")
