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
    CREATE TABLE IF NOT EXISTS units (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_id INTEGER,
        name TEXT NOT NULL,
        description TEXT,
        monthly_rent REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tenants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        unit_id INTEGER,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        lease_start TEXT,
        lease_end TEXT,
        deposit REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lease_id INTEGER,
        receipt_number TEXT UNIQUE, 
        payment_date TEXT,
        amount REAL,
        payment_method TEXT,
        notes TEXT

    )
    """)

    cursor.execute("""
CREATE TABLE IF NOT EXISTS leases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER,
    unit_id INTEGER,
    lease_start TEXT,
    lease_end TEXT,
    monthly_rent REAL,
    security_deposit REAL,
    active INTEGER DEFAULT 1

)
""")

    connection.commit()
    connection.close()