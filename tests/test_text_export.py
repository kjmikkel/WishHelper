from wishhelper.exporters.text import export_text
from wishhelper.models import Wish, WishList


def test_heading_with_year():
    wl = WishList(event="jul", year=2026, include_year=True)
    text = export_text(wl)
    assert text.splitlines()[0] == "Ønskeseddel til jul for 2026"


def test_heading_without_year():
    wl = WishList(event="jul", year=2026, include_year=False)
    assert export_text(wl).splitlines()[0] == "Ønskeseddel til jul"


def test_numbered_rows_and_price():
    wl = WishList(currency="kr.", wishes=[
        Wish(title="Tastatur", price=899, type="Elektronik"),
        Wish(title="Sko", price=0, type="Tøj"),
    ])
    text = export_text(wl)
    assert "1. Tastatur — Elektronik — 899 kr." in text
    assert "2. Sko — Tøj — ?" in text


def test_note_on_indented_line():
    wl = WishList(wishes=[Wish(title="Tastatur", note="Brune switches")])
    lines = export_text(wl).splitlines()
    note_line = next(line for line in lines if "Brune switches" in line)
    assert note_line.startswith("\t")


def test_promise_marker_inline():
    wl = WishList(wishes=[
        Wish(title="Spil", promise_ok=True, promise_reason="udkommer i marts 2027"),
    ])
    text = export_text(wl)
    assert "(løfte er fint — udkommer i marts 2027)" in text
    assert "1. Spil" in text


def test_promise_marker_without_reason():
    wl = WishList(wishes=[Wish(title="Spil", promise_ok=True)])
    assert "(løfte er fint)" in export_text(wl)
