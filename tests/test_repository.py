import sqlite3

import pytest

import database.db as db
from database import repository
from database.migrations import run_migrations


@pytest.fixture()
def temp_db(tmp_path, monkeypatch):
    """Point the app at a fresh temporary database for each test."""
    test_db_path = tmp_path / "test_renttrack.db"
    monkeypatch.setattr(db, "DATABASE_PATH", test_db_path)
    db.initialize_database()
    run_migrations()
    yield


def _seed_lease():
    """Create a property -> unit -> tenant -> lease chain and return lease id."""
    repository.add_property("My House", "1 Main St")
    property_id = repository.list_properties()[0][0]

    repository.add_unit(property_id, "Room 1", "Spare bedroom", 500.0)
    unit_id = repository.units_for_property(property_id)[0][0]

    repository.add_tenant("Sam", "Lee", "sam@example.com", "555-0100")
    tenant_id = repository.list_tenants()[0][0]

    repository.create_lease(
        tenant_id, property_id, unit_id, "2026-01-01", "2026-12-31", 500.0, 500.0
    )
    return repository.active_leases_with_details()[0][0]


def test_add_and_list_property(temp_db):
    repository.add_property("House", "123 St")
    rows = repository.list_properties()
    assert len(rows) == 1
    assert rows[0][1] == "House"
    assert rows[0][2] == "123 St"


def test_add_and_list_unit(temp_db):
    repository.add_property("House", "123 St")
    property_id = repository.list_properties()[0][0]
    repository.add_unit(property_id, "Room 1", "Spare", 450.0)

    units = repository.units_for_property(property_id)
    assert len(units) == 1
    assert units[0][1] == "Room 1"
    assert units[0][2] == 450.0

    with_property = repository.list_units_with_property()
    assert with_property[0][0] == "House"
    assert with_property[0][1] == "Room 1"


def test_add_and_list_tenant(temp_db):
    repository.add_tenant("Sam", "Lee", "sam@example.com", "555-0100")
    tenants = repository.list_tenants()
    assert len(tenants) == 1
    assert tenants[0][1] == "Sam"
    assert tenants[0][2] == "Lee"


def test_create_lease_appears_in_details(temp_db):
    _seed_lease()
    details = repository.list_leases_with_details()
    assert len(details) == 1
    assert details[0][0] == "Sam"
    assert details[0][2] == "My House"
    assert details[0][4] == 500.0


def test_add_payment_returns_unique_receipts(temp_db):
    lease_id = _seed_lease()

    first = repository.add_payment(lease_id, 500.0, "Cash")
    second = repository.add_payment(lease_id, 500.0, "Cash")

    assert first != second
    assert first.startswith("RT-")

    payments = repository.list_payments()
    assert len(payments) == 2


def test_total_collected_and_rent_roll(temp_db):
    lease_id = _seed_lease()
    repository.add_payment(lease_id, 500.0, "Cash")
    repository.add_payment(lease_id, 250.0, "eTransfer")

    assert repository.total_collected() == 750.0
    assert repository.active_lease_count() == 1
    assert repository.monthly_rent_roll() == 500.0


def test_payments_summary_by_lease(temp_db):
    lease_id = _seed_lease()
    repository.add_payment(lease_id, 500.0, "Cash")

    summary = repository.payments_summary_by_lease()
    assert len(summary) == 1
    first_name, last_name, property_name, unit_name, count, total = summary[0]
    assert (first_name, last_name) == ("Sam", "Lee")
    assert count == 1
    assert total == 500.0


def test_foreign_key_enforced_on_payment(temp_db):
    # No lease with id 9999 exists; FK enforcement should reject it.
    with pytest.raises(sqlite3.IntegrityError):
        repository.add_payment(9999, 100.0, "Cash")
