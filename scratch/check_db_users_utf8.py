import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect('database.sqlite')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get all column names of users table
cursor.execute("PRAGMA table_info(users)")
print("Users table columns:")
for row in cursor.fetchall():
    print(dict(row))

# Get existing student users details
cursor.execute("SELECT * FROM users WHERE role = 'student' LIMIT 5")
print("\nSample Student details in database:")
for row in cursor.fetchall():
    print(dict(row))

conn.close()
