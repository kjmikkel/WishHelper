"""The Windows taskbar-identity helper must be safe to call on any platform."""

import sys

from wishhelper.__main__ import _APP_USER_MODEL_ID, _set_windows_app_id


def test_set_windows_app_id_never_raises():
    # No-op off Windows; on Windows it sets the AppUserModelID. Either way it
    # must not raise (the taskbar icon is cosmetic and must never block startup).
    _set_windows_app_id()


def test_app_user_model_id_is_dotted():
    # The shell wants a non-empty, dotted CompanyName.Product identifier.
    assert "." in _APP_USER_MODEL_ID
    assert _APP_USER_MODEL_ID.strip() == _APP_USER_MODEL_ID


def test_sets_current_process_id_on_windows():
    if sys.platform != "win32":
        return
    import ctypes
    from ctypes import wintypes

    _set_windows_app_id()
    buf = ctypes.c_wchar_p()
    # GetCurrentProcessExplicitAppUserModelID returns S_OK (0) and fills buf.
    hr = ctypes.windll.shell32.GetCurrentProcessExplicitAppUserModelID(
        ctypes.byref(buf))
    assert hr == 0
    assert buf.value == _APP_USER_MODEL_ID
