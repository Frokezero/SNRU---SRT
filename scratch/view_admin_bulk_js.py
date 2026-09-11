with open('admin.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if "update-status-bulk" in line or "updateStatus" in line:
        # Print surrounding lines
        print(f"--- MATCH AT LINE {i} ---")
        start = max(0, i - 15)
        end = min(len(lines), i + 25)
        for idx in range(start, end):
            print(f"{idx+1}: {lines[idx]}", end="")
