import sqlite3

def find_user():
    conn = sqlite3.connect('database.sqlite')
    conn.row_factory = sqlite3.Row
    
    # Try exact match
    print("Exact search for '69102122101':")
    row = conn.execute("SELECT * FROM users WHERE username = '69102122101'").fetchone()
    if row:
        print(dict(row))
    else:
        print("Not found.")
        
    # Search for anything starting with '6910212'
    print("\nSearch for starting with '6910212':")
    rows = conn.execute("SELECT username, name, password, role FROM users WHERE username LIKE '6910212%'").fetchall()
    for r in rows:
        print(f"Username: {r['username']}, Name: {r['name']}, Password: {r['password']}")
        
    # Search for anything starting with '691021'
    print("\nSearch for starting with '691021':")
    rows = conn.execute("SELECT username, name FROM users WHERE username LIKE '691021%' LIMIT 10").fetchall()
    for r in rows:
        print(f"Username: {r['username']}, Name: {r['name']}")
        
    conn.close()

if __name__ == "__main__":
    find_user()
