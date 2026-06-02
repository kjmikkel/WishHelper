"""Modal dialog to edit application settings (author, currency, theme)."""

from __future__ import annotations

from dataclasses import replace

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
)

from wishhelper.i18n import t
from wishhelper.settings import Settings
from wishhelper.ui.resources import APP_ICON

_THEME_VALUES = ("system", "light", "dark")
_THEME_LABEL_KEYS = {
    "system": "theme_system",
    "light": "theme_light",
    "dark": "theme_dark",
}


class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self.setWindowTitle(t("action_settings"))
        self.setWindowIcon(QIcon(APP_ICON))
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QFormLayout(self)
        self.author_edit = QLineEdit(self._settings.author)
        self.currency_edit = QLineEdit(self._settings.currency)
        self.theme_combo = QComboBox()
        for value in _THEME_VALUES:
            self.theme_combo.addItem(t(_THEME_LABEL_KEYS[value]), value)
        index = self.theme_combo.findData(self._settings.theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

        layout.addRow(t("label_author"), self.author_edit)
        layout.addRow(t("label_currency"), self.currency_edit)
        layout.addRow(t("label_theme"), self.theme_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def result_settings(self) -> Settings:
        """Return a copy of the settings with the edited fields applied.

        Non-edited fields (last-used folders, language) are preserved. A blank
        currency falls back to the previous value so price rendering never
        loses its unit.
        """
        return replace(
            self._settings,
            author=self.author_edit.text().strip(),
            currency=self.currency_edit.text().strip() or self._settings.currency,
            theme=self.theme_combo.currentData(),
        )
