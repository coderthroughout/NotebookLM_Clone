from __future__ import annotations

import time
import asyncio
from datetime import datetime, timezone
from typing import Optional, Tuple
from urllib.parse import urlparse, urlunparse
from urllib import robotparser

import requests
import httpx
from robotexclusionrulesparser import RobotExclusionRulesParser


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


class RobotsTxtCache:
    """Caches robots.txt rules for domains."""
    def __init__(self):
        self._cache: dict[str, RobotExclusionRulesParser] = {}
        self._last_fetch: dict[str, datetime] = {}
        self._fetch_interval = 3600  # Re-fetch robots.txt every hour

    async def _fetch_robots_txt(self, domain: str) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"http://{domain}/robots.txt")
                response.raise_for_status()
                return response.text
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return ""  # No robots.txt
            print(f"Error fetching robots.txt for {domain}: {e}")
            return None
        except httpx.RequestError as e:
            print(f"Network error fetching robots.txt for {domain}: {e}")
            return None

    async def get_parser(self, url: str) -> Optional[RobotExclusionRulesParser]:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        if not domain:
            return None

        now = datetime.now()
        if domain not in self._cache or (now - self._last_fetch.get(domain, datetime.min)).seconds > self._fetch_interval:
            robots_txt_content = await self._fetch_robots_txt(domain)
            if robots_txt_content is not None:
                parser = RobotExclusionRulesParser()
                parser.parse(robots_txt_content)
                self._cache[domain] = parser
                self._last_fetch[domain] = now
            else:
                return None  # Failed to fetch robots.txt

        return self._cache.get(domain)


class AsyncHTMLFetcher:
    """Fetches HTML content with robots.txt respect and per-domain rate limiting."""
    def __init__(self, user_agent: str = "Mozilla/5.0 (compatible; NotebookLM/1.0)", delay: float = 0.5):
        self.client = httpx.AsyncClient(headers={"User-Agent": user_agent}, follow_redirects=True, timeout=10)
        self.robots_cache = RobotsTxtCache()
        self.delay = delay  # Minimum delay between requests to the same domain
        self._last_request_time: dict[str, float] = {}
        self._domain_locks: dict[str, asyncio.Lock] = {}

    async def fetch(self, url: str) -> Optional[httpx.Response]:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        if not domain:
            return None

        # Get or create domain lock
        if domain not in self._domain_locks:
            self._domain_locks[domain] = asyncio.Lock()

        async with self._domain_locks[domain]:
            # Check robots.txt
            robots_parser = await self.robots_cache.get_parser(url)
            if robots_parser and not robots_parser.is_url_allowed(url, self.client.headers["User-Agent"]):
                print(f"Blocked by robots.txt: {url}")
                return None

            # Enforce rate limit
            now = time.monotonic()
            last_request = self._last_request_time.get(domain, 0)
            elapsed = now - last_request
            if elapsed < self.delay:
                await asyncio.sleep(self.delay - elapsed)

            try:
                response = await self.client.get(url)
                response.raise_for_status()
                self._last_request_time[domain] = time.monotonic()
                return response
            except httpx.HTTPStatusError as e:
                print(f"HTTP error fetching {url}: {e.response.status_code} - {e.response.text[:100]}")
                return None
            except httpx.RequestError as e:
                print(f"Network error fetching {url}: {e}")
                return None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()


