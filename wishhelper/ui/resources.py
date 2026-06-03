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
#
# APP_ICON is a multi-size .ico: the Windows shell (taskbar / Alt-Tab) picks the
# size it needs at the current DPI, which a single 32x32 PNG could not satisfy.
APP_ICON = str(_RESOURCES / "wishlist.ico")
ADD_ICON = str(_RESOURCES / "wishlist_add.png")
