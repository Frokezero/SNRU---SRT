with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Look for '/api/registrations/<reg_id>/status' or similar
matches = []
for i, line in enumerate(content.splitlines(), 1):
    if "/api/registrations/" in line or "/status" in line:
        if "reg" in line or "status" in line or "api" in line:
            matches.append((i, line))

print(f"Total matches: {len(matches)}")
for line_num, text in matches[:50]:
    print(f"Line {line_num}: {text[:120]}")
