import json
from pathlib import Path

import pytest

from wishhelper.errors import LegacyFormatError
from wishhelper.legacy_import import convert

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_convert_v1_positional():
    wl = convert(load_fixture("legacy_v1.json"))
    assert wl.event == "jul"
    assert wl.year == 2026
    assert wl.include_year is True
    assert [w.title for w in wl.wishes] == ["Mekanisk tastatur", "Løbesko"]
    assert wl.wishes[0].price == 899
    assert wl.wishes[0].type == "Elektronik"
    assert wl.wishes[0].note == "Brune switches"
    assert wl.wishes[0].link == ""
    assert wl.wishes[0].promise_ok is False


def test_convert_notes_dict_resolves_note_keys():
    wl = convert(load_fixture("legacy_notes.json"))
    assert wl.event == "fødselsdag"
    assert wl.year == 2025
    assert wl.include_year is False
    assert [w.title for w in wl.wishes] == ["Mekanisk tastatur", "Løbesko"]
    assert wl.wishes[0].note == "Brune switches"
    assert wl.wishes[1].note == "Størrelse 44"
    assert wl.wishes[1].price == 0
    assert wl.wishes[1].type == "Tøj"


def test_convert_unrecognized_shape_raises():
    with pytest.raises(LegacyFormatError):
        convert({"totally": "unexpected"})


def test_convert_wrong_length_list_raises():
    with pytest.raises(LegacyFormatError):
        convert([1, 2, 3])


def test_convert_malformed_notes_table_raises():
    # length-6 shape, but a notes entry is not a 2-item pair
    data = ["header", [["n1", "ok"], ["broken", "extra", "bad"]],
            [[1, "X", 0, "T", "n1"]], "jul", 2026.0, True]
    with pytest.raises(LegacyFormatError):
        convert(data)


def test_convert_non_iterable_wishes_raises():
    # length-4 shape, but wishes slot is not iterable
    with pytest.raises(LegacyFormatError):
        convert([None, "jul", 2026.0, True])
