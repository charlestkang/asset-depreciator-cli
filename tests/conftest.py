"""Pytest configuration for import path setup."""

from pathlib import Path
import sys

# Ensure src/ is importable when tests are run from tests/.
SRC = Path(__file__).resolve().parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
