from __future__ import annotations

import hashlib
import os
import json
from typing import Optional, Dict, Any


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


# New functions for HTML and text caching
CACHE_DIR = "cache"
HTML_CACHE_SUBDIR = "html"
TEXT_CACHE_SUBDIR = "text"

os.makedirs(os.path.join(CACHE_DIR, HTML_CACHE_SUBDIR), exist_ok=True)
os.makedirs(os.path.join(CACHE_DIR, TEXT_CACHE_SUBDIR), exist_ok=True)


def _get_cache_path(url: str, subdir: str) -> str:
    url_hash = hashlib.sha256(url.encode('utf-8')).hexdigest()
    return os.path.join(CACHE_DIR, subdir, f"{url_hash}.json")


def get_cached_html(url: str) -> Optional[str]:
    cache_path = _get_cache_path(url, HTML_CACHE_SUBDIR)
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("html")
    return None


def save_cached_html(url: str, html_content: str) -> None:
    cache_path = _get_cache_path(url, HTML_CACHE_SUBDIR)
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump({"url": url, "html": html_content}, f, ensure_ascii=False, indent=2)


def get_cached_text(url: str) -> Optional[Dict[str, Any]]:
    cache_path = _get_cache_path(url, TEXT_CACHE_SUBDIR)
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_cached_text(url: str, text: Optional[str], title: Optional[str]) -> None:
    cache_path = _get_cache_path(url, TEXT_CACHE_SUBDIR)
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump({"url": url, "text": text, "title": title}, f, ensure_ascii=False, indent=2)


