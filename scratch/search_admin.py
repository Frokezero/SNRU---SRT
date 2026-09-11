with open('d:/โฟลเดอร์ใหม่ (6)/1122220/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = [m.start() for m in re.finditer(r'@app\.route\(\'/api/events', content)]
for m in matches:
    start_line = content[:m].count('\n') + 1
    # print context of 3 lines
    snippet = '\n'.join(content.split('\n')[start_line-1:start_line+4])
    print(f"Match found at line {start_line}:")
    print(snippet)
    print("---")
