import re

with open('style.css', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all selectors containing dark-theme or dark
matches = re.findall(r'(\S*dark\S*)\s*\{([^}]+)\}', content, re.IGNORECASE)
print(f"Total dark-theme matching blocks: {len(matches)}")
for sel, body in matches[:10]:
    print(f"Selector: {sel}")
