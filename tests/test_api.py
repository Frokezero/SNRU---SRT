import base64
import hashlib
import hmac
import json
import os
import uuid

import pytest
from werkzeug.security import generate_password_hash

import database
import app as app_module
from app import (
    app, _cache, add_notification, consume_reset_token, create_reset_token, get_reset_token,
    db_delete_event, db_delete_user, db_get_user, db_update_registration_status, get_event_by_id,
    load_otp_store, save_otp_store,
)


@pytest.fixture()
def client(monkeypatch, request):
    """Use an isolated SQLite database; never touch the live database."""
    db_path = os.path.join(os.getcwd(), f".test-db-{uuid.uuid4().hex}.sqlite")
    monkeypatch.setattr(database, "DB_FILE", db_path)
    request.addfinalizer(lambda: [
        os.path.exists(path) and os.remove(path)
        for path in (db_path, db_path + '-wal', db_path + '-shm')
    ])
    monkeypatch.setenv("LINE_CHANNEL_SECRET", "test-line-secret")
    database.init_db()
    conn = database.get_db_connection()
    users = [
        ("admin", "Admin", "admin@example.com", None, "admin"),
        ("major-a", "Major A", "a@example.com", None, "major"),
        ("major-b", "Major B", "b@example.com", None, "major"),
        ("65001", "Student A", "student@example.com", "Major A", "student"),
        ("65002", "Student B", "student2@example.com", "Major A", "student"),
    ]
    conn.executemany(
        "INSERT INTO users (username,password,name,email,major,role) VALUES (?,?,?,?,?,?)",
        [(u, generate_password_hash("password"), n, e, m, r) for u, n, e, m, r in users],
    )
    conn.execute(
        "INSERT INTO events (id,title,owner,score) VALUES (?,?,?,?)",
        ("event-b", "Event B", "Major B", 10),
    )
    conn.execute(
        "INSERT INTO events (id,title,owner,score,max_participants,registration_open) VALUES (?,?,?,?,?,?)",
        ("event-cap", "Capacity Event", "Major A", 5, 1, 1),
    )
    conn.commit()
    conn.close()
    for entry in _cache.values():
        entry["data"] = None

    app.config.update(TESTING=True, SECRET_KEY="test-secret")
    with app.test_client() as test_client:
        yield test_client


def login_as(client, username):
    with client.session_transaction() as sess:
        sess["username"] = username


def test_capacity_guard_on_update(client):
    conn = database.get_db_connection()
    conn.executemany("INSERT INTO registrations(id,event_id,username,status) VALUES (?,?,?,?)", [
        ('seat', 'event-cap', '65001', 'confirmed'),
        ('waiting', 'event-cap', '65002', 'waitlist')])
    conn.execute("UPDATE registrations SET status='confirmed' WHERE id='waiting'")
    assert conn.execute("SELECT status FROM registrations WHERE id='waiting'").fetchone()[0] == 'waitlist'
    conn.commit()
    conn.close()


@pytest.mark.parametrize('field,value', [('registration_open', 0), ('registration_start', '2099-01-01T00:00'), ('registration_end', '2000-01-01T00:00')])
def test_chat_respects_registration_window(client, field, value):
    conn = database.get_db_connection()
    conn.execute(f'UPDATE events SET {field}=? WHERE id=?', (value, 'event-cap'))
    conn.commit()
    conn.close()
    handled, message = app_module.handle_direct_chat_registration('65001', 'จอง Capacity Event')
    assert handled and 'เปิดรับ' in message
    conn = database.get_db_connection()
    assert conn.execute('SELECT COUNT(*) FROM registrations').fetchone()[0] == 0
    conn.close()


def test_outbox_does_not_steal_live_claim(client, monkeypatch):
    import time
    job = app_module.enqueue_outbox_job('line', {'to_id': 'test', 'message': 'hello'})
    conn = database.get_db_connection()
    conn.execute("UPDATE outbox_jobs SET status='processing', lease_until=?, claim_token='owner' WHERE id=?", (time.time() + 300, job))
    conn.commit()
    conn.close()
    assert app_module.process_outbox_once() is False
    delivered = []
    monkeypatch.setattr(app_module, '_deliver_line', lambda *args: delivered.append(args))
    conn = database.get_db_connection()
    conn.execute('UPDATE outbox_jobs SET lease_until=0 WHERE id=?', (job,))
    conn.commit()
    conn.close()
    assert app_module.process_outbox_once() is True
    assert len(delivered) == 1


