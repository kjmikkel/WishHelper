# WishHelper Modernization — Design

**Date:** 2026-06-01
**Status:** Approved for planning
**Author:** Mikkel Kjær Jensen (with Claude)

## 1. Goal & Scope

Re-platform the existing Python 2 / PyGTK 2 desktop app onto a modern,
Windows-friendly stack, **with an explicit cleanup phase** that fixes the
architecture along the way. WishHelper creates a prioritized personal wishlist
(birthdays, Christmas, etc.) and exports it as plain text or a polished PDF.

This is a **re-platform + cleanup**, not a feature-for-feature clone:
- Move off GTK to **PySide6 / Qt**.
- Replace the `pdflatex` external dependency with **direct PDF generation
  (ReportLab)** — no LaTeX install required.
- Split the old `GUI` god-class into testable, single-purpose modules.
- Keep the app **Danish by default** but structure all strings for i18n.

### Target runtime
- **Python 3.12+** (developed and tested on the latest 3.x, currently 3.13).
- Pure-pip dependencies, no system libraries: **PySide6**, **reportlab**.
- Dev: **pytest**.

## 2. Non-Goals (YAGNI)

- No full i18n shipped now (Danish only; just structured so translation is trivial later).
- No web/server version; this stays a single-user desktop app.
- No multi-user, sync, or cloud features.
- No click-to-sort columns (conflicts with manual priority — see §5).
- No system tray icon (dropped).
- No multiple links per wish (one optional link — see §4).

## 3. Architecture

Clean separation of **core logic** (GUI-free, unit-testable) from the **Qt UI**.

```
wishhelper/
  models.py            # Wish, WishList dataclasses (pure data + small helpers)
  storage.py           # load/save v2 JSON; dispatch to legacy import
  legacy_import.py     # one-time conversion of old positional/legacy formats
  settings.py          # persisted app settings (folders, author, currency, theme, language)
  i18n.py              # all user-facing strings; Danish default, i18n-ready
  exporters/
    text.py            # .txt export
    pdf.py             # ReportLab PDF export (inline notes, hyperlinks)
  ui/
    main_window.py     # QMainWindow: list + document fields + actions
    wish_editor.py     # QDialog: add/edit a single wish
    wish_table_model.py# QAbstractTableModel over a WishList
    theme.py           # light/dark/system palette application
  __main__.py          # entry point: python -m wishhelper
tests/
  test_models.py
  test_storage.py      # round-trip v2
  test_legacy_import.py# old format -> v2
  test_text_export.py
  test_pdf_export.py   # smoke: produces a valid PDF, contains expected text/links
pyproject.toml         # deps: PySide6, reportlab; dev: pytest
```

**Layering rule:** `models`, `storage`, `legacy_import`, `exporters`, `i18n`,
and `settings` must not import any Qt module. Only `ui/` and `__main__.py` touch
PySide6. This is what makes the core testable without a display.

### UI table approach
**`QAbstractTableModel` + `QTableView`** (not `QTableWidget`). The `Wish`
objects live in `wish_table_model.py`; the view renders them. Drag-and-drop row
reordering is enabled; click-to-sort is disabled so row order always equals
priority. The model is unit-testable without instantiating widgets.

## 4. Data Model

### `Wish` (dataclass)
| Field            | Type   | Notes |
|------------------|--------|-------|
| `title`          | str    | Required, non-empty. |
| `price`          | int    | `0` means "unknown", rendered as `?`. |
| `type`           | str    | Free-text category (e.g. "Elektronik"). |
| `note`           | str    | Free text. Rendered inline under the item (style B1). |
| `link`           | str    | Optional single URL. Makes the item clickable in the PDF. |
| `promise_ok`     | bool   | A promise/IOU is acceptable (item may not be on the market yet). |
| `promise_reason` | str    | Optional reason shown with the marker (e.g. "udkommer i marts 2027"). |

**Priority** is implicit: it equals the wish's position in the list (1-based).

### `WishList` (document, dataclass)
| Field          | Type        | Notes |
|----------------|-------------|-------|
| `event`        | str         | Event title (e.g. "jul"). |
| `year`         | int         | Defaults to current year. |
| `include_year` | bool        | Whether the year appears in the heading. |
| `author`       | str         | Defaults from settings; editable. |
| `currency`     | str         | Defaults from settings (e.g. "kr."). |
| `wishes`       | list[Wish]  | Order = priority. |

`currency` and `author` are stored in the document for reproducibility, seeded
from settings when a new list is created.

## 5. File Format & Migration

### New canonical format (`format_version: 2`)
Versioned, named-key JSON:

