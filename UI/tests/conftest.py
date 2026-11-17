"""Shared test configuration for importing application modules."""

import sys
from pathlib import Path

ui_directory = str(Path(__file__).resolve().parents[1])
if ui_directory not in sys.path:
    sys.path.insert(0, ui_directory)
