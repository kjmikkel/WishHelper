# WishHelper Modernization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Re-platform WishHelper from Python 2 / PyGTK 2 to Python 3.12+ / PySide6 with a clean, test-driven core and a ReportLab PDF exporter, preserving the Danish wishlist workflow while dropping the LaTeX/pdflatex dependency.

**Architecture:** A Qt-free core (`models`, `storage`, `legacy_import`, `errors`, `i18n`, `settings`, `exporters`) holds all logic and is built strictly test-first (red/green TDD). A thin PySide6 UI layer (`ui/`) renders a `QAbstractTableModel` over a `WishList` and is verified manually. The layering rule: nothing outside `ui/` and `__main__.py` may import Qt.

**Tech Stack:** Python 3.12+, PySide6 (Qt for Python), ReportLab (PDF), pytest (tests). Settings persisted as JSON in the per-user config dir.

---

## File Structure

```
pyproject.toml                 # project metadata, deps, pytest config
wishhelper/
  __init__.py
  errors.py                    # exception hierarchy (Qt-free)
  models.py                    # Wish, WishList dataclasses
  storage.py                   # v2 JSON save/load + legacy dispatch
  legacy_import.py             # convert old positional/notes-dict formats -> WishList
  i18n.py                      # Danish string table + t() accessor
  settings.py                  # Settings dataclass + JSON load/save
  exporters/
    __init__.py
    text.py                    # export_text(wishlist) -> str
    pdf.py                     # build_story(wishlist) / export_pdf(wishlist, path)
  ui/
    __init__.py
    wish_table_model.py        # QAbstractTableModel over a WishList
    wish_editor.py             # QDialog for add/edit
    theme.py                   # light/dark/system palette
    main_window.py             # QMainWindow wiring it all together
  __main__.py                  # entry point: python -m wishhelper
tests/
  __init__.py
  test_models.py
  test_storage.py
  test_legacy_import.py
  test_i18n.py
  test_settings.py
  test_text_export.py
  test_pdf_export.py
  fixtures/
    legacy_v1.json             # [wishes, title, year, year_check]
    legacy_notes.json          # 6-element notes-dict format
```

**Note on `errors.py`:** the design doc's module list did not name it explicitly; it is introduced here as a small supporting module so `storage` and `legacy_import` can share an exception hierarchy without a circular import. It is Qt-free, consistent with §3 of the spec.

---

## Task 1: Project skeleton and tooling

**Files:**
- Create: `pyproject.toml`
- Create: `wishhelper/__init__.py`
- Create: `wishhelper/exporters/__init__.py`
- Create: `wishhelper/ui/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "wishhelper"
version = "2.0.0"
description = "Create a prioritized wishlist and export it as text or PDF."
requires-python = ">=3.12"
license = { text = "GPL-3.0-or-later" }
authors = [{ name = "Mikkel Kjær Jensen" }]
dependencies = [
    "PySide6>=6.7",
    "reportlab>=4.1",
]

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[project.scripts]
wishhelper = "wishhelper.__main__:main"

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
include = ["wishhelper*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
```

- [ ] **Step 2: Create empty package marker files**

Create each of these files with a single line of content:

`wishhelper/__init__.py`:
```python
"""WishHelper — create and export a prioritized wishlist."""
```

`wishhelper/exporters/__init__.py`:
```python
"""Exporters: text and PDF output for a WishList."""
```

`wishhelper/ui/__init__.py`:
```python
"""PySide6 UI layer. The only package permitted to import Qt."""
```

`tests/__init__.py`:
```python
```
(empty file)

- [ ] **Step 3: Create and activate a virtual environment, install dev deps**

Run (PowerShell):
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```
Expected: installs PySide6, reportlab, pytest with no errors. `python -c "import PySide6, reportlab"` exits 0.

- [ ] **Step 4: Verify pytest runs (collects zero tests)**

Run: `pytest`
Expected: `no tests ran` (exit code 5 is acceptable here — there are no tests yet).

- [ ] **Step 5: Add `.venv/` to `.gitignore` and commit**

Add this line to `.gitignore` under a new `# Virtual environment #` heading:
```
.venv/
```

```bash
git add pyproject.toml wishhelper/__init__.py wishhelper/exporters/__init__.py wishhelper/ui/__init__.py tests/__init__.py .gitignore
git commit -m "Add Python 3.12 package skeleton and tooling"
```

---

## Task 2: Error hierarchy

**Files:**
- Create: `wishhelper/errors.py`
- Test: covered indirectly via later tasks (no behavior of its own)

- [ ] **Step 1: Create `wishhelper/errors.py`**

```python
"""Exception hierarchy for the Qt-free core."""


class WishHelperError(Exception):
    """Base class for all WishHelper errors."""


class StorageError(WishHelperError):
    """Raised when a wishlist file cannot be read, parsed, or written."""


class LegacyFormatError(StorageError):
    """Raised when an old-format file cannot be converted to the current model."""


class SettingsError(WishHelperError):
    """Raised when the settings file cannot be read or written."""
```

- [ ] **Step 2: Verify it imports**

Run: `python -c "from wishhelper.errors import WishHelperError, StorageError, LegacyFormatError, SettingsError"`
Expected: exits 0, no output.

- [ ] **Step 3: Commit**

```bash
git add wishhelper/errors.py
git commit -m "Add core exception hierarchy"
```

---

## Task 3: Data model (`Wish`, `WishList`)

**Files:**
- Create: `wishhelper/models.py`
- Test: `tests/test_models.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_models.py`:
```python
from wishhelper.models import Wish, WishList


def test_wish_defaults():
    w = Wish(title="Bog")
    assert w.title == "Bog"
    assert w.price == 0
    assert w.type == ""
    assert w.note == ""
    assert w.link == ""
    assert w.promise_ok is False
    assert w.promise_reason == ""


def test_wishlist_defaults():
    wl = WishList()
    assert wl.event == ""
    assert wl.year == 0
    assert wl.include_year is True
    assert wl.author == ""
    assert wl.currency == "kr."
    assert wl.wishes == []


def test_wishlist_holds_wishes_in_order():
    wl = WishList(wishes=[Wish(title="A"), Wish(title="B")])
    assert [w.title for w in wl.wishes] == ["A", "B"]


def test_two_wishlists_do_not_share_wishes_list():
    a = WishList()
    b = WishList()
    a.wishes.append(Wish(title="X"))
    assert b.wishes == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'wishhelper.models'`.

- [ ] **Step 3: Write minimal implementation**

Create `wishhelper/models.py`:
```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_models.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add wishhelper/models.py tests/test_models.py
git commit -m "Add Wish and WishList data model (TDD)"
```

---

## Task 4: Storage — v2 JSON round-trip

