from __future__ import annotations

import hashlib
import os
from typing import Optional


def _hash_key(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def get_cache_path(base_dir: str, key: str, ext: str = ".txt") -> str:
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, _hash_key(key) + ext)


def read_cache(base_dir: str, key: str) -> Optional[str]:
    path = get_cache_path(base_dir, key)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return None
    return None


def write_cache(base_dir: str, key: str, value: str) -> None:
    path = get_cache_path(base_dir, key)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(value)
    except Exception:
        pass


