import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

for i, line in enumerate(content.splitlines(), 1):
    if '17.18994' in line or '104.09153' in line or 'latitude' in line or 'longitude' in line:
        print(f"{i}: {line}")
