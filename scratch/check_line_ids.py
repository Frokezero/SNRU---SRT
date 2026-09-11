import sqlite3
conn = sqlite3.connect('database.sqlite')
cursor = conn.cursor()
cursor.execute("SELECT username, name, line_id FROM users WHERE line_id IS NOT NULL AND line_id != ''")
rows = cursor.fetchall()
print(f"Users with line_id (Total: {len(rows)}):")
for r in rows:
    print(r)
conn.close()
