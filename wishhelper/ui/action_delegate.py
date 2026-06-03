"""Delegate that renders per-row 'Rediger' / 'Slet' text links in the action column.

Lives in the view layer so WishTableModel can stay data-only (QtCore only). The
delegate paints the links and translates clicks into row-scoped signals that the
main window connects to its edit/delete slots.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QEvent, QRect, QSize, Qt, Signal
from PySide6.QtWidgets import QStyle, QStyledItemDelegate

from wishhelper.i18n import t

_PAD = 8   # left/right padding inside the cell
_GAP = 14  # space between the two links


class ActionColumnDelegate(QStyledItemDelegate):
    edit_requested = Signal(int)
    delete_requested = Signal(int)

    def __init__(self, is_add_row: Callable[[int], bool], parent=None):
        super().__init__(parent)
        self._is_add_row = is_add_row  # skip the phantom "add wish" row

    # --- geometry shared by painting and hit-testing -----------------------
    def _hit_rects(self, option) -> tuple[QRect, QRect]:
        fm = option.fontMetrics
        edit_w = fm.horizontalAdvance(t("action_edit"))
        delete_w = fm.horizontalAdvance(t("action_delete"))
        r = option.rect
        edit_rect = QRect(r.left() + _PAD, r.top(), edit_w, r.height())
        delete_rect = QRect(
            r.left() + _PAD + edit_w + _GAP, r.top(), delete_w, r.height())
        return edit_rect, delete_rect

    # --- Qt delegate interface ---------------------------------------------
    def paint(self, painter, option, index):
        if self._is_add_row(index.row()):
            return  # the phantom row shows no edit/delete controls
        painter.save()
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
            painter.setPen(option.palette.highlightedText().color())
        else:
            painter.setPen(option.palette.link().color())
        edit_rect, delete_rect = self._hit_rects(option)
        align = Qt.AlignLeft | Qt.AlignVCenter
        painter.drawText(edit_rect, align, t("action_edit"))
        painter.drawText(delete_rect, align, t("action_delete"))
        painter.restore()

    def sizeHint(self, option, index):
        fm = option.fontMetrics
        width = (_PAD + fm.horizontalAdvance(t("action_edit"))
                 + _GAP + fm.horizontalAdvance(t("action_delete")) + _PAD)
        height = max(fm.height() + 6, super().sizeHint(option, index).height())
        return QSize(width, height)

    def editorEvent(self, event, model, option, index):
        if self._is_add_row(index.row()):
            return False
        if event.type() == QEvent.MouseButtonRelease:
            pos = event.position().toPoint()
            edit_rect, delete_rect = self._hit_rects(option)
            # Hit area is the link text itself; a click in the gap is ignored.
            if edit_rect.contains(pos):
                self.edit_requested.emit(index.row())
                return True
            if delete_rect.contains(pos):
                self.delete_requested.emit(index.row())
                return True
        return False
