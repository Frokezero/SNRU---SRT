import sqlite3
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def check_owners():
    conn = sqlite3.connect('database.sqlite')
    conn.row_factory = sqlite3.Row
    
    rows = conn.execute("SELECT DISTINCT owner FROM events").fetchall()
    print("Distinct event owners in database.sqlite:")
    for r in rows:
        val = r['owner']
        print(f"- {repr(val)}")
        
    print("\nDistinct event categories:")
    rows_cat = conn.execute("SELECT DISTINCT category FROM events").fetchall()
    for r in rows_cat:
        val = r['category']
        print(f"- {repr(val)}")
        
    # Let's inspect the target event
    event_id = "ac19d975-3b42-4dbe-b5da-853e61e2d49c"
    e = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if e:
        print(f"\nTarget Event Owner: {repr(e['owner'])}")
        
    conn.close()

if __name__ == "__main__":
    check_owners()
