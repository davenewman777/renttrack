from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QListWidget
)

from database.db import get_connection


class PropertyWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Properties")
        self.resize(500,400)

        layout = QVBoxLayout()

        self.name = QLineEdit()
        self.name.setPlaceholderText(
            "Property Name"
        )

        self.address = QLineEdit()
        self.address.setPlaceholderText(
            "Address"
        )

        save = QPushButton(
            "Save Property"
        )

        save.clicked.connect(
            self.save_property
        )

        self.list = QListWidget()

        layout.addWidget(
            QLabel("Property Management")
        )

        layout.addWidget(self.name)
        layout.addWidget(self.address)
        layout.addWidget(save)
        layout.addWidget(self.list)

        self.setLayout(layout)

        self.load_properties()


    def save_property(self):

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO properties
            (
            name,
            address
            )
            VALUES (?,?)
            """,
            (
            self.name.text(),
            self.address.text()
            )
        )

        connection.commit()
        connection.close()

        self.load_properties()


    def load_properties(self):

        self.list.clear()

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT name,address
            FROM properties
            """
        )

        for row in cursor.fetchall():

            self.list.addItem(
                f"{row[0]} - {row[1]}"
            )

        connection.close()