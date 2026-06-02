"""Application entry point: python -m wishhelper."""

from __future__ import annotations

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from wishhelper.settings import default_settings_path, load_settings
from wishhelper.ui.main_window import MainWindow
from wishhelper.ui.resources import APP_ICON
from wishhelper.ui.theme import apply_theme


def main() -> int:
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(APP_ICON))
    settings_path = default_settings_path()
    settings = load_settings(settings_path)
    apply_theme(app, settings.theme)
    window = MainWindow(settings, settings_path)
    window.resize(820, 520)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
