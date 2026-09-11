import sqlite3
import sys
import io
from werkzeug.security import check_password_hash

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect('database.sqlite')
cursor = conn.cursor()

# Get count of Year 69 students
cursor.execute("SELECT COUNT(*) FROM users WHERE username LIKE '69%'")
count = cursor.fetchone()[0]
print(f"Total students from Year 69: {count}")

# Check first 5 students to verify details and password hashes
cursor.execute("SELECT username, name, email, major, role, password FROM users WHERE username LIKE '69%' LIMIT 5")
rows = cursor.fetchall()
print("\nSample Year 69 students:")
for row in rows:
    username, name, email, major, role, password_hash = row
    last_3 = username[-3:]
    pw_matches = check_password_hash(password_hash, last_3)
    print(f"ID: {username} | Name: {name} | Major: {major} | Email: '{email}' | Role: {role} | PW Matches last 3 ({last_3})?: {pw_matches}")

conn.close()
