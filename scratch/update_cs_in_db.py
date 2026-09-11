import sqlite3
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

try:
    conn = sqlite3.connect('database.sqlite')
    cursor = conn.cursor()
    
    # Check current count
    cursor.execute("SELECT COUNT(*) FROM users WHERE major = 'CS'")
    count_before = cursor.fetchone()[0]
    print(f"Users with major 'CS' before update: {count_before}")
    
    # Perform update
    cursor.execute("UPDATE users SET major = 'สาขาวิชาวิทยาการคอมพิวเตอร์' WHERE major = 'CS'")
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE major = 'CS'")
    count_after = cursor.fetchone()[0]
    print(f"Users with major 'CS' after update: {count_after}")
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE major = 'สาขาวิชาวิทยาการคอมพิวเตอร์'")
    cs_full_count = cursor.fetchone()[0]
    print(f"Total users with major 'สาขาวิชาวิทยาการคอมพิวเตอร์': {cs_full_count}")
    
    conn.close()
    print("Database updated successfully!")
except Exception as e:
    print(f"Error updating database: {e}")
