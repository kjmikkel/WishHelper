import pytest

from wishhelper.i18n import t


def test_simple_string():
    assert t("price_unknown") == "?"


def test_app_title_is_danish():
    assert t("app_title") == "Ønske hjælper"


def test_heading_without_year():
    assert t("doc_heading", event="jul") == "Ønskeseddel til jul"


def test_heading_with_year():
    assert t("doc_heading_year", event="jul", year=2026) == "Ønskeseddel til jul for 2026"


def test_promise_marker_with_reason():
    assert t("promise_marker", reason="udkommer i marts 2027") == \
        "(løfte er fint — udkommer i marts 2027)"


def test_promise_marker_without_reason():
    assert t("promise_marker_plain") == "(løfte er fint)"


def test_unknown_key_raises():
    with pytest.raises(KeyError):
        t("no_such_key")
