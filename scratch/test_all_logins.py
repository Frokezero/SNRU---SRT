import sqlite3
from werkzeug.security import check_password_hash

conn = sqlite3.connect('database.sqlite')
cursor = conn.cursor()

# Get all users
cursor.execute("SELECT username, name, role, password FROM users")
rows = cursor.fetchall()

candidates = ['admin', 'password', '1234', '123456']

print("=== CHECKING LOGINS AGAINST DEFAULT CANDIDATES ===")
for row in rows:
    username, name, role, password_hash = row
    
    # Check default passwords
    matching_pw = None
    for pw in candidates:
        if check_password_hash(password_hash, pw):
            matching_pw = pw
            break
            
    # For student accounts, also check if last 3 digits of student ID works
    if not matching_pw and role == 'student':
        last_3 = username[-3:]
        if check_password_hash(password_hash, last_3):
            matching_pw = f"last 3 digits ('{last_3}')"
            
    # For student accounts, also check if full student ID works
    if not matching_pw and role == 'student':
        if check_password_hash(password_hash, username):
            matching_pw = f"full student ID ('{username}')"
            
    if matching_pw:
        print(f"User: {username} ({role}) | Name: {name} | PW IS: {matching_pw}")
    else:
        print(f"User: {username} ({role}) | Name: {name} | PW IS: [Unknown custom password]")

conn.close()
