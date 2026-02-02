# fix_plain_admin.py
import sqlite3, os, secrets, hashlib

DB = os.path.join("database","niyojan.db")

def hash_pw(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100_000).hex()

email = 'admin@niyojan.ai'
plain_pw = 'admin123'   # the current known plain password

salt = secrets.token_hex(16)
pwd_hash = hash_pw(plain_pw, salt)

con = sqlite3.connect(DB)
cur = con.cursor()
# check if row uses 'password' column or 'password_hash'
try:
    # try update password_hash column
    cur.execute("UPDATE users SET password_hash=?, salt=? WHERE email=?", (pwd_hash, salt, email))
    if cur.rowcount == 0:
        # maybe table has plain 'password' column — overwrite it and add password_hash
        cur.execute("UPDATE users SET password=?, password_hash=?, salt=? WHERE email=?", (None, pwd_hash, salt, email))
    con.commit()
finally:
    con.close()

print("Updated admin password to hashed value.")
