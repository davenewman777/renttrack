from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QLineEdit,
    QListWidget,
    QMessageBox
)

from database import repository

import sqlite3
from datetime import date


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


        layout.addWidget(
            QLabel("Payment History")
        )


        self.payment_list = QListWidget()

        layout.addWidget(
            self.payment_list
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



    #
    # Load Payments
    #
    def load_payments(self):

        self.payment_list.clear()

        for payment in repository.list_payments():

            self.payment_list.addItem(

                f"{payment[0]} | "
                f"${payment[1]} | "
                f"{payment[2]}"

            )