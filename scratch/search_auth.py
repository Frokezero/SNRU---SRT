with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

for i, line in enumerate(content.splitlines(), 1):
    if 'password' in line or 'login' in line or 'hash' in line:
        if 'def ' in line or '@app.' in line or 'check_password' in line:
            print(f"{i}: {line}")