**Files:**
- Create: `wishhelper/storage.py`
- Test: `tests/test_storage.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_storage.py`:
```python
import json

import pytest

from wishhelper.errors import StorageError
from wishhelper.models import Wish, WishList
from wishhelper.storage import FORMAT_VERSION, load, save, to_dict


def sample_wishlist():
    return WishList(
        event="jul",
        year=2026,
        include_year=True,
        author="Mikkel Kjær Jensen",
        currency="kr.",
        wishes=[
            Wish(title="Mekanisk tastatur", price=899, type="Elektronik",
                 note="Brune switches.", link="https://example.com/kb"),
            Wish(title="Løbesko", price=0, type="Tøj",
                 promise_ok=True, promise_reason="udkommer i marts 2027"),
        ],
    )


def test_to_dict_has_version_and_named_fields():
    data = to_dict(sample_wishlist())
    assert data["format_version"] == FORMAT_VERSION
    assert data["event"] == "jul"
    assert data["wishes"][0]["title"] == "Mekanisk tastatur"
    assert data["wishes"][1]["promise_ok"] is True


def test_save_then_load_round_trips(tmp_path):
    original = sample_wishlist()
    path = tmp_path / "wishes.json"
    save(original, str(path))
    loaded = load(str(path))
    assert loaded == original


def test_save_writes_utf8_json(tmp_path):
    path = tmp_path / "wishes.json"
    save(sample_wishlist(), str(path))
    raw = path.read_text(encoding="utf-8")
    assert "Mikkel Kjær Jensen" in raw
    parsed = json.loads(raw)
    assert parsed["format_version"] == FORMAT_VERSION


def test_load_missing_file_raises_storage_error(tmp_path):
    with pytest.raises(StorageError):
        load(str(tmp_path / "does-not-exist.json"))


def test_load_invalid_json_raises_storage_error(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(StorageError):
        load(str(path))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_storage.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'wishhelper.storage'`.

- [ ] **Step 3: Write minimal implementation**

Create `wishhelper/storage.py`:
```python
"""Persistence for WishList documents. v2 JSON format. Qt-free."""

from __future__ import annotations

import json
from dataclasses import asdict

from wishhelper import legacy_import
from wishhelper.errors import StorageError
from wishhelper.models import Wish, WishList

FORMAT_VERSION = 2


def to_dict(wishlist: WishList) -> dict:
    """Serialize a WishList to a v2-format dict."""
    data = asdict(wishlist)
    data["format_version"] = FORMAT_VERSION
    return data


def from_dict(data: dict) -> WishList:
    """Build a WishList from a v2-format dict."""
    wishes = [Wish(**w) for w in data.get("wishes", [])]
    return WishList(
        event=data.get("event", ""),
        year=data.get("year", 0),
        include_year=data.get("include_year", True),
        author=data.get("author", ""),
        currency=data.get("currency", "kr."),
        wishes=wishes,
    )


def save(wishlist: WishList, path: str) -> None:
    """Write a WishList to `path` as UTF-8 v2 JSON."""
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(to_dict(wishlist), fh, ensure_ascii=False, indent=2)
    except OSError as exc:
        raise StorageError(f"Could not write file: {path}") from exc


def load(path: str) -> WishList:
    """Read a WishList from `path`, converting legacy formats if needed."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw = fh.read()
    except OSError as exc:
        raise StorageError(f"Could not read file: {path}") from exc

    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise StorageError(f"Could not parse JSON: {path}") from exc

    if isinstance(data, dict) and "format_version" in data:
        return from_dict(data)
    return legacy_import.convert(data)
```

- [ ] **Step 4: Create a temporary stub so the import resolves**

`legacy_import` does not exist yet; create a minimal stub so `storage` imports. Create `wishhelper/legacy_import.py`:
```python
"""Conversion of legacy wishlist files to the current model. Qt-free."""

from __future__ import annotations

from wishhelper.errors import LegacyFormatError
from wishhelper.models import WishList


def convert(data) -> WishList:  # pragma: no cover - replaced in Task 5
    raise LegacyFormatError("Legacy conversion not implemented yet")
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_storage.py -v`
Expected: PASS (5 passed). The legacy stub is not exercised by these tests.

- [ ] **Step 6: Commit**

```bash
git add wishhelper/storage.py wishhelper/legacy_import.py tests/test_storage.py
git commit -m "Add v2 JSON storage with round-trip (TDD)"
```

---

## Task 5: Legacy import

**Files:**
- Modify: `wishhelper/legacy_import.py` (replace the stub)
- Create: `tests/test_legacy_import.py`
- Create: `tests/fixtures/legacy_v1.json`
- Create: `tests/fixtures/legacy_notes.json`

Background — the two historical shapes the old app read:
- **v1 positional (length 4):** `[wishes, title, year, year_check]`, where each wish is `[number, title, price, type, note]`.
- **notes-dict (length 6):** `[header, notes, wishes, text, year, check]`, where `notes` is a list of `[key, note_text]` pairs and each wish is either `[number, title, price, type, note_key]` or the older `[title, price, type, note_key]`.

- [ ] **Step 1: Create the fixtures**

Create `tests/fixtures/legacy_v1.json`:
```json
[
  [
    [1, "Mekanisk tastatur", 899, "Elektronik", "Brune switches"],
    [2, "Løbesko", 0, "Tøj", ""]
  ],
  "jul",
  2026.0,
  true
]
```

Create `tests/fixtures/legacy_notes.json`:
```json
[
  "header",
  [["n1", "Brune switches"], ["n2", "Størrelse 44"]],
  [
    [1, "Mekanisk tastatur", 899, "Elektronik", "n1"],
    ["Løbesko", 0, "Tøj", "n2"]
  ],
  "fødselsdag",
  2025.0,
  false
]
```

- [ ] **Step 2: Write the failing test**

Create `tests/test_legacy_import.py`:
```python
import json
from pathlib import Path

import pytest

from wishhelper.errors import LegacyFormatError
from wishhelper.legacy_import import convert

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_convert_v1_positional():
    wl = convert(load_fixture("legacy_v1.json"))
    assert wl.event == "jul"
    assert wl.year == 2026
    assert wl.include_year is True
    assert [w.title for w in wl.wishes] == ["Mekanisk tastatur", "Løbesko"]
    assert wl.wishes[0].price == 899
    assert wl.wishes[0].type == "Elektronik"
    assert wl.wishes[0].note == "Brune switches"
    # New fields default safely
    assert wl.wishes[0].link == ""
    assert wl.wishes[0].promise_ok is False


def test_convert_notes_dict_resolves_note_keys():
    wl = convert(load_fixture("legacy_notes.json"))
    assert wl.event == "fødselsdag"
    assert wl.year == 2025
    assert wl.include_year is False
    assert [w.title for w in wl.wishes] == ["Mekanisk tastatur", "Løbesko"]
    # Note keys resolved to their text
    assert wl.wishes[0].note == "Brune switches"
    assert wl.wishes[1].note == "Størrelse 44"
    # Four-element wish (no leading number) handled
    assert wl.wishes[1].price == 0
    assert wl.wishes[1].type == "Tøj"


def test_convert_unrecognized_shape_raises():
    with pytest.raises(LegacyFormatError):
        convert({"totally": "unexpected"})
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_legacy_import.py -v`
Expected: FAIL — `convert` raises the stub `LegacyFormatError("Legacy conversion not implemented yet")` for the valid fixtures (the unrecognized-shape test passes by accident; the two conversion tests fail).

