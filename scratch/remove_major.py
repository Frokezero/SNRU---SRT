import sqlite3
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

try:
    conn = sqlite3.connect('database.sqlite')
    cursor = conn.cursor()
    
    # Check if there are any users with this major
    cursor.execute("SELECT username, name, role FROM users WHERE major = 'สาขาวิชาคหกรรมศาสตร์'")
    rows = cursor.fetchall()
    print(f"Found {len(rows)} user(s) with major='สาขาวิชาคหกรรมศาสตร์' before deletion:")
    for r in rows:
        print(f"- Username: {r[0]}, Name: {r[1]}, Role: {r[2]}")
        
    # Delete them
    cursor.execute("DELETE FROM users WHERE major = 'สาขาวิชาคหกรรมศาสตร์'")
    conn.commit()
    print("Deleted successfully!")
    
    # Check count after
    cursor.execute("SELECT COUNT(*) FROM users WHERE major = 'สาขาวิชาคหกรรมศาสตร์'")
    count_after = cursor.fetchone()[0]
    print(f"Users with major='สาขาวิชาคหกรรมศาสตร์' after deletion: {count_after}")
    
    conn.close()
except Exception as e:
    print(f"Error removing major: {e}")
