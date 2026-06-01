"""Conversion of legacy wishlist files to the current model. Qt-free.

Handles two historical shapes:
  * v1 positional (length 4): [wishes, title, year, year_check]
  * notes-dict (length 6):    [header, notes, wishes, text, year, check]
Each wish row is [number, title, price, type, note] or, in older files,
[title, price, type, note] (no leading number).
"""

from __future__ import annotations

from wishhelper.errors import LegacyFormatError
from wishhelper.models import Wish, WishList


def _wish_from_row(row, note_lookup: dict) -> Wish:
    """Build a Wish from a legacy row, resolving a note key if present."""
    if len(row) == 5:
        _number, title, price, type_, note = row
    elif len(row) == 4:
        title, price, type_, note = row
    else:
        raise LegacyFormatError(f"Unrecognized wish row: {row!r}")
    note_text = note_lookup.get(note, note) if note_lookup else note
    return Wish(
        title=str(title),
        price=int(price),
        type=str(type_),
        note=str(note_text),
    )


def convert(data) -> WishList:
    """Convert a parsed legacy JSON structure into a WishList."""
    if not isinstance(data, list):
        raise LegacyFormatError(f"Unrecognized legacy structure: {type(data).__name__}")

    if len(data) == 6:
        _header, notes, wishes, text, year, check = data
        try:
            note_lookup = {key: value for key, value in notes}
        except (TypeError, ValueError) as exc:
            raise LegacyFormatError(f"Malformed notes table: {exc}") from exc
    elif len(data) == 4:
        wishes, text, year, check = data
        note_lookup = {}
    else:
        raise LegacyFormatError(f"Unrecognized legacy length: {len(data)}")

    if not isinstance(wishes, list):
        raise LegacyFormatError(
            f"Expected a list of wishes, got {type(wishes).__name__}"
        )

    return WishList(
        event=str(text),
        year=int(year),
        include_year=bool(check),
        wishes=[_wish_from_row(row, note_lookup) for row in wishes],
    )
