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


class PropertyWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Properties")
        self.resize(500, 400)

        # id of the record currently loaded into the form (None => new record)
        self.selected_id = None

        layout = QVBoxLayout()

        self.name = QLineEdit()
        self.name.setPlaceholderText(
            "Property Name"
        )

        self.address = QLineEdit()
        self.address.setPlaceholderText(
            "Address"
        )

        self.save_button = QPushButton(
            "Save Property"
        )

        self.save_button.clicked.connect(
            self.save_property
        )

        new_button = QPushButton("New")
        new_button.clicked.connect(self.clear_form)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_property)
        self.delete_button.setEnabled(False)

        buttons = QHBoxLayout()
        buttons.addWidget(self.save_button)
        buttons.addWidget(new_button)
        buttons.addWidget(self.delete_button)

        self.list = QListWidget()
        self.list.itemClicked.connect(self.select_property)

        layout.addWidget(
            QLabel("Property Management")
        )

        layout.addWidget(self.name)
        layout.addWidget(self.address)
        layout.addLayout(buttons)
        layout.addWidget(
            QLabel("Existing Properties (click to edit)")
        )
        layout.addWidget(self.list)

        self.setLayout(layout)

        self.load_properties()


    def load_properties(self):

        self.list.clear()

        for row in repository.list_properties():

            item = QListWidgetItem(
                f"{row[1]} - {row[2]}"
            )
            item.setData(Qt.UserRole, row[0])
            self.list.addItem(item)


    def select_property(self, item):

        property_id = item.data(Qt.UserRole)
        record = repository.get_property(property_id)

        if record is None:
            return

        # record = (id, name, address)
        self.selected_id = record[0]
        self.name.setText(record[1] or "")
        self.address.setText(record[2] or "")

        self.save_button.setText("Update Property")
        self.delete_button.setEnabled(True)


    def clear_form(self):

        self.selected_id = None
        self.name.clear()
        self.address.clear()
        self.list.clearSelection()

        self.save_button.setText("Save Property")
        self.delete_button.setEnabled(False)


    def save_property(self):

        name = self.name.text().strip()

        if not name:
            QMessageBox.warning(
                self,
                "Missing Name",
                "Property name is required."
            )
            return

        address = self.address.text().strip()

        try:
            if self.selected_id is None:
                repository.add_property(name, address)
            else:
                repository.update_property(self.selected_id, name, address)
        except Exception as error:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not save property:\n{error}"
            )
            return

        self.clear_form()
        self.load_properties()


    def delete_property(self):

        if self.selected_id is None:
            return

        confirm = QMessageBox.question(
            self,
            "Delete Property",
            "Delete this property?"
        )

        if confirm != QMessageBox.Yes:
            return

        try:
            repository.delete_property(self.selected_id)
        except Exception as error:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not delete property:\n{error}"
            )
            return

        self.clear_form()
        self.load_properties()