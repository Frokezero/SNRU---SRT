import sqlite3
import json
import os

def update_scores():
    print("=== Updating Database (database.sqlite) ===")
    if os.path.exists('database.sqlite'):
        conn = sqlite3.connect('database.sqlite')
        conn.row_factory = sqlite3.Row
        
        # 1. Update events
        cursor = conn.cursor()
        cursor.execute("UPDATE events SET score = 100")
        events_updated = cursor.rowcount
        print(f"Updated {events_updated} events in database.sqlite to 100 score.")
        
        # 2. Update participations
        cursor.execute("UPDATE participations SET score = 100")
        participations_updated = cursor.rowcount
        print(f"Updated {participations_updated} participations in database.sqlite to 100 score.")
        
        conn.commit()
        conn.close()
    else:
        print("database.sqlite not found")
        
    print("\n=== Updating JSON Files ===")
    
    # 3. Update events.json
    if os.path.exists('events.json'):
        with open('events.json', 'r', encoding='utf-8') as f:
            events_json = json.load(f)
        
        updated_events_count = 0
        for e in events_json:
            e['score'] = 100
            updated_events_count += 1
            
        with open('events.json', 'w', encoding='utf-8') as f:
            json.dump(events_json, f, ensure_ascii=False, indent=4)
            
        print(f"Updated {updated_events_count} events in events.json to 100 score.")
    else:
        print("events.json not found")
        
    # 4. Update participations.json
    if os.path.exists('participations.json'):
        with open('participations.json', 'r', encoding='utf-8') as f:
            parts_json = json.load(f)
            
        updated_parts_count = 0
        for p in parts_json:
            p['score'] = 100
            updated_parts_count += 1
            
        with open('participations.json', 'w', encoding='utf-8') as f:
            json.dump(parts_json, f, ensure_ascii=False, indent=4)
            
        print(f"Updated {updated_parts_count} participations in participations.json to 100 score.")
    else:
        print("participations.json not found")

if __name__ == '__main__':
    update_scores()
