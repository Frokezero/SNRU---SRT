import openpyxl
import sqlite3
import json
import os
import sys
import io
from werkzeug.security import generate_password_hash

# Ensure terminal output supports UTF-8 on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Database & File Paths
DB_FILE = 'database.sqlite'
USERS_JSON = 'users.json'
EXCEL_FILE = r"D:\โฟลเดอร์ใหม่ (6)\รายชื่อนักศึกษาปี69.xlsx"

# Major mapping defined in requirements
MAJOR_MAP = {
    'คณิตศาสตร์': 'สาขาวิชาคณิตศาสตร์',
    'ชีววิทยา': 'สาขาวิชาชีววิทยา',
    'วิทยาการคอมพิวเตอร์': 'สาขาวิชาวิทยาการคอมพิวเตอร์',
    'วิทยาศาสตร์สิ่งแวดล้อม': 'สาขาวิชาวิทยาศาสตร์สิ่งแวดล้อม',
    'สาธารณสุขศาสตร์': 'สาขาวิชาสาธารณสุขศาสตร์',
    'เคมี': 'สาขาวิชาเคมี',
    'เทคโนโลยีสารสนเทศ': 'สาขาวิชาเทคโนโลยีสารสนเทศ'
}

def seed_students():
    print(f"Loading Excel file: {EXCEL_FILE}...")
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: Excel file not found at {EXCEL_FILE}!")
        return

    wb = openpyxl.load_workbook(EXCEL_FILE, data_only=True)
    sheet = wb.active
    max_row = sheet.max_row
    print(f"Excel loaded. Total rows (including header): {max_row}")

    # Connect to SQLite
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Load existing users from users.json to update it as well
    users_json_data = {}
    if os.path.exists(USERS_JSON):
        try:
            with open(USERS_JSON, 'r', encoding='utf-8') as f:
                users_json_data = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load users.json: {e}")

    inserted_sqlite = 0
    skipped_sqlite = 0
    updated_json = 0

    # Cache password hashes by their last 3 digits to avoid redundant CPU hashing cost
    hash_cache = {}

    for r in range(2, max_row + 1):
        y_in = str(sheet.cell(row=r, column=1).value or '').strip()
        student_id = str(sheet.cell(row=r, column=2).value or '').strip()
        prefix = str(sheet.cell(row=r, column=3).value or '').strip()
        fname = str(sheet.cell(row=r, column=4).value or '').strip()
        lname = str(sheet.cell(row=r, column=5).value or '').strip()
        major_abbr = str(sheet.cell(row=r, column=6).value or '').strip()

        if not student_id or not fname or not lname:
            print(f"Skipping row {r} due to missing vital student info.")
            continue

        # Format student full name
        full_name = f"{prefix}{fname} {lname}".strip()

        # Get last 3 digits of student ID as the plain password
        if len(student_id) >= 3:
            plain_password = student_id[-3:]
        else:
            plain_password = student_id

        # Map major
        mapped_major = MAJOR_MAP.get(major_abbr)
        if not mapped_major:
            print(f"Warning: Unmapped major '{major_abbr}' at row {r}. Using raw value.")
            mapped_major = major_abbr

        # Hash password (utilize cache to run fast)
        if plain_password not in hash_cache:
            hash_cache[plain_password] = generate_password_hash(plain_password)
        hashed_password = hash_cache[plain_password]

        email = "" # Keep email empty initially, student will edit it in their profile
        role = "student"

        # Check if user already exists in SQLite
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (student_id,))
        exists = cursor.fetchone()[0] > 0

        if not exists:
            # Insert into SQLite database
            cursor.execute('''
                INSERT INTO users (username, password, name, email, major, role)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_id, hashed_password, full_name, email, mapped_major, role))
            inserted_sqlite += 1
        else:
            skipped_sqlite += 1

        # Add or update in users.json to keep it in sync
        # If user exists in users.json, preserve their existing password/email unless it's empty
        if student_id not in users_json_data:
            users_json_data[student_id] = {
                "password": hashed_password,
                "name": full_name,
                "email": email,
                "major": mapped_major,
                "role": role
            }
            updated_json += 1
        else:
            # Just update fields that don't reset login
            users_json_data[student_id]["name"] = full_name
            users_json_data[student_id]["major"] = mapped_major
            users_json_data[student_id]["role"] = role

    # Commit SQLite changes
    conn.commit()
    conn.close()

    # Save synchronized users.json
    try:
        with open(USERS_JSON, 'w', encoding='utf-8') as f:
            json.dump(users_json_data, f, ensure_ascii=False, indent=4)
        print(f"Successfully synchronized '{USERS_JSON}'")
    except Exception as e:
        print(f"Error saving '{USERS_JSON}': {e}")

    print("\n=== Seeding Summary ===")
    print(f"New students inserted into SQLite: {inserted_sqlite}")
    print(f"Existing student IDs skipped: {skipped_sqlite}")
    print(f"Total students added to users.json: {updated_json}")
    print("=======================")

if __name__ == "__main__":
    seed_students()
