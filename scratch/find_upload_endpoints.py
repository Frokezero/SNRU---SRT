import re

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Searching for upload/image/participation in app.py:")
for idx, line in enumerate(lines, 1):
    if any(keyword in line.lower() for keyword in ['upload', 'file', 'image', 'photo', 'participation', 'db_save_participation']):
        # print first 10 matches or so, or format it
        if 'def ' in line or '@app.route' in line or 'save' in line or 'secure_filename' in line:
            print(f"Line {idx}: {line.strip()}")
