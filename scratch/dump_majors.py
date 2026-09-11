import sqlite3
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def dump_db():
    conn = sqlite3.connect('database.sqlite')
    conn.row_factory = sqlite3.Row
    
    # 1. Check distinct majors from users table
    rows = conn.execute("SELECT DISTINCT major FROM users").fetchall()
    print("Distinct majors in users table:")
    for r in rows:
        val = r['major']
        if val:
            # Let's try to fix encoding if it looks corrupted
            # Commonly, if utf-8 bytes were read as latin1/cp1252 and then encoded to utf-8
            try:
                fixed = val.encode('cp1252').decode('utf-8')
            except:
                try:
                    fixed = val.encode('latin1').decode('utf-8')
                except:
                    try:
                        fixed = val.encode('utf-8').decode('cp874')
                    except:
                        fixed = val
            print(f"- Raw: {repr(val)} -> Fixed: {repr(fixed)}")
            
    # 2. Check registrations majors
    rows = conn.execute("SELECT DISTINCT major FROM registrations").fetchall()
    print("\nDistinct majors in registrations table:")
    for r in rows:
        val = r['major']
        print(f"- Raw: {repr(val)}")
        
    conn.close()

if __name__ == "__main__":
    dump_db()
