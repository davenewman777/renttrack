from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
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

        self.selected_id = None

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
        self.save_button = QPushButton(
            "Create Lease"
        )

        self.save_button.clicked.connect(
            self.save_lease
        )

        new_button = QPushButton("New")
        new_button.clicked.connect(self.clear_form)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_lease)
        self.delete_button.setEnabled(False)

        buttons = QHBoxLayout()
        buttons.addWidget(self.save_button)
        buttons.addWidget(new_button)
        buttons.addWidget(self.delete_button)

        layout.addLayout(buttons)


        #
        # Existing Leases
        #
        layout.addWidget(
            QLabel("Existing Leases (click to edit)")
        )

        self.lease_list = QListWidget()
        self.lease_list.itemClicked.connect(self.select_lease)

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

            if self.selected_id is None:
                repository.create_lease(
                    tenant_id,
                    property_id,
                    unit["id"],
                    start_text,
                    end_text,
                    monthly_rent,
                    security_deposit,
                )
            else:
                repository.update_lease(
                    self.selected_id,
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
                f"Could not save lease:\n{error}"
            )

            return


        self.clear_form()
        self.load_leases()



    #
    # Load One Lease Into The Form
    #
    def select_lease(self, item):

        lease_id = item.data(Qt.UserRole)
        record = repository.get_lease(lease_id)

        if record is None:
            return

        # record = (id, tenant_id, property_id, unit_id,
        #           lease_start, lease_end, monthly_rent, security_deposit)
        self.selected_id = record[0]

        tenant_index = self.tenant_combo.findData(record[1])
        if tenant_index >= 0:
            self.tenant_combo.setCurrentIndex(tenant_index)

        # Setting the property repopulates the unit combo (and resets rent),
        # so choose the unit and rent/deposit afterwards.
        property_index = self.property_combo.findData(record[2])
        if property_index >= 0:
            self.property_combo.setCurrentIndex(property_index)

        for i in range(self.unit_combo.count()):
            data = self.unit_combo.itemData(i)
            if data and data.get("id") == record[3]:
                self.unit_combo.setCurrentIndex(i)
                break

        self.start_date.setText(record[4] or "")
        self.end_date.setText(record[5] or "")
        self.rent.setText(str(record[6]) if record[6] is not None else "")
        self.deposit.setText(str(record[7]) if record[7] is not None else "")

        self.save_button.setText("Update Lease")
        self.delete_button.setEnabled(True)



    #
    # Reset The Form For A New Lease
    #
    def clear_form(self):

        self.selected_id = None
        self.start_date.clear()
        self.end_date.clear()
        self.rent.clear()
        self.deposit.clear()
        self.lease_list.clearSelection()

        self.save_button.setText("Create Lease")
        self.delete_button.setEnabled(False)



    #
    # Delete The Selected Lease
    #
    def delete_lease(self):

        if self.selected_id is None:
            return

        confirm = QMessageBox.question(
            self,
            "Delete Lease",
            "Delete this lease?"
        )

        if confirm != QMessageBox.Yes:
            return

        try:
            repository.delete_lease(self.selected_id)
        except sqlite3.Error as error:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not delete lease:\n{error}"
            )
            return

        self.clear_form()
        self.load_leases()



    #
    # Display Existing Leases
    #
    def load_leases(self):

        self.lease_list.clear()

        # row = (id, tenant_id, property_id, unit_id, first_name, last_name,
        #        property_name, unit_name, lease_start, lease_end,
        #        monthly_rent, security_deposit)
        for row in repository.list_leases_full():

            item = QListWidgetItem(

                f"{row[4]} {row[5]} | "
                f"{row[6]} | "
                f"{row[7]} | "
                f"${row[10]}"

            )
            item.setData(Qt.UserRole, row[0])
            self.lease_list.addItem(item)