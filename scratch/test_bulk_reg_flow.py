import sys
import os

# Add root folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database import get_db_connection

def test_bulk_reg_flow():
    print("--- Running Bulk Registration Flow Verification ---")
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret'
    app.secret_key = 'test-secret'
    
    # 1. Setup a dummy registration if none exists
    conn = get_db_connection()
    student = conn.execute("SELECT * FROM users WHERE role = 'student' LIMIT 1").fetchone()
    event = conn.execute("SELECT * FROM events LIMIT 1").fetchone()
    
    if not student or not event:
        print("[FAIL] Missing student or event in DB to perform test!")
        conn.close()
        return
        
    student_id = student['username']
    event_id = event['id']
    
    # Check if a registration exists; if not, create one
    reg = conn.execute("SELECT * FROM registrations WHERE event_id = ? AND username = ?", (event_id, student_id)).fetchone()
    if not reg:
        conn.execute("""
            INSERT INTO registrations (id, event_id, event_title, event_date, username, name, major, email, timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
        """, ('test_reg_1', event_id, event['title'], event['date'], student_id, student['name'], student['major'], student['email'], '2026-06-19T12:00:00'))
        conn.commit()
    
    conn.close()
    
    # Run test using Flask client
    with app.test_client() as client:
        # Mock admin login
        with client.session_transaction() as sess:
            sess['username'] = 'admin'
            sess['role'] = 'admin'
            
        # Test 1: Bulk Approve with custom score of 15
        print(f"Approving student {student_id} with score 15...")
        res = client.post('/api/admin/update-status-bulk', json={
            'event_id': event_id,
            'usernames': [student_id],
            'status': 'approved',
            'scores': {student_id: 15}
        })
        
        print(f"Approve Status: {res.status_code}")
        print(f"Response: {res.get_json()}")
        
        # Verify in DB
        conn = get_db_connection()
        part = conn.execute("SELECT * FROM participations WHERE event_id = ? AND username = ?", (event_id, student_id)).fetchone()
        reg_updated = conn.execute("SELECT * FROM registrations WHERE event_id = ? AND username = ?", (event_id, student_id)).fetchone()
        conn.close()
        
        if not part or part['status'] != 'approved' or part['score'] != 15:
            print(f"[FAIL] Participation not correctly approved! DB: {dict(part) if part else None}")
        elif not reg_updated or reg_updated['status'] != 'confirmed':
            print(f"[FAIL] Registration status not synced to confirmed! DB: {dict(reg_updated) if reg_updated else None}")
        else:
            print("[PASS] Bulk approve and score and registration sync succeeded!")
            
        # Test 2: Bulk Cancel registrations
        print(f"Cancelling registration for student {student_id}...")
        res = client.post('/api/admin/registrations/status-bulk', json={
            'event_id': event_id,
            'usernames': [student_id],
            'status': 'cancelled'
        })
        
        print(f"Cancel Status: {res.status_code}")
        print(f"Response: {res.get_json()}")
        
        # Verify in DB
        conn = get_db_connection()
        part_deleted = conn.execute("SELECT * FROM participations WHERE event_id = ? AND username = ?", (event_id, student_id)).fetchone()
        reg_cancelled = conn.execute("SELECT * FROM registrations WHERE event_id = ? AND username = ?", (event_id, student_id)).fetchone()
        conn.close()
        
        if part_deleted:
            print(f"[FAIL] Participation record was not deleted upon registration cancellation! DB: {dict(part_deleted)}")
        elif not reg_cancelled or reg_cancelled['status'] != 'cancelled':
            print(f"[FAIL] Registration status not updated to cancelled! DB: {dict(reg_cancelled) if reg_cancelled else None}")
        else:
            print("[PASS] Bulk cancel registration and participation cleanup succeeded!")

if __name__ == '__main__':
    test_bulk_reg_flow()
