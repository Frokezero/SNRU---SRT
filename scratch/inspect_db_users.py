import sqlite3

conn = sqlite3.connect('database.sqlite')
conn.row_factory = sqlite3.Row
users = conn.execute("SELECT username, name, role, email FROM users WHERE role IN ('admin', 'major')").fetchall()
conn.close()

print("Admin/Major users:")
for u in users:
    print(dict(u))
