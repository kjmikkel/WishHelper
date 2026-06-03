# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] — 2026-06-03

### Added
- Per-row **action column** with inline *Edit* / *Delete* links, and a trailing
  **"add wish" row** for creating items — replacing the row buttons on the
  bottom bar.
- **English UI** alongside Danish, switchable live from the settings dialog (no
  restart). String tables are key-checked so a language can't be half-translated.
- **System tray icon** with a Show/Quit menu (left-click to re-raise). The
  window's close button still quits.
- Read-only display of a loaded document's **currency and author** under the
  document fields.
- One-step **install** (`install.sh` / `install.ps1`) and **launch**
  (`run.sh` / `run.ps1`) scripts.
- **Standalone executable** packaging via PyInstaller (`build.ps1` / `build.sh`)
  producing a one-file, windowed `WishHelper.exe` with the icon embedded.

### Changed
- Bottom bar now holds document-level actions only (Load / Save / Export / Settings).
- Row reordering uses incremental `beginMoveRows` instead of a full model reset,
  preserving selection and view state during a drag.
- Icons are bundled as package data and resolved via `importlib.resources`, so
  they ship correctly in a wheel; the app icon is now a multi-size `.ico`.
- The `"system"` theme now follows the OS light/dark scheme **live**, not just at
  startup.

### Fixed
- The Windows **taskbar now shows the WishHelper icon** when run as the packaged
  `WishHelper.exe` (running through `python.exe` shows the Python icon, an
  inherent limitation of launching a GUI via the interpreter). An explicit
  AppUserModelID is set for correct taskbar grouping/pinning.

### Internal
- PDF export tests assert on the **rendered PDF** (via `pypdf`) — extracted text
  and link annotations — instead of ReportLab's private flowable internals.
- A `conftest.py` forces Qt's offscreen platform so the GUI tests run headless.

## [2.0.0] — 2026-06-02

### Changed
- Complete rewrite from Python 2 to **Python 3.12 + PySide6 (Qt 6)**; the legacy
  Python 2 sources were retired.

### Added
- Qt main window: editable wishlist table with drag-to-reorder, a wish editor
  dialog, and a settings dialog with live theme switching.
- Light / dark / system **themes** (Fusion style, palette-driven).
- Export to **plain text** and a polished **PDF** (ReportLab) with inline notes
  and clickable links.
- Versioned **JSON** save/load with automatic import of older files.
- Application / window icons; Danish UI routed through a translation layer.
