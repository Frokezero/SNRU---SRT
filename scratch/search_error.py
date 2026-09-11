import os

search_terms = ['โครงสร้างรหัสความปลอดภัย', 'รูปแบบ Token ผิดพลาด']
target_extensions = ['.py', '.html', '.js', '.css', '.json']

results = []

for root, dirs, files in os.walk('.'):
    if any(ignore in root for ignore in ['.venv', '__pycache__', '.git', 'backups', 'uploads', 'activity_calendar']):
        continue
    for file in files:
        if any(file.endswith(ext) for ext in target_extensions):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                for i, line in enumerate(content.splitlines(), 1):
                    for term in search_terms:
                        if term in line:
                            results.append((filepath, i, line))
                            break
            except Exception as e:
                pass

for r in results:
    print(f"{r[0]}:{r[1]} -> {r[2].strip()}")
