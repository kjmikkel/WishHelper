"""Light/dark/system palette application for the Qt app.

Always uses the **Fusion** style. The native Windows 11 style only partially
honours a forced QPalette — it keeps drawing its own (dark-mode) button chrome
while using the palette's text colour, so forcing a light palette over it
produced unreadable button text. Fusion honours the palette fully and renders
consistently across platforms.

`"system"` follows the OS colour scheme via `QStyleHints.colorScheme()`.
"""

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
    p.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(120, 120, 120))
    p.setColor(QPalette.Disabled, QPalette.Text, QColor(120, 120, 120))
    return p


def _light_palette() -> QPalette:
    p = QPalette()
    text = QColor(20, 20, 20)
    p.setColor(QPalette.Window, QColor(240, 240, 240))
    p.setColor(QPalette.WindowText, text)
    p.setColor(QPalette.Base, QColor(255, 255, 255))
    p.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    p.setColor(QPalette.Text, text)
    p.setColor(QPalette.Button, QColor(235, 235, 235))
    p.setColor(QPalette.ButtonText, text)
    p.setColor(QPalette.Highlight, QColor(21, 88, 176))
    p.setColor(QPalette.HighlightedText, Qt.white)
    p.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(150, 150, 150))
    p.setColor(QPalette.Disabled, QPalette.Text, QColor(150, 150, 150))
    return p


def _effective_theme(theme: str, os_is_dark: bool) -> str:
    """Resolve a theme name to the concrete palette ('light' or 'dark').

    'system' follows the OS; explicit 'light'/'dark' win regardless of the OS.
    """
    if theme == "dark":
        return "dark"
    if theme == "light":
        return "light"
    return "dark" if os_is_dark else "light"


def apply_theme(app: QApplication, theme: str) -> None:
    """Apply 'light', 'dark', or 'system' theme to the application."""
    app.setStyle("Fusion")
    os_is_dark = app.styleHints().colorScheme() == Qt.ColorScheme.Dark
    if _effective_theme(theme, os_is_dark) == "dark":
        app.setPalette(_dark_palette())
    else:
        app.setPalette(_light_palette())
