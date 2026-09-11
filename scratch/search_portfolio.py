with open('portfolio.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines, 1):
    if 'item.date' in line or 'item.title' in line or 'item.event_date' in line or 'item.event_title' in line:
        print(f"Line {idx}: {line.strip()}")
