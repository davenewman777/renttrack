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

from database.db import get_connection

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


        connection = get_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            SELECT

            l.id,

            t.first_name,
            t.last_name,

            p.name,

            u.name,

            l.monthly_rent


            FROM leases l


            JOIN tenants t
            ON l.tenant_id=t.id


            JOIN units u
            ON l.unit_id=u.id


            JOIN properties p
            ON l.property_id=p.id


            WHERE l.active=1

            """
        )


        leases = cursor.fetchall()


        for lease in leases:

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


        connection.close()



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


        connection = get_connection()

        cursor = connection.cursor()


        receipt_number = (
            f"RT-{date.today().year}-"
            f"{cursor.execute('SELECT COUNT(*) FROM payments').fetchone()[0]+1:06d}"
        )


        cursor.execute(
            """
            INSERT INTO payments
            (
            lease_id,
            receipt_number,
            payment_date,
            amount,
            payment_method
            )

            VALUES (?,?,?,?,?)

            """,

            (

            lease_id,

            receipt_number,

            str(date.today()),

            self.amount.text(),

            self.method.currentText()

            )
        )


        connection.commit()

        connection.close()


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


        connection = get_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            SELECT
            receipt_number,
            amount,
            payment_date

            FROM payments

            ORDER BY id DESC

            """
        )


        for payment in cursor.fetchall():

            self.payment_list.addItem(

                f"{payment[0]} | "
                f"${payment[1]} | "
                f"{payment[2]}"

            )


        connection.close()