def test_restore_event_restores_cascade_only(client):
    conn = database.get_db_connection()
    conn.execute("INSERT INTO registrations(id,event_id,username,status) VALUES ('restore-reg','event-b','65001','confirmed')")
    conn.execute("INSERT INTO participations(id,event_id,username,deleted_at) VALUES ('old-deleted','event-b','65001','2000-01-01')")
    conn.commit()
    conn.close()
    db_delete_event('event-b')
    login_as(client, 'admin')
    assert client.post('/api/admin/trash/events/event-b/restore').status_code == 200
    conn = database.get_db_connection()
    assert conn.execute("SELECT deleted_at FROM registrations WHERE id='restore-reg'").fetchone()[0] is None
    assert conn.execute("SELECT deleted_at FROM participations WHERE id='old-deleted'").fetchone()[0] is not None
    conn.close()


def test_rejected_proof_can_be_resubmitted(client, monkeypatch):
    import io
    from PIL import Image
    conn = database.get_db_connection()
    conn.execute("INSERT INTO participations(id,event_id,username,status) VALUES ('retry-proof','event-b','65001','rejected')")
    conn.commit()
    conn.close()
    login_as(client, '65001')
    picture = io.BytesIO()
    Image.new('RGB', (2, 2)).save(picture, format='PNG')
    picture.seek(0)
    saved_images = []
    monkeypatch.setattr(Image.Image, 'save', lambda self, path, **kwargs: saved_images.append(path))
    response = client.post('/api/student/participate', data={'event_id': 'event-b', 'file': (picture, 'proof.png')})
    assert response.status_code == 200, response.get_json()
    assert len(saved_images) == 1
    conn = database.get_db_connection()
    rows = conn.execute("SELECT id,status FROM participations WHERE username='65001'").fetchall()
    assert [(r['id'], r['status']) for r in rows] == [('retry-proof', 'pending')]
    conn.close()


def test_login_page_loads(client):
    assert client.get("/").status_code == 200


def test_health_checks(client):
    assert client.get("/health/live").get_json()["status"] == "ok"
    assert client.get("/health/ready").get_json()["status"] == "ready"


def test_api_security_headers(client):
    response = client.get("/api/events")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Cache-Control"] == "no-store"


def test_unauthorized_admin_access(client):
    assert client.get("/api/admin/dashboard-stats").status_code == 401


def test_dashboard_stats_with_admin_session(client):
    login_as(client, "admin")
    response = client.get("/api/admin/dashboard-stats")
    assert response.status_code == 200
    assert response.get_json()["success"] is True


def test_admin_can_export_registrations_csv(client):
    login_as(client, "admin")
    response = client.get("/api/admin/reports/registrations.csv")
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert response.data.startswith(b"\xef\xbb\xbfregistration_id")


def test_admin_users_api_never_exposes_password_hashes(client):
    login_as(client, "admin")
    response = client.get("/api/admin/users")
    assert response.status_code == 200
    assert all("password" not in user for user in response.get_json().values())


def test_major_cannot_update_another_majors_event(client):
    login_as(client, "major-a")
    response = client.post(
        "/api/admin/participations/update_status",
        json={"event_id": "event-b", "updates": [{"username": "65001", "status": "approved"}]},
    )
    assert response.status_code == 403


@pytest.mark.parametrize("path", [
    "/api/events/event-b/registrations",
    "/api/admin/event/event-b/students",
])
def test_major_cannot_read_another_majors_event(client, path):
    login_as(client, "major-a")
    assert client.get(path).status_code == 403


def test_major_cannot_bulk_update_another_majors_event(client):
    login_as(client, "major-a")
    response = client.post(
        "/api/admin/update-status-bulk",
        json={"event_id": "event-b", "usernames": ["65001"], "status": "approved"},
    )
    assert response.status_code == 403


def test_admin_reset_rejects_weak_or_missing_password(client):
    login_as(client, "admin")
    response = client.post("/api/admin/reset-password", json={"username": "65001"})
    assert response.status_code == 400


def test_reset_tokens_are_hashed_and_one_time(client):
    token = create_reset_token("65001")
    conn = database.get_db_connection()
    stored = conn.execute("SELECT token_hash FROM password_reset_tokens").fetchone()[0]
    conn.close()
    assert stored != token
    assert get_reset_token(token)["username"] == "65001"
    consume_reset_token(token)
    assert get_reset_token(token) is None


