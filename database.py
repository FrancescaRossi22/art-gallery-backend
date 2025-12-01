import os
import sqlite3

# Path dinamico: locale = backend/feedback.db | Render = /data/feedback.db
IS_PRODUCTION = os.getenv("RENDER") is not None

if IS_PRODUCTION:
    DB_PATH = "/data/feedback.db"
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "feedback.db")


def init_db():
    """Crea il database se non esiste."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
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


def get_connection():
    """Ritorna una connessione al DB corretto."""
    return sqlite3.connect(DB_PATH)
