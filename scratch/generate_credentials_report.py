import sqlite3
import json
import os
from werkzeug.security import check_password_hash

def generate_report():
    sqlite_file = 'database.sqlite'
    json_file = 'users.json'
    artifact_path = r"C:\Users\froke\.gemini\antigravity-ide\brain\986b7f39-2918-48bf-81e8-0a5379426344\user_credentials_report.md"
    
    # 1. Read SQLite Users
    sqlite_users = []
    if os.path.exists(sqlite_file):
        try:
            conn = sqlite3.connect(sqlite_file)
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT username, password, name, role, major, email, line_id FROM users").fetchall()
            sqlite_users = [dict(r) for r in rows]
            conn.close()
        except Exception as e:
            print(f"Error reading SQLite: {e}")

    # 2. Read JSON Users
    json_users = {}
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json_users = json.load(f)
        except Exception as e:
            print(f"Error reading users.json: {e}")

    # 3. Analyze passwords
    common_passwords = ['1234', 'password', 'admin', 'student123']
    
    # Analyze SQLite users
    admin_users = []
    major_users = []
    student_users = []
    
    for u in sqlite_users:
        username = u['username']
        pwd_hash = u['password']
        role = u['role']
        
        # Test password
        plaintext_pwd = "รหัสผ่านแบบ Hash (ไม่พบรหัสทั่วไป)"
        if not (pwd_hash.startswith('scrypt:') or pwd_hash.startswith('pbkdf2:')):
            plaintext_pwd = pwd_hash
        else:
            # check last 3 digits of username
            last3 = username[-3:] if len(username) >= 3 else ""
            if last3 and check_password_hash(pwd_hash, last3):
                plaintext_pwd = f"เลข 3 ตัวท้ายของรหัสนักศึกษา ('{last3}')"
            else:
                for cp in common_passwords:
                    if check_password_hash(pwd_hash, cp):
                        plaintext_pwd = f"'{cp}'"
                        break
        
        u['plaintext_password'] = plaintext_pwd
        
        if role == 'admin':
            admin_users.append(u)
        elif role == 'major':
            major_users.append(u)
        else:
            student_users.append(u)
            
    # Check if there are users in users.json but not in SQLite (e.g. admin with 'admin' password)
    json_only_admins = []
    for username, data in json_users.items():
        if data.get('role') == 'admin':
            pwd_hash = data.get('password')
            plaintext_pwd = "รหัสผ่านแบบ Hash"
            for cp in ['admin', 'password', '1234']:
                if check_password_hash(pwd_hash, cp):
                    plaintext_pwd = f"'{cp}'"
                    break
            
            # Check if this admin is different from SQLite
            exists_in_sqlite = any(su['username'] == username for su in admin_users)
            if not exists_in_sqlite:
                json_only_admins.append({
                    'username': username,
                    'name': data.get('name'),
                    'role': 'admin',
                    'plaintext_password': plaintext_pwd,
                    'major': '-',
                    'email': data.get('email') or '-',
                    'line_id': '-'
                })

    # 4. Generate Markdown
    md = []
    md.append("# 🔑 รายงานข้อมูลบัญชีผู้ใช้งานและรหัสผ่านทั้งหมด (User Credentials Report)")
    md.append("\nเอกสารนี้สรุปบัญชีผู้ใช้งานทั้งหมดในระบบ แบ่งตามบทบาทการทำงานและประเภทของรหัสผ่าน เพื่อให้ผู้ดูแลระบบสามารถตรวจสอบได้ง่ายขึ้น")
    
    # Section 1: Admin Accounts
    md.append("\n## 1. บัญชีผู้ดูแลระบบ (Admin Accounts)")
    md.append("บัญชีสำหรับควบคุมและดูแลระบบกิจกรรมทั้งหมด")
    md.append("\n| ชื่อผู้ใช้ (Username) | ชื่อ-นามสกุล | แหล่งข้อมูล | รหัสผ่าน (Password) | อีเมล |")
    md.append("| --- | --- | --- | --- | --- |")
    for u in admin_users:
        md.append(f"| `{u['username']}` | {u['name']} | SQLite Database | **{u['plaintext_password']}** | {u['email'] or '-'} |")
    for u in json_only_admins:
        md.append(f"| `{u['username']}` | {u['name']} | users.json เท่านั้น | **{u['plaintext_password']}** | {u['email'] or '-'} |")

    # Section 2: Major Admins
    md.append("\n## 2. บัญชีผู้ดูแลประจำสาขาวิชา/สโมสร (Major & SMO Accounts)")
    md.append("บัญชีสำหรับตัวแทนสาขาวิชาและสโมสรนักศึกษาเพื่อจัดการกิจกรรมของตนเอง")
    md.append("\n| ชื่อผู้ใช้ (Username) | หน่วยงาน/สาขาวิชา | รหัสผ่าน (Password) | บทบาท |")
    md.append("| --- | --- | --- | --- |")
    for u in major_users:
        md.append(f"| `{u['username']}` | {u['name']} | **{u['plaintext_password']}** | {u['role']} |")

    # Section 3: Student Accounts
    md.append("\n## 3. บัญชีนักศึกษา (Student Accounts)")
    md.append(f"ปัจจุบันมีบัญชีนักศึกษาทั้งหมดในฐานข้อมูล SQLite: **{len(student_users)} บัญชี**")
    
    # Group students into:
    # A. Seeded students (passwords are last 3 digits of ID)
    # B. Test students (common password '1234')
    # C. Custom/Registered students (encrypted/hashed password)
    seeded_students = []
    test_students = []
    custom_students = []
    
    for u in student_users:
        if "เลข 3 ตัวท้าย" in u['plaintext_password']:
            seeded_students.append(u)
        elif u['plaintext_password'] == "'1234'":
            test_students.append(u)
        else:
            custom_students.append(u)
            
    md.append(f"\n### 3.1 นักศึกษาทั่วไป (ระบบนำเข้าข้อมูลอัตโนมัติ) : **{len(seeded_students)} คน**")
    md.append("> [!NOTE]\n> **สูตรสร้างรหัสผ่าน:** นักศึกษาที่ถูกนำเข้าข้อมูลผ่านไฟล์ Excel รหัสผ่านเริ่มต้นจะเป็น **เลข 3 ตัวท้ายของรหัสนักศึกษา**\n> *ตัวอย่าง: รหัสนักศึกษา `69102101101` -> รหัสผ่านคือ `101`*")
    
    md.append("\n**ตัวอย่างบัญชีนักศึกษาที่นำเข้า:**")
    md.append("\n| รหัสนักศึกษา (Username) | ชื่อ-นามสกุล | สาขาวิชา | รหัสผ่านเริ่มต้น |")
    md.append("| --- | --- | --- | --- |")
    for u in seeded_students[:15]:
        last3 = u['username'][-3:]
        md.append(f"| `{u['username']}` | {u['name']} | {u['major']} | **{last3}** |")
    if len(seeded_students) > 15:
        md.append(f"| ... | ... | ... | ... (และอีก {len(seeded_students) - 15} บัญชี) |")

    if test_students:
        md.append(f"\n### 3.2 บัญชีนักศึกษาสำหรับทดสอบระบบ : **{len(test_students)} คน**")
        md.append("\n| รหัสนักศึกษา (Username) | ชื่อ-นามสกุล | สาขาวิชา | รหัสผ่าน (Password) |")
        md.append("| --- | --- | --- | --- |")
        for u in test_students:
            md.append(f"| `{u['username']}` | {u['name']} | {u['major']} | **1234** |")

    if custom_students:
        md.append(f"\n### 3.3 บัญชีที่สมัครเอง / เปลี่ยนรหัสผ่านแล้ว (Custom Passwords) : **{len(custom_students)} คน**")
        md.append("> [!WARNING]\n> บัญชีเหล่านี้ใช้วิธีสมัครใช้งานด้วยตนเองผ่านหน้าเว็บ หรือมีการเปลี่ยนรหัสผ่านแล้ว รหัสผ่านจะถูกเข้ารหัสแบบทางเดียวเพื่อความปลอดภัย (ไม่สามารถแสดงผลเป็นตัวอักษรธรรมดาได้) แต่ผู้ดูแลระบบ (Admin) สามารถกดรีเซ็ตรหัสผ่านให้ใหม่ได้หากนักศึกษาลืมรหัสผ่าน")
        md.append("\n| รหัสนักศึกษา (Username) | ชื่อ-นามสกุล | สาขาวิชา | สถานะรหัสผ่าน |")
        md.append("| --- | --- | --- | --- |")
        for u in custom_students:
            md.append(f"| `{u['username']}` | {u['name']} | {u['major']} | 🔒 เข้ารหัสปลอดภัย (Hashed) |")
            
    # Write to file
    with open(artifact_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(md))
    print(f"Report generated successfully at: {artifact_path}")

if __name__ == "__main__":
    generate_report()
