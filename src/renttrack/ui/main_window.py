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
from ui.reports import ReportsWindow

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

        tenants = QPushButton(
            "Manage Tenants"
        )

        tenants.clicked.connect(
            self.open_tenants
        )

        properties = QPushButton(
            "Manage Properties"
        )

        properties.clicked.connect(
            self.open_properties
        )

        units = QPushButton(
            "Manage Units"
        )

        units.clicked.connect(
            self.open_units
        )

        leases = QPushButton(
            "Manage Leases"
        )

        leases.clicked.connect(
            self.open_leases
        )

        payments = QPushButton(
            "Payments"
        )

        payments.clicked.connect(
            self.open_payments
        )

        reports = QPushButton(
            "Reports"
        )

        reports.clicked.connect(
            self.open_reports
        )

        layout.addWidget(title)
        layout.addWidget(properties)
        layout.addWidget(units)
        layout.addWidget(tenants)
        layout.addWidget(leases)
        layout.addWidget(payments)
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

    def open_reports(self):

        self.reports_window = ReportsWindow()
        self.reports_window.show()