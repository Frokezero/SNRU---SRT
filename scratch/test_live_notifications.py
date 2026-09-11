import os
import sys
import json
import sqlite3
import urllib.request
from dotenv import load_dotenv

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def make_premium_notification_flex(title, subtitle, items, accent_color='#0ea5e9', button_text=None, button_url=None):
    contents = []
    for k, v in items:
        contents.append({
            "type": "box",
            "layout": "horizontal",
            "margin": "md",
            "contents": [
                {
                    "type": "text",
                    "text": str(k),
                    "size": "sm",
                    "color": "#94a3b8",
                    "flex": 3
                },
                {
                    "type": "text",
                    "text": str(v),
                    "size": "sm",
                    "color": "#e2e8f0",
                    "flex": 7,
                    "weight": "bold",
                    "wrap": True
                }
            ]
        })
        
    bubble = {
        "type": "flex",
        "altText": f"🔔 {title} - SciTech Activity",
        "contents": {
            "type": "bubble",
            "size": "mega",
            "styles": {
                "header": {"backgroundColor": "#0f172a"},
                "body": {"backgroundColor": "#1e293b"},
                "footer": {"backgroundColor": "#0f172a"}
            },
            "header": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "20px",
                "contents": [
                    {
                        "type": "text",
                        "text": str(title),
                        "weight": "bold",
                        "size": "xl",
                        "color": "#ffffff"
                    },
                    {
                        "type": "text",
                        "text": str(subtitle),
                        "size": "xs",
                        "color": accent_color,
                        "margin": "xs",
                        "weight": "bold"
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "20px",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "backgroundColor": "#33415540",
                        "cornerRadius": "md",
                        "paddingAll": "12px",
                        "contents": contents
                    }
                ]
            }
        }
    }
    
    if button_text and button_url:
        bubble["contents"]["footer"] = {
            "type": "box",
            "layout": "vertical",
            "paddingAll": "12px",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": accent_color,
                    "action": {
                        "type": "uri",
                        "label": str(button_text),
                        "uri": str(button_url)
                    },
                    "height": "sm"
                }
            ]
        }
    return bubble

def send_line_notification(to_id, message):
    try:
        token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
        if not token or not to_id:
            return False
        
        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        if isinstance(message, (dict, list)):
            messages = [message] if isinstance(message, dict) else message
        else:
            messages = [
                {
                    "type": "text",
                    "text": str(message)
                }
            ]
        
        body = {
            "to": to_id,
            "messages": messages
        }
        
        req_data = json.dumps(body).encode('utf-8')
        req = urllib.request.Request(url, data=req_data, headers=headers, method='POST')
        with urllib.request.urlopen(req) as response:
            response.read()
        return True
    except Exception as e:
        print(f"[x] Failed to send LINE notification to {to_id}: {e}")
        return False

def get_ngrok_url():
    try:
        url = "http://127.0.0.1:4040/api/tunnels"
        req = urllib.request.Request(url, method='GET')
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode('utf-8'))
        tunnels = data.get('tunnels', [])
        for t in tunnels:
            if t.get('proto') == 'https' or t.get('public_url', '').startswith('https://'):
                return t.get('public_url')
    except Exception:
        pass
    return "https://synopsis-exponent-peddling.ngrok-free.dev"  # Fallback

def test_live_notifications():
    load_dotenv()
    conn = sqlite3.connect('database.sqlite')
    conn.row_factory = sqlite3.Row
    
    event_id = "ac19d975-3b42-4dbe-b5da-853e61e2d49c"
    e_row = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if not e_row:
        print("[x] Event not found!")
        conn.close()
        return
    e = dict(e_row)
    
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
    
    print(f"[*] Sending LIVE test pre-event notifications (Scenario: 1 Day Before) to {len(users)} users...")
    
    for u in users:
        line_id = u['line_id']
        name = u['name'] or u['username']
        is_registered = u['username'] in registered_usernames
        
        location = e.get('location') or 'ยังไม่ระบุสถานที่'
        date_str = e.get('date') or ''
        
        if is_registered:
            title = "พรุ่งนี้เจอกันนะครับ! 🔔"
            subtitle = "แจ้งเตือนล่วงหน้า 1 วันสำหรับกิจกรรมที่คุณได้จองไว้ (ทดสอบระบบ)"
            accent_color = "#0ea5e9"  # Sky blue
        else:
            title = "มีกิจกรรมวันพรุ่งนี้! 📢"
            subtitle = "ประชาสัมพันธ์กิจกรรมที่กำลังจะจัดขึ้นในวันพรุ่งนี้ (ทดสอบระบบ)"
            accent_color = "#10b981"  # Emerald green
            
        msg = make_premium_notification_flex(
            title=title,
            subtitle=subtitle,
            items=[
                ("ผู้รับ", name),
                ("กิจกรรม", e['title']),
                ("วันจัดงาน", date_str),
                ("สถานที่", location)
            ],
            accent_color=accent_color,
            button_text="ดูข้อมูลโปรไฟล์และกิจกรรม",
            button_url=f"{get_ngrok_url()}/profile"
        )
        
        print(f"[*] Sending to {name} ({'Registered' if is_registered else 'Unregistered'})... ", end="")
        success = send_line_notification(line_id, msg)
        if success:
            print("SUCCESS")
        else:
            print("FAILED")
            
    conn.close()

if __name__ == "__main__":
    test_live_notifications()
