import sqlite3, os, hashlib, secrets

DB_PATH = os.path.join(os.path.dirname(__file__), 'niyojan.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

# ---- Database Initialization ----
def init_db():
    """
    Initialize the SQLite database using schema.sql,
    ensuring tables include created_at and alert/forecast columns.
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        # Apply schema from file if exists
        if os.path.exists(SCHEMA_PATH):
            with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
        else:
            # Fallback inline schema including 'users' table
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS forecasts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product TEXT NOT NULL,
                    forecast REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product TEXT NOT NULL,
                    forecast REAL,
                    alert TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
        conn.commit()

# ---- Forecast / Alert Operations ----
# ---- Forecast / Alert Operations ----
# ---- Forecast / Alert Operations ----
def insert_forecast(product, forecast, category=None, last_week_sales=0):
    """Single insert."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO forecasts (product, forecast, category, last_week_sales) VALUES (?, ?, ?, ?)",
            (product, float(forecast), category, float(last_week_sales))
        )
        conn.commit()

def bulk_insert_forecasts(data_list):
    """
    Bulk insert forecasts.
    data_list: list of tuples (product, forecast, category, last_week_sales)
    """
    if not data_list:
        return
    with sqlite3.connect(DB_PATH) as conn:
        # Check if length matches 4 columns
        if len(data_list[0]) == 4:
            conn.executemany(
                "INSERT INTO forecasts (product, forecast, category, last_week_sales) VALUES (?, ?, ?, ?)",
                data_list
            )
        else:
            # Fallback for old calls if any
            conn.executemany(
                "INSERT INTO forecasts (product, forecast, category) VALUES (?, ?, ?)",
                data_list
            )
        conn.commit()

def insert_alert(product, alert, category=None):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO alerts (product, alert, category) VALUES (?, ?, ?)",
            (product, alert, category)
        )
        conn.commit()

def insert_alert_with_forecast(product, forecast, alert, category=None):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO alerts (product, forecast, alert, category) VALUES (?, ?, ?, ?)",
            (product, float(forecast), alert, category)
        )
        conn.commit()

def bulk_insert_alerts(data_list):
    """
    Bulk insert alerts.
    data_list: list of tuples (product, forecast, alert, category)
    """
    if not data_list:
        return
    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            "INSERT INTO alerts (product, forecast, alert, category) VALUES (?, ?, ?, ?)",
            data_list
        )
        conn.commit()

def get_all_alerts():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            "SELECT product, category, forecast, alert, created_at FROM alerts ORDER BY created_at DESC"
        )
        rows = c.fetchall()
    return [dict(r) for r in rows]

def get_all_forecasts_raw_query(max_ts):
    """Fetch forecasts created in the given batch window."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        query = """
            SELECT product, category, last_week_sales, forecast, created_at
            FROM forecasts 
            WHERE created_at > datetime(?, '-60 seconds')
        """
        c.execute(query, (max_ts,))
        rows = c.fetchall()
    return [dict(r) for r in rows]

def get_latest_batch_timestamp():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT MAX(created_at) FROM forecasts")
        row = cur.fetchone()
        return row[0] if row else None

# ---- Authentication Helpers ----
def _hash_password(password: str, salt: str) -> str:
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100_000)
    return dk.hex()

def create_user(email: str, name: str, password: str):
    salt = secrets.token_hex(16)
    pwd_hash = _hash_password(password, salt)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO users (email, name, password_hash, salt) VALUES (?, ?, ?, ?)",
            (email, name, pwd_hash, salt)
        )
        conn.commit()

def find_user_by_email(email: str):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        # Try selecting role if it exists
        try:
            cur.execute(
                "SELECT id, email, name, password_hash, salt, role FROM users WHERE email = ?",
                (email,)
            )
            row = cur.fetchone()
        except sqlite3.OperationalError:
            # If 'role' column does not exist yet
            cur.execute(
                "SELECT id, email, name, password_hash, salt FROM users WHERE email = ?",
                (email,)
            )
            row = cur.fetchone()
            if row:
                row = list(row) + [None]  # add placeholder for role

    if not row:
        return None
    return {
        'id': row[0],
        'email': row[1],
        'name': row[2],
        'password_hash': row[3],
        'salt': row[4],
        'role': row[5] or 'analyst',
    }


def verify_user_credentials(email: str, password: str) -> bool:
    user = find_user_by_email(email)
    if not user:
        return False
    candidate = _hash_password(password, user['salt'])
    return secrets.compare_digest(candidate, user['password_hash'])

def ensure_default_admin():
    """Create default admin user if not exists."""
    try:
        admin = find_user_by_email('admin@niyojan.ai')
        if not admin:
            create_user('admin@niyojan.ai', 'Admin', 'admin123')
            print("Default admin created")
    except Exception as e:
        print("Could not create default admin:", e)
