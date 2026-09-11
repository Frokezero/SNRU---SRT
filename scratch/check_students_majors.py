import sqlite3
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def check_students():
    conn = sqlite3.connect('database.sqlite')
    conn.row_factory = sqlite3.Row
    
    # Query all students and group by their major
    rows = conn.execute("SELECT major, COUNT(*) as count FROM users WHERE role = 'student' GROUP BY major").fetchall()
    print("Student majors in database.sqlite:")
    for r in rows:
        print(f"- Major: {repr(r['major'])}, Count: {r['count']}")
        
    conn.close()

if __name__ == "__main__":
    check_students()
