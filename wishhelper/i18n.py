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
    "add_row_hint": "Tilføj ønske…",
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
    "action_export_pdf": "Eksportér som PDF",
    "action_export_text": "Eksportér som tekst",
    "action_settings": "Indstillinger",
    "action_quit": "Afslut",
    "tray_show": "Vis",
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
    "theme_system": "System",
    "theme_light": "Lyst",
    "theme_dark": "Mørkt",
    # Errors
    "error_load_title": "Kunne ikke hente filen",
    "error_save_title": "Kunne ikke gemme filen",
    "error_empty_title": "Navn må ikke være tomt.",
    "error_negative_price": "Pris må ikke være negativ.",
}

STRINGS_EN: dict[str, str] = {
    # Application / window
    "app_title": "Wish Helper",
    # Table columns
    "col_number": "#",
    "col_name": "Name",
    "col_price": "Price",
    "col_type": "Type",
    "col_note": "Note",
    "add_row_hint": "Add wish…",
    # Document
    "doc_heading": "Wishlist for {event}",
    "doc_heading_year": "Wishlist for {event} {year}",
    "intro_line": "The following wishes are ordered from most to least wanted.",
    "price_unknown": "?",
    "price_with_currency": "{price} {currency}",
    "promise_marker": "(a promise is fine — {reason})",
    "promise_marker_plain": "(a promise is fine)",
    # Actions / buttons
    "action_add": "Add",
    "action_edit": "Edit",
    "action_delete": "Delete",
    "action_save": "Save",
    "action_load": "Load",
    "action_export": "Export",
    "action_export_pdf": "Export as PDF",
    "action_export_text": "Export as text",
    "action_settings": "Settings",
    "action_quit": "Quit",
    "tray_show": "Show",
    # Field labels
    "label_event": "Event",
    "label_year": "Year",
    "label_include_year": "Show year",
    "label_title": "Name",
    "label_price": "Price",
    "label_type": "Type",
    "label_note": "Note",
    "label_link": "Link",
    "label_promise_ok": "A promise is enough",
    "label_promise_reason": "Reason",
    "label_author": "Author",
    "label_currency": "Currency",
    "label_language": "Language",
    "label_theme": "Theme",
    "theme_system": "System",
    "theme_light": "Light",
    "theme_dark": "Dark",
    # Errors
    "error_load_title": "Could not load the file",
    "error_save_title": "Could not save the file",
    "error_empty_title": "Name must not be empty.",
    "error_negative_price": "Price must not be negative.",
}

_TABLES = {"da": STRINGS_DA, "en": STRINGS_EN}
# Language display names are endonyms (shown in their own language).
_LANGUAGE_NAMES = {"da": "Dansk", "en": "English"}
_DEFAULT_LANG = "da"
_active_lang = _DEFAULT_LANG


def available_languages() -> tuple[str, ...]:
    """Language codes that have a string table, in display order."""
    return tuple(_TABLES)


def language_name(code: str) -> str:
    """Human-readable (native) name for a language code."""
    return _LANGUAGE_NAMES.get(code, code)


def set_language(lang: str) -> None:
    """Set the active language for `t()`; unknown codes fall back to default."""
    global _active_lang
    _active_lang = lang if lang in _TABLES else _DEFAULT_LANG


def get_language() -> str:
    """Return the active language code."""
    return _active_lang


def translate(lang: str, key: str, **kwargs) -> str:
    """Return `key` in `lang`, formatted with kwargs. Pure (no global state)."""
    table = _TABLES.get(lang, _TABLES[_DEFAULT_LANG])
    template = table[key]  # KeyError on unknown key, by design
    if kwargs:
        return template.format(**kwargs)
    return template


def t(key: str, **kwargs) -> str:
    """Return the localized string for `key` in the active language."""
    return translate(_active_lang, key, **kwargs)
