with open('admin.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "qr-gps-status" in line:
        print(f"Line {idx+1}: {line.strip()}")
        # Print next 10 lines if it is Javascript assignment
        if idx > 1200:
            for j in range(idx, min(idx + 25, len(lines))):
                print(f"  {j+1}: {lines[j].strip()}")
