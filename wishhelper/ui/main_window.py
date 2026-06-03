"""Main application window. The only place that wires UI to the core."""

from __future__ import annotations

import datetime
import os

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView as AIV,
    QApplication,
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from wishhelper import storage
from wishhelper.errors import WishHelperError
from wishhelper.exporters.pdf import export_pdf
from wishhelper.exporters.text import export_text
from wishhelper.i18n import t
from wishhelper.models import WishList
from wishhelper.settings import Settings, save_settings
from wishhelper.ui.resources import APP_ICON
from wishhelper.ui.settings_dialog import SettingsDialog
from wishhelper.ui.theme import apply_theme, install_color_scheme_follower
from wishhelper.ui.action_delegate import ActionColumnDelegate
from wishhelper.ui.wish_editor import WishEditor
from wishhelper.ui.wish_table_model import COL_ACTIONS, WishTableModel


class MainWindow(QMainWindow):
    def __init__(self, settings: Settings, settings_path: str, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._settings_path = settings_path
        self.setWindowTitle(t("app_title"))
        self.setWindowIcon(QIcon(APP_ICON))
        self._model = WishTableModel(self._new_wishlist())
        self._build_ui()
        # Follow the OS colour scheme live while the theme is "system". The
        # lambda reads the live setting, which _open_settings may replace.
        self._theme_follower = install_color_scheme_follower(
            QApplication.instance(), lambda: self._settings.theme)

    def _new_wishlist(self) -> WishList:
        return WishList(
            year=datetime.datetime.now().year,
            author=self._settings.author,
            currency=self._settings.currency,
        )

    def _build_ui(self) -> None:
        central = QWidget()
        outer = QVBoxLayout(central)

        # Document fields
        doc_row = QHBoxLayout()
        self.event_edit = QLineEdit(self._model.wishlist().event)
        self.year_spin = QSpinBox()
        self.year_spin.setRange(1900, 9999)
        self.year_spin.setValue(self._model.wishlist().year)
        self.include_year_check = QCheckBox(t("label_include_year"))
        self.include_year_check.setChecked(self._model.wishlist().include_year)
        doc_row.addWidget(QLabel(t("label_event")))
        doc_row.addWidget(self.event_edit)
        doc_row.addWidget(QLabel(t("label_year")))
        doc_row.addWidget(self.year_spin)
        doc_row.addWidget(self.include_year_check)
        outer.addLayout(doc_row)

        # Table
        self.table = QTableView()
        self.table.setModel(self._model)
        self.table.setSelectionBehavior(AIV.SelectRows)
        self.table.setSelectionMode(AIV.SingleSelection)
        self.table.setSortingEnabled(False)  # order == priority
        self.table.setDragDropMode(AIV.InternalMove)
        self.table.setDragDropOverwriteMode(False)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(lambda *_: self._edit_selected())
        self.table.clicked.connect(self._on_cell_clicked)

        # Per-row "Rediger" / "Slet" links live in the action column.
        self._action_delegate = ActionColumnDelegate(
            self._model.is_add_row, self.table)
        self._action_delegate.edit_requested.connect(self._edit_row)
        self._action_delegate.delete_requested.connect(self._delete_row)
        self.table.setItemDelegateForColumn(COL_ACTIONS, self._action_delegate)
        self.table.horizontalHeader().setSectionResizeMode(
            COL_ACTIONS, QHeaderView.ResizeToContents)
        outer.addWidget(self.table)

        # Action bar
        # Bottom bar holds document-level actions only; row actions (add/edit/
        # delete) live in the table itself (phantom add row + action column).
        bar = QHBoxLayout()
        for label, slot in [
            (t("action_load"), self._load),
            (t("action_save"), self._save),
            (t("action_export_pdf"), self._export_pdf),
            (t("action_export_text"), self._export_text),
            (t("action_settings"), self._open_settings),
        ]:
            button = QPushButton(label)
            button.clicked.connect(slot)
            bar.addWidget(button)
        outer.addLayout(bar)

        self.setCentralWidget(central)

    # --- document sync ------------------------------------------------------
    def _sync_document_fields(self) -> None:
        wl = self._model.wishlist()
        wl.event = self.event_edit.text().strip()
        wl.year = self.year_spin.value()
        wl.include_year = self.include_year_check.isChecked()

    def _selected_row(self) -> int:
        rows = self.table.selectionModel().selectedRows()
        return rows[0].row() if rows else -1

    # --- actions ------------------------------------------------------------
    def _add(self) -> None:
        editor = WishEditor(parent=self)
        if editor.exec():
            self._model.add_wish(editor.wish())

    def _on_cell_clicked(self, index) -> None:
        # A single click on the trailing phantom row starts a new wish.
        if self._model.is_add_row(index.row()):
            self._add()

    def _edit_selected(self) -> None:
        self._edit_row(self._selected_row())

    def _edit_row(self, row: int) -> None:
        if row < 0 or self._model.is_add_row(row):
            return
        editor = WishEditor(self._model.wish_at(row), parent=self)
        if editor.exec():
            self._model.replace_wish(row, editor.wish())

    def _delete_row(self, row: int) -> None:
        if 0 <= row and not self._model.is_add_row(row):
            self._model.remove_wish(row)

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self._settings, parent=self)
        if not dialog.exec():
            return
        self._settings = dialog.result_settings()
        apply_theme(QApplication.instance(), self._settings.theme)
        # Reflect the new author/currency defaults in the open document so the
        # price column and exports use them immediately.
        wishlist = self._model.wishlist()
        wishlist.author = self._settings.author
        wishlist.currency = self._settings.currency
        self._model.set_wishlist(wishlist)
        self._persist_settings()

    def _load(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, t("action_load"), self._settings.last_load_dir,
            "WishHelper (*.json)")
        if not path:
            return
        try:
            wishlist = storage.load(path)
        except WishHelperError as exc:
            QMessageBox.critical(self, t("error_load_title"), str(exc))
            return
        self._model.set_wishlist(wishlist)
        self.event_edit.setText(wishlist.event)
        self.year_spin.setValue(wishlist.year or self.year_spin.value())
        self.include_year_check.setChecked(wishlist.include_year)
        self._settings.last_load_dir = os.path.dirname(path)
        self._persist_settings()

    def _save(self) -> None:
        self._sync_document_fields()
        path, _ = QFileDialog.getSaveFileName(
            self, t("action_save"), self._settings.last_save_dir,
            "WishHelper (*.json)")
        if not path:
            return
        if not path.lower().endswith(".json"):
            path += ".json"
        try:
            storage.save(self._model.wishlist(), path)
        except WishHelperError as exc:
            QMessageBox.critical(self, t("error_save_title"), str(exc))
            return
        self._settings.last_save_dir = os.path.dirname(path)
        self._persist_settings()

    def _export_pdf(self) -> None:
        self._export("pdf", "PDF (*.pdf)", export_pdf)

    def _export_text(self) -> None:
        def write_text(wishlist, path):
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(export_text(wishlist))

        self._export("txt", "Text (*.txt)", write_text)

    def _export(self, extension: str, file_filter: str, write_fn) -> None:
        self._sync_document_fields()
        path, _ = QFileDialog.getSaveFileName(
            self, t("action_export"), self._settings.last_export_dir, file_filter)
        if not path:
            return
        if not path.lower().endswith("." + extension):
            path += "." + extension
        try:
            write_fn(self._model.wishlist(), path)
        except (OSError, WishHelperError) as exc:
            QMessageBox.critical(self, t("error_save_title"), str(exc))
            return
        self._settings.last_export_dir = os.path.dirname(path)
        self._persist_settings()

    def _persist_settings(self) -> None:
        try:
            save_settings(self._settings, self._settings_path)
        except WishHelperError:
            pass  # non-fatal: a failed settings write must not block the user
