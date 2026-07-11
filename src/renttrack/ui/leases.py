from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QLineEdit,
    QListWidget,
    QMessageBox
)

from database import repository

import sqlite3
from datetime import datetime


class LeaseWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Lease Management")
        self.resize(500, 600)

        layout = QVBoxLayout()

        #
        # Tenant Selection
        #
        layout.addWidget(
            QLabel("Tenant")
        )

        self.tenant_combo = QComboBox()

        layout.addWidget(
            self.tenant_combo
        )


        #
        # Property Selection
        #
        layout.addWidget(
            QLabel("Property")
        )

        self.property_combo = QComboBox()

        self.property_combo.currentIndexChanged.connect(
            self.load_units
        )

        layout.addWidget(
            self.property_combo
        )


        #
        # Unit Selection
        #
        layout.addWidget(
            QLabel("Unit")
        )

        self.unit_combo = QComboBox()

        self.unit_combo.currentIndexChanged.connect(
            self.load_rent
        )

        layout.addWidget(
            self.unit_combo
        )


        #
        # Lease Dates
        #
        layout.addWidget(
            QLabel("Lease Start YYYY-MM-DD")
        )

        self.start_date = QLineEdit()

        layout.addWidget(
            self.start_date
        )


        layout.addWidget(
            QLabel("Lease End YYYY-MM-DD")
        )

        self.end_date = QLineEdit()

        layout.addWidget(
            self.end_date
        )


        #
        # Rent
        #
        layout.addWidget(
            QLabel("Monthly Rent")
        )

        self.rent = QLineEdit()

        layout.addWidget(
            self.rent
        )


        #
        # Deposit
        #
        layout.addWidget(
            QLabel("Security Deposit")
        )

        self.deposit = QLineEdit()

        layout.addWidget(
            self.deposit
        )


        #
        # Save
        #
        save_button = QPushButton(
            "Create Lease"
        )

        save_button.clicked.connect(
            self.save_lease
        )

        layout.addWidget(
            save_button
        )


        #
        # Existing Leases
        #
        layout.addWidget(
            QLabel("Existing Leases")
        )

        self.lease_list = QListWidget()

        layout.addWidget(
            self.lease_list
        )


        self.setLayout(
            layout
        )


        self.load_tenants()
        self.load_properties()
        self.load_leases()



    #
    # Load Tenants
    #
    def load_tenants(self):

        self.tenant_combo.clear()

        for tenant in repository.list_tenants():

            tenant_id = tenant[0]

            name = (
                f"{tenant[1]} {tenant[2]}"
            )

            self.tenant_combo.addItem(
                name,
                tenant_id
            )



    #
    # Load Properties
    #
    def load_properties(self):

        self.property_combo.clear()

        for prop in repository.list_properties():

            self.property_combo.addItem(
                prop[1],
                prop[0]
            )

        self.load_units()



    #
    # Load Units Based on Property
    #
    def load_units(self):

        self.unit_combo.clear()

        property_id = (
            self.property_combo.currentData()
        )

        if property_id is None:
            self.unit_combo.clear()
            return

        for unit in repository.units_for_property(property_id):

            self.unit_combo.addItem(
                unit[1],
                {
                    "id": unit[0],
                    "rent": unit[2]
                }
            )

        self.load_rent()



    #
    # Auto Populate Rent
    #
    def load_rent(self):

        unit = (
            self.unit_combo.currentData()
        )


        if unit:

            self.rent.setText(
                str(unit["rent"])
            )



    #
    # Save Lease
    #
    def save_lease(self):

        tenant_id = (
            self.tenant_combo.currentData()
        )

        property_id = (
            self.property_combo.currentData()
        )

        unit = (
            self.unit_combo.currentData()
        )


        if not tenant_id or not unit:

            QMessageBox.warning(
                self,
                "Missing Information",
                "Please select tenant and unit."
            )

            return


        rent_text = self.rent.text().strip()

        try:
            monthly_rent = float(rent_text)
        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Rent",
                "Monthly rent must be a number."
            )
            return

        if monthly_rent <= 0:
            QMessageBox.warning(
                self,
                "Invalid Rent",
                "Monthly rent must be greater than zero."
            )
            return


        deposit_text = self.deposit.text().strip()

        if deposit_text:
            try:
                security_deposit = float(deposit_text)
            except ValueError:
                QMessageBox.warning(
                    self,
                    "Invalid Deposit",
                    "Security deposit must be a number."
                )
                return
        else:
            security_deposit = 0.0


        start_text = self.start_date.text().strip()
        end_text = self.end_date.text().strip()

        for label, value in (("start", start_text), ("end", end_text)):
            if value:
                try:
                    datetime.strptime(value, "%Y-%m-%d")
                except ValueError:
                    QMessageBox.warning(
                        self,
                        "Invalid Date",
                        f"Lease {label} date must be in YYYY-MM-DD format."
                    )
                    return


        try:

            repository.create_lease(
                tenant_id,
                property_id,
                unit["id"],
                start_text,
                end_text,
                monthly_rent,
                security_deposit,
            )

        except sqlite3.Error as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not create lease:\n{error}"
            )

            return


        QMessageBox.information(
            self,
            "Success",
            "Lease created successfully."
        )

        self.load_leases()


        self.load_leases()



    #
    # Display Existing Leases
    #
    def load_leases(self):

        self.lease_list.clear()

        for lease in repository.list_leases_with_details():

            self.lease_list.addItem(

                f"{lease[0]} {lease[1]} | "
                f"{lease[2]} | "
                f"{lease[3]} | "
                f"${lease[4]}"

            )