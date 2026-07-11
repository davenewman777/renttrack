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
    QComboBox,
    QMessageBox
)

from database import repository

import sqlite3


class UnitWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Unit Management")
        self.resize(500, 600)

        self.selected_id = None

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
        # Action Buttons
        #
        self.save_button = QPushButton(
            "Save Unit"
        )

        self.save_button.clicked.connect(
            self.save_unit
        )

        new_button = QPushButton("New")
        new_button.clicked.connect(self.clear_form)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_unit)
        self.delete_button.setEnabled(False)

        buttons = QHBoxLayout()
        buttons.addWidget(self.save_button)
        buttons.addWidget(new_button)
        buttons.addWidget(self.delete_button)

        layout.addLayout(buttons)


        #
        # Existing Units
        #
        layout.addWidget(
            QLabel("Existing Units (click to edit)")
        )

        self.unit_list = QListWidget()
        self.unit_list.itemClicked.connect(self.select_unit)

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

        for prop in repository.list_properties():

            self.property_combo.addItem(
                prop[1],
                prop[0]
            )



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


        name = self.name.text().strip()

        if not name:

            QMessageBox.warning(
                self,
                "Missing Name",
                "Unit name is required."
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


        try:
            if self.selected_id is None:
                repository.add_unit(
                    property_id,
                    name,
                    self.description.text(),
                    monthly_rent,
                )
            else:
                repository.update_unit(
                    self.selected_id,
                    property_id,
                    name,
                    self.description.text(),
                    monthly_rent,
                )
        except sqlite3.Error as error:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not save unit:\n{error}"
            )
            return


        self.clear_form()
        self.load_units()



    #
    # Load One Unit Into The Form
    #
    def select_unit(self, item):

        unit_id = item.data(Qt.UserRole)
        record = repository.get_unit(unit_id)

        if record is None:
            return

        # record = (id, property_id, name, description, monthly_rent)
        self.selected_id = record[0]

        index = self.property_combo.findData(record[1])
        if index >= 0:
            self.property_combo.setCurrentIndex(index)

        self.name.setText(record[2] or "")
        self.description.setText(record[3] or "")
        self.rent.setText(str(record[4]) if record[4] is not None else "")

        self.save_button.setText("Update Unit")
        self.delete_button.setEnabled(True)



    #
    # Reset The Form For A New Unit
    #
    def clear_form(self):

        self.selected_id = None
        self.name.clear()
        self.description.clear()
        self.rent.clear()
        self.unit_list.clearSelection()

        self.save_button.setText("Save Unit")
        self.delete_button.setEnabled(False)



    #
    # Delete The Selected Unit
    #
    def delete_unit(self):

        if self.selected_id is None:
            return

        confirm = QMessageBox.question(
            self,
            "Delete Unit",
            "Delete this unit?"
        )

        if confirm != QMessageBox.Yes:
            return

        try:
            repository.delete_unit(self.selected_id)
        except sqlite3.Error as error:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not delete unit:\n{error}"
            )
            return

        self.clear_form()
        self.load_units()



    #
    # Display Existing Units
    #
    def load_units(self):

        self.unit_list.clear()

        # row = (id, property_id, property_name, name, description, monthly_rent)
        for row in repository.list_units():

            item = QListWidgetItem(

                f"{row[2]} | "
                f"{row[3]} | "
                f"{row[4]} | "
                f"${row[5]}"

            )
            item.setData(Qt.UserRole, row[0])
            self.unit_list.addItem(item)