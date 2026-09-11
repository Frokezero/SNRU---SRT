import sqlite3
import json
import os
import re

def search_databases():
    print("=== SEARCHING JSON FILES ===")
    json_files = ['users.json', 'events.json', 'registrations.json', 'participations.json', 'activity_calendar/users.json', 'activity_calendar/events.json']
    for jf in json_files:
        if os.path.exists(jf):
            try:
                with open(jf, 'r', encoding='utf-8') as f:
                    content = f.read()
                    matches_comp = re.findall(r'"[^"]*คอมพิวเตอร์[^"]*"', content)
                    matches_health = re.findall(r'"[^"]*สุขภาพ[^"]*"', content)
                    if matches_comp or matches_health:
                        print(f"\nIn {jf}:")
                        if matches_comp:
                            print(f"  Computer matches: {set(matches_comp)}")
                        if matches_health:
                            print(f"  Health matches: {set(matches_health)}")
            except Exception as e:
                print(f"Error reading {jf}: {e}")

    print("\n=== SEARCHING SQLITE ===")
    if os.path.exists('database.sqlite'):
        try:
            conn = sqlite3.connect('database.sqlite')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r['name'] for r in cursor.fetchall()]
            
            for t in tables:
                cursor.execute(f"PRAGMA table_info({t})")
                cols = [r['name'] for r in cursor.fetchall()]
                
                for col in cols:
                    # Search computer
                    cursor.execute(f"SELECT DISTINCT [{col}] FROM [{t}] WHERE [{col}] LIKE '%คอมพิวเตอร์%' OR [{col}] LIKE '%สุขภาพ%'")
                    rows = cursor.fetchall()
                    if rows:
                        print(f"\nIn Table '{t}', Column '{col}':")
                        for r in rows:
                            print(f"  Value: {r[0]}")
            conn.close()
        except Exception as e:
            print(f"Error searching database.sqlite: {e}")

if __name__ == "__main__":
    search_databases()