def test_otp_is_hashed_in_database(client):
    save_otp_store({
        "65001": {
            "email": "student@example.com", "otp": "123456",
            "ref_code": "REF-TEST", "expiry": 9999999999,
            "type": "reset", "attempts": 0,
        }
    })
    stored = load_otp_store()["65001"]["otp"]
    assert stored != "123456"
    assert stored.startswith(("scrypt:", "pbkdf2:"))


def test_notifications_are_persisted_and_scoped(client):
    add_notification("65001", "Title", "Message", "success")
    login_as(client, "65001")
    response = client.get("/api/notifications")
    assert response.status_code == 200
    notifications = response.get_json()
    assert len(notifications) == 1
    assert notifications[0]["title"] == "Title"
    assert client.get("/api/notifications/unread-count").get_json()["count"] == 1
    client.post("/api/notifications/mark-as-read", json={"id": notifications[0]["id"]})
    assert client.get("/api/notifications/unread-count").get_json()["count"] == 0


def test_soft_deleted_user_can_be_restored(client):
    db_delete_user("65001")
    assert db_get_user("65001") is None
    login_as(client, "admin")
    trash = client.get("/api/admin/trash").get_json()
    assert any(item["username"] == "65001" for item in trash["users"])
    response = client.post("/api/admin/trash/users/65001/restore")
    assert response.status_code == 200
    assert db_get_user("65001") is not None


def test_soft_deleted_event_can_be_restored(client):
    db_delete_event("event-b")
    assert get_event_by_id("event-b") is None
    login_as(client, "admin")
    response = client.post("/api/admin/trash/events/event-b/restore")
    assert response.status_code == 200
    assert get_event_by_id("event-b") is not None


def test_database_enforces_capacity_and_active_registration_uniqueness(client):
    from app import db_add_registration

    base = {
        "event_id": "event-cap", "event_title": "Capacity Event",
        "event_date": "", "major": "Major A", "email": "",
        "timestamp": "2026-01-01T00:00:00", "status": "confirmed",
    }
    first = {**base, "id": "reg-a", "username": "65001", "name": "Student A"}
    second = {**base, "id": "reg-b", "username": "65002", "name": "Student B"}
    assert db_add_registration(first) == "confirmed"
    assert db_add_registration(second) == "waitlist"
    assert db_add_registration({**first, "id": "reg-duplicate"}) is None


def test_cancelling_confirmed_registration_promotes_oldest_waitlist(client):
    from app import db_add_registration

    base = {
        "event_id": "event-cap", "event_title": "Capacity Event",
        "event_date": "", "major": "Major A", "email": "",
        "status": "confirmed",
    }
    db_add_registration({
        **base, "id": "reg-first", "username": "65001", "name": "Student A",
        "timestamp": "2026-01-01T00:00:00",
    })
    db_add_registration({
        **base, "id": "reg-wait", "username": "65002", "name": "Student B",
        "timestamp": "2026-01-01T00:01:00",
    })
    conn = database.get_db_connection()
    conn.execute(
        """INSERT INTO participations
           (id,username,student_name,major,event_id,event_title,status)
           VALUES (?,?,?,?,?,?,?)""",
        ("part-first", "65001", "Student A", "Major A", "event-cap", "Capacity Event", "pending"),
    )
    conn.commit()
    conn.close()

    assert db_update_registration_status("reg-first", "cancelled") == "65002"
    conn = database.get_db_connection()
    promoted = conn.execute("SELECT status FROM registrations WHERE id='reg-wait'").fetchone()
    deleted = conn.execute("SELECT deleted_at FROM participations WHERE id='part-first'").fetchone()
    conn.close()
    assert promoted["status"] == "confirmed"
    assert deleted["deleted_at"] is not None


def test_major_cannot_bulk_change_another_majors_registrations(client):
    login_as(client, "major-a")
    response = client.post(
        "/api/admin/registrations/status-bulk",
        json={"event_id": "event-b", "usernames": ["65001"], "status": "cancelled"},
    )
    assert response.status_code == 403