- [ ] **Step 4: Write the implementation (replace the stub)**

Replace the entire contents of `wishhelper/legacy_import.py`:
```python
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


def _wish_from_row(row, note_lookup) -> Wish:
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
        note_lookup = {key: value for key, value in notes}
    elif len(data) == 4:
        wishes, text, year, check = data
        note_lookup = {}
    else:
        raise LegacyFormatError(f"Unrecognized legacy length: {len(data)}")

    return WishList(
        event=str(text),
        year=int(year),
        include_year=bool(check),
        wishes=[_wish_from_row(row, note_lookup) for row in wishes],
    )
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_legacy_import.py -v`
Expected: PASS (3 passed).

- [ ] **Step 6: Run the full suite to confirm no regressions**

Run: `pytest`
Expected: PASS (all tests so far green).

- [ ] **Step 7: Commit**

```bash
git add wishhelper/legacy_import.py tests/test_legacy_import.py tests/fixtures/legacy_v1.json tests/fixtures/legacy_notes.json
git commit -m "Add legacy format import (TDD)"
```

---

## Task 6: Internationalization strings

**Files:**
- Create: `wishhelper/i18n.py`
- Test: `tests/test_i18n.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_i18n.py`:
```python
import pytest

from wishhelper.i18n import t


def test_simple_string():
    assert t("price_unknown") == "?"


def test_app_title_is_danish():
    assert t("app_title") == "Ønske hjælper"


def test_heading_without_year():
    assert t("doc_heading", event="jul") == "Ønskeseddel til jul"


def test_heading_with_year():
    assert t("doc_heading_year", event="jul", year=2026) == "Ønskeseddel til jul for 2026"


def test_promise_marker_with_reason():
    assert t("promise_marker", reason="udkommer i marts 2027") == \
        "(løfte er fint — udkommer i marts 2027)"


def test_promise_marker_without_reason():
    assert t("promise_marker_plain") == "(løfte er fint)"


def test_unknown_key_raises():
    with pytest.raises(KeyError):
        t("no_such_key")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_i18n.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'wishhelper.i18n'`.

- [ ] **Step 3: Write minimal implementation**

Create `wishhelper/i18n.py`:
```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_i18n.py -v`
Expected: PASS (7 passed).

- [ ] **Step 5: Commit**

```bash
git add wishhelper/i18n.py tests/test_i18n.py
git commit -m "Add Danish string table and t() accessor (TDD)"
```

---

## Task 7: Settings (JSON, per-user)

**Files:**
- Create: `wishhelper/settings.py`
- Test: `tests/test_settings.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_settings.py`:
```python
import pytest

from wishhelper.errors import SettingsError
from wishhelper.settings import Settings, load_settings, save_settings


def test_defaults():
    s = Settings()
    assert s.author == ""
    assert s.currency == "kr."
    assert s.language == "da"
    assert s.theme == "system"
    assert s.last_load_dir == ""
    assert s.last_save_dir == ""
    assert s.last_export_dir == ""


def test_save_then_load_round_trips(tmp_path):
    path = tmp_path / "settings.json"
    s = Settings(author="Mikkel", currency="DKK", theme="dark",
                 last_load_dir="C:/wishes")
    save_settings(s, str(path))
    loaded = load_settings(str(path))
    assert loaded == s


def test_load_missing_file_returns_defaults(tmp_path):
    path = tmp_path / "settings.json"
    loaded = load_settings(str(path))
    assert loaded == Settings()


def test_load_ignores_unknown_keys(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text('{"author": "Mikkel", "obsolete": 123}', encoding="utf-8")
    loaded = load_settings(str(path))
    assert loaded.author == "Mikkel"


def test_load_corrupt_file_raises(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text("{broken", encoding="utf-8")
    with pytest.raises(SettingsError):
        load_settings(str(path))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_settings.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'wishhelper.settings'`.

- [ ] **Step 3: Write minimal implementation**

Create `wishhelper/settings.py`:
```python
"""Persisted application settings as JSON. Qt-free.

The default location is the per-user config directory, e.g.
%APPDATA%\\WishHelper\\settings.json on Windows. Paths are injectable so the
logic is testable without touching the real user profile.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, fields

from wishhelper.errors import SettingsError


@dataclass
class Settings:
    author: str = ""
    currency: str = "kr."
    language: str = "da"
    theme: str = "system"  # "light" | "dark" | "system"
    last_load_dir: str = ""
    last_save_dir: str = ""
    last_export_dir: str = ""


def default_settings_path() -> str:
    """Return the per-user settings.json path for the current OS."""
    base = os.environ.get("APPDATA") or os.path.expanduser("~/.config")
    return os.path.join(base, "WishHelper", "settings.json")


def load_settings(path: str) -> Settings:
    """Load settings from `path`; return defaults if the file is absent."""
    if not os.path.exists(path):
        return Settings()
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        raise SettingsError(f"Could not read settings: {path}") from exc

    known = {f.name for f in fields(Settings)}
    filtered = {k: v for k, v in data.items() if k in known}
    return Settings(**filtered)


def save_settings(settings: Settings, path: str) -> None:
    """Persist settings to `path`, creating parent directories as needed."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(asdict(settings), fh, ensure_ascii=False, indent=2)
    except OSError as exc:
        raise SettingsError(f"Could not write settings: {path}") from exc
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_settings.py -v`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
git add wishhelper/settings.py tests/test_settings.py
git commit -m "Add JSON settings with defaults and injectable path (TDD)"
```

---

## Task 8: Text exporter

**Files:**
- Create: `wishhelper/exporters/text.py`
- Test: `tests/test_text_export.py`

Output contract (per spec §6): heading line, blank line, intro line, blank line,
then for each wish `"<n>. <title> — <type> — <price>"`; a note (if any) on a
following line indented by a tab; the promise marker appended inline to the
title line when `promise_ok` is set. Price `0` → `?`, else `"<price> <currency>"`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_text_export.py`:
```python
from wishhelper.exporters.text import export_text
from wishhelper.models import Wish, WishList


def test_heading_with_year():
    wl = WishList(event="jul", year=2026, include_year=True)
    text = export_text(wl)
    assert text.splitlines()[0] == "Ønskeseddel til jul for 2026"


def test_heading_without_year():
    wl = WishList(event="jul", year=2026, include_year=False)
    assert export_text(wl).splitlines()[0] == "Ønskeseddel til jul"


def test_numbered_rows_and_price():
    wl = WishList(currency="kr.", wishes=[
        Wish(title="Tastatur", price=899, type="Elektronik"),
        Wish(title="Sko", price=0, type="Tøj"),
    ])
    text = export_text(wl)
    assert "1. Tastatur — Elektronik — 899 kr." in text
    assert "2. Sko — Tøj — ?" in text


def test_note_on_indented_line():
    wl = WishList(wishes=[Wish(title="Tastatur", note="Brune switches")])
    lines = export_text(wl).splitlines()
    note_line = next(line for line in lines if "Brune switches" in line)
    assert note_line.startswith("\t")


def test_promise_marker_inline():
    wl = WishList(wishes=[
        Wish(title="Spil", promise_ok=True, promise_reason="udkommer i marts 2027"),
    ])
    text = export_text(wl)
    assert "(løfte er fint — udkommer i marts 2027)" in text
    assert "1. Spil" in text


def test_promise_marker_without_reason():
    wl = WishList(wishes=[Wish(title="Spil", promise_ok=True)])
    assert "(løfte er fint)" in export_text(wl)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_text_export.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'wishhelper.exporters.text'`.

