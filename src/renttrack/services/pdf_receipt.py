"""Generate a PDF payment receipt as raw bytes.

Uses reportlab so it works without a running Qt application and is easy to
test. ``build_receipt_pdf`` is a pure function (no file or network I/O).
"""

from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

import database.db as db


def build_receipt_pdf(context):
    """Return PDF bytes for a payment receipt.

    ``context`` keys: receipt_number, payment_date, amount, payment_method,
    notes, tenant_name, property_name, unit_name.
    """
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    left = inch
    y = height - inch

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(left, y, "RentTrack Payment Receipt")

    y -= 0.5 * inch
    pdf.setFont("Helvetica", 12)

    lines = [
        f"Receipt number: {context['receipt_number']}",
        f"Date: {context['payment_date']}",
        f"Tenant: {context['tenant_name']}",
        f"Property: {context['property_name']}",
        f"Unit: {context['unit_name']}",
        f"Amount: ${context['amount']}",
        f"Method: {context['payment_method']}",
    ]

    if context.get("notes"):
        lines.append(f"Notes: {context['notes']}")

    for line in lines:
        pdf.drawString(left, y, line)
        y -= 0.3 * inch

    y -= 0.3 * inch
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(left, y, "Thank you for your payment.")

    pdf.showPage()
    pdf.save()

    return buffer.getvalue()


def receipts_dir():
    """Return the directory where receipt PDFs are archived (data/receipts)."""
    return db.DATABASE_PATH.parent / "receipts"


def save_receipt_pdf(context, directory=None):
    """Write the receipt PDF to disk and return the file Path.

    Defaults to ``data/receipts/receipt_<number>.pdf``.
    """
    target_dir = Path(directory) if directory else receipts_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    path = target_dir / f"receipt_{context['receipt_number']}.pdf"
    path.write_bytes(build_receipt_pdf(context))

    return path
