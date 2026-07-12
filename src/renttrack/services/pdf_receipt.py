"""Generate a PDF payment receipt as raw bytes.

Uses reportlab so it works without a running Qt application and is easy to
test. ``build_receipt_pdf`` is a pure function (no file or network I/O).
"""

from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)

import database.db as db


def build_receipt_pdf(context):
    """Return PDF bytes for a payment receipt.

    ``context`` keys: receipt_number, payment_date, amount, payment_method,
    notes, tenant_name, property_name, unit_name.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        leftMargin=inch,
        rightMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )

    styles = getSampleStyleSheet()

    rows = [
        ["Receipt number", str(context["receipt_number"])],
        ["Date", str(context["payment_date"])],
        ["Tenant", str(context["tenant_name"])],
        ["Property", str(context["property_name"])],
        ["Unit", str(context["unit_name"])],
        ["Amount", f"${context['amount']}"],
        ["Method", str(context["payment_method"])],
    ]

    if context.get("notes"):
        rows.append(["Notes", str(context["notes"])])

    table = Table(rows, colWidths=[2.0 * inch, 4.0 * inch])
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.75, colors.black),
                ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    elements = [
        Paragraph("RentTrack Payment Receipt", styles["Title"]),
        Spacer(1, 0.3 * inch),
        table,
        Spacer(1, 0.3 * inch),
        Paragraph("Thank you for your payment.", styles["Italic"]),
    ]

    doc.build(elements)

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
