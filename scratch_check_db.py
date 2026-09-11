import sqlite3
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def check_registrations():
    try:
        conn = sqlite3.connect('database.sqlite')
        conn.row_factory = sqlite3.Row
        
        event_id = "ac19d975-3b42-4dbe-b5da-853e61e2d49c"
        regs = conn.execute("""
            SELECT r.id, r.username, r.name, r.status, u.line_id 
            FROM registrations r
            LEFT JOIN users u ON r.username = u.username
            WHERE r.event_id = ?
        """, (event_id,)).fetchall()
        
        print(f"Registrations found ({len(regs)}):")
        for r in regs:
            print(f"- User: {r['username']}, Name: {r['name']}, Status: {r['status']}, LINE ID: {r['line_id']}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_registrations()
