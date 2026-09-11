import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

filepath = r"d:\โฟลเดอร์ใหม่ (6)\1122220\app.py"
with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

start_pattern = "@app.route('/api/admin/reports/students'"
idx = text.find(start_pattern)
if idx != -1:
    print("--- FOUND get_student_report ---")
    subtext = text[idx:]
    # Let's find the next @app.route
    next_route_idx = subtext.find("@app.route", len(start_pattern))
    if next_route_idx != -1:
        print("--- NEXT ROUTE FOUND ---")
        print(subtext[next_route_idx-100:next_route_idx+1000])
    else:
        print("No next route found in the rest of app.py")
else:
    print("Not found get_student_report")
