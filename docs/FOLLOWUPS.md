# WishHelper — Follow-ups

Non-blocking items deferred during the Python 2 → Python 3.12 / PySide6
modernization (merged to `master`, 2026-06-02). None of these are bugs; the app
works and all 69 tests pass. Listed roughly by value.

Design doc: `docs/superpowers/specs/2026-06-01-wishhelper-modernization-design.md`
Plan: `docs/superpowers/plans/2026-06-01-wishhelper-modernization.md`

---

## 1. Drag-drop reorder: use `beginMoveRows` instead of a full model reset — ✅ DONE
- **Status:** Done. `move_row()` now uses `beginMoveRows()` / `endMoveRows()`
  (with `dataChanged` on the positional `#` column), preserving selection/view
  state instead of resetting the model. Covered by new tests
  (`test_move_row_emits_rows_moved_not_reset`, `…_down_renumbers_across_span`).
- **Where:** `wishhelper/ui/wish_table_model.py` — `move_row()`.
- **Now:** `move_row` brackets the list mutation with `beginResetModel()` /
  `endResetModel()`. Correct and tested, but a full reset is heavy-handed: it
  collapses the selection and any view state on every drag.
- **Do:** switch to `beginMoveRows()` / `endMoveRows()` for incremental,
  selection-preserving updates. Keep the `dropMimeData` "perform move + return
  `False`" idiom (it stops the view from also deleting the source row).
- **Why deferred:** reset works reliably; this is a polish/UX refinement.
- **Effort:** small. Watch the off-by-one in `beginMoveRows`' destination index
  (Qt's semantics differ from a plain list insert).

## 2. Bundle `images/` as package data for wheel builds — ✅ DONE
- **Status:** Done. Icons moved to `wishhelper/resources/*.png` (a sub-package),
  resolved via `importlib.resources.files("wishhelper.resources")`, and declared
  as `[tool.setuptools.package-data]`. Verified a built wheel now contains both
  PNGs. `images/` removed.
- **Where:** `wishhelper/ui/resources.py`, `pyproject.toml`.
- **Now:** icon paths resolve via `Path(__file__).resolve().parents[2] / "images"`,
  i.e. relative to the repo root. This works when running from source
  (`python -m wishhelper`), which is the only supported launch today.
- **Do:** if we ever `pip install`/build a wheel, the icons (outside the
  `wishhelper` package) won't ship. Move `images/` under the package (e.g.
  `wishhelper/resources/`) or add `package-data`/`MANIFEST.in`, and load via
  `importlib.resources`.
- **Why deferred:** not packaged/distributed yet; runs fine from the repo.
- **Effort:** small–medium.

## 3. Additional UI languages (i18n is scaffolded, not multilingual) — ✅ DONE
- **Status:** Done. Added `STRINGS_EN` plus `translate()/set_language()/
  get_language()/available_languages()/language_name()`; `t()` reads the active
  language. `__main__` applies `Settings.language` at startup; the settings
  dialog has a language dropdown; `MainWindow._retranslate_ui()` switches the UI
  live. Key-parity between tables is enforced by a test. (More languages now just
  need another table.)
- **Where:** `wishhelper/i18n.py`, `wishhelper/settings.py` (`Settings.language`),
  `wishhelper/ui/settings_dialog.py`.
- **Now:** all user-facing strings go through `t()` against a single Danish
  table (`STRINGS_DA`). `Settings.language` exists and defaults to `"da"` but is
  never consumed; the settings dialog has no language selector.
- **Do:** add a second string table (or `gettext`/`.po` files), have `t()` pick
  the table by `Settings.language`, and add a language dropdown to the settings
  dialog. The i18n keys `label_language` already exist.
- **Why deferred:** Danish-only was the agreed scope; structure is ready.
- **Effort:** medium (translation content is the bulk).

## 4. PDF tests rely on ReportLab private attributes — ✅ DONE
- **Status:** Done. Tests now render the story to PDF bytes and assert via
  `pypdf` — extracted text for content and link *annotations* (`/Annots` →
  `/A` → `/URI`) for the hyperlink — instead of reaching into
  `Table._cellvalues` / `Paragraph.text`. `pypdf>=4.0` added to the `dev` extra.
- **Where:** `tests/test_pdf_export.py` — `_paragraph_texts` descends into
  `Table._cellvalues` and reads `Paragraph.text`.
- **Now:** the linked title / note / promise marker live inside table cells, so
  the headless assertions reach into ReportLab internals. Passes against the
  pinned `reportlab>=4.1`.
- **Do:** if a ReportLab upgrade breaks these, switch to parsing the rendered
  PDF text (e.g. `pypdf`) or assert on a structured intermediate the exporter
  exposes deliberately.
- **Why deferred:** pragmatic and currently green; only a maintenance risk.
- **Effort:** small if/when it breaks.

