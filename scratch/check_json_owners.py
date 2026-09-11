import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def check_json_owners():
    with open('activity_calendar/events.json', 'r', encoding='utf-8') as f:
        events = json.load(f)
    owners = set(e.get('owner', '') for e in events)
    print("activity_calendar/events.json owners:")
    for o in sorted(owners):
        print(f"- {repr(o)}")
        
    print("\nRoot events.json owners:")
    with open('events.json', 'r', encoding='utf-8') as f:
        root_events = json.load(f)
    root_owners = set(e.get('owner', '') for e in root_events)
    for o in sorted(root_owners):
        print(f"- {repr(o)}")

if __name__ == "__main__":
    check_json_owners()
