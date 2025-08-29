from __future__ import annotations

from typing import List

from .models import CitationRecord
from .search import duckduckgo_search, serpapi_search
from .extract import fetch_and_extract
from .validate import score_source


def run_research(question_id: str, query: str, top_k: int = 8, provider: str = "serpapi", hl: str = "en", gl: str = "us", cred_threshold: float = 0.5) -> List[CitationRecord]:
    if provider == "serpapi":
        results = serpapi_search(query, num_results=top_k * 2, hl=hl, gl=gl)
        if not results:
            results = duckduckgo_search(query, num_results=top_k * 2)
    else:
        results = duckduckgo_search(query, num_results=top_k * 2)
    pages = []
    for r in results[: top_k * 2]:
        page = fetch_and_extract(str(r.url))
        if not page or not page.text.strip():
            continue
        cred = score_source(page)
        if cred.score < cred_threshold:
            continue
        pages.append((page, cred))
        if len(pages) >= top_k:
            break

    citations: List[CitationRecord] = []
    for page, cred in pages:
        snippet = page.text[:300].replace("\n", " ").strip()
        citations.append(
            CitationRecord(
                question_id=question_id,
                url=page.url,
                title=page.title,
                author=page.author,
                site_name=page.site_name,
                published=page.published,
                snippet=snippet,
                credibility=cred.score,
                # metadata currently only available if not cached; safe to leave None when cached
                status_code=None,
                content_length=len(page.text.encode("utf-8")) if page.text else None,
                fetched_at=None,
            )
        )
    return citations


