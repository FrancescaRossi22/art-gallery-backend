import os
import psycopg2
import sqlite3

DATABASE_URL = os.getenv("DATABASE_URL")
IS_POSTGRES = bool(DATABASE_URL)

def get_connection():
    if IS_POSTGRES:
        return psycopg2.connect(DATABASE_URL, sslmode="require")
    else:
        return sqlite3.connect("feedback.db")

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
