import pytest

from wishhelper.i18n import (
    STRINGS_DA,
    STRINGS_EN,
    available_languages,
    get_language,
    language_name,
    set_language,
    t,
    translate,
)


@pytest.fixture(autouse=True)
def _restore_language():
    """Keep the module-level active language from leaking between tests."""
    original = get_language()
    yield
    set_language(original)


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


def test_language_tables_have_identical_keys():
    # A missing key in one table would KeyError at runtime in that language.
    assert set(STRINGS_DA) == set(STRINGS_EN)


def test_translate_is_pure_and_language_specific():
    assert translate("en", "app_title") == "Wish Helper"
    assert translate("da", "app_title") == "Ønske hjælper"
    assert translate("en", "doc_heading", event="Christmas") == "Wishlist for Christmas"


def test_set_language_switches_active_table():
    set_language("en")
    assert get_language() == "en"
    assert t("action_add") == "Add"
    set_language("da")
    assert t("action_add") == "Tilføj"


def test_unknown_language_falls_back_to_default():
    set_language("xx")
    assert get_language() == "da"
    assert t("app_title") == "Ønske hjælper"


def test_available_languages_and_names():
    assert available_languages() == ("da", "en")
    assert language_name("da") == "Dansk"
    assert language_name("en") == "English"
