import sqlite3
import sys
from werkzeug.security import check_password_hash

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def test_all_students_sqlite():
    try:
        conn = sqlite3.connect('database.sqlite')
        conn.row_factory = sqlite3.Row
        
        users = conn.execute("SELECT username, password, name, role FROM users WHERE role = 'student'").fetchall()
        
        print(f"Total students in SQLite: {len(users)}")
        
        matched_count = 0
        unmatched = []
        
        for u in users:
            username = u['username']
            h = u['password']
            name = u['name']
            
            # Candidates
            last3 = username[-3:] if len(username) >= 3 else ''
            last4 = username[-4:] if len(username) >= 4 else ''
            candidates = [last3, last4, username, '1234', 'password']
            
            matched = False
            for c in candidates:
                if c and check_password_hash(h, c):
                    matched = True
                    matched_count += 1
                    # print(f"Student {username} ({name}) -> Password is: '{c}'")
                    break
            if not matched:
                unmatched.append((username, name))
                
        print(f"Successfully matched: {matched_count} / {len(users)}")
        print(f"Unmatched students: {len(unmatched)}")
        print("Sample unmatched:")
        for unm in unmatched[:15]:
            print(f"  - {unm[0]}: {unm[1]}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_all_students_sqlite()
