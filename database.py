import sqlite3
import os
import json

DB_FILE = os.environ.get(
    'DATABASE_PATH',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.sqlite')
)

def get_db_connection():
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.row_factory = sqlite3.Row
    def audit_actor():
        from flask import has_request_context, session
        return session.get('username') if has_request_context() else 'system'
    def review_reason(username):
        from flask import has_request_context, request
        if not has_request_context():
            return ''
        data = request.get_json(silent=True) or {}
        return str(data.get('reason', '')).strip()[:1000] if isinstance(data, dict) else ''
    conn.create_function('audit_actor', 0, audit_actor)
    conn.create_function('review_reason', 1, review_reason)
    # Enforce foreign key constraints and WAL mode for integrity and concurrency
    conn.execute('PRAGMA foreign_keys = ON')
    try:
        conn.execute('PRAGMA journal_mode=WAL')
    except Exception:
        pass # Fallback to default journal mode if WAL is restricted on shared hosting
    conn.execute('PRAGMA synchronous=NORMAL')
    
    # Auto-register connection with Flask app context if available
    try:
        from flask import has_app_context, g
        if has_app_context():
            if not hasattr(g, '_db_connections'):
                g._db_connections = []
            g._db_connections.append(conn)
    except ImportError:
        pass
        
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS schema_migrations (
        version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 1. Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            major TEXT,
            role TEXT NOT NULL DEFAULT 'student',
            line_id TEXT
        )
    ''')
    
    # 2. Events Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            date TEXT,
            category TEXT,
            location TEXT,
            owner TEXT,
            description TEXT,
            registration_open INTEGER DEFAULT 0,
            max_participants INTEGER DEFAULT 0,
            score INTEGER DEFAULT 0,
            hidden INTEGER DEFAULT 0,
            status TEXT DEFAULT 'รอการดำเนินการ',
            created_at TEXT,
            registration_start TEXT,
            registration_end TEXT,
            latitude REAL DEFAULT 17.18994,
            longitude REAL DEFAULT 104.09153
        )
    ''')
    
    # Run migration in case tables were already created
    try:
        c.execute("ALTER TABLE users ADD COLUMN line_id TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE events ADD COLUMN registration_start TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE events ADD COLUMN registration_end TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE events ADD COLUMN latitude REAL DEFAULT 17.18994")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE events ADD COLUMN longitude REAL DEFAULT 104.09153")
    except sqlite3.OperationalError:
        pass
    for table in ('users', 'events', 'participations', 'registrations'):
        try:
            c.execute(f"ALTER TABLE {table} ADD COLUMN deleted_at TEXT")
        except sqlite3.OperationalError:
            pass
        try:
            c.execute(f"ALTER TABLE {table} ADD COLUMN deleted_by TEXT")
        except sqlite3.OperationalError:
            pass
    
    # 3. Participations Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS participations (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            student_name TEXT,
            major TEXT,
            event_id TEXT,
            event_title TEXT,
            event_date TEXT,
            score INTEGER DEFAULT 0,
            timestamp TEXT,
            image_url TEXT,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY(username) REFERENCES users(username),
            FOREIGN KEY(event_id) REFERENCES events(id)
        )
    ''')
    
    # 4. Registrations Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id TEXT PRIMARY KEY,
            event_id TEXT NOT NULL,
            event_title TEXT,
            event_date TEXT,
            username TEXT NOT NULL,
            name TEXT,
            major TEXT,
            email TEXT,
            timestamp TEXT,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY(event_id) REFERENCES events(id),
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')

    # Columns added after legacy installations created these tables.
    for table in ('participations', 'registrations'):
        for column in ('deleted_at TEXT', 'deleted_by TEXT'):
            try:
                c.execute(f"ALTER TABLE {table} ADD COLUMN {column}")
            except sqlite3.OperationalError:
                pass

    # 5. Performance Indexes (Optimization)
    c.execute('CREATE INDEX IF NOT EXISTS idx_participations_username ON participations(username)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_participations_event_id ON participations(event_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_registrations_username ON registrations(username)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_registrations_event_id ON registrations(event_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_events_status ON events(status)')

    # Security audit trail for state-changing HTTP requests.
    c.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT NOT NULL,
            resource TEXT NOT NULL,
            status_code INTEGER NOT NULL,
            ip_address TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_audit_logs_username ON audit_logs(username)')
    try:
        c.execute('ALTER TABLE audit_logs ADD COLUMN details_json TEXT')
    except sqlite3.OperationalError:
        pass

    c.execute('''CREATE TABLE IF NOT EXISTS password_reset_tokens (
        token_hash TEXT PRIMARY KEY, username TEXT NOT NULL, expires_at REAL NOT NULL,
        used_at TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(username) REFERENCES users(username)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS otp_requests (
        username TEXT PRIMARY KEY, email TEXT, otp_hash TEXT NOT NULL,
        ref_code TEXT, expires_at REAL NOT NULL, request_type TEXT NOT NULL,
        attempts INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(username) REFERENCES users(username)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, title TEXT NOT NULL,
        message TEXT NOT NULL, notification_type TEXT NOT NULL DEFAULT 'info',
        is_read INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(username) REFERENCES users(username)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS checkin_sessions (
        id TEXT PRIMARY KEY, event_id TEXT NOT NULL, nonce_hash TEXT NOT NULL,
        expires_at REAL NOT NULL, used_at TEXT, created_by TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(event_id) REFERENCES events(id), FOREIGN KEY(created_by) REFERENCES users(username)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS event_status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL, old_status TEXT,
        new_status TEXT NOT NULL, changed_by TEXT NOT NULL, reason TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(event_id) REFERENCES events(id), FOREIGN KEY(changed_by) REFERENCES users(username)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS outbox_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, job_type TEXT NOT NULL, payload_json TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending', attempts INTEGER NOT NULL DEFAULT 0,
        available_at REAL NOT NULL, last_error TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        completed_at TEXT
    )''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(username, is_read)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_outbox_status_available ON outbox_jobs(status, available_at)')
    columns = {row[1] for row in c.execute('PRAGMA table_info(outbox_jobs)')}
    for column, kind in [('claim_token', 'TEXT'), ('lease_until', 'REAL')]:
        if column not in columns:
            c.execute(f'ALTER TABLE outbox_jobs ADD COLUMN {column} {kind}')

    # A user may re-register after cancellation, but can only have one active
    # registration for an event. Legacy databases with duplicates remain
    # readable and are reported instead of making startup fail.
    try:
        c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS uq_active_registration
                     ON registrations(username, event_id)
                     WHERE status != 'cancelled' AND deleted_at IS NULL''')
    except sqlite3.IntegrityError:
        print('WARNING: active registration duplicates found; unique index was not created')

    try:
        c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS uq_active_participation
                     ON participations(username, event_id)
                     WHERE deleted_at IS NULL''')
    except sqlite3.IntegrityError:
        print('WARNING: participation duplicates found; unique index was not created')

    # SQLite serializes trigger execution with the insert. If concurrent
    # requests both believe the final seat is free, only the first remains
    # confirmed and subsequent rows are moved to the waitlist.
    c.execute('''CREATE TRIGGER IF NOT EXISTS enforce_event_capacity_after_insert
        AFTER INSERT ON registrations
        WHEN NEW.status = 'confirmed'
          AND (SELECT max_participants FROM events WHERE id = NEW.event_id) > 0
          AND (SELECT COUNT(*) FROM registrations
               WHERE event_id = NEW.event_id AND status = 'confirmed'
                 AND deleted_at IS NULL) >
              (SELECT max_participants FROM events WHERE id = NEW.event_id)
        BEGIN
            UPDATE registrations SET status = 'waitlist' WHERE id = NEW.id;
        END
    ''')
    c.execute('''CREATE TRIGGER IF NOT EXISTS enforce_event_capacity_after_update
        AFTER UPDATE OF status, event_id, deleted_at ON registrations
        WHEN NEW.status = 'confirmed' AND NEW.deleted_at IS NULL
          AND (SELECT max_participants FROM events WHERE id=NEW.event_id) > 0
          AND (SELECT COUNT(*) FROM registrations WHERE event_id=NEW.event_id
               AND status='confirmed' AND deleted_at IS NULL) >
              (SELECT max_participants FROM events WHERE id=NEW.event_id)
        BEGIN
            UPDATE registrations SET status='waitlist' WHERE id=NEW.id;
        END
    ''')
    c.execute('INSERT OR IGNORE INTO schema_migrations(version) VALUES (2)')
    c.execute('''CREATE TABLE IF NOT EXISTS participation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT, participation_id TEXT NOT NULL,
        actor TEXT, old_status TEXT, new_status TEXT, old_score INTEGER, new_score INTEGER,
        old_image_url TEXT, new_image_url TEXT, reason TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TRIGGER IF NOT EXISTS participation_review_history
        AFTER UPDATE OF status, score, image_url ON participations
        WHEN OLD.status IS NOT NEW.status OR OLD.score IS NOT NEW.score OR OLD.image_url IS NOT NEW.image_url
        BEGIN
          INSERT INTO participation_history(participation_id,actor,old_status,new_status,old_score,new_score,old_image_url,new_image_url,reason)
          VALUES(NEW.id,audit_actor(),OLD.status,NEW.status,OLD.score,NEW.score,OLD.image_url,NEW.image_url,review_reason(NEW.username));
        END''')
    c.execute('''CREATE TRIGGER IF NOT EXISTS participation_initial_history
        AFTER INSERT ON participations
        BEGIN
          INSERT INTO participation_history(participation_id,actor,new_status,new_score,new_image_url,reason)
          VALUES(NEW.id,audit_actor(),NEW.status,NEW.score,NEW.image_url,review_reason(NEW.username));
        END''')
    c.execute('''CREATE TABLE IF NOT EXISTS notification_preferences (
        username TEXT PRIMARY KEY REFERENCES users(username), reminders INTEGER NOT NULL DEFAULT 1
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS reminder_receipts (
        registration_id TEXT NOT NULL, event_date TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(registration_id,event_date)
    )''')
    c.execute('INSERT OR IGNORE INTO schema_migrations(version) VALUES (3)')
    c.execute('PRAGMA user_version = 3')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
