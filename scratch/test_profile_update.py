import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
import sqlite3
import io

# Setup UTF-8 for console output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("Starting integration test for profile update...")

client = app.test_client()

# Login as student '69102101101' via session transaction
with client.session_transaction() as sess:
    sess['username'] = '69102101101'

# 1. Get initial profile details
res = client.get('/api/me')
print(f"\n1. Initial /api/me response: {res.status_code}")
print(res.get_json())

# 2. Send invalid email format to test validation
res = client.post('/api/user/update-profile', json={"email": "invalid-email"})
print(f"\n2. Invalid email format response: {res.status_code}")
print(res.get_json())

# 3. Send valid email format to test success
test_email = "tee.tha69@snru.ac.th"
res = client.post('/api/user/update-profile', json={"email": test_email})
print(f"\n3. Valid email update response: {res.status_code}")
print(res.get_json())

# 4. Get profile details again to verify it has updated
res = client.get('/api/me')
json_data = res.get_json()
print(f"\n4. Post-update /api/me response: {res.status_code}")
print(json_data)

# Verify email matches what we set
if json_data and json_data.get('user', {}).get('email') == test_email:
    print("\nSUCCESS: Email successfully retrieved from `/api/me`!")
else:
    print("\nFAILURE: Email does not match `/api/me`!")

# 5. Check in SQLite database directly
conn = sqlite3.connect('database.sqlite')
cursor = conn.cursor()
cursor.execute("SELECT username, name, email FROM users WHERE username = '69102101101'")
row = cursor.fetchone()
print(f"\n5. SQLite query result for '69102101101': {row}")
conn.close()

if row and row[2] == test_email:
    print("SUCCESS: SQLite database contains the updated email!")
else:
    print("FAILURE: SQLite database does not contain the updated email!")
