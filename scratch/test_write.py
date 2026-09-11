import sqlite3
import os

def test_write():
    db_file = 'database.sqlite'
    if not os.path.exists(db_file):
        print("DB file does not exist")
        return
        
    try:
        conn = sqlite3.connect(db_file, timeout=10)
        conn.execute('PRAGMA foreign_keys = ON')
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA synchronous=NORMAL')
        
        print("Attempting to insert temporary user...")
        conn.execute("INSERT OR REPLACE INTO users (username, password, name, role) VALUES ('test_temp', '123', 'Test Temp', 'student')")
        conn.commit()
        print("Insert succeeded!")
        
        print("Attempting to delete temporary user...")
        conn.execute("DELETE FROM users WHERE username='test_temp'")
        conn.commit()
        print("Delete succeeded!")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_write()
