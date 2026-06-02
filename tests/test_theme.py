import pytest

from wishhelper.ui.theme import _effective_theme


@pytest.mark.parametrize(
    "theme, os_is_dark, expected",
    [
        ("dark", False, "dark"),
        ("dark", True, "dark"),
        ("light", False, "light"),
        ("light", True, "light"),
        ("system", True, "dark"),   # the bug: system must follow the OS
        ("system", False, "light"),
    ],
)
def test_effective_theme(theme, os_is_dark, expected):
    assert _effective_theme(theme, os_is_dark) == expected
