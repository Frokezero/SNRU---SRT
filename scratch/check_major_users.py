import sqlite3
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('database.sqlite')
conn.row_factory = sqlite3.Row

rows = conn.execute("""
    SELECT major, role, COUNT(*) as count 
    FROM users 
    GROUP BY major, role 
    ORDER BY major, role
""").fetchall()

print("User count by Major and Role in database:")
for r in rows:
    major = r['major'] if r['major'] else '(Empty)'
    print(f"- Major: {major:35} | Role: {r['role']:10} | Count: {r['count']}")

conn.close()
