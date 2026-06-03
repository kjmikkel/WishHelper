"""Shared test configuration.

Force Qt's offscreen platform before any QApplication is created so the GUI
tests run headless (no real window, works in CI).
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
