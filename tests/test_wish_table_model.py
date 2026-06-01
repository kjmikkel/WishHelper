from PySide6.QtCore import Qt

from wishhelper.models import Wish, WishList
from wishhelper.ui.wish_table_model import WishTableModel


def model_with_two():
    wl = WishList(currency="kr.", wishes=[
        Wish(title="Tastatur", price=899, type="Elektronik", note="Brune"),
        Wish(title="Sko", price=0, type="Tøj"),
    ])
    return WishTableModel(wl)


def test_row_and_column_counts():
    m = model_with_two()
    assert m.rowCount() == 2
    assert m.columnCount() == 5  # #, Navn, Pris, Type, Note


def test_priority_column_is_one_based_index():
    m = model_with_two()
    assert m.data(m.index(0, 0), Qt.DisplayRole) == "1"
    assert m.data(m.index(1, 0), Qt.DisplayRole) == "2"


def test_name_and_price_display():
    m = model_with_two()
    assert m.data(m.index(0, 1), Qt.DisplayRole) == "Tastatur"
    assert m.data(m.index(0, 2), Qt.DisplayRole) == "899 kr."
    assert m.data(m.index(1, 2), Qt.DisplayRole) == "?"


def test_header_labels_danish():
    m = model_with_two()
    assert m.headerData(1, Qt.Horizontal, Qt.DisplayRole) == "Navn"


def test_add_wish_appends_and_grows():
    m = model_with_two()
    m.add_wish(Wish(title="Bog", price=120, type="Bog"))
    assert m.rowCount() == 3
    assert m.data(m.index(2, 0), Qt.DisplayRole) == "3"


def test_remove_wish_renumbers():
    m = model_with_two()
    m.remove_wish(0)
    assert m.rowCount() == 1
    assert m.data(m.index(0, 0), Qt.DisplayRole) == "1"
    assert m.data(m.index(0, 1), Qt.DisplayRole) == "Sko"


def test_replace_wish_updates_row():
    m = model_with_two()
    m.replace_wish(0, Wish(title="Mus", price=250, type="Elektronik"))
    assert m.data(m.index(0, 1), Qt.DisplayRole) == "Mus"


def test_move_row_reorders_and_renumbers():
    m = model_with_two()
    m.move_row(1, 0)  # move "Sko" to the top
    assert m.data(m.index(0, 1), Qt.DisplayRole) == "Sko"
    assert m.data(m.index(0, 0), Qt.DisplayRole) == "1"
    assert m.data(m.index(1, 1), Qt.DisplayRole) == "Tastatur"


def test_drag_flags_enabled():
    m = model_with_two()
    flags = m.flags(m.index(0, 0))
    assert flags & Qt.ItemIsDragEnabled
    # Drops are accepted on the empty (invalid) parent for between-row drops
    assert m.flags(m.index(-1, -1)) & Qt.ItemIsDropEnabled


def test_drop_mime_reorders_to_top():
    from PySide6.QtCore import QModelIndex
    m = model_with_two()
    data = m.mimeData([m.index(1, 0)])  # drag "Sko"
    handled = m.dropMimeData(data, Qt.MoveAction, 0, 0, QModelIndex())
    # We perform the move ourselves and return False so the view does not
    # additionally remove the source row.
    assert handled is False
    assert m.data(m.index(0, 1), Qt.DisplayRole) == "Sko"
    assert m.data(m.index(1, 1), Qt.DisplayRole) == "Tastatur"
