"""Shared, Qt-free formatting helpers for rendering a wishlist.

Centralizes the price / promise-marker / heading formatting that the text and
PDF exporters and the Qt table model all need, so the rules live in one place.
"""

from __future__ import annotations

from wishhelper.i18n import t
from wishhelper.models import Wish, WishList


def heading(wishlist: WishList) -> str:
    """The document heading, with or without the year."""
    if wishlist.include_year:
        return t("doc_heading_year", event=wishlist.event, year=wishlist.year)
    return t("doc_heading", event=wishlist.event)


def format_price(price: int, currency: str) -> str:
    """Price text: '?' when unknown (0), otherwise '<price> <currency>'."""
    if price == 0:
        return t("price_unknown")
    return t("price_with_currency", price=price, currency=currency)


def promise_marker(wish: Wish) -> str:
    """Inline promise marker WITH a leading space, or '' when not applicable."""
    if not wish.promise_ok:
        return ""
    if wish.promise_reason:
        return " " + t("promise_marker", reason=wish.promise_reason)
    return " " + t("promise_marker_plain")
