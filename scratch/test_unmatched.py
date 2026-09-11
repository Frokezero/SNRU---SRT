import sqlite3
import sys
import json
from werkzeug.security import check_password_hash

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def test_unmatched():
    try:
        conn = sqlite3.connect('database.sqlite')
        conn.row_factory = sqlite3.Row
        
        unmatched_usernames = ['67102122111', '67102122131', '67102122134', '67102122109', '67102105116']
        
        users = conn.execute(
            "SELECT username, password, name, email FROM users WHERE username IN (?, ?, ?, ?, ?)",
            unmatched_usernames
        ).fetchall()
        
        print(f"Testing unmatched users ({len(users)})...")
        
        # We will test:
        # - Email prefixes
        # - Common numeric combinations
        # - Standard defaults
        for u in users:
            username = u['username']
            pwd_hash = u['password']
            name = u['name']
            email = u['email'] or ""
            
            candidates = []
            
            # 1. Email-based candidates
            if email:
                email_prefix = email.split('@')[0]
                candidates.append(email_prefix) # e.g. kritsada.sr67
                candidates.append(email_prefix.split('.')[0]) # e.g. kritsada
                # lowercase versions
                candidates.append(email_prefix.lower())
                candidates.append(email_prefix.split('.')[0].lower())
                
            # 2. Year 67 special candidates
            candidates.extend([
                '123456', '12345678', '123456789', '0000', '1111', '2222', '3333', '4444', '5555', '6666', '7777', '8888', '9999',
                '671021', '67', 'scitech67', 'scitech', 'snru', 'snru1234', 'snru67'
            ])
            
            matched = False
            for c in candidates:
                if c and check_password_hash(pwd_hash, c):
                    print(f"MATCH FOUND for {username} ({name}): password is '{c}'")
                    matched = True
                    break
            if not matched:
                print(f"No match for {username} ({name}) (Email: {email})")
                
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_unmatched()
