"""Locate bundled image resources (window/app icons).

Icons live inside the package at ``wishhelper/resources/*.png`` and are resolved
via :mod:`importlib.resources`, so they are found regardless of the current
working directory and ship correctly in a wheel / ``pip install``. Importing
this module does NOT import Qt.
"""

from __future__ import annotations

from importlib.resources import files

_RESOURCES = files("wishhelper.resources")

# Concrete filesystem paths (QIcon needs a path string). This assumes a normal
# on-disk install; a zip-imported package would require importlib.resources
# .as_file(), which WishHelper does not target.
APP_ICON = str(_RESOURCES / "wishlist.png")
ADD_ICON = str(_RESOURCES / "wishlist_add.png")
