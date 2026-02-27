import sqlite3
import hashlib
import os

DB_PATH = "users.db"

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with users table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
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
        
        cursor.execute('''
            INSERT INTO users (fullname, username, email, password_hash)
            VALUES (?, ?, ?, ?)
        ''', (fullname, username, email, password_hash))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def verify_user(username, password):
    """Verify user credentials"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        
        cursor.execute('''
            SELECT * FROM users 
            WHERE username = ? AND password_hash = ?
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
        
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
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
        
        cursor.execute('''
            SELECT id, fullname, username, email, created_at 
            FROM users 
            WHERE username = ?
        ''', (username,))
        
        user = cursor.fetchone()
        conn.close()
        
        return dict(user) if user else None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def save_upload(username, image, result):
    """Save upload result to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO uploads (username, image, result)
            VALUES (?, ?, ?)
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
        
        cursor.execute('''
            SELECT id, result, created_at 
            FROM uploads 
            WHERE username = ?
            ORDER BY created_at DESC
        ''', (username,))
        
        uploads = cursor.fetchall()
        conn.close()
        
        return [dict(upload) for upload in uploads]
    except Exception as e:
        print(f"Error getting upload history: {e}")
        return []

if __name__ == "__main__":
    init_db()
    print("Database setup complete!")
