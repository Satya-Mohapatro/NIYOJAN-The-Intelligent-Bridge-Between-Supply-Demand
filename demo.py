import sqlite3, os
DB = os.path.join("database","niyojan.db")
con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute("SELECT email, password_hash, salt, created_at FROM users")
for r in cur.fetchall():
    print(r)
con.close()
