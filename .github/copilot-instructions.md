# RentTrack — Copilot Project Instructions

RentTrack is a PySide6 (Qt) desktop app for rental property management, backed by SQLite.

## Project layout
- Repository root: `renttrack/` (this folder). `requirements.txt` and `.github/` live here.
- Source root: `src/renttrack/`. The app is run from there, so **that folder is the import root**.
- Structure:
  - `src/renttrack/main.py` — entry point (initializes DB, launches `MainWindow`).
  - `src/renttrack/database/db.py` — `get_connection()`, `initialize_database()`.
  - `src/renttrack/ui/*.py` — one window class per module (`main_window.py`, `tenants.py`, `properties.py`, `units.py`, `leases.py`, `payments.py`).
  - `data/` — SQLite database file (`data/renttrack.db`).

## How to run
Run from the source root using the project venv:
```powershell
python src\renttrack\main.py
```

## Imports — IMPORTANT
Because the app runs from `src/renttrack`, always use short, top-level imports:
- Correct: `from ui.leases import LeaseWindow`, `from database.db import get_connection`
- WRONG (never use): `from renttrack.src.renttrack.ui import leases`

Reject any auto-import suggestion of the form `from renttrack.src.renttrack...`.

## Adding a new UI window/button
When adding a feature button to `MainWindow`:
1. Create the `QPushButton`.
2. Connect it: `button.clicked.connect(self.open_x)`.
3. **Add it to the layout**: `layout.addWidget(button)` — omitting this makes the button invisible.
4. Define the handler as a method on the class (not nested inside `__init__`).

## Environment
- Python venv: `.venv` (has PySide6 installed). Activate it before running.
- `requirements.txt` pins `PySide6>=6.10.3` (6.9.1 was yanked from PyPI).

## Conventions
- Package init files must be named `__init__.py` (double underscores).
- Always save files (Ctrl+S / enable Auto Save) so disk matches the editor before running.
- Prefer editing files directly over pasting snippets from external tools.
