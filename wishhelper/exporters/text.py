"""Plain-text exporter for a WishList. Qt-free."""

from __future__ import annotations

from wishhelper.i18n import t
from wishhelper.models import Wish, WishList


def _heading(wishlist: WishList) -> str:
    if wishlist.include_year:
        return t("doc_heading_year", event=wishlist.event, year=wishlist.year)
    return t("doc_heading", event=wishlist.event)


def _price(wish: Wish, currency: str) -> str:
    if wish.price == 0:
        return t("price_unknown")
    return t("price_with_currency", price=wish.price, currency=currency)


def _promise_marker(wish: Wish) -> str:
    if not wish.promise_ok:
        return ""
    if wish.promise_reason:
        return " " + t("promise_marker", reason=wish.promise_reason)
    return " " + t("promise_marker_plain")


def export_text(wishlist: WishList) -> str:
    """Render the wishlist as a plain-text document."""
    lines = [_heading(wishlist), "", t("intro_line"), ""]
    for index, wish in enumerate(wishlist.wishes, start=1):
        marker = _promise_marker(wish)
        lines.append(
            f"{index}. {wish.title} — {wish.type} — "
            f"{_price(wish, wishlist.currency)}{marker}"
        )
        if wish.note:
            lines.append(f"\t{wish.note}")
    return "\n".join(lines)
