import sqlite3
import sys
from werkzeug.security import check_password_hash

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def check_passwords():
    try:
        conn = sqlite3.connect('database.sqlite')
        conn.row_factory = sqlite3.Row
        
        users = conn.execute("SELECT username, password, name, role, major FROM users").fetchall()
        
        common_passwords = ['1234', 'password', 'admin', '123456', '12345678', '123456789', 'admin123', 'scitech']
        
        print(f"Checking passwords for {len(users)} users...")
        print(f"{'Username':<15} | {'Role':<10} | {'Name':<30} | {'Password Status/Value'}")
        print("-" * 80)
        
        for u in users:
            username = u['username']
            pwd_hash = u['password']
            name = u['name']
            role = u['role']
            
            # 1. Check if raw (not hashed)
            if not (pwd_hash.startswith('scrypt:') or pwd_hash.startswith('pbkdf2:')):
                print(f"{username:<15} | {role:<10} | {name:<30} | Plaintext: {pwd_hash}")
                continue
                
            # 2. Try common passwords
            found_pwd = None
            
            # Try username as password
            if check_password_hash(pwd_hash, username):
                found_pwd = username
            else:
                for cp in common_passwords:
                    if check_password_hash(pwd_hash, cp):
                        found_pwd = cp
                        break
            
            if found_pwd:
                print(f"{username:<15} | {role:<10} | {name:<30} | Match: '{found_pwd}'")
            else:
                print(f"{username:<15} | {role:<10} | {name:<30} | Hashed (unmatched)")
                
        conn.close()
    except Exception as e:
        print(f"Error checking passwords: {e}")

if __name__ == "__main__":
    check_passwords()
