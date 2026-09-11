import json
from werkzeug.security import check_password_hash

def test_67():
    with open('users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)
        
    targets = ['67102122111', '67102122131', '67102105116']
    
    for username in targets:
        if username not in users:
            print(f"User {username} not found")
            continue
        h = users[username]['password']
        last3 = username[-3:]
        last4 = username[-4:]
        full = username
        
        candidates = [last3, last4, full, '1234', 'password', 'admin']
        matched = False
        for c in candidates:
            if check_password_hash(h, c):
                print(f"User {username} password is: '{c}'")
                matched = True
                break
        if not matched:
            print(f"User {username} password is UNKNOWN")

if __name__ == "__main__":
    test_67()
