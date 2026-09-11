import io
import time
import json
import hmac
import hashlib
import base64
import os
import sys

# Add root folder to path so app can be imported properly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, get_db_connection, db_get_user, db_save_user, db_delete_user

# Enable testing mode
app.config['TESTING'] = True
client = app.test_client()

# Create a test student user if not exists
test_username = "test_student_checkin"
test_user = db_get_user(test_username)
if not test_user:
    db_save_user(test_username, {
        "password": "testpassword",
        "name": "Test Student Checkin",
        "email": "test@student.com",
        "major": "CS",
        "role": "student",
        "line_id": ""
    })

# Also we need an event in database
conn = get_db_connection()
event_id = "test_event_checkin"
conn.execute("INSERT OR IGNORE INTO events (id, title, date, category, score, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?)",
             (event_id, "Test Event", "12 มิ.ย. 69", "Academic", 5, 17.18994, 104.09153))
# Clean up any existing participations
conn.execute("DELETE FROM participations WHERE username = ? AND event_id = ?", (test_username, event_id))
conn.commit()
conn.close()

# Generate a valid check-in token
# Token payload format: {"event_id": event_id, "timestamp": time.time()}
payload = {
    "event_id": event_id,
    "timestamp": int(time.time())
}
payload_str = json.dumps(payload)
secret_key = app.secret_key
signature = hmac.new(secret_key.encode('utf-8'), payload_str.encode('utf-8'), hashlib.sha256).hexdigest()
token_raw = f"{payload_str}.{signature}"
token = base64.urlsafe_b64encode(token_raw.encode('utf-8')).decode('utf-8')

# Login by placing username in session
with client.session_transaction() as sess:
    sess['username'] = test_username

print("Running test cases:")
print("-------------------")

# Test case 1: Post checkin with no file - should fail
res = client.post('/api/student/checkin', data={
    'token': token,
    'latitude': 17.18994,
    'longitude': 104.09153
})
print("Test 1 (No file) Status:", res.status_code)
print("Test 1 (No file) Response:", res.get_json())
print()

# Test case 2: Post checkin with wrong file type - should fail
data = {
    'token': token,
    'latitude': 17.18994,
    'longitude': 104.09153,
    'file': (io.BytesIO(b"not an image"), "test.txt")
}
res = client.post('/api/student/checkin', data=data, content_type='multipart/form-data')
print("Test 2 (TXT file) Status:", res.status_code)
print("Test 2 (TXT file) Response:", res.get_json())
print()

# Test case 3: Post checkin with valid image - should succeed
# Let's generate a valid PNG image using Pillow
from PIL import Image
img = Image.new('RGB', (10, 10), color = 'blue')
img_bytes = io.BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)

data = {
    'token': token,
    'latitude': 17.18994,
    'longitude': 104.09153,
    'file': (img_bytes, "test.png")
}
res = client.post('/api/student/checkin', data=data, content_type='multipart/form-data')
print("Test 3 (Valid PNG) Status:", res.status_code)
json_res = res.get_json()
print("Test 3 (Valid PNG) Response:", json_res)

# Let's verify that the participation row was created and stores a real file
if json_res and json_res.get('success'):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM participations WHERE username = ? AND event_id = ?", (test_username, event_id)).fetchone()
    conn.close()
    if row:
        print("Success: Database participation row created!")
        print("Row details:", dict(row))
        img_url = row['image_url']
        # Remove leading slash if present to locate the file locally
        local_path = img_url.lstrip('/')
        if os.path.exists(local_path):
            print(f"Success: File exists at {local_path} (Size: {os.path.getsize(local_path)} bytes)")
            # Clean up the file
            try:
                os.remove(local_path)
                print("Cleaned up saved test image file.")
            except Exception as e:
                print(f"Failed to remove file: {e}")
        else:
            print(f"Error: File NOT found at {local_path}")
    else:
        print("Error: Database row was not found!")
print()

# Clean up database test records
db_delete_user(test_username)
conn = get_db_connection()
conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
conn.commit()
conn.close()
print("Cleaned up database test records.")
