from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QListWidget
)

from database.db import get_connection


class TenantWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Tenants")

        layout = QVBoxLayout()

        self.first_name = QLineEdit()
        self.first_name.setPlaceholderText(
            "First Name"
        )

        self.last_name = QLineEdit()
        self.last_name.setPlaceholderText(
            "Last Name"
        )

        self.email = QLineEdit()
        self.email.setPlaceholderText(
            "Email"
        )

        save = QPushButton(
            "Save Tenant"
        )

        save.clicked.connect(
            self.save_tenant
        )

        self.list = QListWidget()

        layout.addWidget(
            QLabel("Tenant Management")
        )

        layout.addWidget(
            self.first_name
        )

        layout.addWidget(
            self.last_name
        )

        layout.addWidget(
            self.email
        )

        layout.addWidget(
            save
        )

        layout.addWidget(
            self.list
        )

        self.setLayout(layout)

        self.load_tenants()


    def save_tenant(self):

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO tenants
            (
            first_name,
            last_name,
            email
            )
            VALUES (?,?,?)
            """,
            (
            self.first_name.text(),
            self.last_name.text(),
            self.email.text()
            )
        )

        connection.commit()
        connection.close()

        self.load_tenants()


    def load_tenants(self):

        self.list.clear()

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT first_name,last_name,email
            FROM tenants
            """
        )

        for row in cursor.fetchall():

            self.list.addItem(
                f"{row[0]} {row[1]} - {row[2]}"
            )

        connection.close()