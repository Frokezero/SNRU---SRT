import sqlite3
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('database.sqlite')
conn.row_factory = sqlite3.Row

rows = conn.execute("SELECT username, name, major, role FROM users WHERE major = 'CS'").fetchall()
print(f"Users with major='CS' ({len(rows)}):")
for r in rows:
    print(f"- Username: {r['username']}, Name: {r['name']}, Major: {r['major']}, Role: {r['role']}")

conn.close()
