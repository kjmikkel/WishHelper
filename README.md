# WishHelper

Create a prioritized wishlist and export it as plain text or a polished PDF.

## Features

- Add, edit, delete, and **drag-to-reorder** wishes (row order = priority).
- Each wish has a name, price, type, free-text note, an optional clickable
  **link**, and a "**a promise is enough**" flag with an optional reason
  (for items not yet on the market).
- Export to plain text or a professional **PDF** (via ReportLab — no LaTeX
  required) with inline notes and clickable links.
- Save/load wishlists as versioned JSON; old files are imported automatically.
- Danish UI, structured for future translation. Light/dark/system themes.

## Requirements

- Python 3.12+

## Install

From the project root:

```sh
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -e ".[dev]"
```

## Run

```sh
python -m wishhelper
```

## Test

```sh
pytest
```

## Icon attribution

- `wishlist_add.png` by [Fatcow Webhosting](http://www.fatcow.com/)
- `wishlist.png` made from altering `wishlist_add.png`

## License

GNU GPL v3 — see [LICENSE](LICENSE).
