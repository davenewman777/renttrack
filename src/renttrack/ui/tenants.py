from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox
)

from database import repository


class TenantWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Tenants")

        self.selected_id = None

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

        self.phone = QLineEdit()
        self.phone.setPlaceholderText(
            "Phone"
        )

        self.save_button = QPushButton(
            "Save Tenant"
        )

        self.save_button.clicked.connect(
            self.save_tenant
        )

        new_button = QPushButton("New")
        new_button.clicked.connect(self.clear_form)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_tenant)
        self.delete_button.setEnabled(False)

        buttons = QHBoxLayout()
        buttons.addWidget(self.save_button)
        buttons.addWidget(new_button)
        buttons.addWidget(self.delete_button)

        self.list = QListWidget()
        self.list.itemClicked.connect(self.select_tenant)

        layout.addWidget(
            QLabel("Tenant Management")
        )

        layout.addWidget(self.first_name)
        layout.addWidget(self.last_name)
        layout.addWidget(self.email)
        layout.addWidget(self.phone)
        layout.addLayout(buttons)
        layout.addWidget(
            QLabel("Existing Tenants (click to edit)")
        )
        layout.addWidget(self.list)

        self.setLayout(layout)

        self.load_tenants()


    def load_tenants(self):

        self.list.clear()

        for row in repository.list_tenants():

            item = QListWidgetItem(
                f"{row[1]} {row[2]} - {row[3]}"
            )
            item.setData(Qt.UserRole, row[0])
            self.list.addItem(item)


    def select_tenant(self, item):

        tenant_id = item.data(Qt.UserRole)
        record = repository.get_tenant(tenant_id)

        if record is None:
            return

        # record = (id, first_name, last_name, email, phone)
        self.selected_id = record[0]
        self.first_name.setText(record[1] or "")
        self.last_name.setText(record[2] or "")
        self.email.setText(record[3] or "")
        self.phone.setText(record[4] or "")

        self.save_button.setText("Update Tenant")
        self.delete_button.setEnabled(True)


    def clear_form(self):

        self.selected_id = None
        self.first_name.clear()
        self.last_name.clear()
        self.email.clear()
        self.phone.clear()
        self.list.clearSelection()

        self.save_button.setText("Save Tenant")
        self.delete_button.setEnabled(False)


    def save_tenant(self):

        first_name = self.first_name.text().strip()
        last_name = self.last_name.text().strip()

        if not first_name or not last_name:
            QMessageBox.warning(
                self,
                "Missing Name",
                "First and last name are required."
            )
            return

        email = self.email.text().strip()
        phone = self.phone.text().strip() or None

        try:
            if self.selected_id is None:
                repository.add_tenant(first_name, last_name, email, phone)
            else:
                repository.update_tenant(
                    self.selected_id, first_name, last_name, email, phone
                )
        except Exception as error:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not save tenant:\n{error}"
            )
            return

        self.clear_form()
        self.load_tenants()


    def delete_tenant(self):

        if self.selected_id is None:
            return

        confirm = QMessageBox.question(
            self,
            "Delete Tenant",
            "Delete this tenant?"
        )

        if confirm != QMessageBox.Yes:
            return

        try:
            repository.delete_tenant(self.selected_id)
        except Exception as error:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not delete tenant:\n{error}"
            )
            return

        self.clear_form()
        self.load_tenants()