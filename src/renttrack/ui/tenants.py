from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QListWidget
)

from database import repository


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

        repository.add_tenant(
            self.first_name.text(),
            self.last_name.text(),
            self.email.text(),
        )

        self.load_tenants()


    def load_tenants(self):

        self.list.clear()

        for row in repository.list_tenants():

            self.list.addItem(
                f"{row[1]} {row[2]} - {row[3]}"
            )