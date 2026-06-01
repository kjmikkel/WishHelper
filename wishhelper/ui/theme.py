"""Light/dark/system palette application for the Qt app."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


def _dark_palette() -> QPalette:
    p = QPalette()
    bg = QColor(45, 45, 48)
    text = QColor(220, 220, 220)
    base = QColor(30, 30, 32)
    p.setColor(QPalette.Window, bg)
    p.setColor(QPalette.WindowText, text)
    p.setColor(QPalette.Base, base)
    p.setColor(QPalette.AlternateBase, bg)
    p.setColor(QPalette.Text, text)
    p.setColor(QPalette.Button, bg)
    p.setColor(QPalette.ButtonText, text)
    p.setColor(QPalette.Highlight, QColor(21, 88, 176))
    p.setColor(QPalette.HighlightedText, Qt.white)
    return p


def apply_theme(app: QApplication, theme: str) -> None:
    """Apply 'light', 'dark', or 'system' theme to the application."""
    if theme == "dark":
        app.setStyle("Fusion")
        app.setPalette(_dark_palette())
    elif theme == "light":
        app.setStyle("Fusion")
        app.setPalette(QPalette())
    else:  # "system": leave the platform default untouched
        app.setPalette(app.style().standardPalette())
