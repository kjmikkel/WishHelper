"""Application entry point: python -m wishhelper."""

from __future__ import annotations

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from wishhelper.i18n import set_language
from wishhelper.settings import default_settings_path, load_settings
from wishhelper.ui.main_window import MainWindow
from wishhelper.ui.resources import APP_ICON
from wishhelper.ui.theme import apply_theme

# Stable per-app identity for the Windows shell (taskbar grouping/pinning).
_APP_USER_MODEL_ID = "MikkelKjaerJensen.WishHelper"


def _set_windows_app_id() -> None:
    """Give the process its own Windows shell identity so the taskbar shows the
    WishHelper icon instead of the generic python.exe icon. No-op off Windows;
    failures are swallowed since the taskbar icon is cosmetic.
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            _APP_USER_MODEL_ID)
    except (AttributeError, OSError):
        pass


def main() -> int:
    _set_windows_app_id()  # before any window is created
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(APP_ICON))
    settings_path = default_settings_path()
    settings = load_settings(settings_path)
    set_language(settings.language)
    apply_theme(app, settings.theme)
    window = MainWindow(settings, settings_path)
    window.resize(820, 520)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
