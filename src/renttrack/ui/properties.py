from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QListWidget
)

from database import repository


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

        repository.add_property(
            self.name.text(),
            self.address.text(),
        )

        self.load_properties()


    def load_properties(self):

        self.list.clear()

        for row in repository.list_properties():

            self.list.addItem(
                f"{row[1]} - {row[2]}"
            )