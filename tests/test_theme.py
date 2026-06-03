import pytest
from PySide6.QtCore import Qt

from wishhelper.ui.theme import _effective_theme, install_color_scheme_follower


@pytest.mark.parametrize(
    "theme, os_is_dark, expected",
    [
        ("dark", False, "dark"),
        ("dark", True, "dark"),
        ("light", False, "light"),
        ("light", True, "light"),
        ("system", True, "dark"),   # the bug: system must follow the OS
        ("system", False, "light"),
    ],
)
def test_effective_theme(theme, os_is_dark, expected):
    assert _effective_theme(theme, os_is_dark) == expected


class _FakeSignal:
    def __init__(self):
        self._slot = None

    def connect(self, slot):
        self._slot = slot

    def emit(self):
        if self._slot is not None:
            self._slot()


class _FakeHints:
    def __init__(self):
        self.colorSchemeChanged = _FakeSignal()

    def colorScheme(self):
        return Qt.ColorScheme.Dark


class _FakeApp:
    """Minimal QApplication stand-in: records palette re-applications."""

    def __init__(self):
        self._hints = _FakeHints()
        self.palette_applications = 0

    def styleHints(self):
        return self._hints

    def setStyle(self, _name):
        pass

    def setPalette(self, _palette):
        self.palette_applications += 1


def test_color_scheme_follower_reapplies_only_for_system():
    app = _FakeApp()
    theme = {"value": "system"}
    install_color_scheme_follower(app, lambda: theme["value"])

    app.styleHints().colorSchemeChanged.emit()
    assert app.palette_applications == 1  # system follows the OS flip

    theme["value"] = "light"
    app.styleHints().colorSchemeChanged.emit()
    assert app.palette_applications == 1  # explicit theme ignores the OS flip
