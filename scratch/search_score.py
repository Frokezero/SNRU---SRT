with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

for i, line in enumerate(content.splitlines(), 1):
    if 'participations' in line or 'score' in line or 'sum' in line:
        if 'def ' in line or '@app.' in line:
            print(f"{i}: {line}")