- [ ] **Step 3: Write minimal implementation**

Create `wishhelper/exporters/text.py`:
```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_text_export.py -v`
Expected: PASS (6 passed).

- [ ] **Step 5: Commit**

```bash
git add wishhelper/exporters/text.py tests/test_text_export.py
git commit -m "Add plain-text exporter (TDD)"
```

---

## Task 9: PDF exporter (ReportLab)

**Files:**
- Create: `wishhelper/exporters/pdf.py`
- Test: `tests/test_pdf_export.py`

The exporter exposes two functions. `build_story(wishlist)` returns the list of
ReportLab flowables (testable by inspecting paragraph text without rendering).
`export_pdf(wishlist, path)` builds the document to a file. Inline notes
(style B1): the note appears under the item name in a smaller, muted paragraph.
Links make the item name a clickable `<a href>`. Promise marker appended inline.

- [ ] **Step 1: Write the failing test**

Create `tests/test_pdf_export.py`:
```python
from reportlab.platypus import Paragraph

from wishhelper.exporters.pdf import build_story, export_pdf
from wishhelper.models import Wish, WishList


def _paragraph_texts(story):
    return [f.text for f in story if isinstance(f, Paragraph)]


def sample():
    return WishList(event="jul", year=2026, include_year=True, currency="kr.",
                    author="Mikkel Kjær Jensen", wishes=[
        Wish(title="Tastatur", price=899, type="Elektronik",
             note="Brune switches", link="https://example.com/kb"),
        Wish(title="Spil", price=0, type="Spil",
             promise_ok=True, promise_reason="udkommer i marts 2027"),
    ])


def test_story_contains_heading():
    texts = " ".join(_paragraph_texts(build_story(sample())))
    assert "Ønskeseddel til jul for 2026" in texts


def test_story_renders_link_as_anchor():
    texts = " ".join(_paragraph_texts(build_story(sample())))
    assert '<a href="https://example.com/kb"' in texts
    assert "Tastatur" in texts


def test_story_inline_note_present():
    texts = " ".join(_paragraph_texts(build_story(sample())))
    assert "Brune switches" in texts


def test_story_unknown_price_is_question_mark():
    texts = " ".join(_paragraph_texts(build_story(sample())))
    assert "?" in texts


def test_story_promise_marker_present():
    texts = " ".join(_paragraph_texts(build_story(sample())))
    assert "(løfte er fint — udkommer i marts 2027)" in texts


def test_export_pdf_writes_valid_pdf(tmp_path):
    path = tmp_path / "wishes.pdf"
    export_pdf(sample(), str(path))
    data = path.read_bytes()
    assert data[:5] == b"%PDF-"
    assert len(data) > 1000
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_pdf_export.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'wishhelper.exporters.pdf'`.

- [ ] **Step 3: Write minimal implementation**

Create `wishhelper/exporters/pdf.py`:
```python
"""ReportLab PDF exporter for a WishList. Qt-free.

Inline notes (style B1): each item's note is shown under its name in a smaller,
muted paragraph. A `link` turns the item name into a clickable hyperlink. The
promise marker is appended inline after the name.
"""

from __future__ import annotations

from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from wishhelper.i18n import t
from wishhelper.models import Wish, WishList

_styles = getSampleStyleSheet()

_TITLE = ParagraphStyle("WishTitle", parent=_styles["Title"], alignment=TA_CENTER)
_SUBTITLE = ParagraphStyle(
    "WishSubtitle", parent=_styles["Normal"], alignment=TA_CENTER,
    fontName="Helvetica-Oblique", textColor=colors.HexColor("#444444"),
    spaceAfter=14,
)
_ITEM = ParagraphStyle("WishItem", parent=_styles["Normal"], fontSize=11, leading=14)
_NOTE = ParagraphStyle(
    "WishNote", parent=_styles["Normal"], fontSize=9, leading=11,
    fontName="Helvetica-Oblique", textColor=colors.HexColor("#555555"),
    leftIndent=2,
)
_CELL = ParagraphStyle("WishCell", parent=_styles["Normal"], fontSize=11, leading=14)
_HEADER = ParagraphStyle(
    "WishHeader", parent=_styles["Normal"], fontSize=9,
    fontName="Helvetica-Bold", textColor=colors.HexColor("#666666"),
)


def _heading_text(wishlist: WishList) -> str:
    if wishlist.include_year:
        return t("doc_heading_year", event=wishlist.event, year=wishlist.year)
    return t("doc_heading", event=wishlist.event)


def _price_text(wish: Wish, currency: str) -> str:
    if wish.price == 0:
        return t("price_unknown")
    return t("price_with_currency", price=wish.price, currency=currency)


def _promise_text(wish: Wish) -> str:
    if not wish.promise_ok:
        return ""
    if wish.promise_reason:
        return " " + t("promise_marker", reason=wish.promise_reason)
    return " " + t("promise_marker_plain")


def _name_cell(wish: Wish) -> list:
    """Build the name cell: linked/plain title + promise marker, then note."""
    safe_title = escape(wish.title)
    if wish.link:
        safe_link = escape(wish.link, {'"': "&quot;"})
        name_html = f'<a href="{safe_link}" color="#1558b0">{safe_title}</a>'
    else:
        name_html = safe_title
    name_html += escape(_promise_text(wish))
    flowables = [Paragraph(name_html, _ITEM)]
    if wish.note:
        flowables.append(Paragraph(escape(wish.note), _NOTE))
    return flowables


def build_story(wishlist: WishList) -> list:
    """Return the ordered list of ReportLab flowables for the document."""
    story = [
        Paragraph(escape(_heading_text(wishlist)), _TITLE),
        Paragraph(escape(t("intro_line")), _SUBTITLE),
    ]
    if wishlist.author:
        story.append(Paragraph(escape(wishlist.author), _SUBTITLE))

    header = [
        Paragraph(t("col_number"), _HEADER),
        Paragraph(t("col_name"), _HEADER),
        Paragraph(t("col_type"), _HEADER),
        Paragraph(t("col_price"), _HEADER),
    ]
    rows = [header]
    for index, wish in enumerate(wishlist.wishes, start=1):
        rows.append([
            Paragraph(str(index), _CELL),
            _name_cell(wish),
            Paragraph(escape(wish.type), _CELL),
            Paragraph(escape(_price_text(wish, wishlist.currency)), _CELL),
        ])

    table = Table(rows, colWidths=[1.2 * cm, 9.5 * cm, 3.5 * cm, 2.8 * cm])
    table.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, 0), 1.2, colors.HexColor("#333333")),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, colors.HexColor("#e0e0e0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (3, 0), (3, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(Spacer(1, 6))
    story.append(table)
    return story


def export_pdf(wishlist: WishList, path: str) -> None:
    """Render the wishlist to a PDF file at `path`."""
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title=_heading_text(wishlist),
        author=wishlist.author or "WishHelper",
    )
    doc.build(build_story(wishlist))
```

