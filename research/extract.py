from __future__ import annotations

import trafilatura
import requests
from typing import Optional
from .models import PageContent
from .cache import read_cache, write_cache
from .fetcher import fetch_url_with_policies
from .utils import normalize_url


def fetch_and_extract(url: str) -> Optional[PageContent]:
    cached = read_cache(".cache_html", url)
    status_code = None
    fetched_at = None
    content_length = None
    if cached is None:
        fetched = fetch_url_with_policies(url, timeout=20)
        if fetched is None:
            return None
        status_code, html_text, fetched_at, content_length = fetched
        write_cache(".cache_html", url, html_text)
    else:
        html_text = cached

    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        downloaded = html_text
    text = trafilatura.extract(downloaded) or ""
    if not text.strip():
        return None
    meta = trafilatura.extract_metadata(downloaded) or {}
    if hasattr(meta, "as_dict"):
        try:
            meta = meta.as_dict()
        except Exception:
            meta = {}

    return PageContent(
        url=normalize_url(url),
        title=meta.get("title"),
        text=text,
        html=None,
        author=(meta.get("author") if isinstance(meta, dict) else None),
        site_name=(meta.get("sitename") if isinstance(meta, dict) else None),
        published=(meta.get("date") if isinstance(meta, dict) else None),
    )


