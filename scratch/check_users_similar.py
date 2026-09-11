import sqlite3

def find_similar():
    conn = sqlite3.connect('database.sqlite')
    conn.row_factory = sqlite3.Row
    
    print("Searching for username='67102122101':")
    row = conn.execute("SELECT * FROM users WHERE username = '67102122101'").fetchone()
    if row:
        print(dict(row))
    else:
        print("Not found.")
        
    print("\nUsers starting with '67102122':")
    rows = conn.execute("SELECT username, name, major FROM users WHERE username LIKE '67102122%'").fetchall()
    for r in rows:
        print(f"Username: {r['username']}, Name: {r['name']}, Major: {r['major']}")
        
    print("\nUsers starting with '69102106':")
    rows = conn.execute("SELECT username, name, major FROM users WHERE username LIKE '69102106%' LIMIT 5").fetchall()
    for r in rows:
        print(f"Username: {r['username']}, Name: {r['name']}, Major: {r['major']}")
        
    conn.close()

if __name__ == "__main__":
    find_similar()
