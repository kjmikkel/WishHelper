"""Conversion of legacy wishlist files to the current model. Qt-free."""

from __future__ import annotations

from wishhelper.errors import LegacyFormatError
from wishhelper.models import WishList


def convert(data) -> WishList:  # pragma: no cover - replaced in Task 5
    raise LegacyFormatError("Legacy conversion not implemented yet")
