import sqlite3
import os

# cartella dentro il progetto (scrivibile)
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend_data")

os.makedirs(BASE_DIR, exist_ok=True)

DB_PATH = os.path.join(BASE_DIR, "feedback.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            email TEXT,
            rating INTEGER NOT NULL,
            comment TEXT NOT NULL,
            date TEXT
        );
    """)

    conn.commit()
    conn.close()
