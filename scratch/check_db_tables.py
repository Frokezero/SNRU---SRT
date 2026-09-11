import sqlite3

def check_db():
    conn = sqlite3.connect('database.sqlite')
    cursor = conn.cursor()
    # List tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", tables)
    for table_name in tables:
        t_name = table_name[0]
        print(f"\nSchema for {t_name}:")
        cursor.execute(f"PRAGMA table_info({t_name});")
        print(cursor.fetchall())
        cursor.execute(f"PRAGMA foreign_key_list({t_name});")
        print("Foreign Keys:", cursor.fetchall())
    conn.close()

if __name__ == "__main__":
    check_db()
