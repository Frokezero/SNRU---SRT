import sqlite3
import sys
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def list_all_users():
    try:
        conn = sqlite3.connect('database.sqlite')
        conn.row_factory = sqlite3.Row
        
        users = conn.execute("SELECT username, password, name, email, major, role, line_id FROM users").fetchall()
        
        print(f"Total Users in SQLite: {len(users)}")
        print("="*80)
        for u in users:
            pwd = u['password']
            # Determine if password is hashed or plain text
            is_hashed = pwd.startswith('pbkdf2:') or pwd.startswith('scrypt:')
            pwd_display = "[HASHED]" if is_hashed else pwd
            print(f"Username: {u['username']}")
            print(f"  Name: {u['name']}")
            print(f"  Role: {u['role']}")
            print(f"  Password: {pwd_display} (Raw: {pwd[:30]}...)")
            print(f"  Email: {u['email']}")
            print(f"  Major: {u['major']}")
            print(f"  LINE ID: {u['line_id']}")
            print("-" * 50)
            
        conn.close()
    except Exception as e:
        print(f"Error querying SQLite: {e}")

if __name__ == "__main__":
    list_all_users()
