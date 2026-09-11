import re

with open('admin.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("image_url or image search in admin.html:")
for m in re.finditer(r'image_url|img|photo', content, re.IGNORECASE):
    start = max(0, m.start() - 50)
    end = min(len(content), m.end() + 50)
    print(f"Context: ... {content[start:end].strip()} ...")
