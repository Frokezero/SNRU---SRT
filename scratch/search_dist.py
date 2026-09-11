with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

for i, line in enumerate(content.splitlines(), 1):
    if 'dist >' in line or 'เมตร เกินกำหนด' in line or '100' in line:
        if 'latitude' in line or 'longitude' in line or 'dist' in line or 'เมตร' in line:
            print(f"{i}: {line}")
