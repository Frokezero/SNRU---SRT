import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

filepath = r"d:\โฟลเดอร์ใหม่ (6)\1122220\app.py"
with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

# Let's find get_event_students
start_pattern = "@app.route('/api/admin/event/<event_id>/students'"
idx = text.find(start_pattern)
if idx != -1:
    print("--- FOUND get_event_students ---")
    print(text[idx:idx+1500])
else:
    print("Not found get_event_students")

# Let's find update_status_bulk
start_pattern2 = "@app.route('/api/admin/update-status-bulk'"
idx2 = text.find(start_pattern2)
if idx2 != -1:
    print("\n--- FOUND update_status_bulk ---")
    print(text[idx2:idx2+2500])
else:
    print("Not found update_status_bulk")
