from __future__ import annotations

from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Literal
from datetime import datetime


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
    fetched_at: Optional[datetime] = None


class NormalizedDoc(BaseModel):
    url: HttpUrl
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    published_at: Optional[str] = None
    site_name: Optional[str] = None
    lang: str = "en"
    quality: Optional[dict] = None


class Section(BaseModel):
    doc_id: Optional[int] = None
    heading: Optional[str] = None
    text: str
    page: Optional[int] = None
    ord: int = 0


class ExtractedPage(BaseModel):
    url: HttpUrl
    title: Optional[str] = None
    text: Optional[str] = None
    author: Optional[str] = None
    site_name: Optional[str] = None
    published: Optional[str] = None
    status_code: Optional[int] = None
    content_length: Optional[int] = None
    fetched_at: Optional[datetime] = None


# ----------------------------
# Phase A: Content Models
# ----------------------------

class Beat(BaseModel):
    title: str
    learning_goal: Optional[str] = None
    key_points: List[str] = []
    citations: List[HttpUrl] = []
    estimated_time_s: Optional[float] = Field(default=None, ge=5.0, le=60.0)
    planned_slides: Optional[int] = Field(default=None, ge=1, le=8)


class OutlineModel(BaseModel):
    title: Optional[str] = None
    beats: List[Beat]


class ScriptSection(BaseModel):
    beat_title: str
    narration: str
    citations: List[HttpUrl] = []
    estimated_time_s: Optional[float] = Field(default=None, ge=5.0, le=60.0)


class ScriptModel(BaseModel):
    title: Optional[str] = None
    sections: List[ScriptSection]
    total_time_s: Optional[float] = Field(default=None, ge=60.0, le=600.0)


class VisualElement(BaseModel):
    type: Literal["formula", "diagram", "chart", "image", "callout"]
    content: Optional[str] = None
    # Minimal diagram DSL support (optional fields)
    nodes: Optional[List[dict]] = None
    edges: Optional[List[dict]] = None


class SlideSpec(BaseModel):
    title: str
    content: Optional[str] = None
    bullets: Optional[List[str]] = None
    visual_elements: Optional[List[VisualElement]] = None
    duration: float = Field(default=6.0, ge=3.0, le=12.0)
    type: Literal["title", "concept", "example", "formula", "summary"] = "concept"
    citations: List[HttpUrl] = []
    build_sequence: Optional[List[int]] = None
    color_scheme: Optional[str] = None


class SlidesModel(BaseModel):
    slides: List[SlideSpec]

