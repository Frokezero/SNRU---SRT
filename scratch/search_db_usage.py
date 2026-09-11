with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Check for JSON loading/saving functions
print("=== JSON Loader/Saver usages in app.py ===")
for i, line in enumerate(content.splitlines(), 1):
    if any(keyword in line for keyword in ['load_users', 'load_events', 'load_participations', 'load_registrations', 'save_users', 'save_events', 'save_participations', 'save_registrations']):
        print(f"Line {i}: {line.strip()}")

print("\n=== raw JSON file paths referenced in app.py ===")
for i, line in enumerate(content.splitlines(), 1):
    if any(keyword in line for keyword in ['users.json', 'events.json', 'participations.json', 'registrations.json']):
        print(f"Line {i}: {line.strip()}")
