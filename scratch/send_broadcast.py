import os
import sys
import json
import urllib.request
from dotenv import load_dotenv

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def send_broadcast():
    load_dotenv()
    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    if not token:
        print("[x] Error: LINE_CHANNEL_ACCESS_TOKEN not found in .env file!")
        sys.exit(1)
        
    message_text = (
        "📢 ประชาสัมพันธ์กิจกรรมคณะวิทยาศาสตร์และเทคโนโลยี\n\n"
        "🌟 กิจกรรม: อบรมพัฒนาทักษะในศตวรรษที่ 21 นักศึกษาคณะวิทยาศาสตร์และเทคโนโลยี\n"
        "📅 วันจัดกิจกรรม: 19 มิ.ย. 69\n"
        "📍 สถานที่: คณะวิทยาศาสตร์และเทคโนโลยี\n\n"
        "💡 นักศึกษาที่สนใจเข้าร่วมสามารถลงทะเบียนจองสิทธิ์ได้แล้วผ่านทางหน้าเว็บไซต์หลัก หรือส่งข้อความพิมพ์คำสั่งจองสิทธิ์ผ่าน LINE Bot\n"
        "🔑 รหัสจองด่วนสำหรับ LINE Bot: /book ac19d975-3b42-4dbe-b5da-853e61e2d49c"
    )
    
    print("[*] Message to be broadcasted:")
    print("-" * 50)
    print(message_text)
    print("-" * 50)
    
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    payload = {
        "messages": [
            {
                "type": "text",
                "text": message_text
            }
        ]
    }
    
    req_body = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=req_body, headers=headers, method='POST')
    
    try:
        print("[*] Sending request to LINE Broadcast API...")
        with urllib.request.urlopen(req) as resp:
            resp.read()
            print("[+] Broadcast sent successfully to all followers!")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        print(f"[x] LINE API Error: {e.code} {e.reason}")
        print(f"Details: {err_body}")
    except Exception as e:
        print(f"[x] Error sending broadcast: {e}")

if __name__ == "__main__":
    send_broadcast()
