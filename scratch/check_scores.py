import sqlite3
import json
import os

def check_scores():
    print("=== SQLite Database ===")
    if os.path.exists('database.sqlite'):
        conn = sqlite3.connect('database.sqlite')
        conn.row_factory = sqlite3.Row
        
        # Check events
        events = conn.execute('SELECT id, title, score FROM events').fetchall()
        print(f"Total events in SQLite: {len(events)}")
        event_scores = [e['score'] for e in events]
        print(f"Event scores: min={min(event_scores or [0])}, max={max(event_scores or [0])}, set of scores={set(event_scores)}")
        
        # Check participations
        parts = conn.execute('SELECT id, student_name, event_title, score FROM participations').fetchall()
        print(f"Total participations in SQLite: {len(parts)}")
        part_scores = [p['score'] for p in parts]
        print(f"Participation scores: min={min(part_scores or [0])}, max={max(part_scores or [0])}, set of scores={set(part_scores)}")
        
        conn.close()
    else:
        print("database.sqlite not found")
        
    print("\n=== JSON Files ===")
    if os.path.exists('events.json'):
        with open('events.json', 'r', encoding='utf-8') as f:
            events_json = json.load(f)
            print(f"Total events in events.json: {len(events_json)}")
            json_scores = [e.get('score', 0) for e in events_json]
            print(f"Event scores in JSON: min={min(json_scores or [0])}, max={max(json_scores or [0])}, set={set(json_scores)}")
    else:
        print("events.json not found")
        
    if os.path.exists('participations.json'):
        with open('participations.json', 'r', encoding='utf-8') as f:
            parts_json = json.load(f)
            print(f"Total participations in participations.json: {len(parts_json)}")
            part_json_scores = [p.get('score', 0) for p in parts_json]
            print(f"Participation scores in JSON: min={min(part_json_scores or [0])}, max={max(part_json_scores or [0])}, set={set(part_json_scores)}")
    else:
        print("participations.json not found")

if __name__ == '__main__':
    check_scores()
