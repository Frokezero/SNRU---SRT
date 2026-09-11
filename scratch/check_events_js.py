import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def check_events_js():
    with open('activity_calendar/events.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find any occurrences of 'สาขา' or major names
    print("activity_calendar/events.js search results:")
    for m in re.finditer(r'"owner":\s*"([^"]*)"', content):
        print(f"Owner match: {m.group(0)}")
        
    # Print distinct owners in the file if any
    owners = set(re.findall(r'"owner":\s*"([^"]*)"', content))
    print(f"Owners in events.js: {owners}")

if __name__ == "__main__":
    check_events_js()
