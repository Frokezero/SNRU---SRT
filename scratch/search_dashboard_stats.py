with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines, 1):
    if 'dashboard-stats' in line or 'dashboard_stats' in line or 'dashboard' in line:
        print(f"Line {idx}: {line.strip()}")
