"""Main application window. The only place that wires UI to the core."""

from __future__ import annotations

import datetime
import os

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView as AIV,
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
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
from wishhelper.ui.wish_editor import WishEditor
from wishhelper.ui.wish_table_model import WishTableModel


class MainWindow(QMainWindow):
    def __init__(self, settings: Settings, settings_path: str, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._settings_path = settings_path
        self.setWindowTitle(t("app_title"))
        self.setWindowIcon(QIcon(APP_ICON))
        self._model = WishTableModel(self._new_wishlist())
        self._build_ui()

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
        outer.addWidget(self.table)

        # Action bar
        bar = QHBoxLayout()
        for label, slot in [
            (t("action_add"), self._add),
            (t("action_edit"), self._edit_selected),
            (t("action_delete"), self._delete_selected),
            (t("action_load"), self._load),
            (t("action_save"), self._save),
            (t("action_export"), self._export),
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

    def _edit_selected(self) -> None:
        row = self._selected_row()
        if row < 0:
            return
        editor = WishEditor(self._model.wish_at(row), parent=self)
        if editor.exec():
            self._model.replace_wish(row, editor.wish())

    def _delete_selected(self) -> None:
        row = self._selected_row()
        if row >= 0:
            self._model.remove_wish(row)

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

    def _export(self) -> None:
        self._sync_document_fields()
        path, selected = QFileDialog.getSaveFileName(
            self, t("action_export"), self._settings.last_export_dir,
            "PDF (*.pdf);;Text (*.txt)")
        if not path:
            return
        try:
            if selected.startswith("Text") or path.lower().endswith(".txt"):
                if not path.lower().endswith(".txt"):
                    path += ".txt"
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(export_text(self._model.wishlist()))
            else:
                if not path.lower().endswith(".pdf"):
                    path += ".pdf"
                export_pdf(self._model.wishlist(), path)
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
