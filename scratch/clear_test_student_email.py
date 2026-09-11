import sqlite3
import json
import os

DB_FILE = 'database.sqlite'
USERS_JSON = 'users.json'
target_id = '69102101101'

# Restore SQLite
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute("UPDATE users SET email = '' WHERE username = ?", (target_id,))
conn.commit()
conn.close()

# Restore users.json
if os.path.exists(USERS_JSON):
    with open(USERS_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if target_id in data:
        data[target_id]['email'] = ''
        with open(USERS_JSON, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

print("Test student email restored to empty string successfully.")
