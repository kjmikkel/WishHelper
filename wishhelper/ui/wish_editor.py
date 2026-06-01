"""Modal dialog to add or edit a single Wish."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QSpinBox,
)

from wishhelper.i18n import t
from wishhelper.models import Wish


class WishEditor(QDialog):
    def __init__(self, wish: Wish | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("label_title"))
        self._build_ui()
        if wish is not None:
            self._load(wish)

    def _build_ui(self) -> None:
        layout = QFormLayout(self)
        self.title_edit = QLineEdit()
        self.price_spin = QSpinBox()
        self.price_spin.setRange(0, 1_000_000)
        self.type_edit = QLineEdit()
        self.note_edit = QLineEdit()
        self.link_edit = QLineEdit()
        self.promise_check = QCheckBox(t("label_promise_ok"))
        self.promise_reason_edit = QLineEdit()
        self.promise_reason_edit.setEnabled(False)
        self.promise_check.toggled.connect(self.promise_reason_edit.setEnabled)

        layout.addRow(t("label_title"), self.title_edit)
        layout.addRow(t("label_price"), self.price_spin)
        layout.addRow(t("label_type"), self.type_edit)
        layout.addRow(t("label_note"), self.note_edit)
        layout.addRow(t("label_link"), self.link_edit)
        layout.addRow("", self.promise_check)
        layout.addRow(t("label_promise_reason"), self.promise_reason_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _load(self, wish: Wish) -> None:
        self.title_edit.setText(wish.title)
        self.price_spin.setValue(wish.price)
        self.type_edit.setText(wish.type)
        self.note_edit.setText(wish.note)
        self.link_edit.setText(wish.link)
        self.promise_check.setChecked(wish.promise_ok)
        self.promise_reason_edit.setText(wish.promise_reason)

    def _on_accept(self) -> None:
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, t("app_title"), t("error_empty_title"))
            return
        self.accept()

    def wish(self) -> Wish:
        """Return the Wish described by the current field values."""
        return Wish(
            title=self.title_edit.text().strip(),
            price=self.price_spin.value(),
            type=self.type_edit.text().strip(),
            note=self.note_edit.text().strip(),
            link=self.link_edit.text().strip(),
            promise_ok=self.promise_check.isChecked(),
            promise_reason=self.promise_reason_edit.text().strip(),
        )
