from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView
)

from database import repository


class ReportsWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Reports")
        self.resize(700, 500)

        layout = QVBoxLayout()

        layout.addWidget(
            QLabel("Reports")
        )

        #
        # Summary figures
        #
        self.summary = QLabel()
        layout.addWidget(self.summary)

        #
        # Per-lease payment breakdown
        #
        layout.addWidget(
            QLabel("Payments by Lease")
        )

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            [
                "Tenant",
                "Property",
                "Unit",
                "Payments",
                "Total Paid",
            ]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        layout.addWidget(self.table)

        #
        # Refresh
        #
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.load_report)
        layout.addWidget(refresh)

        self.setLayout(layout)

        self.load_report()


    def load_report(self):

        active = repository.active_lease_count()
        rent_roll = repository.monthly_rent_roll()
        collected = repository.total_collected()

        self.summary.setText(
            f"Active leases: {active}\n"
            f"Monthly rent roll: ${rent_roll:,.2f}\n"
            f"Total collected: ${collected:,.2f}"
        )

        rows = repository.payments_summary_by_lease()

        self.table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):

            first_name, last_name, property_name, unit_name, count, total = row

            values = [
                f"{first_name} {last_name}",
                property_name,
                unit_name,
                str(count),
                f"${total:,.2f}",
            ]

            for col_index, value in enumerate(values):

                self.table.setItem(
                    row_index,
                    col_index,
                    QTableWidgetItem(value),
                )
