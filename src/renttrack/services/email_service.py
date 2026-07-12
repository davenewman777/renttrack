"""Email delivery for payment receipts.

SMTP settings are read from environment variables first, then from an optional
JSON file at ``data/email_config.json`` (which is git-ignored). Credentials are
never hard-coded.

Environment variables:
    RENTTRACK_SMTP_HOST      e.g. smtp.gmail.com
    RENTTRACK_SMTP_PORT      e.g. 587 (default)
    RENTTRACK_SMTP_USER      login user / from address
    RENTTRACK_SMTP_PASSWORD  password or app-specific password
    RENTTRACK_SMTP_FROM      from address (defaults to SMTP_USER)
    RENTTRACK_SMTP_USE_TLS   "1"/"true" to use STARTTLS (default on)

JSON config keys mirror the names without the prefix, e.g.:
    {"host": "...", "port": 587, "username": "...", "password": "...",
     "from_address": "...", "use_tls": true}
"""

import json
import os
import smtplib
import ssl
from email.message import EmailMessage

from database.db import DATABASE_PATH
from services.pdf_receipt import build_receipt_pdf


CONFIG_PATH = DATABASE_PATH.parent / "email_config.json"


class EmailNotConfigured(Exception):
    """Raised when SMTP settings are incomplete."""


def _file_config():
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return {}
    return {}


def load_config():
    """Merge environment variables (priority) with the optional JSON file."""
    file_config = _file_config()

    def value(env_name, file_key, default=None):
        return os.environ.get(env_name) or file_config.get(file_key) or default

    username = value("RENTTRACK_SMTP_USER", "username")
    use_tls_raw = value("RENTTRACK_SMTP_USE_TLS", "use_tls", "1")

    return {
        "host": value("RENTTRACK_SMTP_HOST", "host"),
        "port": int(value("RENTTRACK_SMTP_PORT", "port", 587)),
        "username": username,
        "password": value("RENTTRACK_SMTP_PASSWORD", "password"),
        "from_address": value("RENTTRACK_SMTP_FROM", "from_address") or username,
        "use_tls": str(use_tls_raw).lower() in ("1", "true", "yes", "on"),
        "sender_name": value("RENTTRACK_SENDER_NAME", "sender_name"),
    }


def is_configured():
    config = load_config()
    return all(
        [
            config["host"],
            config["username"],
            config["password"],
            config["from_address"],
        ]
    )


def build_receipt(context):
    """Build (subject, body) for a payment receipt.

    ``context`` keys: receipt_number, payment_date, amount, payment_method,
    notes, tenant_name, property_name, unit_name, sender_name (optional).

    Pure function (no I/O) so it can be tested directly.
    """
    subject = f"RentTrack Receipt {context['receipt_number']}"

    body = (
        f"Hello {context['tenant_name']},\n\n"
        f"Thank you for your payment. Here is your receipt.\n\n"
        f"Receipt number: {context['receipt_number']}\n"
        f"Date: {context['payment_date']}\n"
        f"Amount: ${context['amount']}\n"
        f"Method: {context['payment_method']}\n"
        f"Property: {context['property_name']}\n"
        f"Unit: {context['unit_name']}\n"
    )

    if context.get("notes"):
        body += f"Notes: {context['notes']}\n"

    sender_name = context.get("sender_name")
    if sender_name:
        body += f"\nRegards,\n{sender_name}\nRentTrack\n"
    else:
        body += "\nRegards,\nRentTrack\n"

    return subject, body


def build_receipt_html(context):
    """Build an HTML receipt body with a gridlined details table.

    Mirrors the fields in ``build_receipt`` but lays them out in a bordered
    two-column table. Pure function (no I/O) so it can be tested directly.
    """
    import html

    rows = [
        ("Receipt number", context["receipt_number"]),
        ("Date", context["payment_date"]),
        ("Amount", f"${context['amount']}"),
        ("Method", context["payment_method"]),
        ("Property", context["property_name"]),
        ("Unit", context["unit_name"]),
    ]

    if context.get("notes"):
        rows.append(("Notes", context["notes"]))

    table_rows = "".join(
        (
            "<tr>"
            f"<td style=\"border:1px solid #333;padding:6px 10px;"
            f"background:#f5f5f5;font-weight:bold;\">{html.escape(str(label))}</td>"
            f"<td style=\"border:1px solid #333;padding:6px 10px;\">"
            f"{html.escape(str(value))}</td>"
            "</tr>"
        )
        for label, value in rows
    )

    sender_name = context.get("sender_name")
    signature = (
        f"{html.escape(sender_name)}<br>RentTrack" if sender_name else "RentTrack"
    )

    return (
        "<html><body style=\"font-family:Arial,sans-serif;color:#222;\">"
        f"<p>Hello {html.escape(str(context['tenant_name']))},</p>"
        "<p>Thank you for your payment. Here is your receipt.</p>"
        "<table style=\"border-collapse:collapse;border:1px solid #333;\">"
        f"{table_rows}"
        "</table>"
        f"<p>Regards,<br>{signature}</p>"
        "</body></html>"
    )


def send_receipt(to_email, context):
    """Send a receipt email to ``to_email``.

    Raises ``EmailNotConfigured`` if settings are incomplete, ``ValueError`` if
    ``to_email`` is empty, or ``smtplib``/``OSError`` exceptions on send failure.
    """
    if not to_email:
        raise ValueError("Tenant has no email address on file.")

    if not is_configured():
        raise EmailNotConfigured(
            "SMTP settings are not configured. Set RENTTRACK_SMTP_* "
            "environment variables or create data/email_config.json."
        )

    config = load_config()

    # Include the configured signature name in the receipt body.
    context = {**context, "sender_name": context.get("sender_name") or config.get("sender_name")}

    subject, body = build_receipt(context)

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = config["from_address"]
    message["To"] = to_email
    message.set_content(body)
    message.add_alternative(build_receipt_html(context), subtype="html")

    pdf_bytes = build_receipt_pdf(context)
    message.add_attachment(
        pdf_bytes,
        maintype="application",
        subtype="pdf",
        filename=f"receipt_{context['receipt_number']}.pdf",
    )

    with smtplib.SMTP(config["host"], config["port"]) as server:
        if config["use_tls"]:
            server.starttls(context=ssl.create_default_context())
        server.login(config["username"], config["password"])
        server.send_message(message)
