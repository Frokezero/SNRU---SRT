import sqlite3
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def test_api_majors_logic():
    try:
        conn = sqlite3.connect('database.sqlite')
        conn.row_factory = sqlite3.Row
        
        # This mirrors the query inside app.py:
        # SELECT DISTINCT major FROM users WHERE major IS NOT NULL AND major != ''
        # And filtering out: 'คณะวิทยาศาสตร์และเทคโนโลยี', 'สโมสรนักศึกษา', 'แอดมินส่วนกลาง'
        cursor = conn.execute("""
            SELECT DISTINCT major 
            FROM users 
            WHERE major IS NOT NULL 
              AND major != '' 
              AND major NOT IN ('คณะวิทยาศาสตร์และเทคโนโลยี', 'สโมสรนักศึกษา', 'แอดมินส่วนกลาง')
            ORDER BY major
        """)
        majors = [row['major'] for row in cursor.fetchall()]
        print(f"Majors dynamically found in database ({len(majors)}):")
        for m in majors:
            print(f"- {m}")
        
        conn.close()
    except Exception as e:
        print(f"Error checking majors: {e}")

if __name__ == "__main__":
    test_api_majors_logic()
