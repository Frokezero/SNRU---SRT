with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx in range(1999, min(2070, len(lines))):
    print(f"{idx+1}: {lines[idx]}", end="")