def test_checkin_token_has_database_backed_session(client):
    login_as(client, "major-a")
    response = client.get("/api/admin/event/event-cap/checkin-token")
    assert response.status_code == 200
    token = response.get_json()["token"]
    decoded = base64.urlsafe_b64decode(token).decode("utf-8")
    payload = json.loads(decoded.rsplit(".", 1)[0])
    conn = database.get_db_connection()
    stored = conn.execute(
        "SELECT event_id FROM checkin_sessions WHERE id = ?",
        (payload["session_id"],),
    ).fetchone()
    conn.close()
    assert stored["event_id"] == "event-cap"


def test_line_webhook_rejects_invalid_signature(client):
    response = client.post(
        "/api/line/webhook",
        data=b'{"events":[]}',
        content_type="application/json",
        headers={"X-Line-Signature": "invalid"},
    )
    assert response.status_code == 401


def test_line_webhook_accepts_valid_signature(client):
    body = b'{"events":[]}'
    signature = base64.b64encode(
        hmac.new(b"test-line-secret", body, hashlib.sha256).digest()
    ).decode("ascii")
    response = client.post(
        "/api/line/webhook",
        data=body,
        content_type="application/json",
        headers={"X-Line-Signature": signature},
    )
    assert response.status_code == 200


def test_ai_assistant_is_disabled_by_default(client, monkeypatch):
    monkeypatch.setenv("ENABLE_AI_ASSISTANT", "false")
    response = client.post("/api/chatbot/ask", json={"message": "hello"})
    assert response.status_code == 503


@pytest.mark.parametrize('enabled', [True, False])
def test_chatbot_public_status_matches_configuration(client, monkeypatch, enabled):
    monkeypatch.setenv('ENABLE_AI_ASSISTANT', str(enabled).lower())
    response = client.get('/api/chatbot/status')
    assert response.status_code == 200
    assert response.get_json() == {'enabled': enabled}
    assert response.headers['Cache-Control'] == 'no-store'


def test_notification_outbox_persists_and_completes_job(client, monkeypatch):
    delivered = []
    monkeypatch.setattr(
        app_module, "_deliver_line",
        lambda to_id, message: delivered.append((to_id, message)),
    )
    job_id = app_module.send_line_notification("line-user", "hello")

    conn = database.get_db_connection()
    queued = conn.execute(
        "SELECT status FROM outbox_jobs WHERE id=?", (job_id,)
    ).fetchone()
    conn.close()
    assert queued["status"] == "pending"

    assert app_module.process_outbox_once() is True
    conn = database.get_db_connection()
    completed = conn.execute(
        "SELECT status, attempts FROM outbox_jobs WHERE id=?", (job_id,)
    ).fetchone()
    conn.close()
    assert delivered == [("line-user", "hello")]
    assert completed["status"] == "completed"
    assert completed["attempts"] == 1


def test_notification_outbox_retries_failed_job(client, monkeypatch):
    def fail_delivery(_to_id, _message):
        raise RuntimeError("temporary failure")

    monkeypatch.setattr(app_module, "_deliver_line", fail_delivery)
    job_id = app_module.send_line_notification("line-user", "hello")
    assert app_module.process_outbox_once() is True

    conn = database.get_db_connection()
    failed = conn.execute(
        "SELECT status, attempts, last_error FROM outbox_jobs WHERE id=?", (job_id,)
    ).fetchone()
    conn.close()
    assert failed["status"] == "pending"
    assert failed["attempts"] == 1
    assert "temporary failure" in failed["last_error"]


def test_admin_edit_participation_persists_status_and_score(client):
    conn = database.get_db_connection()
    conn.execute(
        "INSERT INTO participations(id, username, event_id, status, score) VALUES(?,?,?,?,?)",
        ('edit-proof', '65001', 'event-cap', 'pending', 0),
    )
    conn.commit()
    conn.close()
    login_as(client, 'admin')
    response = client.put('/api/admin/participations/edit-proof', json={'status': 'approved', 'score': 5})
    assert response.status_code == 200
    conn = database.get_db_connection()
    row = conn.execute('SELECT status, score FROM participations WHERE id=?', ('edit-proof',)).fetchone()
    conn.close()
    assert dict(row) == {'status': 'approved', 'score': 5}


def test_admin_bulk_approval_commits_with_notifications(client):
    login_as(client, 'admin')
    response = client.post('/api/admin/update-status-bulk', json={
        'event_id': 'event-cap', 'usernames': ['65001'], 'status': 'approved', 'scores': {'65001': 5},
    })
    assert response.status_code == 200, response.get_json()
