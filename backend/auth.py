import os, sqlite3, hmac
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
print("ENV LOADED:", os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASSWORD"))

auth = Blueprint("auth", __name__)
login_manager = LoginManager()
login_manager.login_view = "auth.login"

DATABASE_URL = os.environ.get("DATABASE_URL")   # use your real variable name from Render
SQLITE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "jobs.db")
PH = "%s" if DATABASE_URL else "?"

IST = timezone(timedelta(hours=5, minutes=30))
FMT = "%Y-%m-%d %H:%M:%S"
SESSION_MINUTES = 30
ADMIN_EMAIL = "admin@resumeai.com"
ADMIN_PASSWORD = "Admin@12345"

def now_ist():
    return datetime.now(IST).strftime(FMT)

def get_conn():
    if DATABASE_URL:
        import psycopg2
        return psycopg2.connect(DATABASE_URL)
    return sqlite3.connect(SQLITE_PATH)

def _try(conn, cur, sql):
    try:
        cur.execute(sql); conn.commit()
    except Exception:
        conn.rollback()

def init_auth_table():
    conn = get_conn(); cur = conn.cursor()
    pk = "SERIAL PRIMARY KEY" if DATABASE_URL else "INTEGER PRIMARY KEY AUTOINCREMENT"
    cur.execute(f"CREATE TABLE IF NOT EXISTS users (id {pk}, name TEXT, email TEXT)")
    conn.commit()
    _try(conn, cur, "ALTER TABLE users ADD COLUMN password_hash TEXT")
    _try(conn, cur, "ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
    cur.execute(f"""CREATE TABLE IF NOT EXISTS login_log (
        id {pk}, user_id INTEGER NOT NULL, login_time TEXT NOT NULL,
        last_seen TEXT, logout_time TEXT)""")
    conn.commit(); conn.close()

class User(UserMixin):
    def __init__(self, id, name, email, is_admin=0):
        self.id, self.name, self.email = str(id), name, email
        self.is_admin = bool(is_admin)

@login_manager.user_loader
def load_user(user_id):
    conn = get_conn(); cur = conn.cursor()
    cur.execute(f"SELECT id, name, email, is_admin FROM users WHERE id = {PH}", (user_id,))
    row = cur.fetchone(); conn.close()
    return User(*row) if row else None

# ---------- login activity log ----------
def start_log(user_id):
    conn = get_conn(); cur = conn.cursor()
    t = now_ist()
    sql = f"INSERT INTO login_log (user_id, login_time, last_seen) VALUES ({PH},{PH},{PH})"
    if DATABASE_URL:
        cur.execute(sql + " RETURNING id", (int(user_id), t, t))
        log_id = cur.fetchone()[0]
    else:
        cur.execute(sql, (int(user_id), t, t))
        log_id = cur.lastrowid
    conn.commit(); conn.close()
    return log_id

def end_log(log_id):
    conn = get_conn(); cur = conn.cursor()
    t = now_ist()
    cur.execute(f"UPDATE login_log SET logout_time = {PH}, last_seen = {PH} "
                f"WHERE id = {PH} AND logout_time IS NULL", (t, t, int(log_id)))
    conn.commit(); conn.close()

@auth.before_app_request
def track_activity():
    if request.endpoint in (None, "static"):
        return
    log_id = session.get("log_id")
    if log_id and current_user.is_authenticated:
        conn = get_conn(); cur = conn.cursor()
        cur.execute(f"UPDATE login_log SET last_seen = {PH} WHERE id = {PH}", (now_ist(), int(log_id)))
        conn.commit(); conn.close()

# ---------- user register / login / logout ----------
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        pw = request.form["password"]
        if len(pw) < 8:
            flash("Password must be at least 8 characters.")
            return render_template("register.html")
        conn = get_conn(); cur = conn.cursor()
        cur.execute(f"SELECT id FROM users WHERE email = {PH} AND password_hash IS NOT NULL", (email,))
        if cur.fetchone():
            conn.close(); flash("This email is already registered.")
            return render_template("register.html")
        cur.execute(f"INSERT INTO users (name, email, password_hash) VALUES ({PH}, {PH}, {PH})",
                    (name, email, generate_password_hash(pw)))
        conn.commit(); conn.close()
        flash("Account created. Please log in.")
        return redirect(url_for("auth.login"))
    return render_template("register.html")

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        conn = get_conn(); cur = conn.cursor()
        cur.execute(f"SELECT id, name, email, password_hash, is_admin FROM users "
                    f"WHERE email = {PH} AND password_hash IS NOT NULL", (email,))
        row = cur.fetchone(); conn.close()
        if row and check_password_hash(row[3], request.form["password"]):
            user = User(row[0], row[1], row[2], row[4])
            login_user(user)
            session.permanent = True
            session["log_id"] = start_log(user.id)
            return redirect(url_for("home"))
        flash("Invalid email or password.")
    return render_template("login.html")

@auth.route("/logout")
@login_required
def logout():
    log_id = session.pop("log_id", None)
    if log_id:
        end_log(log_id)
    logout_user()
    return redirect(url_for("auth.login"))

# ---------- separate admin login ----------
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("auth.admin_login"))
        return f(*args, **kwargs)
    return wrapper

@auth.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"].strip().lower().encode()
        pw = request.form["password"].encode()
        print("ADMIN CHECK -> typed:", email, "| expected:", ADMIN_EMAIL.encode(), "| password set:", bool(ADMIN_PASSWORD), "| password matches:", pw == ADMIN_PASSWORD.encode())
        ok = bool(ADMIN_EMAIL and ADMIN_PASSWORD) \
             and hmac.compare_digest(email, ADMIN_EMAIL.encode()) \
             and hmac.compare_digest(pw, ADMIN_PASSWORD.encode())
        if ok:
            session["is_admin"] = True
            session.permanent = True
            return redirect(url_for("auth.admin_dashboard"))
        flash("Invalid admin email or password.")
    return render_template("admin_login.html")

@auth.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("auth.admin_login"))

@auth.route("/admin")
@admin_required
def admin_dashboard():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT l.id, u.name, u.email, l.login_time, l.last_seen, l.logout_time "
                "FROM login_log l JOIN users u ON u.id = l.user_id ORDER BY l.id DESC LIMIT 200")
    rows = cur.fetchall()
    cur.execute("SELECT id, name, email, is_admin FROM users WHERE password_hash IS NOT NULL ORDER BY id DESC")
    users = cur.fetchall()
    conn.close()

    now = datetime.now(IST).replace(tzinfo=None)
    today = now.strftime("%Y-%m-%d")
    logs, active, today_count = [], 0, 0
    for _id, name, email, login_t, seen_t, logout_t in rows:
        t_in = datetime.strptime(login_t, FMT)
        if logout_t:
            status, end = "Logged out", datetime.strptime(logout_t, FMT)
        else:
            seen = datetime.strptime(seen_t or login_t, FMT)
            if now - seen < timedelta(minutes=SESSION_MINUTES):
                status, end = "Active", now
                active += 1
            else:
                status, end = "Session expired", seen
        if login_t.startswith(today):
            today_count += 1
        logs.append({"name": name, "email": email, "login_time": login_t,
                     "logout_time": logout_t or "-", "status": status,
                     "minutes": int((end - t_in).total_seconds() // 60)})

    return render_template("admin.html", logs=logs, users=users,
                           active=active, today_count=today_count, total_users=len(users))