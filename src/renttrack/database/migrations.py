"""Lightweight, idempotent schema migrations for the RentTrack database.

Each migration checks the current schema and only applies changes that are
missing, so it is safe to run on every startup (after ``initialize_database``).

This exists because ``CREATE TABLE IF NOT EXISTS`` never alters an existing
table, so databases created with an earlier schema need explicit patching.
"""

from database.db import get_connection


def _column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def _add_column_if_missing(cursor, table, column, definition):
    if not _column_exists(cursor, table, column):
        cursor.execute(
            f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
        )


def run_migrations():
    connection = get_connection()
    cursor = connection.cursor()

    # leases: UI joins on leases.property_id (older schema lacked it).
    _add_column_if_missing(cursor, "leases", "property_id", "INTEGER")

    # payments: schema moved from tenant_id -> lease_id and added notes.
    _add_column_if_missing(cursor, "payments", "lease_id", "INTEGER")
    _add_column_if_missing(cursor, "payments", "notes", "TEXT")

    # Enforce unique receipt numbers even on databases created before the
    # UNIQUE constraint existed (NULLs are allowed and not considered equal).
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS "
        "idx_payments_receipt_number ON payments(receipt_number)"
    )

    connection.commit()
    connection.close()
