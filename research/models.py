from __future__ import annotations

from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List


class SearchResult(BaseModel):
    title: str
    url: HttpUrl
    snippet: Optional[str] = None
    rank: int


class PageContent(BaseModel):
    url: HttpUrl
    title: Optional[str] = None
    text: str
    html: Optional[str] = None
    author: Optional[str] = None
    site_name: Optional[str] = None
    published: Optional[str] = None


class SourceCredibility(BaseModel):
    url: HttpUrl
    domain: str
    score: float = Field(ge=0.0, le=1.0)
    reasons: List[str] = []


class CitationRecord(BaseModel):
    question_id: str
    url: HttpUrl
    title: Optional[str] = None
    author: Optional[str] = None
    site_name: Optional[str] = None
    published: Optional[str] = None
    snippet: Optional[str] = None
    credibility: float = Field(ge=0.0, le=1.0)
    status_code: Optional[int] = None
    content_length: Optional[int] = None
    fetched_at: Optional[str] = None


