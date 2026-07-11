"""Send a test receipt email to verify SMTP (e.g. Gmail) is configured.

Reads settings from environment variables or data/email_config.json (the same
config the app uses), then sends a sample receipt to the address you pass.

Usage (from the project root):
    python tools/send_test_email.py you@example.com
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "renttrack"))

from services import email_service  # noqa: E402


SAMPLE_CONTEXT = {
    "receipt_number": "RT-TEST-000001",
    "payment_date": "2026-07-11",
    "amount": 950.00,
    "payment_method": "eTransfer",
    "notes": "This is a test receipt.",
    "tenant_name": "Test Tenant",
    "property_name": "123 Maple St",
    "unit_name": "Basement Suite",
}


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/send_test_email.py <recipient-email>")
        return 1

    recipient = sys.argv[1]

    if not email_service.is_configured():
        print(
            "SMTP is not configured.\n"
            "Set RENTTRACK_SMTP_* environment variables or fill in "
            "data/email_config.json, then run again."
        )
        return 1

    config = email_service.load_config()
    print(f"Sending via {config['host']}:{config['port']} as {config['username']} ...")

    try:
        email_service.send_receipt(recipient, SAMPLE_CONTEXT)
    except Exception as error:  # surface the real SMTP error to the user
        print(f"FAILED: {type(error).__name__}: {error}")
        return 1

    print(f"Success. Test receipt sent to {recipient}. Check the inbox (and spam).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
