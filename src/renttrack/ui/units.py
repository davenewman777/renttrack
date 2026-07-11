from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QListWidget
)

from database.db import get_connection


class UnitWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Units"
        )

        layout = QVBoxLayout()

        self.property_id = QLineEdit()
        self.property_id.setPlaceholderText(
            "Property ID"
        )

        self.name = QLineEdit()
        self.name.setPlaceholderText(
            "Unit / Room Name"
        )

        self.description = QLineEdit()
        self.description.setPlaceholderText(
            "Description"
        )

        self.rent = QLineEdit()
        self.rent.setPlaceholderText(
            "Monthly Rent"
        )

        save = QPushButton(
            "Save Unit"
        )

        save.clicked.connect(
            self.save_unit
        )

        self.list = QListWidget()

        layout.addWidget(
            QLabel("Unit Management")
        )

        layout.addWidget(self.property_id)
        layout.addWidget(self.name)
        layout.addWidget(self.description)
        layout.addWidget(self.rent)
        layout.addWidget(save)
        layout.addWidget(self.list)

        self.setLayout(layout)

        self.load_units()


    def save_unit(self):

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
            self.property_id.text(),
            self.name.text(),
            self.description.text(),
            self.rent.text()
            )
        )

        connection.commit()
        connection.close()

        self.load_units()


    def load_units(self):

        self.list.clear()

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT name,monthly_rent
            FROM units
            """
        )

        for row in cursor.fetchall():

            self.list.addItem(
                f"{row[0]} - ${row[1]}"
            )

        connection.close()