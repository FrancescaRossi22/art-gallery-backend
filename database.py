import os
import sqlite3
from typing import Optional

import psycopg2


DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")


def get_connection():
    """
    Se esiste DATABASE_URL -> usa PostgreSQL (Render).
    Altrimenti usa SQLite locale (feedback.db) per sviluppo.
    """
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    else:
        return sqlite3.connect("feedback.db")


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    if DATABASE_URL:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                surname TEXT NOT NULL,
                email TEXT,
                rating INTEGER NOT NULL,
                comment TEXT NOT NULL,
                date TIMESTAMPTZ DEFAULT NOW()
            );
            """
        )
    else:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                surname TEXT NOT NULL,
                email TEXT,
                rating INTEGER NOT NULL,
                comment TEXT NOT NULL,
                date TEXT
            );
            """
        )

    conn.commit()
    cur.close()
    conn.close()