## 5. Loaded file's `currency`/`author` aren't surfaced in the UI — ✅ DONE
- **Status:** Done (read-only). A `_doc_info_label` under the document row shows
  the document's own `Valuta`/`Forfatter`, refreshed on load, on settings change,
  and on language switch. Editing them stays in the settings dialog by design.
- **Where:** `wishhelper/ui/main_window.py` — `_load()`.
- **Now:** a loaded wishlist carries its own `currency`/`author`; the table shows
  the right prices, but there's no visible field for them and they can only be
  changed via the settings dialog (which writes the *defaults*, then copies them
  onto the open document). Slightly opaque.
- **Do:** consider showing currency/author somewhere in the main window, or make
  the relationship between "document values" and "settings defaults" explicit.
- **Why deferred:** minor UX nuance flagged in the final review, not a bug.
- **Effort:** small.

## 6. `"system"` theme is resolved once at startup — ✅ DONE
- **Status:** Done. `install_color_scheme_follower()` connects
  `QStyleHints.colorSchemeChanged`; `MainWindow` installs it and re-applies the
  palette live, but only while the active theme is `"system"` (read via a live
  callable so settings changes are tracked). Covered by
  `test_color_scheme_follower_reapplies_only_for_system`.
- **Where:** `wishhelper/ui/theme.py` — `apply_theme()`.
- **Now:** the OS colour scheme is read when the theme is applied (startup and on
  settings change). If the OS flips light↔dark while the app is open, the app
  won't follow until restarted or re-applied.
- **Do:** optionally connect `QStyleHints.colorSchemeChanged` to re-apply the
  theme live when `Settings.theme == "system"`.
- **Why deferred:** rare in practice; live OS theme switching mid-session is an
  edge case.
- **Effort:** small.

## 7. One-step install script — ✅ DONE
- **Status:** Done. `install.sh` + `install.ps1` create `.venv` (checking for
  Python 3.12+) and `pip install -e ".[dev]"`; idempotent and cwd-preserving;
  documented in `README.md`. `.gitattributes` pins `*.sh` to LF.
- **Where:** new `install.sh` (+ a Windows sibling, e.g. `install.ps1`) at the
  repo root; reference it from `README.md`.
- **Now:** install is manual and multi-step (see README): create a venv, activate
  it, then `pip install -e ".[dev]"`. Easy to get a step wrong, and the activate
  command differs per platform.
- **Do:** ship a single script the user runs once that takes care of everything —
  check the Python version (3.12+), create `.venv` if missing, and install the
  package + deps into it. Keep it idempotent (safe to re-run) and print a clear
  "now launch with …" message at the end. Provide `install.ps1` alongside
  `install.sh` since the primary dev environment is Windows (a bare `.sh` needs
  Git Bash/WSL there).
- **Why deferred:** the manual steps work; this is onboarding convenience.
- **Effort:** small.

## 8. One-step launch script — ✅ DONE
- **Status:** Done. `run.sh` + `run.ps1` invoke the app via the `.venv`
  interpreter directly (no activation), so the shell/cwd are untouched on exit;
  they auto-run the installer if `.venv` is absent. Documented in `README.md`.
- **Where:** new `run.sh` (+ a Windows sibling, e.g. `run.ps1`) at the repo root;
  reference it from `README.md`.
- **Now:** launching requires activating the venv first, then `python -m
  wishhelper` — two steps, and activation pollutes the user's shell session.
- **Do:** ship a single script that invokes the app via the venv's interpreter
  directly (`.venv/bin/python -m wishhelper` / `.venv\Scripts\python.exe -m
  wishhelper`) without activating, so the user's shell and working directory are
  exactly as they left them once the program exits. Pair with #7 so a fresh clone
  is install-then-run. Consider auto-running the installer if `.venv` is absent.
- **Why deferred:** the two-step launch works; this is everyday convenience.
- **Effort:** small.

## 9. System tray icon — ✅ DONE
- **Status:** Done. `MainWindow._build_tray()` shows a `QSystemTrayIcon` (reusing
  `APP_ICON`) with a Show/Quit menu and left-click-to-raise, guarded on
  `isSystemTrayAvailable()`. Per decision, the window's close button still quits
  (no minimise-to-tray); the tray is presence + a re-raise shortcut. Menu/tooltip
  retranslate with the UI language.
- **Where:** `wishhelper/ui/main_window.py` (or a small new `ui/tray.py`); reuse
  `APP_ICON` from `wishhelper/ui/resources.py`.
- **Now:** the app only lives in its main window; closing it quits. There is no
  presence in the system tray / notification area.
- **Do:** add a `QSystemTrayIcon` using the existing `QIcon(APP_ICON)` (no new
  art needed), with a small context menu — at least *Show/Hide* and *Quit*, and
  ideally activate-on-click to restore the window. Decide and document the
  close-button behaviour (minimise-to-tray vs. quit). Guard on
  `QSystemTrayIcon.isSystemTrayAvailable()` so the app still runs where no tray
  exists.
- **Why deferred:** purely additive convenience; the app is fully usable without
  it.
- **Effort:** small–medium.
