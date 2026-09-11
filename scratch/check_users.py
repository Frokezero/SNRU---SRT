import sqlite3

def check_users():
    conn = sqlite3.connect('database.sqlite')
    conn.row_factory = sqlite3.Row
    print("Listing some users:")
    rows = conn.execute('SELECT username, name, role, length(password) as pw_len FROM users LIMIT 20').fetchall()
    for r in rows:
        print(f"Username: {r['username']}, Name: {r['name']}, Role: {r['role']}, PW Len: {r['pw_len']}")
        
    print("\nSearching for username like '69%':")
    rows = conn.execute("SELECT username, name, password, role FROM users WHERE username LIKE '69%'").fetchall()
    for r in rows:
        print(f"Username: {r['username']}, Name: {r['name']}, Password (hashed/plain): {r['password']}, Role: {r['role']}")
        
    conn.close()

if __name__ == "__main__":
    check_users()
