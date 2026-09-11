with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines, 1):
    if 'with data_lock:' in line:
        # print some context lines around it
        start = max(0, idx - 3)
        end = min(len(lines), idx + 4)
        print(f"--- Occurrence at line {idx} ---")
        for i in range(start, end):
            print(f"{i}: {lines[i-1].rstrip()}")
