from wishhelper.formatting import format_price, heading, promise_marker
from wishhelper.models import Wish, WishList


def test_heading_with_year():
    wl = WishList(event="jul", year=2026, include_year=True)
    assert heading(wl) == "Ønskeseddel til jul for 2026"


def test_heading_without_year():
    wl = WishList(event="jul", year=2026, include_year=False)
    assert heading(wl) == "Ønskeseddel til jul"


def test_format_price_known():
    assert format_price(899, "kr.") == "899 kr."


def test_format_price_zero_is_question_mark():
    assert format_price(0, "kr.") == "?"


def test_promise_marker_none_when_not_set():
    assert promise_marker(Wish(title="X")) == ""


def test_promise_marker_with_reason_has_leading_space():
    w = Wish(title="X", promise_ok=True, promise_reason="udkommer i marts 2027")
    assert promise_marker(w) == " (løfte er fint — udkommer i marts 2027)"


def test_promise_marker_without_reason():
    w = Wish(title="X", promise_ok=True)
    assert promise_marker(w) == " (løfte er fint)"