Note: the link/promise assertions inspect the *name cell* paragraphs. Because
`_name_cell` returns a list nested inside the table (not top-level flowables),
adjust the test helper to also collect paragraphs from table cells. Update
`_paragraph_texts` in the test (Step 1) is already written for top-level only —
so in Step 3 we ALSO add a tiny helper export. To keep the test as written,
`build_story` must surface those paragraphs at a level the test can see.

- [ ] **Step 4: Make name-cell paragraphs reachable by the test**

The Step 1 test scans only top-level `Paragraph` flowables, but the title link,
note, and promise marker live inside table cells. Rather than loosen the test,
add a flat debug projection the test already relies on by having the test walk
the table. Update `tests/test_pdf_export.py`'s `_paragraph_texts` to also descend
into `Table` cells:

```python
from reportlab.platypus import Paragraph, Table


def _paragraph_texts(story):
    texts = []
    for flowable in story:
        if isinstance(flowable, Paragraph):
            texts.append(flowable.text)
        elif isinstance(flowable, Table):
            for row in flowable._cellvalues:
                for cell in row:
                    items = cell if isinstance(cell, list) else [cell]
                    for item in items:
                        if isinstance(item, Paragraph):
                            texts.append(item.text)
    return texts
```

(Replace the original `_paragraph_texts` definition with this one; keep the rest
of the test file unchanged.)

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_pdf_export.py -v`
Expected: PASS (6 passed).

- [ ] **Step 6: Run the full suite**

Run: `pytest`
Expected: PASS (entire core green).

- [ ] **Step 7: Commit**

```bash
git add wishhelper/exporters/pdf.py tests/test_pdf_export.py
git commit -m "Add ReportLab PDF exporter with inline notes and links (TDD)"
```

---

## Task 10: Qt table model

**Files:**
- Create: `wishhelper/ui/wish_table_model.py`
- Test: `tests/test_wish_table_model.py`

This is UI-adjacent but headless-testable: `QAbstractTableModel` needs only
`QtCore` (no display, no `QApplication`). We therefore keep it under TDD.

- [ ] **Step 1: Write the failing test**

Create `tests/test_wish_table_model.py`:
```python
from PySide6.QtCore import Qt

from wishhelper.models import Wish, WishList
from wishhelper.ui.wish_table_model import WishTableModel


def model_with_two():
    wl = WishList(currency="kr.", wishes=[
        Wish(title="Tastatur", price=899, type="Elektronik", note="Brune"),
        Wish(title="Sko", price=0, type="Tøj"),
    ])
    return WishTableModel(wl)


def test_row_and_column_counts():
    m = model_with_two()
    assert m.rowCount() == 2
    assert m.columnCount() == 5  # #, Navn, Pris, Type, Note


def test_priority_column_is_one_based_index():
    m = model_with_two()
    assert m.data(m.index(0, 0), Qt.DisplayRole) == "1"
    assert m.data(m.index(1, 0), Qt.DisplayRole) == "2"


def test_name_and_price_display():
    m = model_with_two()
    assert m.data(m.index(0, 1), Qt.DisplayRole) == "Tastatur"
    assert m.data(m.index(0, 2), Qt.DisplayRole) == "899 kr."
    assert m.data(m.index(1, 2), Qt.DisplayRole) == "?"


def test_header_labels_danish():
    m = model_with_two()
    assert m.headerData(1, Qt.Horizontal, Qt.DisplayRole) == "Navn"


def test_add_wish_appends_and_grows():
    m = model_with_two()
    m.add_wish(Wish(title="Bog", price=120, type="Bog"))
    assert m.rowCount() == 3
    assert m.data(m.index(2, 0), Qt.DisplayRole) == "3"


def test_remove_wish_renumbers():
    m = model_with_two()
    m.remove_wish(0)
    assert m.rowCount() == 1
    assert m.data(m.index(0, 0), Qt.DisplayRole) == "1"
    assert m.data(m.index(0, 1), Qt.DisplayRole) == "Sko"


def test_replace_wish_updates_row():
    m = model_with_two()
    m.replace_wish(0, Wish(title="Mus", price=250, type="Elektronik"))
    assert m.data(m.index(0, 1), Qt.DisplayRole) == "Mus"


def test_move_row_reorders_and_renumbers():
    m = model_with_two()
    m.move_row(1, 0)  # move "Sko" to the top
    assert m.data(m.index(0, 1), Qt.DisplayRole) == "Sko"
    assert m.data(m.index(0, 0), Qt.DisplayRole) == "1"
    assert m.data(m.index(1, 1), Qt.DisplayRole) == "Tastatur"


def test_drag_flags_enabled():
    m = model_with_two()
    flags = m.flags(m.index(0, 0))
    assert flags & Qt.ItemIsDragEnabled
    # Drops are accepted on the empty (invalid) parent for between-row drops
    assert m.flags(m.index(-1, -1)) & Qt.ItemIsDropEnabled


def test_drop_mime_reorders_to_top():
    from PySide6.QtCore import QModelIndex
    m = model_with_two()
    data = m.mimeData([m.index(1, 0)])  # drag "Sko"
    handled = m.dropMimeData(data, Qt.MoveAction, 0, 0, QModelIndex())
    # We perform the move ourselves and return False so the view does not
    # additionally remove the source row.
    assert handled is False
    assert m.data(m.index(0, 1), Qt.DisplayRole) == "Sko"
    assert m.data(m.index(1, 1), Qt.DisplayRole) == "Tastatur"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_wish_table_model.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'wishhelper.ui.wish_table_model'`.

- [ ] **Step 3: Write minimal implementation**

Create `wishhelper/ui/wish_table_model.py`:
```python
"""QAbstractTableModel over a WishList. Headless-testable (QtCore only)."""

