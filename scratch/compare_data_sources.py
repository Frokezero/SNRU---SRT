import sqlite3
import json
import os

print("=== COMPARING SQLITE VS JSON BACKUPS ===")

def count_json(path):
    if not os.path.exists(path):
        return 0, "File not found"
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return len(data), "OK (Dict)"
            elif isinstance(data, list):
                return len(data), "OK (List)"
            else:
                return 0, f"OK (Unknown type: {type(data)})"
    except Exception as e:
        return 0, f"Error: {e}"

# SQLite connection
conn = sqlite3.connect('database.sqlite')
cursor = conn.cursor()

# 1. Users
cursor.execute("SELECT COUNT(*) FROM users")
users_db = cursor.fetchone()[0]
users_json, users_json_status = count_json('users.json')
print(f"Users: SQLite = {users_db} | JSON = {users_json} ({users_json_status})")

# 2. Events
cursor.execute("SELECT COUNT(*) FROM events")
events_db = cursor.fetchone()[0]
events_json, events_json_status = count_json('events.json')
print(f"Events: SQLite = {events_db} | JSON = {events_json} ({events_json_status})")

# 3. Participations
cursor.execute("SELECT COUNT(*) FROM participations")
parts_db = cursor.fetchone()[0]
parts_json, parts_json_status = count_json('participations.json')
print(f"Participations: SQLite = {parts_db} | JSON = {parts_json} ({parts_json_status})")

# 4. Registrations
cursor.execute("SELECT COUNT(*) FROM registrations")
regs_db = cursor.fetchone()[0]
regs_json, regs_json_status = count_json('registrations.json')
print(f"Registrations: SQLite = {regs_db} | JSON = {regs_json} ({regs_json_status})")

conn.close()
