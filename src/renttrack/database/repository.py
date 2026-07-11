"""Data-access layer for RentTrack.

Centralizes all SQL so the UI never talks to sqlite3 directly. Every write is
wrapped in a transaction that commits on success and rolls back on error.
"""

from contextlib import contextmanager
from datetime import date

from database.db import get_connection


@contextmanager
def _cursor():
    """Yield a cursor inside a transaction (commit on success, rollback on error)."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        yield cursor
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------
def add_property(name, address):
    with _cursor() as cursor:
        cursor.execute(
            "INSERT INTO properties (name, address) VALUES (?, ?)",
            (name, address),
        )


def list_properties():
    """Return rows of (id, name, address) ordered by name."""
    with _cursor() as cursor:
        return cursor.execute(
            "SELECT id, name, address FROM properties ORDER BY name"
        ).fetchall()


# ---------------------------------------------------------------------------
# Units
# ---------------------------------------------------------------------------
def add_unit(property_id, name, description, monthly_rent):
    with _cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO units (property_id, name, description, monthly_rent)
            VALUES (?, ?, ?, ?)
            """,
            (property_id, name, description, monthly_rent),
        )


def list_units_with_property():
    """Return rows of (property_name, unit_name, description, monthly_rent)."""
    with _cursor() as cursor:
        return cursor.execute(
            """
            SELECT p.name, u.name, u.description, u.monthly_rent
            FROM units u
            JOIN properties p ON u.property_id = p.id
            ORDER BY p.name, u.name
            """
        ).fetchall()


def units_for_property(property_id):
    """Return rows of (id, name, monthly_rent) for one property."""
    with _cursor() as cursor:
        return cursor.execute(
            """
            SELECT id, name, monthly_rent
            FROM units
            WHERE property_id = ?
            ORDER BY name
            """,
            (property_id,),
        ).fetchall()