from __future__ import annotations

from PySide6.QtCore import (
    QAbstractTableModel,
    QByteArray,
    QMimeData,
    QModelIndex,
    Qt,
)

from wishhelper.i18n import t
from wishhelper.models import Wish, WishList

COL_NUMBER, COL_NAME, COL_PRICE, COL_TYPE, COL_NOTE = range(5)
_HEADER_KEYS = ("col_number", "col_name", "col_price", "col_type", "col_note")
_MIME = "application/x-wishhelper-row"


class WishTableModel(QAbstractTableModel):
    def __init__(self, wishlist: WishList | None = None, parent=None):
        super().__init__(parent)
        self._wishlist = wishlist or WishList()

    # --- Qt model interface -------------------------------------------------
    def rowCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._wishlist.wishes)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(_HEADER_KEYS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return t(_HEADER_KEYS[section])
        return None

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        wish = self._wishlist.wishes[index.row()]
        column = index.column()
        if column == COL_NUMBER:
            return str(index.row() + 1)
        if column == COL_NAME:
            return wish.title
        if column == COL_PRICE:
            return self._price_text(wish)
        if column == COL_TYPE:
            return wish.type
        if column == COL_NOTE:
            return wish.note
        return None

    def _price_text(self, wish: Wish) -> str:
        if wish.price == 0:
            return t("price_unknown")
        return t("price_with_currency", price=wish.price,
                 currency=self._wishlist.currency)

    # --- Convenience mutators ----------------------------------------------
    def wishlist(self) -> WishList:
        return self._wishlist

    def set_wishlist(self, wishlist: WishList) -> None:
        self.beginResetModel()
        self._wishlist = wishlist
        self.endResetModel()

    def wish_at(self, row: int) -> Wish:
        return self._wishlist.wishes[row]

    def add_wish(self, wish: Wish) -> None:
        row = len(self._wishlist.wishes)
        self.beginInsertRows(QModelIndex(), row, row)
        self._wishlist.wishes.append(wish)
        self.endInsertRows()

    def remove_wish(self, row: int) -> None:
        self.beginRemoveRows(QModelIndex(), row, row)
        del self._wishlist.wishes[row]
        self.endRemoveRows()

    def replace_wish(self, row: int, wish: Wish) -> None:
        self._wishlist.wishes[row] = wish
        top = self.index(row, 0)
        bottom = self.index(row, self.columnCount() - 1)
        self.dataChanged.emit(top, bottom)

    def move_row(self, source: int, dest: int) -> None:
        wish = self._wishlist.wishes.pop(source)
        self._wishlist.wishes.insert(dest, wish)
        self.beginResetModel()
        self.endResetModel()

    # --- drag & drop reordering (internal move) -----------------------------
    def flags(self, index):
        base = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if index.isValid():
            return base | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        return base | Qt.ItemIsDropEnabled

    def supportedDropActions(self):
        return Qt.MoveAction

    def mimeTypes(self):
        return [_MIME]

    def mimeData(self, indexes):
        rows = sorted({i.row() for i in indexes if i.isValid()})
        payload = QMimeData()
        payload.setData(_MIME, QByteArray(str(rows[0]).encode("ascii")))
        return payload

    def dropMimeData(self, data, action, row, column, parent):
        if action != Qt.MoveAction or not data.hasFormat(_MIME):
            return False
        source = int(bytes(data.data(_MIME).data()).decode("ascii"))
        if row != -1:
            dest = row
        elif parent.isValid():
            dest = parent.row()
        else:
            dest = len(self._wishlist.wishes)
        if dest > source:
            dest -= 1
        if dest != source:
            self.move_row(source, dest)
        # Return False so the view does not also remove the dragged source row
        # (we have already moved it in place).
        return False
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_wish_table_model.py -v`
Expected: PASS (10 passed).

- [ ] **Step 5: Commit**

```bash
git add wishhelper/ui/wish_table_model.py tests/test_wish_table_model.py
git commit -m "Add QAbstractTableModel over WishList (TDD)"
```

---

## Task 11: Theme helper

**Files:**
- Create: `wishhelper/ui/theme.py`

This applies a palette to the `QApplication`. It is not unit-tested (pure Qt
side effects); it is verified manually in Task 14.

- [ ] **Step 1: Create `wishhelper/ui/theme.py`**

```python
"""Light/dark/system palette application for the Qt app."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


def _dark_palette() -> QPalette:
    p = QPalette()
    bg = QColor(45, 45, 48)
    text = QColor(220, 220, 220)
    base = QColor(30, 30, 32)
    p.setColor(QPalette.Window, bg)
    p.setColor(QPalette.WindowText, text)
    p.setColor(QPalette.Base, base)
    p.setColor(QPalette.AlternateBase, bg)
    p.setColor(QPalette.Text, text)
    p.setColor(QPalette.Button, bg)
    p.setColor(QPalette.ButtonText, text)
    p.setColor(QPalette.Highlight, QColor(21, 88, 176))
    p.setColor(QPalette.HighlightedText, Qt.white)
    return p


def apply_theme(app: QApplication, theme: str) -> None:
    """Apply 'light', 'dark', or 'system' theme to the application."""
    if theme == "dark":
        app.setStyle("Fusion")
        app.setPalette(_dark_palette())
    elif theme == "light":
        app.setStyle("Fusion")
        app.setPalette(QPalette())
    else:  # "system": leave the platform default untouched
        app.setPalette(app.style().standardPalette())
```

- [ ] **Step 2: Verify import (needs an app instance to be meaningful, but import must succeed)**

Run: `python -c "import wishhelper.ui.theme"`
Expected: exits 0.

- [ ] **Step 3: Commit**

```bash
git add wishhelper/ui/theme.py
git commit -m "Add light/dark/system theme helper"
```

---

## Task 12: Wish editor dialog

**Files:**
- Create: `wishhelper/ui/wish_editor.py`

A `QDialog` to create/edit one `Wish`. Validation (non-empty title, non-negative
price) is enforced before accept. Verified manually in Task 14.

- [ ] **Step 1: Create `wishhelper/ui/wish_editor.py`**

```python
"""Modal dialog to add or edit a single Wish."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QSpinBox,
)

from wishhelper.i18n import t
from wishhelper.models import Wish


