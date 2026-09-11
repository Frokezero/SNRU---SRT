with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

terms = ['email', 'profile', 'update', 'me']
for i, line in enumerate(content.splitlines(), 1):
    if any(t in line for t in terms):
        if 'def ' in line or '@app.' in line or 'route' in line:
            print(f"{i}: {line}")
