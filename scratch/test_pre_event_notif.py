import os
import sys
import json
import urllib.request
from dotenv import load_dotenv

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def make_premium_notification_flex(title, subtitle, items, accent_color='#0ea5e9', button_text=None, button_url=None):
    # Construct rows of items (key-value pairs)
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
            print("[x] Missing token or user ID")
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

def main():
    load_dotenv()
    
    # Target user (Aranya or Kritsada) who just registered
    # Kritsada: U07a8d7f93707eb5acc0facb0424df332
    target_user_id = "U07a8d7f93707eb5acc0facb0424df332"
    target_name = "กฤษฎา ศรีคิลิน"
    
    event_title = "มิ.ย. 69 อบรมพัฒนาทักษะในศตวรรษที่ 21 นักศึกษาคณะวิทยาศาสตร์และเทคโนโลยี"
    event_date = "19 มิ.ย. 69"
    location = "คณะวิทยาศาสตร์และเทคโนโลยี"
    
    print(f"[*] Simulating 'tomorrow' (1-day pre-event) notification for user: {target_name}")
    print(f"[*] Target LINE ID: {target_user_id}")
    
    # Construct exact message sent by scheduler
    msg = make_premium_notification_flex(
        title="พรุ่งนี้เจอกันนะครับ! 🔔",
        subtitle="แจ้งเตือนล่วงหน้า 1 วันสำหรับกิจกรรมที่คุณได้จองไว้ (ทดสอบระบบ)",
        items=[
            ("ผู้รับ", target_name),
            ("กิจกรรม", event_title),
            ("วันจัดงาน", event_date),
            ("สถานที่", location)
        ],
        accent_color="#0ea5e9",
        button_text="ดูข้อมูลโปรไฟล์และกิจกรรม",
        button_url=f"{get_ngrok_url()}/profile"
    )
    
    success = send_line_notification(target_user_id, msg)
    if success:
        print("[+] Test notification sent successfully!")
    else:
        print("[x] Failed to send test notification.")

if __name__ == "__main__":
    main()
