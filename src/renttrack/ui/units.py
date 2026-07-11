from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QListWidget,
    QComboBox,
    QMessageBox
)

from database.db import get_connection


class UnitWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Unit Management")
        self.resize(500, 600)

        layout = QVBoxLayout()


        #
        # Property Selection
        #
        layout.addWidget(
            QLabel("Property")
        )

        self.property_combo = QComboBox()

        layout.addWidget(
            self.property_combo
        )


        #
        # Unit Name
        #
        layout.addWidget(
            QLabel("Unit Name")
        )

        self.name = QLineEdit()

        self.name.setPlaceholderText(
            "Example: Bedroom 3"
        )

        layout.addWidget(
            self.name
        )


        #
        # Description
        #
        layout.addWidget(
            QLabel("Description")
        )

        self.description = QLineEdit()

        self.description.setPlaceholderText(
            "Example: Spare bedroom"
        )

        layout.addWidget(
            self.description
        )


        #
        # Rent
        #
        layout.addWidget(
            QLabel("Monthly Rent")
        )

        self.rent = QLineEdit()

        self.rent.setPlaceholderText(
            "500"
        )

        layout.addWidget(
            self.rent
        )


        #
        # Save Button
        #
        save_button = QPushButton(
            "Save Unit"
        )

        save_button.clicked.connect(
            self.save_unit
        )

        layout.addWidget(
            save_button
        )


        #
        # Existing Units
        #
        layout.addWidget(
            QLabel("Existing Units")
        )

        self.unit_list = QListWidget()

        layout.addWidget(
            self.unit_list
        )


        self.setLayout(
            layout
        )


        self.load_properties()

        self.load_units()



    #
    # Load Existing Properties
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



    #
    # Save Unit
    #
    def save_unit(self):

        property_id = (
            self.property_combo.currentData()
        )


        if property_id is None:

            QMessageBox.warning(
                self,
                "Missing Property",
                "Please select a property."
            )

            return


        connection = get_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            INSERT INTO units
            (
            property_id,
            name,
            description,
            monthly_rent
            )

            VALUES (?,?,?,?)

            """,

            (
                property_id,
                self.name.text(),
                self.description.text(),
                self.rent.text()
            )
        )


        connection.commit()

        connection.close()


        QMessageBox.information(
            self,
            "Success",
            "Unit created successfully."
        )


        self.load_units()



    #
    # Display Existing Units
    #
    def load_units(self):

        self.unit_list.clear()


        connection = get_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            SELECT
            p.name,
            u.name,
            u.description,
            u.monthly_rent

            FROM units u

            JOIN properties p
            ON u.property_id=p.id

            ORDER BY p.name,u.name

            """
        )


        units = cursor.fetchall()


        for unit in units:

            self.unit_list.addItem(

                f"{unit[0]} | "
                f"{unit[1]} | "
                f"{unit[2]} | "
                f"${unit[3]}"

            )


        connection.close()