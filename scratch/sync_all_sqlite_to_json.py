import sqlite3
import json
import os

DB_FILE = 'database.sqlite'

def sync_all():
    print("=== STARTING FULL DATABASE SYNC (SQLITE -> JSON) ===")
    if not os.path.exists(DB_FILE):
        print(f"Error: {DB_FILE} not found!")
        return

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Sync Users
    try:
        cursor.execute("SELECT * FROM users")
        users_rows = cursor.fetchall()
        users_dict = {}
        for row in users_rows:
            r = dict(row)
            username = r.pop('username')
            users_dict[username] = r
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(users_dict, f, ensure_ascii=False, indent=4)
        print(f"Synced {len(users_dict)} users to 'users.json'")
    except Exception as e:
        print(f"Error syncing users: {e}")

    # 2. Sync Events
    try:
        cursor.execute("SELECT * FROM events")
        events_rows = cursor.fetchall()
        events_list = []
        for row in events_rows:
            r = dict(row)
            # Convert integer booleans back to True/False for compatibility
            r['hidden'] = bool(r.get('hidden', 0))
            r['registration_open'] = bool(r.get('registration_open', 0))
            # Convert none values or keep empty
            r['registration_start'] = r.get('registration_start') or ""
            r['registration_end'] = r.get('registration_end') or ""
            r['latitude'] = float(r.get('latitude') or 17.18994)
            r['longitude'] = float(r.get('longitude') or 104.09153)
            events_list.append(r)
        with open('events.json', 'w', encoding='utf-8') as f:
            json.dump(events_list, f, ensure_ascii=False, indent=4)
        print(f"Synced {len(events_list)} events to 'events.json'")
    except Exception as e:
        print(f"Error syncing events: {e}")

    # 3. Sync Participations
    try:
        cursor.execute("SELECT * FROM participations")
        parts_rows = cursor.fetchall()
        parts_list = []
        for row in parts_rows:
            r = dict(row)
            parts_list.append(r)
        with open('participations.json', 'w', encoding='utf-8') as f:
            json.dump(parts_list, f, ensure_ascii=False, indent=4)
        print(f"Synced {len(parts_list)} participations to 'participations.json'")
    except Exception as e:
        print(f"Error syncing participations: {e}")

    # 4. Sync Registrations
    try:
        cursor.execute("SELECT * FROM registrations")
        regs_rows = cursor.fetchall()
        regs_list = []
        for row in regs_rows:
            r = dict(row)
            regs_list.append(r)
        with open('registrations.json', 'w', encoding='utf-8') as f:
            json.dump(regs_list, f, ensure_ascii=False, indent=4)
        print(f"Synced {len(regs_list)} registrations to 'registrations.json'")
    except Exception as e:
        print(f"Error syncing registrations: {e}")

    conn.close()
    print("=== SYNC COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    sync_all()
