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
