with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("=== json.load or json.loads reading from files in app.py ===")
for i, line in enumerate(content.splitlines(), 1):
    if 'json.load' in line:
        print(f"Line {i}: {line.strip()}")
