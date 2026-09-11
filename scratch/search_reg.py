with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

for i, line in enumerate(content.splitlines(), 1):
    if '/register' in line or 'db_save_registration' in line or 'registration' in line:
        if 'def ' in line or '@app.' in line:
            print(f"{i}: {line}")
