import os
import time
import psycopg2
import sqlite3

DATABASE_URL = os.getenv("DATABASE_URL")
IS_POSTGRES = bool(DATABASE_URL)


def get_connection(retries=5, delay=2):
    """
    Retry connection to avoid Render Postgres cold start issues
    """
    last_error = None

    for attempt in range(retries):
        try:
            if IS_POSTGRES:
                return psycopg2.connect(
                    DATABASE_URL,
                    sslmode="require",
                    connect_timeout=5
                )
            else:
                return sqlite3.connect("feedback.db")
        except Exception as e:
            last_error = e
            print(f"⏳ Database not ready (attempt {attempt + 1}/{retries})")
            time.sleep(delay)

    print("❌ Database connection failed after retries")
    raise last_error


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    if IS_POSTGRES:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                surname TEXT NOT NULL,
                email TEXT,
                rating INTEGER NOT NULL,
                comment TEXT NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
    else:
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
