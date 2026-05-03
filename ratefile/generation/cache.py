from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable, TypeVar

T = TypeVar("T")


def ensure_cache_dir(path: str | Path) -> Path:
    # API discovery stores normalized JSON payloads on disk so repeated runs can
    # reuse LocalCallingGuide responses instead of re-fetching every prefix/LATA.
    cache_dir = Path(path)
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def is_fresh(path: Path, max_age_days: int) -> bool:
    if not path.exists():
        return False
    return (time.time() - path.stat().st_mtime) <= max_age_days * 86400


def load_cached_json(path: Path, max_age_days: int) -> dict | list | None:
    if not is_fresh(path, max_age_days):
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_cached_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def get_or_fetch_json(
    cache_dir: str | Path,
    cache_name: str,
    max_age_days: int,
    fetcher: Callable[[], dict | list],
) -> dict | list:
    cache_path = ensure_cache_dir(cache_dir) / cache_name
    cached = load_cached_json(cache_path, max_age_days)
    if cached is not None:
        return cached
    payload = fetcher()
    save_cached_json(cache_path, payload)
    return payload
