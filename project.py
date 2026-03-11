"""Compatibility entry point for running the CLI from repository root."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from asset_depreciator.project import main


if __name__ == "__main__":
    main()
