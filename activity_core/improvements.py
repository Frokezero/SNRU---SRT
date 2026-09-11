"""Student workspace, operations tools, calendar and safe backup verification."""
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import zipfile
from datetime import datetime, timedelta, timezone

from flask import Response, jsonify, request, session, send_file, send_from_directory
from itsdangerous import URLSafeSerializer, BadSignature
from database import get_db_connection


def event_day(value, thai_parser):
    value = value or ''
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        # Do not silently invent dates for legacy incomplete date labels.
        import re
        if not re.search(r'[ก-๙]', value) or len(re.findall(r'\d+', value)) < 2:
            return None
        return thai_parser(value)


def create_backup(upload_root):
    """SQLite online snapshot plus uploads; no credentials or legacy user dumps."""
    output = io.BytesIO()
    with tempfile.TemporaryDirectory() as folder:
        snapshot = Path(folder) / 'database.sqlite'
        source = get_db_connection()
        target = sqlite3.connect(snapshot)
        try:
            source.backup(target)
            assert target.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        finally:
            target.close()
            source.close()
        manifest = {}
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
            files = [(snapshot, 'database.sqlite')]
            root = Path(upload_root).resolve()
            if root.exists():
                files += [(p, 'uploads/' + p.relative_to(root).as_posix())
                          for p in root.rglob('*') if p.is_file() and not p.is_symlink()
                          and root in p.resolve().parents]
            for path, name in files:
                data = path.read_bytes()
                archive.writestr(name, data)
                manifest[name] = hashlib.sha256(data).hexdigest()
            archive.writestr('manifest.json', json.dumps(manifest))
    output.seek(0)
    return output


def verify_backup(stream):
    """Verify in isolation, never extract or replace the live database."""
    with zipfile.ZipFile(stream) as archive:
        infos = archive.infolist()
        if sum(i.file_size for i in infos) > 512 * 1024 * 1024:
            raise ValueError('ไฟล์สำรองหลังขยายต้องไม่เกิน 512 MB')
        names = [i.filename for i in infos]
        if len(names) != len(set(names)) or 'manifest.json' not in names:
            raise ValueError('รูปแบบไฟล์สำรองไม่ถูกต้อง')
        manifest = json.loads(archive.read('manifest.json'))
        if not isinstance(manifest, dict) or set(manifest) != set(names) - {'manifest.json'} or 'database.sqlite' not in manifest:
            raise ValueError('รายการไฟล์ไม่ครบ')
        for name, digest in manifest.items():
            if name != 'database.sqlite' and (not name.startswith('uploads/') or '..' in Path(name).parts or '\\' in name):
                raise ValueError('ชื่อไฟล์ไม่ปลอดภัย')
            if hashlib.sha256(archive.read(name)).hexdigest() != digest:
                raise ValueError('ไฟล์สำรองเสียหาย: ' + name)
        with tempfile.TemporaryDirectory() as folder:
            snapshot = Path(folder) / 'restore-check.sqlite'
            snapshot.write_bytes(archive.read('database.sqlite'))
            conn = sqlite3.connect(snapshot)
            try:
                if conn.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                    raise ValueError('ฐานข้อมูลเสียหาย')
                if conn.execute('PRAGMA foreign_key_check').fetchone():
                    raise ValueError('ข้อมูลอ้างอิงไม่ครบ')
                missing = []
                for row in conn.execute("SELECT image_url FROM participations WHERE deleted_at IS NULL AND image_url LIKE '/uploads/%'"):
                    if row[0].lstrip('/') not in manifest:
                        missing.append(row[0])
                if missing:
                    raise ValueError(f'ขาดไฟล์หลักฐาน {len(missing)} ไฟล์')
            finally:
                conn.close()
    return len(manifest)


