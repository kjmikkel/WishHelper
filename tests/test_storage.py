import json

import pytest

from wishhelper.errors import StorageError
from wishhelper.models import Wish, WishList
from wishhelper.storage import FORMAT_VERSION, load, save, to_dict


def sample_wishlist():
    return WishList(
        event="jul",
        year=2026,
        include_year=True,
        author="Mikkel Kjær Jensen",
        currency="kr.",
        wishes=[
            Wish(title="Mekanisk tastatur", price=899, type="Elektronik",
                 note="Brune switches.", link="https://example.com/kb"),
            Wish(title="Løbesko", price=0, type="Tøj",
                 promise_ok=True, promise_reason="udkommer i marts 2027"),
        ],
    )


def test_to_dict_has_version_and_named_fields():
    data = to_dict(sample_wishlist())
    assert data["format_version"] == FORMAT_VERSION
    assert data["event"] == "jul"
    assert data["wishes"][0]["title"] == "Mekanisk tastatur"
    assert data["wishes"][1]["promise_ok"] is True


def test_save_then_load_round_trips(tmp_path):
    original = sample_wishlist()
    path = tmp_path / "wishes.json"
    save(original, str(path))
    loaded = load(str(path))
    assert loaded == original


def test_save_writes_utf8_json(tmp_path):
    path = tmp_path / "wishes.json"
    save(sample_wishlist(), str(path))
    raw = path.read_text(encoding="utf-8")
    assert "Mikkel Kjær Jensen" in raw
    parsed = json.loads(raw)
    assert parsed["format_version"] == FORMAT_VERSION


def test_load_missing_file_raises_storage_error(tmp_path):
    with pytest.raises(StorageError):
        load(str(tmp_path / "does-not-exist.json"))


def test_load_invalid_json_raises_storage_error(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(StorageError):
        load(str(path))


def test_load_structurally_invalid_wish_raises_storage_error(tmp_path):
    path = tmp_path / "bad_shape.json"
    path.write_text(
        '{"format_version": 2, "wishes": [{"bogus_field": "x"}]}',
        encoding="utf-8",
    )
    with pytest.raises(StorageError):
        load(str(path))
