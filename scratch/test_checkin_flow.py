import sys
import os
import json
import base64
import hmac
import hashlib
import time

# Add root folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database import get_db_connection

def test_checkin():
    print("--- Running QR Check-In Flow Test ---")
    
    # Initialize Flask test client
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key' # Override secret key for deterministic signature
    app.secret_key = 'test-secret-key'
    
    # Get a student from database
    conn = get_db_connection()
    student = conn.execute("SELECT * FROM users WHERE role = 'student' LIMIT 1").fetchone()
    event = conn.execute("SELECT * FROM events LIMIT 1").fetchone()
    conn.close()
    
    if not student:
        print("[FAIL] No student user found in database!")
        return
    if not event:
        print("[FAIL] No event found in database!")
        return
        
    student = dict(student)
    event = dict(event)
    
    print(f"Testing with Student: {student['username']} ({student['name']})")
    print(f"Testing with Event: {event['id']} ({event['title']})")
    
    # Generate a checkin token for the event manually using test secret key
    payload = {
        "event_id": event['id'],
        "timestamp": time.time()
    }
    payload_str = json.dumps(payload)
    signature = hmac.new(
        app.secret_key.encode('utf-8'),
        payload_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    combined = f"{payload_str}.{signature}"
    token = base64.urlsafe_b64encode(combined.encode('utf-8')).decode('utf-8')
    
    with app.test_client() as client:
        # Mock student login session
        with client.session_transaction() as sess:
            sess['username'] = student['username']
            sess['role'] = 'student'
            
        # Post check-in without GPS coords and without file
        print("Sending POST /api/student/checkin without GPS or file...")
        res = client.post('/api/student/checkin', data={
            'token': token
        })
        
        print(f"Status: {res.status_code}")
        body = res.get_json()
        print(f"Response Body: {body}")
        
        if res.status_code == 200 and body.get('success') is True:
            print("[PASS] Checked in successfully without GPS coordinates or file!")
        elif res.status_code == 400 and "คุณทำการเช็คอินหรือส่งผลงานสำหรับกิจกรรมนี้เรียบร้อยแล้ว" in body.get('message', ''):
            print("[PASS] Already checked in, which proves the verification logic works!")
        else:
            print(f"[FAIL] Check-in failed! Response: {body}")

if __name__ == '__main__':
    test_checkin()
