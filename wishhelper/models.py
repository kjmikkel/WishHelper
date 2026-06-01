"""Core data model. Qt-free."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Wish:
    """A single wishlist item. Priority is its position in the WishList."""

    title: str
    price: int = 0  # 0 means "unknown", rendered as "?"
    type: str = ""
    note: str = ""
    link: str = ""  # optional single URL
    promise_ok: bool = False  # a promise/IOU is acceptable for this item
    promise_reason: str = ""


@dataclass
class WishList:
    """A wishlist document. wishes order == priority order (1-based)."""

    event: str = ""
    year: int = 0
    include_year: bool = True
    author: str = ""
    currency: str = "kr."
    wishes: list[Wish] = field(default_factory=list)