class WishEditor(QDialog):
    def __init__(self, wish: Wish | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("label_title"))
        self._build_ui()
        if wish is not None:
            self._load(wish)

    def _build_ui(self) -> None:
        layout = QFormLayout(self)
        self.title_edit = QLineEdit()
        self.price_spin = QSpinBox()
        self.price_spin.setRange(0, 1_000_000)
        self.type_edit = QLineEdit()
        self.note_edit = QLineEdit()
        self.link_edit = QLineEdit()
        self.promise_check = QCheckBox(t("label_promise_ok"))
        self.promise_reason_edit = QLineEdit()
        self.promise_reason_edit.setEnabled(False)
        self.promise_check.toggled.connect(self.promise_reason_edit.setEnabled)

        layout.addRow(t("label_title"), self.title_edit)
        layout.addRow(t("label_price"), self.price_spin)
        layout.addRow(t("label_type"), self.type_edit)
        layout.addRow(t("label_note"), self.note_edit)
        layout.addRow(t("label_link"), self.link_edit)
        layout.addRow("", self.promise_check)
        layout.addRow(t("label_promise_reason"), self.promise_reason_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _load(self, wish: Wish) -> None:
        self.title_edit.setText(wish.title)
        self.price_spin.setValue(wish.price)
        self.type_edit.setText(wish.type)
        self.note_edit.setText(wish.note)
        self.link_edit.setText(wish.link)
        self.promise_check.setChecked(wish.promise_ok)
        self.promise_reason_edit.setText(wish.promise_reason)

    def _on_accept(self) -> None:
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, t("app_title"), t("error_empty_title"))
            return
        self.accept()

    def wish(self) -> Wish:
        """Return the Wish described by the current field values."""
        return Wish(
            title=self.title_edit.text().strip(),
            price=self.price_spin.value(),
            type=self.type_edit.text().strip(),
            note=self.note_edit.text().strip(),
            link=self.link_edit.text().strip(),
            promise_ok=self.promise_check.isChecked(),
            promise_reason=self.promise_reason_edit.text().strip(),
        )
```

- [ ] **Step 2: Verify import**

Run: `python -c "import wishhelper.ui.wish_editor"`
Expected: exits 0.

- [ ] **Step 3: Commit**

```bash
git add wishhelper/ui/wish_editor.py
git commit -m "Add wish editor dialog"
```

---

## Task 13: Main window

**Files:**
- Create: `wishhelper/ui/main_window.py`

The `QMainWindow`: document fields (event/year/include-year), the wish table
(`QTableView` with drag reorder, sorting disabled), an action bar, and
save/load/export wired to the core. Verified manually in Task 14.

- [ ] **Step 1: Create `wishhelper/ui/main_window.py`**

```python
"""Main application window. The only place that wires UI to the core."""

from __future__ import annotations

import datetime
import os

