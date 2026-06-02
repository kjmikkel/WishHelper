"""QAbstractTableModel over a WishList. Headless-testable (QtCore only)."""

from __future__ import annotations

from PySide6.QtCore import (
    QAbstractTableModel,
    QByteArray,
    QMimeData,
    QModelIndex,
    Qt,
)

from wishhelper.formatting import format_price
from wishhelper.i18n import t
from wishhelper.models import WishList

COL_NUMBER, COL_NAME, COL_PRICE, COL_TYPE, COL_NOTE = range(5)
_HEADER_KEYS = ("col_number", "col_name", "col_price", "col_type", "col_note")
_MIME = "application/x-wishhelper-row"


class WishTableModel(QAbstractTableModel):
    def __init__(self, wishlist: WishList | None = None, parent=None):
        super().__init__(parent)
        self._wishlist = wishlist or WishList()

    # --- Qt model interface -------------------------------------------------
    def rowCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._wishlist.wishes)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(_HEADER_KEYS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return t(_HEADER_KEYS[section])
        return None

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        wish = self._wishlist.wishes[index.row()]
        column = index.column()
        if column == COL_NUMBER:
            return str(index.row() + 1)
        if column == COL_NAME:
            return wish.title
        if column == COL_PRICE:
            return format_price(wish.price, self._wishlist.currency)
        if column == COL_TYPE:
            return wish.type
        if column == COL_NOTE:
            return wish.note
        return None

    # --- Convenience mutators ----------------------------------------------
    def wishlist(self) -> WishList:
        return self._wishlist

    def set_wishlist(self, wishlist: WishList) -> None:
        self.beginResetModel()
        self._wishlist = wishlist
        self.endResetModel()

    def wish_at(self, row: int) -> Wish:
        return self._wishlist.wishes[row]

    def add_wish(self, wish: Wish) -> None:
        row = len(self._wishlist.wishes)
        self.beginInsertRows(QModelIndex(), row, row)
        self._wishlist.wishes.append(wish)
        self.endInsertRows()

    def remove_wish(self, row: int) -> None:
        self.beginRemoveRows(QModelIndex(), row, row)
        del self._wishlist.wishes[row]
        self.endRemoveRows()

    def replace_wish(self, row: int, wish: Wish) -> None:
        self._wishlist.wishes[row] = wish
        top = self.index(row, 0)
        bottom = self.index(row, self.columnCount() - 1)
        self.dataChanged.emit(top, bottom)

    def move_row(self, source: int, dest: int) -> None:
        self.beginResetModel()
        wish = self._wishlist.wishes.pop(source)
        self._wishlist.wishes.insert(dest, wish)
        self.endResetModel()

    # --- drag & drop reordering (internal move) -----------------------------
    def flags(self, index):
        base = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if index.isValid():
            return base | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        return base | Qt.ItemIsDropEnabled

    def supportedDropActions(self):
        return Qt.MoveAction

    def mimeTypes(self):
        return [_MIME]

    def mimeData(self, indexes):
        payload = QMimeData()
        rows = sorted({i.row() for i in indexes if i.isValid()})
        if not rows:
            return payload
        # Only the first row is moved; multi-row drag is not supported.
        payload.setData(_MIME, QByteArray(str(rows[0]).encode("ascii")))
        return payload

    def dropMimeData(self, data, action, row, column, parent):
        if action != Qt.MoveAction or not data.hasFormat(_MIME):
            return False
        source = int(bytes(data.data(_MIME).data()).decode("ascii"))
        if row != -1:
            dest = row
        elif parent.isValid():
            dest = parent.row()
        else:
            dest = len(self._wishlist.wishes)
        if dest > source:
            dest -= 1
        if dest != source:
            self.move_row(source, dest)
        # Return False so the view does not also remove the dragged source row
        # (we have already moved it in place).
        return False
