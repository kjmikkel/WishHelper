"""Locate bundled image resources (window/app icons).

Repo layout: ``<root>/images/*.png`` alongside ``<root>/wishhelper/ui/``.
Paths are resolved relative to this file so the app finds its icons regardless
of the current working directory. Importing this module does NOT import Qt.
"""

from __future__ import annotations

from pathlib import Path

_IMAGES_DIR = Path(__file__).resolve().parents[2] / "images"

APP_ICON = str(_IMAGES_DIR / "wishlist.png")
ADD_ICON = str(_IMAGES_DIR / "wishlist_add.png")
