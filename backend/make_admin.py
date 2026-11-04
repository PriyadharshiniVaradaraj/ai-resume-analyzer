import sys
from auth import get_conn, PH, init_auth_table

if len(sys.argv) < 2:
    print("Usage: python backend/make_admin.py <your-email>")
    sys.exit(1)

init_auth_table()
email = sys.argv[1].strip().lower()
conn = get_conn(); cur = conn.cursor()
cur.execute(f"UPDATE users SET is_admin = 1 WHERE email = {PH} AND password_hash IS NOT NULL", (email,))
conn.commit()
print("Admin set for", email) if cur.rowcount else print("No registered user found with that email")
conn.close()