```json
{
  "format_version": 2,
  "event": "jul",
  "year": 2026,
  "include_year": true,
  "author": "Mikkel Kjær Jensen",
  "currency": "kr.",
  "wishes": [
    {
      "title": "Mekanisk tastatur",
      "price": 899,
      "type": "Elektronik",
      "note": "Helst med brune switches.",
      "link": "https://www.keychron.com/k8",
      "promise_ok": false,
      "promise_reason": ""
    }
  ]
}
```

### Legacy import (one-time)
`storage.load()` inspects the parsed JSON:
- Has `"format_version"` → load directly as v2.
- Otherwise → route to `legacy_import.py`, which handles **both** historical
  shapes the old app supported:
  - The positional list format `[wishes, title, year, year_check]` where each
    wish is `[number, title, price, type, note]`.
  - The older 6-element format the old `legacy_wishes()` handled (separate
    notes dict + 4-field wishes).
  New fields (`link`, `promise_ok`, `promise_reason`) default to empty/false;
  any URL found in a converted note is left in the note (no automatic field
  extraction — kept simple).

Saving always writes v2. Migration is therefore "on open"; the user can re-save
to persist the upgrade.

## 6. Exporters

Both consume a `WishList` and produce a string / file. Pure functions, no Qt.

### Text (`.txt`)
Heading (`Ønskeseddel til <event>[ for <year>]`), the intro line, then numbered
rows: `<n>. <title> — <type> — <price>`. Notes on a following indented line.
Promise marker appended inline, e.g. `(løfte er fint — udkommer i marts 2027)`.
Price `0` renders as `?`; otherwise `<price> <currency>`.

### PDF (`.pdf`, ReportLab)
Professional, single-document layout using ReportLab Platypus:
- Centered title + italic subtitle (intro line).
- A table of wishes: `#`, `Navn`, `Type`, `Pris`.
- **Notes inline (style B1):** the note text appears directly under the item
  name in a smaller, muted style. No page-bottom footnotes.
- **Links:** if a wish has a `link`, the item name is a clickable hyperlink
  (ReportLab `<a href>` in the cell paragraph).
- **Promise marker:** qualifying items show an inline tag such as
  *"(løfte er fint — <reason>)"* next to/under the name.
- Honors the document `currency`; `0` → `?`.
- Author rendered in the heading area.

No external tools required; works anywhere `reportlab` is pip-installed.

## 7. Settings & Theming

Persisted settings (replacing the old `config.ini`), stored as a small JSON
file in the per-user config directory (e.g. `%APPDATA%\WishHelper\settings.json`
on Windows). A JSON file is chosen over `QSettings` so `settings.py` stays
Qt-free and unit-testable:
- `last_load_dir`, `last_save_dir`, `last_export_dir` — remembered between sessions.
- `author` — default author for new lists (editable).
- `currency` — default currency for new lists.
- `language` — default `"da"`.
- `theme` — `light` | `dark` | `system`.

`ui/theme.py` applies the chosen palette to the Qt app. "system" follows the OS
appearance where available, otherwise falls back to light.

## 8. Internationalization

All user-facing strings live in `i18n.py` (a Danish string table behind small
accessor functions). No string literals for UI/exports embedded in logic.
Danish is the only shipped language; the structure makes adding `gettext`/`.po`
or another table a localized, low-risk change later. (Not done now — see §2.)

## 9. Error Handling

- **Load:** invalid JSON, unreadable file, or unrecognized shape → a clear,
  localized error dialog; the current list is left untouched (no silent
  `store.clear()` like the old bug). Legacy conversion failures report which
  shape failed.
- **Save/Export:** I/O errors surface a dialog with the path and reason.
- **Validation:** empty title or negative price is rejected in the editor before
  the wish is added/updated.
- Core modules raise typed exceptions; the UI layer translates them to dialogs.

## 10. Testing

`pytest`, targeting the GUI-free core:
- **models:** construction, defaults, priority-as-order invariants.
- **storage:** v2 save → load round-trip is lossless.
- **legacy_import:** each historical shape converts to correct v2 (fixtures of
  real old files).
- **text export:** golden-string checks incl. `?` price, currency, promise marker.
- **pdf export:** smoke test — produces a non-empty, valid PDF byte stream and
  contains expected text/link (parse with a light PDF reader or assert on
  ReportLab story structure).
UI is exercised manually; logic is covered by the above.

## 11. Build Order (high level)

1. `pyproject.toml`, package skeleton, Python version pin.
2. `models.py` + tests.
3. `storage.py` (v2) + `legacy_import.py` + tests.
4. `i18n.py`, `settings.py`.
5. Exporters (`text.py`, `pdf.py`) + tests.
6. Qt UI: `wish_table_model.py`, `main_window.py`, `wish_editor.py`, `theme.py`.
7. Wire entry point `__main__.py`; manual end-to-end pass.
8. Remove/retire old Py2 sources.

(Detailed, ordered implementation plan to be produced by the writing-plans step.)
