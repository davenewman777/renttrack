import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/renttrack.db")


def get_connection():
    DATABASE_PATH.parent.mkdir(exist_ok=True)

    return sqlite3.connect(DATABASE_PATH)


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tenants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT,
        phone TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receipt_number TEXT,
        tenant_id INTEGER,
        amount REAL,
        payment_date TEXT,
        payment_method TEXT
    )
    """)

    connection.commit()
    connection.close()