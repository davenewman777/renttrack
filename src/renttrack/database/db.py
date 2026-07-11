import sqlite3
from pathlib import Path


# Project root is four levels up from this file:
# <root>/src/renttrack/database/db.py -> parents[3] == <root>
DATABASE_PATH = Path(__file__).resolve().parents[3] / "data" / "renttrack.db"


def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    # SQLite requires foreign key enforcement to be enabled per connection.
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


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
        monthly_rent REAL,
        FOREIGN KEY (property_id) REFERENCES properties(id)
    )
    """)

    # Lease-specific data lives in the leases table; tenants only holds
    # contact details.
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
        lease_id INTEGER,
        receipt_number TEXT UNIQUE,
        payment_date TEXT,
        amount REAL,
        payment_method TEXT,
        notes TEXT,
        FOREIGN KEY (lease_id) REFERENCES leases(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tenant_id INTEGER,
        property_id INTEGER,
        unit_id INTEGER,
        lease_start TEXT,
        lease_end TEXT,
        monthly_rent REAL,
        security_deposit REAL,
        active INTEGER DEFAULT 1,
        FOREIGN KEY (tenant_id) REFERENCES tenants(id),
        FOREIGN KEY (property_id) REFERENCES properties(id),
        FOREIGN KEY (unit_id) REFERENCES units(id)
    )
    """)

    connection.commit()
    connection.close()