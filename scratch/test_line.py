import os
import json
import urllib.request
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

def test_line_notification():
    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    admin_id = os.environ.get("LINE_ADMIN_USER_ID")
    
    print("=== [TEST] Starting LINE Notification Test ===")
    print(f"LINE_ADMIN_USER_ID: {admin_id}")
    print(f"Token (First 15 chars): {token[:15]}..." if token else "None")
    
    if not token or not admin_id:
        print("[FAIL] Missing LINE_CHANNEL_ACCESS_TOKEN or LINE_ADMIN_USER_ID in .env file!")
        return
        
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    message = "🔔 แจ้งเตือนการเชื่อมต่อสำเร็จ!\n\nระบบบอร์ดกิจกรรม SciTech ได้ทำการเปิดใช้งานระบบแจ้งเตือนทาง LINE (LINE Messaging API) บนบอทของคุณเป็นที่เรียบร้อยแล้วค่ะ/ครับ! 🎉🚀"
    
    body = {
        "to": admin_id,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    
    req_data = json.dumps(body).encode('utf-8')
    req = urllib.request.Request(url, data=req_data, headers=headers, method='POST')
    
    try:
        print("[SENDING] Sending POST request to LINE API...")
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            print("[SUCCESS] Message sent successfully!")
            print(f"LINE API Response: {res_body}")
    except Exception as e:
        print(f"[FAIL] Error sending LINE notification: {e}")
        if hasattr(e, 'read'):
            try:
                print(f"Error Response Body: {e.read().decode('utf-8')}")
            except:
                pass

if __name__ == "__main__":
    test_line_notification()
