from __future__ import annotations

import trafilatura
import httpx
from typing import Optional, List, Tuple
from datetime import datetime
import fitz  # PyMuPDF
import re

from .models import ExtractedPage, NormalizedDoc, Section
from .cache import get_cached_html, save_cached_html, get_cached_text, save_cached_text
from .fetcher import AsyncHTMLFetcher
from .utils import normalize_url


def extract_pdf(url: str, pdf_bytes: bytes) -> Tuple[ExtractedPage, List[Section]]:
    """Extract text and sections from PDF content."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        sections = []
        full_text = ""
        
        for i, page in enumerate(doc, start=1):
            text = page.get_text()
            if text.strip():
                full_text += text + "\n\n"
                # Split page into sections by paragraphs
                paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
                for j, para in enumerate(paragraphs):
                    sections.append(Section(
                        heading=None,
                        text=para,
                        page=i,
                        ord=len(sections)
                    ))
        
        doc.close()
        
        # Create ExtractedPage
        extracted_page = ExtractedPage(
            url=url,
            title=None,  # PDFs don't have titles in content
            text=full_text,
            author=None,
            site_name=None,
            published=None,
            status_code=200,
            content_length=len(pdf_bytes),
            fetched_at=None
        )
        
        return extracted_page, sections
        
    except Exception as e:
        print(f"Error extracting PDF from {url}: {e}")
        return None, []


def normalize_content(page: ExtractedPage) -> Tuple[NormalizedDoc, List[Section]]:
    """Normalize extracted content into structured document and sections."""
    text = page.text or ""
    
    # Simple section splitting by paragraphs and headers
    # This is a basic implementation - can be improved with ML later
    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 20]  # Reduced threshold
    
    sections = []
    for i, para in enumerate(paragraphs):
        # Try to detect headers (lines that are shorter and end without period)
        is_header = (len(para) < 200 and 
                    not para.endswith('.') and 
                    not para.endswith('!') and 
                    not para.endswith('?') and
                    (para.isupper() or para[0].isupper()))
        
        # If it's a header, create a section with the header text
        if is_header:
            sections.append(Section(
                heading=para,
                text="",  # Header sections have no body text
                page=page.page if hasattr(page, 'page') else None,
                ord=i
            ))
        else:
            # Regular content section
            sections.append(Section(
                heading=None,
                text=para,
                page=page.page if hasattr(page, 'page') else None,
                ord=i
            ))
    
    # If no sections were created, create at least one with the full text
    if not sections and text.strip():
        sections.append(Section(
            heading=None,
            text=text.strip(),
            page=page.page if hasattr(page, 'page') else None,
            ord=0
        ))
    
    # Create normalized document
    ndoc = NormalizedDoc(
        url=page.url,
        title=page.title,
        authors=[page.author] if page.author else [],
        published_at=page.published,
        site_name=page.site_name,
        lang="en",  # Default to English
        quality={
            "length": len(text),
            "sections_count": len(sections),
            "avg_section_length": sum(len(s.text) for s in sections) / max(len(sections), 1)
        }
    )
    
    return ndoc, sections


async def fetch_and_extract(url: str, fetcher: AsyncHTMLFetcher) -> Optional[Tuple[ExtractedPage, List[Section]]]:
    """Fetches a URL, extracts content, and returns normalized document and sections."""
    str_url = str(url)
    
    # Check if it's a PDF by URL or we need to detect content type
    is_pdf = str_url.lower().endswith('.pdf')
    
    if is_pdf:
        # Handle PDF content
        print(f"Processing PDF: {str_url}")
        response = await fetcher.fetch(str_url)
        if not response:
            return None
            
        # Check if response is actually PDF
        content_type = response.headers.get('content-type', '').lower()
        if 'pdf' in content_type or str_url.lower().endswith('.pdf'):
            pdf_bytes = response.content
            extracted_page, sections = extract_pdf(str_url, pdf_bytes)
            if extracted_page:
                return extracted_page, sections
        else:
            print(f"URL suggests PDF but content-type is: {content_type}")
    
    # Handle HTML content (existing logic)
    cached_text_data = get_cached_text(str_url)
    if cached_text_data:
        print(f"Using cached text for {str_url}")
        # Reconstruct ExtractedPage from cache
        extracted_page = ExtractedPage(
            url=url,
            text=cached_text_data.get("text"),
            title=cached_text_data.get("title"),
            status_code=None,
            content_length=None,
            fetched_at=datetime.now()
        )
        # Re-normalize to get sections
        ndoc, sections = normalize_content(extracted_page)
        return extracted_page, sections

    # Try to get HTML from cache first
    html_content = get_cached_html(str_url)
    response_status_code: Optional[int] = None
    response_content_length: Optional[int] = None
    fetched_at = datetime.now()

    if not html_content:
        # If not in cache, fetch it
        print(f"Fetching {str_url}...")
        response = await fetcher.fetch(str_url)
        if not response:
            return None
        html_content = response.text
        response_status_code = response.status_code
        response_content_length = len(response.content)
        save_cached_html(str_url, html_content)

    # Extract text and metadata using trafilatura
    extracted_text = trafilatura.extract(html_content, include_comments=False, include_tables=False, no_fallback=True)
    
    if not extracted_text:
        return None
    
    # Get title from HTML or use URL as fallback
    title = None
    if extracted_text:
        lines = extracted_text.split('\n')
        if lines:
            title = lines[0].strip()
    
    # Save extracted text to cache
    save_cached_text(str_url, text=extracted_text, title=title)

    # Create ExtractedPage
    extracted_page = ExtractedPage(
        url=url,
        title=title,
        text=extracted_text,
        status_code=response_status_code,
        content_length=response_content_length,
        fetched_at=fetched_at
    )
    
    # Normalize content into sections
    ndoc, sections = normalize_content(extracted_page)
    
    return extracted_page, sections


