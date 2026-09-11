# SNRU SciTech Activity System

ระบบจัดการกิจกรรมนักศึกษา พัฒนาด้วย Flask และ SQLite รองรับการสมัครกิจกรรม
การส่งหลักฐาน เช็กอิน อนุมัติคะแนน เกียรติบัตร การแจ้งเตือน และ LINE Messaging API

## Requirements

- Python 3.10 ขึ้นไป (แนะนำ 3.12)
- Windows, Linux หรือโฮสติ้งที่รองรับ WSGI

## Development setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python database.py
python app.py
```

เปิด `http://localhost:5000`

แก้ `.env` ก่อนใช้งาน โดยเฉพาะ `SECRET_KEY`, email และ LINE credentials
ห้ามนำ `.env` หรือฐานข้อมูลจริงขึ้น Git

## Testing

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

ชุดทดสอบใช้ฐานข้อมูล SQLite ชั่วคราวและต้องไม่แก้ไข `database.sqlite`

## Production

ตั้งค่าต่อไปนี้เป็นอย่างน้อย:

```dotenv
APP_ENV=production
SECRET_KEY=<random-secret-with-high-entropy>
DATABASE_PATH=<absolute-database-path>
SESSION_TIMEOUT_MINUTES=60
LINE_CHANNEL_ACCESS_TOKEN=<token>
LINE_CHANNEL_SECRET=<secret>
ENABLE_AI_ASSISTANT=false
AI_INCLUDE_PERSONAL_CONTEXT=false
OUTBOX_WORKER_ENABLED=true
```

Email and LINE notifications are persisted in `outbox_jobs` before delivery.
The built-in worker retries failed deliveries up to five times with backoff.
Set `OUTBOX_WORKER_ENABLED=false` on web processes when running a dedicated
worker process that calls `run_outbox_worker()`.

AI ถูกปิดเป็นค่าเริ่มต้น หากเปิดใช้งาน ข้อมูลส่วนบุคคลจะยังไม่ถูกส่งไปยังผู้ให้บริการ AI
จนกว่าจะกำหนด `AI_INCLUDE_PERSONAL_CONTEXT=true` อย่างชัดเจนและมีฐานทางกฎหมายหรือความยินยอมที่เหมาะสม

เมื่อรันหลาย process ให้ตั้ง `SESSION_BACKEND=redis` และ `REDIS_URL` เพื่อใช้ session ร่วมกัน
หากวางหลัง reverse proxy ที่เชื่อถือได้ ให้ตั้ง `BEHIND_PROXY=true` และจำกัด proxy ไม่ให้เข้าถึงจากภายนอกโดยตรง

Production mode จะไม่เริ่มทำงานหากไม่มี `SECRET_KEY` ที่เหมาะสม และ session cookie
จะถูกส่งผ่าน HTTPS เท่านั้น ควรรันหลัง reverse proxy ที่เปิด HTTPS และสำรองฐานข้อมูลสม่ำเสมอ

## Project notes

- `app.py`: แอปพลิเคชันหลักและ API เดิม
- `database.py`: schema และ SQLite connection
- `tests/`: automated tests ที่แยกจากฐานข้อมูลจริง
- `uploads/`: ไฟล์จากผู้ใช้ ซึ่งถูกละเว้นจาก Git
- `.github/workflows/test.yml`: compile และ test อัตโนมัติ

โค้ดเดิมยังอยู่ระหว่างการแยกเป็น Flask Blueprints ควรเพิ่ม regression tests ก่อนย้ายแต่ละโมดูล
เพื่อลดความเสี่ยงต่อข้อมูลและพฤติกรรมของระบบ
# ศูนย์งานกิจกรรมและคู่มือรอบพัฒนาล่าสุด

เข้า `/workspace` หลังล็อกอินเพื่อใช้รายการรอตรวจ คะแนน/ประวัติหลักฐาน รายงาน และเครื่องมือสำรองข้อมูลตามสิทธิ์ ดูวิธีตั้งค่าและข้อจำกัดใน [DEVELOPMENT_HANDOFF.md](DEVELOPMENT_HANDOFF.md)
