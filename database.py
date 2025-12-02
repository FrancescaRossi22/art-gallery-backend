import os
import sqlite3
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")
IS_POSTGRES = bool(DATABASE_URL)

def get_connection():
    if IS_POSTGRES:
        return psycopg2.connect(DATABASE_URL, sslmode="require")
    else:
        return sqlite3.connect("feedback.db")