def schedule_reminders(api, now=None):
    now = now or datetime.now()
    conn = get_db_connection()
    try:
        conn.execute('BEGIN IMMEDIATE')
        rows = conn.execute('''SELECT r.id,r.username,e.date,e.title FROM registrations r
            JOIN events e ON e.id=r.event_id JOIN users u ON u.username=r.username
            LEFT JOIN notification_preferences p ON p.username=r.username
            WHERE r.status='confirmed' AND r.deleted_at IS NULL AND e.deleted_at IS NULL
            AND u.deleted_at IS NULL AND COALESCE(p.reminders,1)=1''').fetchall()
        count = 0
        for row in rows:
            day = event_day(row['date'], api['parse_thai_date_to_comparable'])
            if day != (now + timedelta(days=1)).date():
                continue
            inserted = conn.execute('INSERT OR IGNORE INTO reminder_receipts(registration_id,event_date) VALUES (?,?)', (row['id'], row['date'])).rowcount
            if inserted:
                conn.execute('INSERT INTO notifications(username,title,message,notification_type) VALUES (?,?,?,?)',
                             (row['username'], 'กิจกรรมของคุณเริ่มพรุ่งนี้', row['title'] + ' — ' + row['date'], 'info'))
                count += 1
        conn.commit()
        return count
    finally:
        conn.close()


