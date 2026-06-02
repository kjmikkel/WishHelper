"""Plain-text exporter for a WishList. Qt-free."""

from __future__ import annotations

from wishhelper.formatting import format_price, heading, promise_marker
from wishhelper.i18n import t
from wishhelper.models import WishList


def export_text(wishlist: WishList) -> str:
    """Render the wishlist as a plain-text document."""
    lines = [heading(wishlist), "", t("intro_line"), ""]
    for index, wish in enumerate(wishlist.wishes, start=1):
        marker = promise_marker(wish)
        lines.append(
            f"{index}. {wish.title} — {wish.type} — "
            f"{format_price(wish.price, wishlist.currency)}{marker}"
        )
        if wish.note:
            lines.append(f"\t{wish.note}")
    return "\n".join(lines)
