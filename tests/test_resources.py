from pathlib import Path

from wishhelper.ui import resources


def test_app_icon_file_exists():
    assert Path(resources.APP_ICON).is_file()


def test_add_icon_file_exists():
    assert Path(resources.ADD_ICON).is_file()
