"""Preview a payment-receipt email without sending it.

Builds the same subject, body, and attached PDF that RentTrack would email,
prints the text to the console, and writes an openable .eml file plus the PDF
to data/preview/. No SMTP account required.

Run from the project root:
    python tools/preview_email.py
"""

import sys
from email.message import EmailMessage
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "renttrack"))

from services.email_service import build_receipt          # noqa: E402
from services.pdf_receipt import build_receipt_pdf         # noqa: E402


SAMPLE_CONTEXT = {
    "receipt_number": "RT-2026-000123",
    "payment_date": "2026-07-11",
    "amount": 950.00,
    "payment_method": "eTransfer",
    "notes": "July rent",
    "tenant_name": "Jordan Smith",
    "property_name": "123 Maple St",
    "unit_name": "Basement Suite",
}


def main(context=SAMPLE_CONTEXT):
    subject, body = build_receipt(context)

    print("=" * 60)
    print("SUBJECT:", subject)
    print("=" * 60)
    print(body)
    print("=" * 60)

    pdf_bytes = build_receipt_pdf(context)

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = "you@example.com"
    message["To"] = "tenant@example.com"
    message.set_content(body)
    message.add_attachment(
        pdf_bytes,
        maintype="application",
        subtype="pdf",
        filename=f"receipt_{context['receipt_number']}.pdf",
    )

    out_dir = Path("data/preview")
    out_dir.mkdir(parents=True, exist_ok=True)

    eml_path = out_dir / "preview.eml"
    pdf_path = out_dir / f"receipt_{context['receipt_number']}.pdf"

    eml_path.write_bytes(bytes(message))
    pdf_path.write_bytes(pdf_bytes)

    print("Wrote email preview:", eml_path.resolve())
    print("Wrote PDF receipt: ", pdf_path.resolve())
    print()
    print("Open the .eml in Outlook/Mail to see the full email, or open the PDF directly.")


if __name__ == "__main__":
    main()
