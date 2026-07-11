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

from database.db import get_connection


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

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, first_name, last_name
            FROM tenants
            ORDER BY last_name
            """
        )

        tenants = cursor.fetchall()

        for tenant in tenants:

            tenant_id = tenant[0]

            name = (
                f"{tenant[1]} {tenant[2]}"
            )

            self.tenant_combo.addItem(
                name,
                tenant_id
            )

        connection.close()



    #
    # Load Properties
    #
    def load_properties(self):

        self.property_combo.clear()

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id,name
            FROM properties
            ORDER BY name
            """
        )

        properties = cursor.fetchall()


        for prop in properties:

            self.property_combo.addItem(
                prop[1],
                prop[0]
            )


        connection.close()


        self.load_units()



    #
    # Load Units Based on Property
    #
    def load_units(self):

        self.unit_combo.clear()

        property_id = (
            self.property_combo.currentData()
        )

        print("Loading units for property:", property_id)

        if property_id is None:
            self.unit_combo.clear()
            print("No property selected, clearing units.")
            return


        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id,name,monthly_rent
            FROM units
            WHERE property_id=?
            ORDER BY name
            """,
            (
                property_id,
            )
        )


        units = cursor.fetchall()


        for unit in units:

            self.unit_combo.addItem(
                unit[1],
                {
                    "id": unit[0],
                    "rent": unit[2]
                }
            )


        connection.close()


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


        connection = get_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            INSERT INTO leases
            (
            tenant_id,
            property_id,
            unit_id,
            lease_start,
            lease_end,
            monthly_rent,
            security_deposit
            )

            VALUES (?,?,?,?,?,?,?)

            """,

            (

            tenant_id,

            property_id,

            unit["id"],

            self.start_date.text(),

            self.end_date.text(),

            self.rent.text(),

            self.deposit.text()

            )
        )


        connection.commit()

        connection.close()


        QMessageBox.information(
            self,
            "Success",
            "Lease created successfully."
        )


        self.load_leases()



    #
    # Display Existing Leases
    #
    def load_leases(self):

        self.lease_list.clear()


        connection = get_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            SELECT
            t.first_name,
            t.last_name,
            p.name,
            u.name,
            l.monthly_rent

            FROM leases l

            JOIN tenants t
            ON l.tenant_id=t.id

            JOIN properties p
            ON l.property_id=p.id

            JOIN units u
            ON l.unit_id=u.id

            ORDER BY l.id DESC

            """
        )


        leases = cursor.fetchall()


        for lease in leases:

            self.lease_list.addItem(

                f"{lease[0]} {lease[1]} | "
                f"{lease[2]} | "
                f"{lease[3]} | "
                f"${lease[4]}"

            )


        connection.close()