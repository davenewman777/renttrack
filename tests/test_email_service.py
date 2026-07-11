import smtplib

import pytest

import database.db as db
from database import repository
from database.migrations import run_migrations
from services import email_service
from services.pdf_receipt import build_receipt_pdf


SMTP_ENV_VARS = [
    "RENTTRACK_SMTP_HOST",
    "RENTTRACK_SMTP_PORT",
    "RENTTRACK_SMTP_USER",
    "RENTTRACK_SMTP_PASSWORD",
    "RENTTRACK_SMTP_FROM",
    "RENTTRACK_SMTP_USE_TLS",
]


@pytest.fixture()
def email_env(tmp_path, monkeypatch):
    """Isolate email config: clear env vars and point config file at tmp."""
    for name in SMTP_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(
        email_service, "CONFIG_PATH", tmp_path / "email_config.json"
    )
    yield monkeypatch


def _context():
    return {
        "receipt_number": "RT-2026-000001",
        "payment_date": "2026-07-11",
        "amount": 500.0,
        "payment_method": "Cash",
        "notes": "July rent",
        "tenant_name": "Sam Lee",
        "property_name": "My House",
        "unit_name": "Room 1",
    }


def test_build_receipt_contains_key_fields():
    subject, body = email_service.build_receipt(_context())
    assert "RT-2026-000001" in subject
    assert "Sam Lee" in body
    assert "$500.0" in body
    assert "My House" in body
    assert "July rent" in body


def test_build_receipt_signature_includes_sender_name():
    context = {**_context(), "sender_name": "Dave Newman"}
    _, body = email_service.build_receipt(context)
    assert "Dave Newman" in body
    assert "RentTrack" in body


def test_build_receipt_signature_defaults_to_app_name():
    _, body = email_service.build_receipt(_context())
    assert "Regards,\nRentTrack" in body


def test_is_configured_false_when_unset(email_env):
    assert email_service.is_configured() is False


def test_send_receipt_raises_when_not_configured(email_env):
    with pytest.raises(email_service.EmailNotConfigured):
        email_service.send_receipt("tenant@example.com", _context())


def test_send_receipt_requires_email(email_env):
    with pytest.raises(ValueError):
        email_service.send_receipt("", _context())


def test_send_receipt_uses_smtp_when_configured(email_env, monkeypatch):
    monkeypatch.setenv("RENTTRACK_SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("RENTTRACK_SMTP_USER", "me@example.com")
    monkeypatch.setenv("RENTTRACK_SMTP_PASSWORD", "secret")
    monkeypatch.setenv("RENTTRACK_SMTP_FROM", "me@example.com")

    sent = {}

    class FakeSMTP:
        def __init__(self, host, port):
            sent["host"] = host
            sent["port"] = port

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def starttls(self, context=None):
            sent["tls"] = True

        def login(self, user, password):
            sent["login"] = (user, password)

        def send_message(self, message):
            sent["to"] = message["To"]
            sent["subject"] = message["Subject"]

    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)

    email_service.send_receipt("tenant@example.com", _context())

    assert sent["host"] == "smtp.example.com"
    assert sent["login"] == ("me@example.com", "secret")
    assert sent["to"] == "tenant@example.com"
    assert "RT-2026-000001" in sent["subject"]


def test_build_receipt_pdf_returns_pdf_bytes():
    data = build_receipt_pdf(_context())
    assert isinstance(data, (bytes, bytearray))
    assert data.startswith(b"%PDF")
    assert len(data) > 500


def test_save_receipt_pdf_writes_file(tmp_path):
    from services.pdf_receipt import save_receipt_pdf

    path = save_receipt_pdf(_context(), directory=tmp_path)

    assert path.exists()
    assert path.name == "receipt_RT-2026-000001.pdf"
    assert path.read_bytes().startswith(b"%PDF")


def test_send_receipt_attaches_pdf(email_env, monkeypatch):
    monkeypatch.setenv("RENTTRACK_SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("RENTTRACK_SMTP_USER", "me@example.com")
    monkeypatch.setenv("RENTTRACK_SMTP_PASSWORD", "secret")
    monkeypatch.setenv("RENTTRACK_SMTP_FROM", "me@example.com")

    captured = {}

    class FakeSMTP:
        def __init__(self, host, port):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def starttls(self, context=None):
            pass

        def login(self, user, password):
            pass

        def send_message(self, message):
            captured["message"] = message

    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)

    email_service.send_receipt("tenant@example.com", _context())

    attachments = [
        part
        for part in captured["message"].iter_attachments()
    ]
    assert len(attachments) == 1
    assert attachments[0].get_content_type() == "application/pdf"
    assert attachments[0].get_filename() == "receipt_RT-2026-000001.pdf"


def test_get_payment_receipt_context_includes_email(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DATABASE_PATH", tmp_path / "test.db")
    db.initialize_database()
    run_migrations()

    repository.add_property("My House", "1 Main St")
    property_id = repository.list_properties()[0][0]
    repository.add_unit(property_id, "Room 1", "Spare", 500.0)
    unit_id = repository.units_for_property(property_id)[0][0]
    repository.add_tenant("Sam", "Lee", "sam@example.com")
    tenant_id = repository.list_tenants()[0][0]
    repository.create_lease(
        tenant_id, property_id, unit_id, "2026-01-01", "2026-12-31", 500.0, 500.0
    )
    lease_id = repository.active_leases_with_details()[0][0]
    repository.add_payment(lease_id, 500.0, "Cash")
    payment_id = repository.list_payments_with_id()[0][0]

    row = repository.get_payment_receipt_context(payment_id)
    # (receipt, date, amount, method, notes, first, last, email, property, unit)
    assert row[7] == "sam@example.com"
    assert row[8] == "My House"
