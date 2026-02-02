import sqlite3
import os

# === FIXED PATHS ===
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "niyojan.db")        #  creates directly here
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")    #  reads schema from same folder

print(" Creating Niyojan database...")

try:
    # Remove old DB if exists (optional for clean rebuild)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Old database removed")

    # Create new DB and apply schema
    with sqlite3.connect(DB_PATH) as conn:
        if not os.path.exists(SCHEMA_PATH):
            raise FileNotFoundError(f"Schema file not found at: {SCHEMA_PATH}")
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            script = f.read()
        conn.executescript(script)
        conn.commit()
    print(f"niyojan.db created successfully at: {DB_PATH}")

except Exception as e:
    print(f" Failed to create database: {e}")

# Optional: create default admin user directly
try:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO users (email, name, password_hash, salt) VALUES (?, ?, ?, ?)",
            ('admin@niyojan.ai', 'Admin', 'admin123', 'default_salt')
        )
        conn.commit()
    print(" Default admin user added successfully")
except Exception as e:
    print(f"Could not create default admin: {e}")
