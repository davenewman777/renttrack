from PySide6.QtWidgets import (
    QMainWindow,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget
)
from ui.tenants import TenantWindow

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("RentTrack")
        self.resize(900, 600)

        layout = QVBoxLayout()

        title = QLabel(
            "RentTrack\nRental Management System"
        )

        title.setStyleSheet(
            "font-size: 24px;"
        )

        new_payment = QPushButton(
            "New Payment"
        )

        tenants = QPushButton(
        "Manage Tenants"
        )

        tenants.clicked.connect(
            self.open_tenants
        )

        reports = QPushButton(
            "Reports"
        )

        layout.addWidget(title)
        layout.addWidget(new_payment)
        layout.addWidget(tenants)
        layout.addWidget(reports)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def open_tenants(self):

        self.tenant_window = TenantWindow()

        self.tenant_window.show()