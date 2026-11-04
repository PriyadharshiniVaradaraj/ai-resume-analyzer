import os
import sys
import json

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
from auth import get_conn, PH, DATABASE_URL

def init_history_table():
    conn = get_conn(); cur = conn.cursor()
    pk = "SERIAL PRIMARY KEY" if DATABASE_URL else "INTEGER PRIMARY KEY AUTOINCREMENT"
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id {pk},
            user_id INTEGER NOT NULL,
            file_name TEXT,
            score_json TEXT,
            skills_json TEXT,
            gaps_json TEXT,
            jobs_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
    conn.commit(); conn.close()

def save_history(user_id, file_name, score, skills, gaps, jobs):
    conn = get_conn(); cur = conn.cursor()
    cur.execute(
        f"INSERT INTO analysis_history (user_id, file_name, score_json, skills_json, gaps_json, jobs_json) "
        f"VALUES ({PH},{PH},{PH},{PH},{PH},{PH})",
        (int(user_id), file_name,
         json.dumps(score, default=str), json.dumps(skills, default=str),
         json.dumps(gaps, default=str), json.dumps(jobs, default=str)))
    conn.commit(); conn.close()

def get_history(user_id):
    conn = get_conn(); cur = conn.cursor()
    cur.execute(f"SELECT id, file_name, score_json, created_at FROM analysis_history "
                f"WHERE user_id = {PH} ORDER BY id DESC", (int(user_id),))
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "file_name": r[1], "score": json.loads(r[2]), "created_at": r[3]} for r in rows]

def get_one(user_id, record_id):
    conn = get_conn(); cur = conn.cursor()
    cur.execute(f"SELECT id, file_name, score_json, skills_json, gaps_json, jobs_json, created_at "
                f"FROM analysis_history WHERE id = {PH} AND user_id = {PH}", (int(record_id), int(user_id)))
    r = cur.fetchone(); conn.close()
    if not r: return None
    return {"id": r[0], "file_name": r[1], "score": json.loads(r[2]), "skills": json.loads(r[3]),
            "gaps": json.loads(r[4]), "jobs": json.loads(r[5]), "created_at": r[6]}