def register_features(app, api):
    role = api['require_role']
    signer = lambda: URLSafeSerializer(app.secret_key, salt='certificate-verification-v1')

    @app.before_request
    def validate_review_reason():
        if request.method not in ('POST', 'PUT') or not request.path.startswith('/api/admin/'):
            return None
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return None
        is_review = ('participations' in request.path or request.path == '/api/admin/update-status-bulk')
        updates = data.get('updates') if isinstance(data.get('updates'), list) else []
        rejected = data.get('status') == 'rejected' or any(isinstance(u, dict) and u.get('status') == 'rejected' for u in updates)
        if is_review and rejected and (not isinstance(data.get('reason'), str) or not 1 <= len(data['reason'].strip()) <= 1000):
            return jsonify(success=False, message='กรุณาระบุเหตุผลที่ไม่อนุมัติ (1–1,000 ตัวอักษร)'), 400

    @app.get('/workspace')
    @role('student', 'admin', 'major')
    def workspace_page():
        return send_from_directory(app.root_path, 'workspace.html')

    @app.get('/api/workspace')
    @role('student', 'admin', 'major')
    def workspace_data():
        user = api['db_get_user'](session['username'])
        conn = get_db_connection()
        try:
            if user['role'] != 'student':
                scope, args = (' AND e.owner=?', (user['name'],)) if user['role'] == 'major' else ('', ())
                rows = conn.execute('''SELECT p.id,p.student_name,p.event_title,p.timestamp,p.status,p.image_url
                    FROM participations p JOIN events e ON e.id=p.event_id
                    WHERE p.deleted_at IS NULL AND e.deleted_at IS NULL AND p.status='pending' ''' + scope + ' ORDER BY p.timestamp,p.id LIMIT 200', args).fetchall()
                return jsonify(role=user['role'], pending=[dict(r) for r in rows])
            rows = conn.execute('SELECT * FROM participations WHERE username=? AND deleted_at IS NULL', (user['username'],)).fetchall()
            parts = [dict(r) for r in rows]
            for part in parts:
                part['history'] = [dict(r) for r in conn.execute('SELECT actor,old_status,new_status,old_score,new_score,reason,created_at FROM participation_history WHERE participation_id=? ORDER BY id DESC', (part['id'],))]
            pref = conn.execute('SELECT reminders FROM notification_preferences WHERE username=?', (user['username'],)).fetchone()
            return jsonify(role='student', approved_score=sum(p['score'] or 0 for p in parts if p['status']=='approved'),
                           pending_score=sum(p['score'] or 0 for p in parts if p['status']=='pending'),
                           participations=parts, reminders=bool(pref[0]) if pref else True)
        finally:
            conn.close()

    @app.put('/api/my/notification-preferences')
    @role('student')
    def preferences():
        data = request.get_json(silent=True) or {}
        if type(data.get('reminders')) is not bool:
            return jsonify(message='reminders ต้องเป็น true หรือ false'), 400
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO notification_preferences(username,reminders) VALUES (?,?) ON CONFLICT(username) DO UPDATE SET reminders=excluded.reminders', (session['username'], int(data['reminders'])))
            conn.commit()
        finally:
            conn.close()
        return jsonify(success=True)

    @app.get('/api/admin/outbox')
    @role('admin')
    def outbox():
        conn = get_db_connection()
        try:
            rows = conn.execute('SELECT id,job_type,status,attempts,created_at,completed_at FROM outbox_jobs ORDER BY id DESC LIMIT 200').fetchall()
            # Provider errors may contain addresses or credentials; do not expose raw errors.
            return jsonify(jobs=[{**dict(r), 'error': 'ส่งไม่สำเร็จ กรุณาตรวจสอบการตั้งค่าบริการ' if r['status']=='failed' else ''} for r in rows])
        finally:
            conn.close()

    @app.get('/api/admin/service-readiness')
    @role('admin')
    def readiness():
        return jsonify(
            ai_enabled=os.environ.get('ENABLE_AI_ASSISTANT', 'false').lower()=='true',
            worker_enabled=os.environ.get('OUTBOX_WORKER_ENABLED', 'true').lower()=='true',
            public_url_configured=bool(os.environ.get('PUBLIC_BASE_URL')),
            message='สถานะการตั้งค่าเท่านั้น ไม่ได้ทดสอบการเชื่อมต่อหรือส่งข้อความภายนอก')

    @app.post('/api/admin/outbox/<int:job_id>/retry')
    @role('admin')
    def retry(job_id):
        conn = get_db_connection()
        try:
            count = conn.execute("UPDATE outbox_jobs SET status='pending',attempts=0,available_at=0,last_error=NULL,claim_token=NULL,lease_until=NULL WHERE id=? AND status='failed'", (job_id,)).rowcount
            conn.commit()
            return (jsonify(success=True), 200) if count else (jsonify(message='ลองใหม่ได้เฉพาะงานที่ล้มเหลว กรุณาโหลดใหม่'), 409)
        finally:
            conn.close()

    @app.post('/api/admin/backup/verify')
    @role('admin')
    def backup_verify():
        if 'file' not in request.files:
            return jsonify(message='กรุณาเลือกไฟล์ ZIP'), 400
        try:
            count = verify_backup(request.files['file'])
            return jsonify(success=True, files=count, message='ตรวจสอบฐานข้อมูลและไฟล์หลักฐานผ่าน โดยไม่เปลี่ยนข้อมูลจริง')
        except (ValueError, KeyError, zipfile.BadZipFile, sqlite3.Error) as exc:
            return jsonify(success=False, message=str(exc)), 400

    @app.get('/api/my/calendar.ics')
    @role('student')
    def personal_calendar():
        def esc(value):
            return str(value or '').replace('\\', '\\\\').replace('\r', '').replace('\n', '\\n').replace(';', '\\;').replace(',', '\\,')
        conn = get_db_connection()
        try:
            rows = conn.execute('''SELECT e.* FROM events e JOIN registrations r ON e.id=r.event_id
                WHERE r.username=? AND r.status='confirmed' AND r.deleted_at IS NULL AND e.deleted_at IS NULL''', (session['username'],)).fetchall()
        finally:
            conn.close()
        lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Scitech//Activities//TH', 'CALSCALE:GREGORIAN']
        for r in rows:
            day = event_day(r['date'], api['parse_thai_date_to_comparable'])
            if day:
                lines += ['BEGIN:VEVENT', 'UID:' + hashlib.sha256(r['id'].encode()).hexdigest() + '@scitech',
                          'DTSTAMP:' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'),
                          'DTSTART;VALUE=DATE:' + day.strftime('%Y%m%d'),
                          'DTEND;VALUE=DATE:' + (day+timedelta(days=1)).strftime('%Y%m%d'),
                          'SUMMARY:' + esc(r['title']), 'LOCATION:' + esc(r['location']), 'END:VEVENT']
        lines += ['END:VCALENDAR']
        # Fold by UTF-8 octets without splitting a codepoint.
        folded = []
        for line in lines:
            chunk = ''
            for char in line:
                if len((chunk+char).encode()) > 74:
                    folded.append(chunk)
                    chunk = ' '
                chunk += char
            folded.append(chunk)
        return Response('\r\n'.join(folded)+'\r\n', mimetype='text/calendar', headers={'Content-Disposition':'attachment; filename="activities.ics"'})

    @app.get('/api/certificate/<part_id>/verification')
    @role('student', 'admin')
    def certificate_link(part_id):
        conn = get_db_connection()
        try:
            row = conn.execute("SELECT username FROM participations WHERE id=? AND status='approved' AND deleted_at IS NULL", (part_id,)).fetchone()
        finally:
            conn.close()
        user = api['db_get_user'](session['username'])
        if not row or (row['username'] != user['username'] and user['role'] != 'admin'):
            return jsonify(message='ไม่พบเกียรติบัตร'), 404
        base = os.environ.get('PUBLIC_BASE_URL', '').rstrip('/') or request.host_url.rstrip('/')
        return jsonify(url=base + '/verify-certificate/' + signer().dumps(part_id))

    @app.get('/verify-certificate/<token>')
    def verify_certificate(token):
        from markupsafe import escape
        try:
            part_id = signer().loads(token)
        except BadSignature:
            return 'ลิงก์ตรวจสอบไม่ถูกต้อง', 404
        conn = get_db_connection()
        try:
            row = conn.execute('''SELECT p.student_name,p.event_title,p.event_date FROM participations p
                JOIN events e ON e.id=p.event_id JOIN users u ON u.username=p.username
                WHERE p.id=? AND p.status='approved' AND p.deleted_at IS NULL AND e.deleted_at IS NULL AND u.deleted_at IS NULL''', (part_id,)).fetchone()
        finally:
            conn.close()
        if not row:
            return 'เกียรติบัตรไม่พร้อมใช้งานหรือถูกเพิกถอน', 404
        return '<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>ตรวจสอบเกียรติบัตร</title><main><h1>เกียรติบัตรได้รับการยืนยัน</h1>' + ''.join('<p>'+str(escape(v or ''))+'</p>' for v in row) + '</main></html>'

    @app.get('/api/certificate/<part_id>/qr')
    @role('student', 'admin')
    def certificate_qr(part_id):
        result = certificate_link(part_id)
        if isinstance(result, tuple):
            return result
        import qrcode
        picture = qrcode.make(result.get_json()['url'])
        buffer = io.BytesIO()
        picture.save(buffer, format='PNG')
        buffer.seek(0)
        return send_file(buffer, mimetype='image/png')

    @app.get('/api/admin/reports/activity.csv')
    @role('admin', 'major')
    def activity_report():
        user = api['db_get_user'](session['username'])
        conn = get_db_connection()
        query = '''SELECT p.*,e.owner FROM participations p JOIN events e ON e.id=p.event_id
            WHERE p.deleted_at IS NULL AND e.deleted_at IS NULL'''
        args = []
        if user['role']=='major':
            query += ' AND e.owner=?'
            args.append(user['name'])
        for key, column in [('event_id', 'p.event_id'), ('major', 'p.major')]:
            if request.args.get(key):
                query += f' AND {column}=?'
                args.append(request.args[key])
        try:
            rows = conn.execute(query, args).fetchall()
        finally:
            conn.close()
        start, end = request.args.get('start'), request.args.get('end')
        try:
            start = datetime.strptime(start, '%Y-%m-%d').date() if start else None
            end = datetime.strptime(end, '%Y-%m-%d').date() if end else None
            if start and end and start > end:
                raise ValueError()
        except ValueError:
            return jsonify(message='ช่วงวันที่ไม่ถูกต้อง'), 400
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['student_id', 'student_name', 'major', 'event', 'date', 'status', 'score'])
        for row in rows:
            day = event_day(row['event_date'], api['parse_thai_date_to_comparable'])
            if (start or end) and (not day or (start and day < start) or (end and day > end)):
                continue
            values = [row[k] for k in ('username','student_name','major','event_title','event_date','status','score')]
            writer.writerow(["'"+v if isinstance(v,str) and v.lstrip().startswith(('=','+','-','@')) else v for v in values])
        return Response('\ufeff'+output.getvalue(), mimetype='text/csv', headers={'Content-Disposition':'attachment; filename="activities-report.csv"'})

    app.extensions['schedule_reminders'] = lambda: schedule_reminders(api)
