from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox
)

from database import repository
from services import email_service
from services import pdf_receipt

import sqlite3


class PaymentWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Payment Management"
        )

        self.resize(
            500,
            600
        )

        # id of the payment currently selected in the history list
        self.selected_payment_id = None


        layout = QVBoxLayout()


        layout.addWidget(
            QLabel("Active Lease")
        )


        self.lease_combo = QComboBox()

        layout.addWidget(
            self.lease_combo
        )


        layout.addWidget(
            QLabel("Amount")
        )


        self.amount = QLineEdit()

        layout.addWidget(
            self.amount
        )


        layout.addWidget(
            QLabel("Payment Method")
        )


        self.method = QComboBox()

        self.method.addItems(
            [
                "Cash",
                "Check",
                "eTransfer",
                "Bank Transfer",
                "Other"
            ]
        )

        layout.addWidget(
            self.method
        )


        self.save_button = QPushButton(
            "Save Payment"
        )

        self.save_button.clicked.connect(
            self.save_payment
        )

        layout.addWidget(
            self.save_button
        )


        self.email_button = QPushButton(
            "Email Receipt"
        )

        self.email_button.clicked.connect(
            self.email_receipt
        )

        self.email_button.setEnabled(False)

        layout.addWidget(
            self.email_button
        )


        self.preview_button = QPushButton(
            "Preview Receipt"
        )

        self.preview_button.clicked.connect(
            self.preview_receipt
        )

        self.preview_button.setEnabled(False)

        layout.addWidget(
            self.preview_button
        )


        layout.addWidget(
            QLabel("Payment History (click for details)")
        )


        self.payment_list = QListWidget()
        self.payment_list.itemClicked.connect(self.show_detail)

        layout.addWidget(
            self.payment_list
        )


        self.detail = QLabel(
            "Select a payment to view its details."
        )
        self.detail.setWordWrap(True)

        layout.addWidget(
            self.detail
        )


        self.setLayout(
            layout
        )


        self.load_leases()

        self.load_payments()



    #
    # Load Active Leases
    #
    def load_leases(self):

        self.lease_combo.clear()

        for lease in repository.active_leases_with_details():

            display = (

                f"{lease[1]} {lease[2]} - "
                f"{lease[3]} / "
                f"{lease[4]} - "
                f"${lease[5]}"

            )


            self.lease_combo.addItem(
                display,
                lease[0]
            )



    #
    # Save Payment
    #
    def save_payment(self):

        lease_id = (
            self.lease_combo.currentData()
        )


        if lease_id is None:

            QMessageBox.warning(
                self,
                "Missing Lease",
                "No active lease selected."
            )

            return


        amount_text = self.amount.text().strip()

        try:
            amount = float(amount_text)
        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Amount",
                "Amount must be a number."
            )
            return

        if amount <= 0:
            QMessageBox.warning(
                self,
                "Invalid Amount",
                "Amount must be greater than zero."
            )
            return


        try:

            receipt_number = repository.add_payment(
                lease_id,
                amount,
                self.method.currentText(),
            )

        except sqlite3.Error as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not save payment:\n{error}"
            )

            return


        QMessageBox.information(
            self,
            "Saved",
            f"Payment saved.\nReceipt {receipt_number}"
        )


        self.load_payments()

        new_payment_id = repository.list_payments_with_id()[0][0]

        # Always archive a local PDF copy of the receipt.
        self._save_local_copy(new_payment_id)

        # Auto-send the receipt if email is configured; stay silent otherwise
        # so saving is never blocked by missing SMTP settings.
        if email_service.is_configured():
            self._send_receipt(new_payment_id, announce_disabled=False)



    #
    # Load Payments
    #
    def load_payments(self):

        self.payment_list.clear()

        # row = (id, receipt_number, amount, payment_date)
        for row in repository.list_payments_with_id():

            item = QListWidgetItem(

                f"{row[1]} | "
                f"${row[2]} | "
                f"{row[3]}"

            )
            item.setData(Qt.UserRole, row[0])
            self.payment_list.addItem(item)


    #
    # Show Read-Only Payment Detail
    #
    def show_detail(self, item):

        payment_id = item.data(Qt.UserRole)
        record = repository.get_payment_detail(payment_id)

        if record is None:
            return

        self.selected_payment_id = payment_id
        self.email_button.setEnabled(True)
        self.preview_button.setEnabled(True)

        # record = (receipt_number, payment_date, amount, payment_method,
        #           notes, first_name, last_name, property_name, unit_name)
        (
            receipt_number,
            payment_date,
            amount,
            payment_method,
            notes,
            first_name,
            last_name,
            property_name,
            unit_name,
        ) = record

        self.detail.setText(
            f"Receipt: {receipt_number}\n"
            f"Date: {payment_date}\n"
            f"Amount: ${amount}\n"
            f"Method: {payment_method}\n"
            f"Tenant: {first_name} {last_name}\n"
            f"Property: {property_name}\n"
            f"Unit: {unit_name}\n"
            f"Notes: {notes or ''}"
        )


    #
    # Email The Selected Payment's Receipt
    #
    def email_receipt(self):

        if self.selected_payment_id is None:
            return

        self._send_receipt(
            self.selected_payment_id,
            announce_disabled=True,
        )


    #
    # Generate And Open A PDF Receipt Without Sending
    #
    def preview_receipt(self):

        if self.selected_payment_id is None:
            return

        result = self._context_for(self.selected_payment_id)

        if result is None:
            return

        context, _ = result

        try:
            preview_dir = pdf_receipt.receipts_dir().parent / "preview"
            path = pdf_receipt.save_receipt_pdf(context, directory=preview_dir)
        except OSError as error:
            QMessageBox.critical(
                self,
                "Preview Failed",
                f"Could not create the preview PDF:\n{error}",
            )
            return

        QDesktopServices.openUrl(
            QUrl.fromLocalFile(str(path))
        )


    def _send_receipt(self, payment_id, announce_disabled):
        """Email a receipt for one payment.

        announce_disabled=True shows a message when SMTP is not configured;
        the auto-send path passes False so saving stays silent.
        """

        result = self._context_for(payment_id)

        if result is None:
            return

        context, tenant_email = result

        try:
            email_service.send_receipt(tenant_email, context)

        except email_service.EmailNotConfigured as error:
            if announce_disabled:
                QMessageBox.warning(
                    self,
                    "Email Not Configured",
                    str(error),
                )
            return

        except ValueError as error:
            QMessageBox.warning(
                self,
                "No Email Address",
                str(error),
            )
            return

        except Exception as error:
            QMessageBox.critical(
                self,
                "Email Failed",
                f"Could not send receipt:\n{error}",
            )
            return

        QMessageBox.information(
            self,
            "Receipt Sent",
            f"Receipt {context['receipt_number']} emailed to {tenant_email}.",
        )


    def _context_for(self, payment_id):
        """Build (context, tenant_email) for a payment, or None."""

        row = repository.get_payment_receipt_context(payment_id)

        if row is None:
            return None

        # row = (receipt_number, payment_date, amount, payment_method, notes,
        #        first_name, last_name, email, property_name, unit_name)
        context = {
            "receipt_number": row[0],
            "payment_date": row[1],
            "amount": row[2],
            "payment_method": row[3],
            "notes": row[4],
            "tenant_name": f"{row[5]} {row[6]}",
            "property_name": row[8],
            "unit_name": row[9],
        }
        return context, row[7]


    def _save_local_copy(self, payment_id):
        """Archive a PDF copy of the receipt to data/receipts."""

        result = self._context_for(payment_id)

        if result is None:
            return

        context, _ = result

        try:
            pdf_receipt.save_receipt_pdf(context)
        except OSError as error:
            QMessageBox.warning(
                self,
                "Could Not Save Receipt",
                f"Payment saved, but the local PDF copy failed:\n{error}",
            )