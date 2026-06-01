"""User-facing strings. Danish default; structured for future i18n. Qt-free.

All UI and export text comes through t(); no string literals live in logic.
"""

from __future__ import annotations

STRINGS_DA: dict[str, str] = {
    # Application / window
    "app_title": "Ønske hjælper",
    # Table columns
    "col_number": "#",
    "col_name": "Navn",
    "col_price": "Pris",
    "col_type": "Type",
    "col_note": "Note",
    # Document
    "doc_heading": "Ønskeseddel til {event}",
    "doc_heading_year": "Ønskeseddel til {event} for {year}",
    "intro_line": "Følgende ønsker er arrangeret fra mest ønskede til mindst.",
    "price_unknown": "?",
    "price_with_currency": "{price} {currency}",
    "promise_marker": "(løfte er fint — {reason})",
    "promise_marker_plain": "(løfte er fint)",
    # Actions / buttons
    "action_add": "Tilføj",
    "action_edit": "Rediger",
    "action_delete": "Slet",
    "action_save": "Gem",
    "action_load": "Hent",
    "action_export": "Eksportér",
    "action_settings": "Indstillinger",
    # Field labels
    "label_event": "Begivenhed",
    "label_year": "År",
    "label_include_year": "Vis år",
    "label_title": "Navn",
    "label_price": "Pris",
    "label_type": "Type",
    "label_note": "Note",
    "label_link": "Link",
    "label_promise_ok": "Et løfte er nok",
    "label_promise_reason": "Begrundelse",
    "label_author": "Forfatter",
    "label_currency": "Valuta",
    "label_language": "Sprog",
    "label_theme": "Tema",
    # Errors
    "error_load_title": "Kunne ikke hente filen",
    "error_save_title": "Kunne ikke gemme filen",
    "error_empty_title": "Navn må ikke være tomt.",
    "error_negative_price": "Pris må ikke være negativ.",
}

_TABLE = STRINGS_DA


def t(key: str, **kwargs) -> str:
    """Return the localized string for `key`, formatted with kwargs."""
    template = _TABLE[key]  # KeyError on unknown key, by design
    if kwargs:
        return template.format(**kwargs)
    return template
