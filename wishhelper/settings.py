"""Persisted application settings as JSON. Qt-free.

The default location is the per-user config directory, e.g.
%APPDATA%\\WishHelper\\settings.json on Windows. Paths are injectable so the
logic is testable without touching the real user profile.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, fields

from wishhelper.errors import SettingsError


@dataclass
class Settings:
    author: str = ""
    currency: str = "kr."
    language: str = "da"
    theme: str = "system"  # "light" | "dark" | "system"
    last_load_dir: str = ""
    last_save_dir: str = ""
    last_export_dir: str = ""


def default_settings_path() -> str:
    """Return the per-user settings.json path for the current OS."""
    base = os.environ.get("APPDATA") or os.path.expanduser("~/.config")
    return os.path.join(base, "WishHelper", "settings.json")


def load_settings(path: str) -> Settings:
    """Load settings from `path`; return defaults if the file is absent."""
    if not os.path.exists(path):
        return Settings()
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        raise SettingsError(f"Could not read settings: {path}") from exc

    known = {f.name for f in fields(Settings)}
    filtered = {k: v for k, v in data.items() if k in known}
    return Settings(**filtered)


def save_settings(settings: Settings, path: str) -> None:
    """Persist settings to `path`, creating parent directories as needed."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(asdict(settings), fh, ensure_ascii=False, indent=2)
    except OSError as exc:
        raise SettingsError(f"Could not write settings: {path}") from exc
