import sqlite3

conn = sqlite3.connect('database.sqlite')
cursor = conn.cursor()

# Get total number of users
cursor.execute("SELECT COUNT(*), role FROM users GROUP BY role")
print("User Roles Count in SQLite:")
for row in cursor.fetchall():
    print(row)

# Get some sample student users
cursor.execute("SELECT username, name, major, role FROM users WHERE role = 'student' LIMIT 5")
print("\nSample Students in SQLite:")
for row in cursor.fetchall():
    print(row)

# Get all major and admin users
cursor.execute("SELECT username, name, major, role FROM users WHERE role != 'student'")
print("\nAdmin/Major Users in SQLite:")
for row in cursor.fetchall():
    print(row)

conn.close()
