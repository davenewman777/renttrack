from PySide6.QtWidgets import (
    QMainWindow,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget
)
from ui.tenants import TenantWindow
from ui.properties import PropertyWindow
from ui.units import UnitWindow
from ui.leases import LeaseWindow
from ui.payments import PaymentWindow

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

        properties = QPushButton(
            "Manage Properties"
        )

        properties.clicked.connect(
            self.open_properties
        )

        leases = QPushButton(
            "Manage Leases"
        )

        leases.clicked.connect(
        self.open_leases
        )

        units = QPushButton(
            "Manage Units"
        )

        units.clicked.connect(
            self.open_units
        )

        tenants.clicked.connect(
            self.open_tenants
        )

        payments = QPushButton(
            "Payments"
        )

        payments.clicked.connect(
            self.open_payments
        )

        layout.addWidget(
            payments
        )

        reports = QPushButton(
            "Reports"
        )

        layout.addWidget(title)
        layout.addWidget(new_payment)
        layout.addWidget(tenants)
        layout.addWidget(properties)
        layout.addWidget(units)
        layout.addWidget(leases)
        layout.addWidget(reports)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def open_tenants(self):

        self.tenant_window = TenantWindow()
        self.tenant_window.show()

    def open_properties(self):

        self.property_window = PropertyWindow()
        self.property_window.show()

    def open_units(self):

        self.unit_window = UnitWindow()
        self.unit_window.show()

    def open_leases(self):

        self.lease_window = LeaseWindow()
        self.lease_window.show()

    def open_payments(self):

        self.payment_window = PaymentWindow()
        self.payment_window.show()