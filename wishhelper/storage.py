"""Persistence for WishList documents. v2 JSON format. Qt-free."""

from __future__ import annotations

import json
from dataclasses import asdict

from wishhelper import legacy_import
from wishhelper.errors import StorageError
from wishhelper.models import Wish, WishList

FORMAT_VERSION = 2


def to_dict(wishlist: WishList) -> dict:
    """Serialize a WishList to a v2-format dict."""
    data = asdict(wishlist)
    data["format_version"] = FORMAT_VERSION
    return data


def from_dict(data: dict) -> WishList:
    """Build a WishList from a v2-format dict."""
    try:
        wishes = [Wish(**w) for w in data.get("wishes", [])]
    except (TypeError, KeyError) as exc:
        raise StorageError(f"Malformed wish entry: {exc}") from exc
    return WishList(
        event=data.get("event", ""),
        year=data.get("year", 0),
        include_year=data.get("include_year", True),
        author=data.get("author", ""),
        currency=data.get("currency", "kr."),
        wishes=wishes,
    )


def save(wishlist: WishList, path: str) -> None:
    """Write a WishList to `path` as UTF-8 v2 JSON."""
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(to_dict(wishlist), fh, ensure_ascii=False, indent=2)
    except OSError as exc:
        raise StorageError(f"Could not write file: {path}") from exc


def load(path: str) -> WishList:
    """Read a WishList from `path`, converting legacy formats if needed."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw = fh.read()
    except OSError as exc:
        raise StorageError(f"Could not read file: {path}") from exc

    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise StorageError(f"Could not parse JSON: {path}") from exc

    if isinstance(data, dict) and "format_version" in data:
        return from_dict(data)
    return legacy_import.convert(data)
