from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Optional, Tuple
from urllib.parse import urlparse, urlunparse
from urllib import robotparser

import requests

_robots_cache: dict[str, robotparser.RobotFileParser] = {}
_last_hit_ts: dict[str, float] = {}

USER_AGENT = "NotebookLM-Bot/1.0 (+https://example.com/bot)"
MIN_DOMAIN_INTERVAL_S = 1.0


def _robots_for(netloc: str) -> robotparser.RobotFileParser:
    rp = _robots_cache.get(netloc)
    if rp is not None:
        return rp
    robots_url = urlunparse(("https", netloc, "/robots.txt", "", "", ""))
    rp = robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
    except Exception:
        # If robots cannot be fetched, default allow
        rp = robotparser.RobotFileParser()
        rp.parse(["User-agent: *", "Allow: /"])
    _robots_cache[netloc] = rp
    return rp


def _respect_rate_limit(netloc: str) -> None:
    last = _last_hit_ts.get(netloc, 0.0)
    now = time.time()
    delta = now - last
    if delta < MIN_DOMAIN_INTERVAL_S:
        time.sleep(MIN_DOMAIN_INTERVAL_S - delta)
    _last_hit_ts[netloc] = time.time()


def fetch_url_with_policies(url: str, timeout: int = 20) -> Optional[Tuple[int, str, str, int]]:
    """Return (status_code, html_text, fetched_at_iso, content_length) or None if disallowed/failed."""
    parsed = urlparse(url)
    netloc = parsed.netloc
    # robots.txt check
    rp = _robots_for(netloc)
    if not rp.can_fetch(USER_AGENT, url):
        return None

    # simple per-domain rate limiting
    _respect_rate_limit(netloc)

    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, timeout=timeout, headers=headers)
        status = resp.status_code
        text = resp.text
    except Exception:
        return None

    fetched_at = datetime.now(timezone.utc).isoformat()
    content_length = len(text or "")
    return status, text, fetched_at, content_length