# ---------------------------------------------------------------------------
# Tenants
# ---------------------------------------------------------------------------
def add_tenant(first_name, last_name, email, phone=None):
    with _cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO tenants (first_name, last_name, email, phone)
            VALUES (?, ?, ?, ?)
            """,
            (first_name, last_name, email, phone),
        )


def list_tenants():
    """Return rows of (id, first_name, last_name, email) ordered by last name."""
    with _cursor() as cursor:
        return cursor.execute(
            """
            SELECT id, first_name, last_name, email
            FROM tenants
            ORDER BY last_name
            """
        ).fetchall()


# ---------------------------------------------------------------------------
# Leases
# ---------------------------------------------------------------------------
def create_lease(
    tenant_id,
    property_id,
    unit_id,
    lease_start,
    lease_end,
    monthly_rent,
    security_deposit,
):
    with _cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO leases
            (tenant_id, property_id, unit_id, lease_start, lease_end,
             monthly_rent, security_deposit)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tenant_id,
                property_id,
                unit_id,
                lease_start,
                lease_end,
                monthly_rent,
                security_deposit,
            ),
        )


def list_leases_with_details():
    """Return rows of (first_name, last_name, property_name, unit_name, monthly_rent)."""
    with _cursor() as cursor:
        return cursor.execute(
            """
            SELECT t.first_name, t.last_name, p.name, u.name, l.monthly_rent
            FROM leases l
            JOIN tenants t ON l.tenant_id = t.id
            JOIN properties p ON l.property_id = p.id
            JOIN units u ON l.unit_id = u.id
            ORDER BY l.id DESC
            """
        ).fetchall()


def active_leases_with_details():
    """Return rows of (lease_id, first_name, last_name, property_name, unit_name, monthly_rent)."""
    with _cursor() as cursor:
        return cursor.execute(
            """
            SELECT l.id, t.first_name, t.last_name, p.name, u.name, l.monthly_rent
            FROM leases l
            JOIN tenants t ON l.tenant_id = t.id
            JOIN units u ON l.unit_id = u.id
            JOIN properties p ON l.property_id = p.id
            WHERE l.active = 1
            ORDER BY l.id DESC
            """
        ).fetchall()


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------
def add_payment(lease_id, amount, payment_method, payment_date=None, notes=None):
    """Insert a payment and return its generated receipt number.

    The receipt number is derived from the row id so it is always unique.
    """
    payment_date = payment_date or str(date.today())
    with _cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO payments (lease_id, payment_date, amount, payment_method, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (lease_id, payment_date, amount, payment_method, notes),
        )
        payment_id = cursor.lastrowid
        receipt_number = f"RT-{date.today().year}-{payment_id:06d}"
        cursor.execute(
            "UPDATE payments SET receipt_number = ? WHERE id = ?",
            (receipt_number, payment_id),
        )
        return receipt_number


def list_payments():
    """Return rows of (receipt_number, amount, payment_date), newest first."""
    with _cursor() as cursor:
        return cursor.execute(
            """
            SELECT receipt_number, amount, payment_date
            FROM payments
            ORDER BY id DESC
            """
        ).fetchall()


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------
def total_collected():
    """Return the total amount collected across all payments."""
    with _cursor() as cursor:
        return cursor.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM payments"
        ).fetchone()[0]


def active_lease_count():
    with _cursor() as cursor:
        return cursor.execute(
            "SELECT COUNT(*) FROM leases WHERE active = 1"
        ).fetchone()[0]


def monthly_rent_roll():
    """Return the total monthly rent across active leases."""
    with _cursor() as cursor:
        return cursor.execute(
            "SELECT COALESCE(SUM(monthly_rent), 0) FROM leases WHERE active = 1"
        ).fetchone()[0]


def payments_summary_by_lease():
    """Return per-lease payment totals.

    Rows of (first_name, last_name, property_name, unit_name,
    payment_count, total_paid, last_payment_date) for every lease.
    """
    with _cursor() as cursor:
        return cursor.execute(
            """
            SELECT
                t.first_name,
                t.last_name,
                p.name,
                u.name,
                COUNT(pay.id),
                COALESCE(SUM(pay.amount), 0),
                MAX(pay.payment_date)
            FROM leases l
            JOIN tenants t ON l.tenant_id = t.id
            JOIN properties p ON l.property_id = p.id
            JOIN units u ON l.unit_id = u.id
            LEFT JOIN payments pay ON pay.lease_id = l.id
            GROUP BY l.id
            ORDER BY t.last_name, t.first_name
            """
        ).fetchall()


# ---------------------------------------------------------------------------
# Detail lookups, updates and deletes
# ---------------------------------------------------------------------------
def get_property(property_id):
    """Return (id, name, address) for one property, or None."""
    with _cursor() as cursor:
        return cursor.execute(
            "SELECT id, name, address FROM properties WHERE id = ?",
            (property_id,),
        ).fetchone()


def update_property(property_id, name, address):
    with _cursor() as cursor:
        cursor.execute(
            "UPDATE properties SET name = ?, address = ? WHERE id = ?",
            (name, address, property_id),
        )


def delete_property(property_id):
    with _cursor() as cursor:
        cursor.execute(
            "DELETE FROM properties WHERE id = ?",
            (property_id,),
        )


def list_units():
    """Return (id, property_id, property_name, name, description, monthly_rent)."""
    with _cursor() as cursor:
        return cursor.execute(
            """
            SELECT u.id, u.property_id, p.name, u.name, u.description, u.monthly_rent
            FROM units u
            JOIN properties p ON u.property_id = p.id
            ORDER BY p.name, u.name
            """
        ).fetchall()


def get_unit(unit_id):
    """Return (id, property_id, name, description, monthly_rent), or None."""
    with _cursor() as cursor:
        return cursor.execute(
            """
            SELECT id, property_id, name, description, monthly_rent
            FROM units WHERE id = ?
            """,
            (unit_id,),
        ).fetchone()


def update_unit(unit_id, property_id, name, description, monthly_rent):
    with _cursor() as cursor:
        cursor.execute(
            """
            UPDATE units
            SET property_id = ?, name = ?, description = ?, monthly_rent = ?
            WHERE id = ?
            """,
            (property_id, name, description, monthly_rent, unit_id),
        )


def delete_unit(unit_id):
    with _cursor() as cursor:
        cursor.execute(
            "DELETE FROM units WHERE id = ?",
            (unit_id,),
        )


def get_tenant(tenant_id):
    """Return (id, first_name, last_name, email, phone), or None."""
    with _cursor() as cursor:
        return cursor.execute(
            """
            SELECT id, first_name, last_name, email, phone
            FROM tenants WHERE id = ?
            """,
            (tenant_id,),
        ).fetchone()


def update_tenant(tenant_id, first_name, last_name, email, phone=None):
    with _cursor() as cursor:
        cursor.execute(
            """
            UPDATE tenants
            SET first_name = ?, last_name = ?, email = ?, phone = ?
            WHERE id = ?
            """,
            (first_name, last_name, email, phone, tenant_id),
        )


def delete_tenant(tenant_id):
    with _cursor() as cursor:
        cursor.execute(
            "DELETE FROM tenants WHERE id = ?",
            (tenant_id,),
        )


def list_leases_full():
    """Return full lease rows for display and editing.

    (id, tenant_id, property_id, unit_id, first_name, last_name,
    property_name, unit_name, lease_start, lease_end, monthly_rent,
    security_deposit)
    """
    with _cursor() as cursor:
        return cursor.execute(
            """
            SELECT
                l.id, l.tenant_id, l.property_id, l.unit_id,
                t.first_name, t.last_name, p.name, u.name,
                l.lease_start, l.lease_end, l.monthly_rent, l.security_deposit
            FROM leases l
            JOIN tenants t ON l.tenant_id = t.id
            JOIN properties p ON l.property_id = p.id
            JOIN units u ON l.unit_id = u.id
            ORDER BY l.id DESC
            """
        ).fetchall()


def get_lease(lease_id):
    """Return full lease row, or None.

    (id, tenant_id, property_id, unit_id, lease_start, lease_end,
    monthly_rent, security_deposit)
    """
    with _cursor() as cursor:
        return cursor.execute(
            """
            SELECT id, tenant_id, property_id, unit_id,
                   lease_start, lease_end, monthly_rent, security_deposit
            FROM leases WHERE id = ?
            """,
            (lease_id,),
        ).fetchone()


def update_lease(
    lease_id,
    tenant_id,
    property_id,
    unit_id,
    lease_start,
    lease_end,
    monthly_rent,
    security_deposit,
):
    with _cursor() as cursor:
        cursor.execute(
            """
            UPDATE leases
            SET tenant_id = ?, property_id = ?, unit_id = ?,
                lease_start = ?, lease_end = ?, monthly_rent = ?,
                security_deposit = ?
            WHERE id = ?
            """,
            (
                tenant_id,
                property_id,
                unit_id,
                lease_start,
                lease_end,
                monthly_rent,
                security_deposit,
                lease_id,
            ),
        )


def delete_lease(lease_id):
    with _cursor() as cursor:
        cursor.execute(
            "DELETE FROM leases WHERE id = ?",
            (lease_id,),
        )


def get_payment_detail(payment_id):
    """Return a detailed payment row for the read-only detail view, or None.

    (receipt_number, payment_date, amount, payment_method, notes,
    first_name, last_name, property_name, unit_name)
    """
    with _cursor() as cursor:
        return cursor.execute(
            """
            SELECT
                pay.receipt_number, pay.payment_date, pay.amount,
                pay.payment_method, pay.notes,
                t.first_name, t.last_name, p.name, u.name
            FROM payments pay
            JOIN leases l ON pay.lease_id = l.id
            JOIN tenants t ON l.tenant_id = t.id
            JOIN properties p ON l.property_id = p.id
            JOIN units u ON l.unit_id = u.id
            WHERE pay.id = ?
            """,
            (payment_id,),
        ).fetchone()


def list_payments_with_id():
    """Return (id, receipt_number, amount, payment_date), newest first."""
    with _cursor() as cursor:
        return cursor.execute(
            """
            SELECT id, receipt_number, amount, payment_date
            FROM payments
            ORDER BY id DESC
            """
        ).fetchall()


def get_payment_receipt_context(payment_id):
    """Return a payment's data for emailing a receipt, or None.

    (receipt_number, payment_date, amount, payment_method, notes,
    first_name, last_name, email, property_name, unit_name)
    """
    with _cursor() as cursor:
        return cursor.execute(
            """
            SELECT
                pay.receipt_number, pay.payment_date, pay.amount,
                pay.payment_method, pay.notes,
                t.first_name, t.last_name, t.email, p.name, u.name
            FROM payments pay
            JOIN leases l ON pay.lease_id = l.id
            JOIN tenants t ON l.tenant_id = t.id
            JOIN properties p ON l.property_id = p.id
            JOIN units u ON l.unit_id = u.id
            WHERE pay.id = ?
            """,
            (payment_id,),
        ).fetchone()
