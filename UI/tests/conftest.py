"""Shared test configuration for importing application modules."""

import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ui_directory = str(Path(__file__).resolve().parents[1])
if ui_directory not in sys.path:
    sys.path.insert(0, ui_directory)


@pytest.fixture(scope="session", autouse=True)
def _qapp():
    from PyQt6.QtWidgets import QApplication

    application = QApplication.instance() or QApplication([])
    yield application
