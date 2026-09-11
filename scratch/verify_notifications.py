import sqlite3
import sys

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def parse_thai_date_to_comparable(date_str):
    import re
    from datetime import datetime
    if not date_str or not isinstance(date_str, str):
        return None
    months_map = {
        'ม.ค': 1, 'ก.พ': 2, 'มี.ค': 3, 'เม.ย': 4, 'พ.ค': 5, 'มิ.ย': 6,
        'ก.ค': 7, 'ส.ค': 8, 'ก.ย': 9, 'ต.ค': 10, 'พ.ย': 11, 'ธ.ค': 12,
        'มกราคม': 1, 'กุมภาพันธ์': 2, 'มีนาคม': 3, 'เมษายน': 4, 'พฤษภาคม': 5, 'มิถุนายน': 6,
        'กรกฎาคม': 7, 'สิงหาคม': 8, 'กันยายน': 9, 'ตุลาคม': 10, 'พฤศจิกายน': 11, 'ธันวาคม': 12
    }
    try:
        clean_date = date_str.strip()
        numbers = re.findall(r'\d+', clean_date)
        if not numbers:
            return None
        if len(numbers) == 1:
            day = 1
            year = int(numbers[0])
        else:
            day = int(numbers[0])
            year = int(numbers[-1])
        month = 1
        for m_name, m_idx in months_map.items():
            if m_name in clean_date or m_name.replace('.', '') in clean_date:
                month = m_idx
                break
        if year < 100: 
            year += 2500
        elif year < 2100:
            year += 543
        return datetime(year - 543, month, day).date()
    except Exception as e:
        return None

def simulate_scheduler():
    conn = sqlite3.connect('database.sqlite')
    conn.row_factory = sqlite3.Row
    
    print("=== SIMULATING NOTIFICATION SCHEDULER LOGIC ===")
    
    # Let's inspect the target event
    event_id = "ac19d975-3b42-4dbe-b5da-853e61e2d49c"
    e_row = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if not e_row:
        print("[x] Target event not found!")
        conn.close()
        return
        
    e = dict(e_row)
    print(f"Event: {e['title']}")
    print(f"Date string: {e['date']}")
    
    dt = parse_thai_date_to_comparable(e.get('date', ''))
    print(f"Parsed Comparable Date: {dt}")
    
    # We will simulate two scenarios for today_date:
    # 1. 1 day before: tomorrow_date == dt (so today_date is dt - 1 day)
    # 2. Day of event: today_date == dt
    from datetime import timedelta
    
    scenarios = [
        ("Tomorrow (1 day before)", dt - timedelta(days=1), "tomorrow"),
        ("Today (Day of event)", dt, "today")
    ]
    
    for scenario_name, today_sim, notif_type in scenarios:
        print(f"\n--- Scenario: {scenario_name} (Simulated Today: {today_sim}) ---")
        
        # 1. Fetch confirmed registrations for this event to identify registered users
        regs = conn.execute(
            "SELECT username FROM registrations WHERE event_id = ? AND status = 'confirmed'", 
            (e['id'],)
        ).fetchall()
        registered_usernames = {r['username'] for r in regs}
        
        # 2. Fetch all users who have linked a LINE ID
        users = conn.execute(
            "SELECT username, line_id, name FROM users WHERE line_id != '' AND line_id IS NOT NULL"
        ).fetchall()
        
        print(f"Registered users for event: {list(registered_usernames)}")
        print(f"Total LINE-linked users: {len(users)}")
        
        for u in users:
            name = u['name'] or u['username']
            is_registered = u['username'] in registered_usernames
            
            if notif_type == "tomorrow":
                if is_registered:
                    title = "พรุ่งนี้เจอกันนะครับ! 🔔"
                    subtitle = "แจ้งเตือนล่วงหน้า 1 วันสำหรับกิจกรรมที่คุณได้จองไว้"
                    accent_color = "#0ea5e9"
                else:
                    title = "มีกิจกรรมวันพรุ่งนี้! 📢"
                    subtitle = "ประชาสัมพันธ์กิจกรรมที่กำลังจะจัดขึ้นในวันพรุ่งนี้"
                    accent_color = "#10b981"
            else:  # today
                if is_registered:
                    title = "เริ่มต้นวันนี้แล้วนะ! 📢"
                    subtitle = "แจ้งเตือนวันจัดกิจกรรมที่คุณได้จองสิทธิ์ไว้"
                    accent_color = "#f59e0b"
                else:
                    title = "วันนี้มีกิจกรรมนะ! 🌟"
                    subtitle = "ประชาสัมพันธ์กิจกรรมที่กำลังจัดขึ้นในวันนี้"
                    accent_color = "#8b5cf6"
                    
            print(f"  -> User '{name}' (Registered: {is_registered}):")
            print(f"     Title: {title}")
            print(f"     Subtitle: {subtitle}")
            print(f"     Color: {accent_color}")
            
    conn.close()

if __name__ == "__main__":
    simulate_scheduler()
