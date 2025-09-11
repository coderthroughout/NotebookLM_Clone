from __future__ import annotations

import requests
from typing import List
from urllib.parse import urlencode

from .models import SearchResult
from .utils import normalize_url
from .config import config


def duckduckgo_search(query: str, num_results: int = 10) -> List[SearchResult]:
    params = {
        "q": query,
        "kl": "us-en",
        "kp": -2,
        "no_redirect": 1,
        "no_html": 1,
        "format": "json",
    }
    # Use HTML fallback because JSON API is limited; parse links from HTML
    url = f"https://duckduckgo.com/html/?{urlencode({'q': query})}"
    resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()

    # Simple extraction to avoid heavy deps; prefer bs4 if present
    try:
        from bs4 import BeautifulSoup  # type: ignore
    except Exception:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    results: List[SearchResult] = []
    for rank, a in enumerate(soup.select("a.result__a"), start=1):
        href = a.get("href")
        title = a.get_text(strip=True)
        if not href or not title:
            continue
        # DuckDuckGo uses external link redirects sometimes; keep as-is
        try:
            results.append(SearchResult(title=title, url=normalize_url(href), rank=rank))
        except Exception:
            continue
        if len(results) >= num_results:
            break
    return results


def serpapi_search(query: str, num_results: int = 10, hl: str = "en", gl: str = "us") -> List[SearchResult]:
    from .cache_manager import cache_manager
    
    # Check cache first
    cached_result = cache_manager.get_research_cache(query, "serpapi")
    if cached_result:
        print(f"📋 Using cached SerpAPI results for: {query}")
        return [SearchResult(**item) for item in cached_result]
    
    key = config.SERPAPI_API_KEY
    if not key:
        print("❌ SERPAPI_API_KEY not found in configuration")
        return []
    
    print(f"🔍 Using SerpAPI key: {key[:8]}...")
    
    params = {
        "engine": "google",
        "q": query,
        "num": min(num_results, 10),
        "api_key": key,
        "hl": hl,
        "gl": gl,
    }
    
    print(f"🌐 Searching for: {query}")
    r = requests.get("https://serpapi.com/search.json", params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    organic = data.get("organic_results", []) or []
    results: List[SearchResult] = []
    for idx, item in enumerate(organic[:num_results], start=1):
        link = item.get("link") or item.get("formattedUrl")
        title = item.get("title") or item.get("snippet")
        if not link or not title:
            continue
        try:
            results.append(SearchResult(title=title, url=normalize_url(link), rank=idx))
        except Exception:
            continue
    
    # Cache the results
    cache_data = [{"title": r.title, "url": str(r.url), "rank": r.rank} for r in results]
    cache_manager.set_research_cache(query, cache_data, "serpapi")
    
    print(f"✅ Found {len(results)} results from SerpAPI")
    return results


