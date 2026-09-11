import io
import json
import zipfile
from datetime import datetime

import pytest
import database
import app as app_module
from test_api import client, login_as
from activity_core.improvements import create_backup, verify_backup, schedule_reminders


def seed_part(status='pending'):
    conn = database.get_db_connection()
    conn.execute("INSERT INTO participations(id,username,student_name,event_id,event_title,event_date,score,status) VALUES ('proof','65001','Student A','event-cap','Capacity Event','2026-09-13',5,?)", (status,))
    conn.commit()
    conn.close()


def test_review_reason_history_and_progress(client):
    seed_part()
    login_as(client, 'admin')
    assert client.put('/api/admin/participations/proof', json={'status':'rejected'}).status_code == 400
    assert client.put('/api/admin/participations/proof', json={'status':'rejected','reason':'ภาพไม่ชัด กรุณาส่งใหม่'}).status_code == 200
    login_as(client, '65001')
    data=client.get('/api/workspace').get_json()
    assert data['approved_score'] == 0
    assert data['participations'][0]['history'][0]['reason'] == 'ภาพไม่ชัด กรุณาส่งใหม่'
    assert data['participations'][0]['history'][0]['actor'] == 'admin'
    login_as(client, '65002')
    assert client.get('/api/workspace').get_json()['participations'] == []


@pytest.mark.parametrize('path', ['/api/admin/outbox', '/api/admin/reports/activity.csv'])
def test_operations_permissions(client, path):
    assert client.get(path).status_code == 401
    login_as(client,'65001')
    assert client.get(path).status_code == 403


def test_outbox_retry_only_failed(client):
    job=app_module.enqueue_outbox_job('line', {'to_id':'private','message':'private'})
    login_as(client,'admin')
    assert client.post(f'/api/admin/outbox/{job}/retry').status_code == 409
    conn=database.get_db_connection()
    conn.execute("UPDATE outbox_jobs SET status='failed',last_error='secret' WHERE id=?",(job,))
    conn.commit()
    conn.close()
    response=client.get('/api/admin/outbox')
    assert b'private' not in response.data and b'secret' not in response.data
    assert client.post(f'/api/admin/outbox/{job}/retry').status_code == 200
    assert client.post(f'/api/admin/outbox/{job}/retry').status_code == 409


def test_reminders_once_and_opt_out(client):
    conn=database.get_db_connection()
    conn.execute("UPDATE events SET date='2026-09-13',max_participants=0 WHERE id='event-cap'")
    conn.executemany("INSERT INTO registrations(id,event_id,username,status) VALUES (?,'event-cap',?,'confirmed')", [('a','65001'),('b','65002')])
    conn.commit()
    conn.close()
    login_as(client,'65002')
    assert client.put('/api/my/notification-preferences',json={'reminders':False}).status_code == 200
    assert schedule_reminders(vars(app_module), datetime(2026,9,12)) == 1
    assert schedule_reminders(vars(app_module), datetime(2026,9,12)) == 0
    conn=database.get_db_connection()
    assert conn.execute('SELECT username FROM notifications').fetchone()[0]=='65001'
    conn.close()


def test_backup_roundtrip_and_tampering(client, tmp_path):
    (tmp_path/'proof.png').write_bytes(b'test-proof')
    archive=create_backup(tmp_path)
    assert verify_backup(archive)==2
    archive.seek(0)
    with zipfile.ZipFile(archive) as original:
        entries={name:original.read(name) for name in original.namelist()}
    entries['uploads/proof.png']=b'changed'
    bad=io.BytesIO()
    with zipfile.ZipFile(bad,'w') as target:
        for name,data in entries.items(): target.writestr(name,data)
    bad.seek(0)
    with pytest.raises(ValueError): verify_backup(bad)


def test_certificate_signed_revocation_and_qr(client):
    seed_part('approved')
    login_as(client,'65002')
    assert client.get('/api/certificate/proof/verification').status_code==404
    login_as(client,'65001')
    response=client.get('/api/certificate/proof/verification')
    link=response.get_json()['url']
    with client.session_transaction() as sess:
        sess.clear()
    assert client.get(link).status_code==200
    login_as(client,'65001')
    assert client.get('/api/certificate/proof/qr').mimetype=='image/png'
    conn=database.get_db_connection()
    conn.execute("UPDATE participations SET status='rejected' WHERE id='proof'")
    conn.commit()
    conn.close()
    assert client.get(link).status_code==404


def test_calendar_and_report_scope(client):
    seed_part('approved')
    conn=database.get_db_connection()
    conn.execute("UPDATE events SET date='2026-09-13' WHERE id='event-cap'")
    conn.execute("INSERT INTO registrations(id,event_id,username,status) VALUES ('calendar','event-cap','65001','confirmed')")
    conn.commit()
    conn.close()
    login_as(client,'65001')
    calendar=client.get('/api/my/calendar.ics')
    assert b'DTSTART;VALUE=DATE:20260913' in calendar.data
    login_as(client,'65002')
    assert b'BEGIN:VEVENT' not in client.get('/api/my/calendar.ics').data
    login_as(client,'major-b')
    assert b'Student A' not in client.get('/api/admin/reports/activity.csv').data
    login_as(client,'admin')
    assert b'Student A' in client.get('/api/admin/reports/activity.csv?start=2026-09-01&end=2026-09-30').data
    assert b'Student A' not in client.get('/api/admin/reports/activity.csv?start=2027-01-01').data


def test_mark_all_read_accepts_empty_post(client):
    login_as(client,'65001')
    app_module.add_notification('65001','Test','Reminder')
    assert client.post('/api/notifications/mark-as-read').status_code==200
    conn=database.get_db_connection()
    assert conn.execute("SELECT is_read FROM notifications WHERE username='65001'").fetchone()[0]==1
    conn.close()
