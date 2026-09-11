import sqlite3
from werkzeug.security import check_password_hash

conn = sqlite3.connect('database.sqlite')
cursor = conn.cursor()

# Get all non-student users and check passwords
cursor.execute("SELECT username, name, role, password FROM users WHERE role != 'student'")
rows = cursor.fetchall()
print("Non-student users and password hashes:")
for row in rows:
    username, name, role, password_hash = row
    # Test common default passwords if possible, or just print hash prefix
    print(f"Username: {username} | Name: {name} | Role: {role} | Hash Prefix: {password_hash[:30]}")

conn.close()
