import sys
from pathlib import Path

# Make the application package importable the same way the app runs it
# (from src/renttrack, so `database` and `ui` are top-level packages).
SRC_ROOT = Path(__file__).resolve().parent / "src" / "renttrack"
sys.path.insert(0, str(SRC_ROOT))