from PySide6.QtWidgets import (
    QAbstractItemView as AIV,
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from wishhelper import storage
from wishhelper.errors import WishHelperError
from wishhelper.exporters.pdf import export_pdf
from wishhelper.exporters.text import export_text
from wishhelper.i18n import t
from wishhelper.models import WishList
from wishhelper.settings import Settings, save_settings
from wishhelper.ui.wish_editor import WishEditor
from wishhelper.ui.wish_table_model import WishTableModel


class MainWindow(QMainWindow):
    def __init__(self, settings: Settings, settings_path: str, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._settings_path = settings_path
        self.setWindowTitle(t("app_title"))
        self._model = WishTableModel(self._new_wishlist())
        self._build_ui()

    def _new_wishlist(self) -> WishList:
        return WishList(
            year=datetime.datetime.now().year,
            author=self._settings.author,
            currency=self._settings.currency,
        )

    def _build_ui(self) -> None:
        central = QWidget()
        outer = QVBoxLayout(central)

        # Document fields
        doc_row = QHBoxLayout()
        self.event_edit = QLineEdit(self._model.wishlist().event)
        self.year_spin = QSpinBox()
        self.year_spin.setRange(1900, 9999)
        self.year_spin.setValue(self._model.wishlist().year)
        self.include_year_check = QCheckBox(t("label_include_year"))
        self.include_year_check.setChecked(self._model.wishlist().include_year)
        doc_row.addWidget(QLabel(t("label_event")))
        doc_row.addWidget(self.event_edit)
        doc_row.addWidget(QLabel(t("label_year")))
        doc_row.addWidget(self.year_spin)
        doc_row.addWidget(self.include_year_check)
        outer.addLayout(doc_row)

        # Table
        self.table = QTableView()
        self.table.setModel(self._model)
        self.table.setSelectionBehavior(AIV.SelectRows)
        self.table.setSelectionMode(AIV.SingleSelection)
        self.table.setSortingEnabled(False)  # order == priority
        self.table.setDragDropMode(AIV.InternalMove)
        self.table.setDragDropOverwriteMode(False)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(lambda *_: self._edit_selected())
        outer.addWidget(self.table)

        # Action bar
        bar = QHBoxLayout()
        for label, slot in [
            (t("action_add"), self._add),
            (t("action_edit"), self._edit_selected),
            (t("action_delete"), self._delete_selected),
            (t("action_load"), self._load),
            (t("action_save"), self._save),
            (t("action_export"), self._export),
        ]:
            button = QPushButton(label)
            button.clicked.connect(slot)
            bar.addWidget(button)
        outer.addLayout(bar)

        self.setCentralWidget(central)

    # --- document sync ------------------------------------------------------
    def _sync_document_fields(self) -> None:
        wl = self._model.wishlist()
        wl.event = self.event_edit.text().strip()
        wl.year = self.year_spin.value()
        wl.include_year = self.include_year_check.isChecked()

    def _selected_row(self) -> int:
        rows = self.table.selectionModel().selectedRows()
        return rows[0].row() if rows else -1

    # --- actions ------------------------------------------------------------
    def _add(self) -> None:
        editor = WishEditor(parent=self)
        if editor.exec():
            self._model.add_wish(editor.wish())

    def _edit_selected(self) -> None:
        row = self._selected_row()
        if row < 0:
            return
        editor = WishEditor(self._model.wish_at(row), parent=self)
        if editor.exec():
            self._model.replace_wish(row, editor.wish())

    def _delete_selected(self) -> None:
        row = self._selected_row()
        if row >= 0:
            self._model.remove_wish(row)

    def _load(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, t("action_load"), self._settings.last_load_dir,
            "WishHelper (*.json)")
        if not path:
            return
        try:
            wishlist = storage.load(path)
        except WishHelperError as exc:
            QMessageBox.critical(self, t("error_load_title"), str(exc))
            return
        self._model.set_wishlist(wishlist)
        self.event_edit.setText(wishlist.event)
        self.year_spin.setValue(wishlist.year or self.year_spin.value())
        self.include_year_check.setChecked(wishlist.include_year)
        self._settings.last_load_dir = os.path.dirname(path)
        self._persist_settings()

    def _save(self) -> None:
        self._sync_document_fields()
        path, _ = QFileDialog.getSaveFileName(
            self, t("action_save"), self._settings.last_save_dir,
            "WishHelper (*.json)")
        if not path:
            return
        if not path.lower().endswith(".json"):
            path += ".json"
        try:
            storage.save(self._model.wishlist(), path)
        except WishHelperError as exc:
            QMessageBox.critical(self, t("error_save_title"), str(exc))
            return
        self._settings.last_save_dir = os.path.dirname(path)
        self._persist_settings()

    def _export(self) -> None:
        self._sync_document_fields()
        path, selected = QFileDialog.getSaveFileName(
            self, t("action_export"), self._settings.last_export_dir,
            "PDF (*.pdf);;Text (*.txt)")
        if not path:
            return
        try:
            if selected.startswith("Text") or path.lower().endswith(".txt"):
                if not path.lower().endswith(".txt"):
                    path += ".txt"
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(export_text(self._model.wishlist()))
            else:
                if not path.lower().endswith(".pdf"):
                    path += ".pdf"
                export_pdf(self._model.wishlist(), path)
        except (OSError, WishHelperError) as exc:
            QMessageBox.critical(self, t("error_save_title"), str(exc))
            return
        self._settings.last_export_dir = os.path.dirname(path)
        self._persist_settings()

    def _persist_settings(self) -> None:
        try:
            save_settings(self._settings, self._settings_path)
        except WishHelperError:
            pass  # non-fatal: a failed settings write must not block the user
```

- [ ] **Step 2: Verify import**

Run: `python -c "import wishhelper.ui.main_window"`
Expected: exits 0.

- [ ] **Step 3: Commit**

```bash
git add wishhelper/ui/main_window.py
git commit -m "Add main window wiring UI to the core"
```

---

## Task 14: Entry point and manual end-to-end verification

**Files:**
- Create: `wishhelper/__main__.py`

- [ ] **Step 1: Create `wishhelper/__main__.py`**

```python
"""Application entry point: python -m wishhelper."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from wishhelper.settings import default_settings_path, load_settings
from wishhelper.ui.main_window import MainWindow
from wishhelper.ui.theme import apply_theme


def main() -> int:
    app = QApplication(sys.argv)
    settings_path = default_settings_path()
    settings = load_settings(settings_path)
    apply_theme(app, settings.theme)
    window = MainWindow(settings, settings_path)
    window.resize(820, 520)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run the full automated suite**

Run: `pytest`
Expected: PASS — all core + table-model tests green.

- [ ] **Step 3: Launch the app**

Run: `python -m wishhelper`
Expected: the window opens titled "Ønske hjælper" with an empty table and the action bar.

- [ ] **Step 4: Manual verification checklist**

Confirm each by hand:
- [ ] Add several wishes via "Tilføj"; one with a link, one with "Et løfte er nok" + reason, one with price 0.
- [ ] Double-click a row to edit; changes appear in the table.
- [ ] Drag a row to reorder; the "#" column renumbers; columns do **not** re-sort on header click.
- [ ] Delete a selected row; remaining rows renumber.
- [ ] "Gem" saves a `.json`; reopen the file in a text editor and confirm `format_version: 2` and named fields.
- [ ] "Hent" reloads that file and the table/fields repopulate.
- [ ] "Hent" on `tests/fixtures/legacy_v1.json` imports correctly (titles, year, include-year).
- [ ] "Eksportér" → PDF opens in a viewer: centered Danish heading, table, inline notes under names, clickable link, `(løfte er fint — …)` marker, `?` for unknown price.
- [ ] "Eksportér" → choose Text filter; the `.txt` matches the spec layout.
- [ ] Last-used folders are remembered on the next save/load/export.

- [ ] **Step 5: Commit**

```bash
git add wishhelper/__main__.py
git commit -m "Add entry point; complete end-to-end app"
```

---

## Task 15: Retire the old Python 2 sources and refresh docs

**Files:**
- Delete: `WishHelper.py`, `wish.py`, `wish_editor.py`, `enumerate.py`, `__init__.py` (the legacy top-level one), `Wish.sh`
- Delete: `gui/WishHelperMain.glade`, `gui/WishHelperEditor.glade`, `tex_files/tex_header`
- Modify: `README`

Note: the new package's `wishhelper/__init__.py` is a different file from the
legacy top-level `__init__.py`; only the legacy top-level one is removed. Keep
`images/` — the icons may still be used for the window/app icon (optional
follow-up to wire them in).

- [ ] **Step 1: Confirm nothing in the new package imports the old modules**

Run: `git grep -nE "import (wish|wish_editor|enumerate)\b|from __init__ import"` -- wishhelper tests
Expected: no matches (the new code uses `wishhelper.*` imports only).

- [ ] **Step 2: Remove the legacy files**

```bash
git rm WishHelper.py wish.py wish_editor.py enumerate.py __init__.py Wish.sh
git rm gui/WishHelperMain.glade gui/WishHelperEditor.glade tex_files/tex_header
```
(If `gui/` and `tex_files/` are now empty, git will drop them automatically.)

- [ ] **Step 3: Rewrite `README`**

Replace the contents of `README` with:
```
WishHelper
==========

Create a prioritized wishlist and export it as plain text or a polished PDF.

Requirements:
  - Python 3.12+

Install (from the project root):
  python -m venv .venv
  .venv\Scripts\activate        (Windows)   |   source .venv/bin/activate (Unix)
  pip install -e ".[dev]"

Run:
  python -m wishhelper

Test:
  pytest

Icon attribution:
  wishlist_add.png by Fatcow Webhosting: http://www.fatcow.com/
  wishlist.png made from altering wishlist_add.png

License: GNU GPL v3 (see LICENSE).
```

- [ ] **Step 4: Run the full suite once more**

Run: `pytest`
Expected: PASS — removing legacy files changes nothing in the new package.

- [ ] **Step 5: Launch once more to confirm the app still starts**

Run: `python -m wishhelper`
Expected: window opens normally.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "Retire Python 2 sources; update README for the new app"
```

---

## Self-Review Notes (for the implementer)

- **Spec coverage:** re-platform to PySide6 (Tasks 10–14), ReportLab PDF with inline notes/links/promise marker (Task 9), versioned JSON + legacy import (Tasks 4–5), Danish-but-i18n-ready strings (Task 6), settings/folders/author/currency/theme (Tasks 7, 11), new fields link + promise (Tasks 3, 9, 12), no sort / no tray (Tasks 10, 13), TDD throughout the core (Tasks 2–10), cleanup of old sources (Task 15).
- **Type/name consistency:** `Wish`/`WishList` field names are identical across `models`, `storage`, `legacy_import`, exporters, table model, and editor. `to_dict`/`from_dict`/`load`/`save`, `build_story`/`export_pdf`, `export_text`, `Settings`/`load_settings`/`save_settings`, and `WishTableModel.{add_wish,remove_wish,replace_wish,move_row,wish_at,set_wishlist,wishlist}` are referenced consistently by callers.
- **Known nuance:** the PDF test helper descends into table cells (Task 9, Step 4) because linked names/notes live inside the `Table`, not as top-level flowables.
```
