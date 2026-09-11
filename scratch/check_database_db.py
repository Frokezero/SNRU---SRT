import sqlite3
import os

def check_db_db():
    if os.path.exists('database.db'):
        print("database.db exists!")
        print(f"Size: {os.path.getsize('database.db')} bytes")
        try:
            conn = sqlite3.connect('database.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r['name'] for r in cursor.fetchall()]
            print(f"Tables: {tables}")
            
            if 'users' in tables:
                rows = conn.execute("SELECT DISTINCT major FROM users").fetchall()
                print("Distinct majors in database.db users:")
                for r in rows:
                    print(f"- {repr(r['major'])}")
            conn.close()
        except Exception as e:
            print(f"Error reading database.db: {e}")
    else:
        print("database.db does not exist.")

if __name__ == "__main__":
    check_db_db()
