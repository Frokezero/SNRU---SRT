import sqlite3
import sys
from werkzeug.security import check_password_hash

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def analyze_user_passwords():
    try:
        conn = sqlite3.connect('database.sqlite')
        conn.row_factory = sqlite3.Row
        
        users = conn.execute("SELECT username, password, name, role, major FROM users").fetchall()
        conn.close()
        
        print(f"Total users: {len(users)}")
        
        # Group users by their exact password hash value
        hash_groups = {}
        for u in users:
            pwd_hash = u['password']
            if pwd_hash not in hash_groups:
                hash_groups[pwd_hash] = []
            hash_groups[pwd_hash].append(u)
            
        print(f"Number of unique password hashes: {len(hash_groups)}")
        print("=" * 80)
        
        common_passwords = ['1234', 'password', 'admin', '123456', '12345678', '123456789', 'admin123', 'scitech']
        
        # Verify each unique hash once
        hash_to_plain = {}
        for pwd_hash in hash_groups.keys():
            if not (pwd_hash.startswith('scrypt:') or pwd_hash.startswith('pbkdf2:')):
                hash_to_plain[pwd_hash] = f"Plaintext: {pwd_hash}"
                continue
                
            matched = False
            # Check if it matches any user's username in that group (if it's a small group)
            group_users = hash_groups[pwd_hash]
            if len(group_users) <= 5:
                for gu in group_users:
                    if check_password_hash(pwd_hash, gu['username']):
                        hash_to_plain[pwd_hash] = f"Matches username '{gu['username']}'"
                        matched = True
                        break
            
            if not matched:
                for cp in common_passwords:
                    if check_password_hash(pwd_hash, cp):
                        hash_to_plain[pwd_hash] = f"Match: '{cp}'"
                        matched = True
                        break
                        
            if not matched:
                hash_to_plain[pwd_hash] = "Unknown Hash"
                
        # Now print the summary of groups
        for idx, (pwd_hash, group) in enumerate(hash_groups.items(), 1):
            plain_desc = hash_to_plain[pwd_hash]
            print(f"Group #{idx} (Password: {plain_desc})")
            print(f"  Total users in this group: {len(group)}")
            print(f"  Sample users (up to 10):")
            for u in group[:10]:
                print(f"    - {u['username']} | {u['role']} | {u['name']} | {u['major']}")
            if len(group) > 10:
                print(f"    - ... and {len(group) - 10} more users")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_user_passwords()
