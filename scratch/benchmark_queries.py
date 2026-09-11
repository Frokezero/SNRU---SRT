import sqlite3
import time
import sys
import os

# Configure stdout to use utf-8 to prevent encoding errors on Windows
sys.stdout.reconfigure(encoding='utf-8')

TEMP_DB = 'benchmark_temp.sqlite'

def init_temp_db(num_users=5000):
    if os.path.exists(TEMP_DB):
        os.remove(TEMP_DB)
        
    conn = sqlite3.connect(TEMP_DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            major TEXT,
            role TEXT NOT NULL DEFAULT 'student'
        )
    ''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
    
    # Generate bulk users
    users_data = []
    for i in range(num_users):
        username = f"67102105{i:03d}"
        users_data.append((
            username,
            "scrypt:32768:8:1$mockhash",
            f"นักศึกษา ทดสอบท่านที่ {i}",
            f"student_{i}@snru.ac.th",
            "สาขาวิชาวิทยาการคอมพิวเตอร์",
            "student"
        ))
        
    c.executemany('''
        INSERT INTO users (username, password, name, email, major, role)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', users_data)
    
    conn.commit()
    conn.close()
    print(f"✅ สร้างฐานข้อมูลทดสอบชั่วคราวสำเร็จ พร้อมบัญชีผู้ใช้งานจำลอง {num_users} บัญชี")

def mock_load_users():
    # วิธีการแบบเดิม: ดึงข้อมูลทั้งตารางขึ้นมาจัดเก็บไว้ใน RAM ทุกรอบที่เรียกใช้
    conn = sqlite3.connect(TEMP_DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return {r['username']: dict(r) for r in rows}

def mock_db_get_user(username):
    # วิธีการแบบใหม่: คิวรีแบบเจาะจงรายบุคคลด้วยคำสั่ง SQL เจาะจงเป้าหมาย
    conn = sqlite3.connect(TEMP_DB)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return dict(row) if row else None

def run_benchmark():
    num_users = 5000
    init_temp_db(num_users)
    
    target_username = f"67102105{num_users // 2:03d}"  # ค้นหาคนกึ่งกลางรายการ
    iterations = 100
    
    print(f"\n=== กำลังเริ่มทำการทดสอบสแกนวัดความเร็ว (เปรียบเทียบ {iterations} รอบ) ===")
    print(f"ขนาดตารางผู้ใช้: {num_users} แถว (Rows)")
    print(f"เป้าหมายผู้ทดสอบค้นหา: username='{target_username}'\n")
    
    # 1. ทดสอบประสิทธิภาพวิธีแบบเดิม
    start_time = time.time()
    for _ in range(iterations):
        users = mock_load_users()
        user = users.get(target_username)
    old_method_time = time.time() - start_time
    print(f"⏱️ วิธีแบบเดิม (Full Table Scan in RAM): {old_method_time:.4f} วินาที")
    
    # 2. ทดสอบประสิทธิภาพวิธีแบบใหม่
    start_time = time.time()
    for _ in range(iterations):
        user = mock_db_get_user(target_username)
    new_method_time = time.time() - start_time
    print(f"⚡ วิธีแบบใหม่ (Targeted SQL Query):     {new_method_time:.4f} วินาที")
    
    # คำนวณอัตราความเร็วที่เหนือกว่า
    speedup = old_method_time / new_method_time if new_method_time > 0 else 999
    print("-" * 60)
    print(f"🎯 ผลลัพธ์: วิธีแบบใหม่ทำงานรวดเร็วขึ้นถึง {speedup:.1f} เท่า! 🚀")
    print("-" * 60)
    
    # Clean up
    if os.path.exists(TEMP_DB):
        try:
            os.remove(TEMP_DB)
            # Remove journal file if exists
            if os.path.exists(TEMP_DB + "-journal"):
                os.remove(TEMP_DB + "-journal")
            if os.path.exists(TEMP_DB + "-wal"):
                os.remove(TEMP_DB + "-wal")
            if os.path.exists(TEMP_DB + "-shm"):
                os.remove(TEMP_DB + "-shm")
        except Exception:
            pass

if __name__ == '__main__':
    run_benchmark()
