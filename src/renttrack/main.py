import sys

from PySide6.QtWidgets import QApplication

from database.db import initialize_database
from database.migrations import run_migrations
from ui.main_window import MainWindow


def main():

    initialize_database()
    run_migrations()

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()