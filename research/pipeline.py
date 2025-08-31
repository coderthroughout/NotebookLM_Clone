import asyncio
from typing import List, Tuple
from pydantic import HttpUrl

from .models import SearchResult, ExtractedPage, CitationRecord, NormalizedDoc, Section
from .search import serpapi_search, duckduckgo_search
from .extract import fetch_and_extract, normalize_content
from .validate import score_source
from .fetcher import AsyncHTMLFetcher
from .db import upsert_normalized_doc, insert_sections


async def run_research(
    question_id: str,
    query: str,
    top_k: int = 8,
    provider: str = "serpapi",
    hl: str = "en",
    gl: str = "us",
    cred_threshold: float = 0.5,
    db_conn=None,
) -> List[CitationRecord]:
    """Runs the full research pipeline with normalized document storage."""
    
    # Get search results based on provider
    if provider == "serpapi":
        search_results = serpapi_search(query, num_results=top_k * 2, hl=hl, gl=gl)
        if not search_results:
            search_results = duckduckgo_search(query, num_results=top_k * 2)
    else:
        search_results = duckduckgo_search(query, num_results=top_k * 2)

    citations: List[CitationRecord] = []
    
    async with AsyncHTMLFetcher() as fetcher:
        for r in search_results:
            # Fetch and extract content
            result = await fetch_and_extract(r.url, fetcher)
            if not result:
                continue
                
            extracted_page, sections = result
            
            if not extracted_page.text or len(extracted_page.text.strip()) < 200:
                continue
                
            # Score the source
            cred = score_source(extracted_page)
            if cred.score < cred_threshold:
                continue
                
            # Normalize content into structured document
            ndoc, normalized_sections = normalize_content(extracted_page)
            
            # Store normalized document and sections in database if connection provided
            if db_conn:
                try:
                    doc_id = upsert_normalized_doc(db_conn, ndoc)
                    insert_sections(db_conn, doc_id, normalized_sections)
                except Exception as e:
                    print(f"Failed to store normalized document for {extracted_page.url}: {e}")
            
            # Create citation record
            snippet = extracted_page.text[:300].replace("\n", " ").strip()
            citations.append(
                CitationRecord(
                    question_id=question_id,
                    url=extracted_page.url,
                    title=extracted_page.title,
                    author=extracted_page.author,
                    site_name=extracted_page.site_name,
                    published=extracted_page.published,
                    snippet=snippet,
                    credibility=cred.score,
                    status_code=extracted_page.status_code,
                    content_length=extracted_page.content_length,
                    fetched_at=extracted_page.fetched_at,
                )
            )
            
            if len(citations) >= top_k:
                break
    
    # Sort by credibility and return top_k
    citations.sort(key=lambda c: c.credibility, reverse=True)
    return citations[:top_k]


def run_research_sync(
    question_id: str,
    query: str,
    top_k: int = 8,
    provider: str = "serpapi",
    hl: str = "en",
    gl: str = "us",
    cred_threshold: float = 0.5,
    db_conn=None,
) -> List[CitationRecord]:
    """Synchronous wrapper for the async research pipeline."""
    return asyncio.run(run_research(
        question_id, query, top_k, provider, hl, gl, cred_threshold, db_conn
    ))


