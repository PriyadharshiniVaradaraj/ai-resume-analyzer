import os
import sys

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

try:
    from auth import get_conn, PH, DATABASE_URL
except ModuleNotFoundError:
    from backend.auth import get_conn, PH, DATABASE_URL

def _fmt_dt(val):
    """Format a datetime object or string for display (handles psycopg2 datetime)."""
    if hasattr(val, "strftime"):
        return val.strftime("%Y-%m-%d %H:%M")
    return str(val) if val else ""

def init_applications_table():
    conn = get_conn(); cur = conn.cursor()
    pk = "SERIAL PRIMARY KEY" if DATABASE_URL else "INTEGER PRIMARY KEY AUTOINCREMENT"
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS applications (
            id {pk},
            user_id INTEGER NOT NULL,
            job_title TEXT NOT NULL,
            company TEXT,
            apply_url TEXT,
            status TEXT DEFAULT 'Applied',
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
    conn.commit(); conn.close()

def add_application(user_id, job_title, company, apply_url):
    conn = get_conn(); cur = conn.cursor()
    # do not save the same job twice for the same user
    cur.execute(f"SELECT id FROM applications WHERE user_id = {PH} AND job_title = {PH} AND company = {PH}",
                (int(user_id), job_title, company))
    if cur.fetchone():
        conn.close(); return False
    cur.execute(f"INSERT INTO applications (user_id, job_title, company, apply_url) VALUES ({PH},{PH},{PH},{PH})",
                (int(user_id), job_title, company, apply_url))
    conn.commit(); conn.close()
    return True

def get_applications(user_id):
    conn = get_conn(); cur = conn.cursor()
    cur.execute(f"SELECT id, job_title, company, apply_url, status, applied_at FROM applications "
                f"WHERE user_id = {PH} ORDER BY id DESC", (int(user_id),))
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "job_title": r[1], "company": r[2], "apply_url": r[3],
             "status": r[4], "applied_at": _fmt_dt(r[5])} for r in rows]
