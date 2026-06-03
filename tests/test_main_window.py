"""Headless (offscreen) tests for MainWindow wiring: the read-only document
info line and live language retranslation."""

import pytest
from PySide6.QtWidgets import QApplication

from wishhelper.i18n import set_language
from wishhelper.models import Wish, WishList
from wishhelper.settings import Settings
from wishhelper.ui.main_window import MainWindow


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture(autouse=True)
def _restore_language():
    yield
    set_language("da")


def test_doc_info_shows_currency_and_author(app):
    window = MainWindow(Settings(), "ignored.json")
    window._model.set_wishlist(
        WishList(currency="€", author="Anna", wishes=[Wish(title="Bog")]))
    window._update_doc_info()
    text = window._doc_info_label.text()
    assert "€" in text
    assert "Anna" in text


def test_doc_info_omits_author_when_blank(app):
    window = MainWindow(Settings(), "ignored.json")
    window._model.set_wishlist(WishList(currency="kr.", author="", wishes=[]))
    window._update_doc_info()
    text = window._doc_info_label.text()
    assert "kr." in text
    assert "Forfatter" not in text  # author label hidden when empty


def test_retranslation_switches_button_and_info_language(app):
    window = MainWindow(Settings(language="da"), "ignored.json")
    assert window._action_buttons[0][0].text() == "Hent"
    assert window._doc_info_label.text().startswith("Valuta")

    set_language("en")
    window._retranslate_ui()
    assert window._action_buttons[0][0].text() == "Load"
    assert window._doc_info_label.text().startswith("Currency")
