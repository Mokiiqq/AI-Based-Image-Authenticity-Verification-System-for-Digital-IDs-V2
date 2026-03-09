import sqlite3
import hashlib
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    """Create a database connection — PostgreSQL if DATABASE_URL is set, else SQLite"""
    if DATABASE_URL:
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        conn = sqlite3.connect("users.db")
        conn.row_factory = sqlite3.Row
        return conn

def _use_pg():
    return DATABASE_URL is not None

def _ph(index):
    """Return placeholder style: %s for Postgres, ? for SQLite"""
    return "%s" if _use_pg() else "?"

def init_db():
    """Initialize the database with users and uploads tables"""
    conn = get_db_connection()
    cursor = conn.cursor()

    if _use_pg():
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                fullname TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS uploads (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL,
                image TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fullname TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                image TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully")

def hash_password(password):
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(fullname, username, email, password):
    """Create a new user in the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        p = "%s" if _use_pg() else "?"
        cursor.execute(f'''
            INSERT INTO users (fullname, username, email, password_hash)
            VALUES ({p}, {p}, {p}, {p})
        ''', (fullname, username, email, password_hash))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        if 'unique' in str(e).lower() or 'duplicate' in str(e).lower() or 'integrity' in str(e).lower():
            return False
        print(f"Error creating user: {e}")
        return False

def verify_user(username, password):
    """Verify user credentials"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        p = "%s" if _use_pg() else "?"
        cursor.execute(f'''
            SELECT * FROM users 
            WHERE username = {p} AND password_hash = {p}
        ''', (username, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        return user is not None
    except Exception as e:
        print(f"Error verifying user: {e}")
        return False

def user_exists(username):
    """Check if a username already exists"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        p = "%s" if _use_pg() else "?"
        cursor.execute(f'SELECT id FROM users WHERE username = {p}', (username,))
        user = cursor.fetchone()
        conn.close()
        
        return user is not None
    except Exception as e:
        print(f"Error checking user: {e}")
        return False

def get_user(username):
    """Get user information by username"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        p = "%s" if _use_pg() else "?"
        cursor.execute(f'''
            SELECT id, fullname, username, email, created_at 
            FROM users 
            WHERE username = {p}
        ''', (username,))
        
        user = cursor.fetchone()
        conn.close()
        if not user:
            return None
        if _use_pg():
            cols = [desc[0] for desc in cursor.description]
            return dict(zip(cols, user))
        return dict(user)
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def save_upload(username, image, result):
    """Save upload result to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        p = "%s" if _use_pg() else "?"
        cursor.execute(f'''
            INSERT INTO uploads (username, image, result)
            VALUES ({p}, {p}, {p})
        ''', (username, image, result))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving upload: {e}")
        return False

def get_upload_history(username):
    """Get upload history for a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        p = "%s" if _use_pg() else "?"
        cursor.execute(f'''
            SELECT id, result, created_at 
            FROM uploads 
            WHERE username = {p}
            ORDER BY created_at DESC
        ''', (username,))
        
        uploads = cursor.fetchall()
        conn.close()
        if _use_pg():
            cols = [desc[0] for desc in cursor.description]
            return [dict(zip(cols, row)) for row in uploads]
        return [dict(upload) for upload in uploads]
    except Exception as e:
        print(f"Error getting upload history: {e}")
        return []

if __name__ == "__main__":
    init_db()
    print("Database setup complete!")
