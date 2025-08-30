from __future__ import annotations

import sqlite3
import json
from typing import Iterable, List, Optional
from .models import CitationRecord, NormalizedDoc, Section
from pydantic import HttpUrl
from datetime import datetime


SCHEMA = """
CREATE TABLE IF NOT EXISTS citations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  question_id TEXT NOT NULL,
  url TEXT NOT NULL,
  title TEXT,
  author TEXT,
  site_name TEXT,
  published TEXT,
  snippet TEXT,
  credibility REAL NOT NULL,
  status_code INTEGER,
  content_length INTEGER,
  fetched_at TEXT
);

CREATE TABLE IF NOT EXISTS normalized_doc (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  url TEXT UNIQUE NOT NULL,
  title TEXT,
  authors TEXT,
  published_at TEXT,
  site_name TEXT,
  lang TEXT DEFAULT 'en',
  quality TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS section (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  doc_id INTEGER NOT NULL,
  heading TEXT,
  text TEXT NOT NULL,
  page INTEGER,
  ord INTEGER DEFAULT 0,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (doc_id) REFERENCES normalized_doc(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_citations_question ON citations(question_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_citations_unique ON citations(question_id, url);
CREATE INDEX IF NOT EXISTS idx_sections_doc ON section(doc_id);
CREATE INDEX IF NOT EXISTS idx_sections_ord ON section(doc_id, ord);
"""


def init_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.executescript(SCHEMA)
    return conn


def upsert_citations(conn: sqlite3.Connection, records: Iterable[CitationRecord]) -> None:
    conn.executemany(
        """
        INSERT INTO citations (question_id, url, title, author, site_name, published, snippet, credibility, status_code, content_length, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(question_id, url) DO UPDATE SET
          title=excluded.title,
          author=excluded.author,
          site_name=excluded.site_name,
          published=excluded.published,
          snippet=excluded.snippet,
          credibility=excluded.credibility,
          status_code=excluded.status_code,
          content_length=excluded.content_length,
          fetched_at=excluded.fetched_at
        """,
        [
            (
                r.question_id,
                str(r.url),
                r.title,
                r.author,
                r.site_name,
                r.published,
                r.snippet,
                r.credibility,
                r.status_code,
                r.content_length,
                r.fetched_at.isoformat() if r.fetched_at else None,
            )
            for r in records
        ],
    )
    conn.commit()


def upsert_normalized_doc(conn: sqlite3.Connection, ndoc: NormalizedDoc) -> int:
    """Upsert a normalized document and return its ID."""
    cur = conn.cursor()
    authors_str = ",".join(ndoc.authors or []) if ndoc.authors else None
    quality_str = json.dumps(ndoc.quality or {}) if ndoc.quality else None
    
    cur.execute("""
      INSERT INTO normalized_doc(url, title, authors, published_at, site_name, lang, quality)
      VALUES (?, ?, ?, ?, ?, ?, ?)
      ON CONFLICT(url) DO UPDATE SET
        title=excluded.title, authors=excluded.authors, published_at=excluded.published_at,
        site_name=excluded.site_name, lang=excluded.lang, quality=excluded.quality
      """, (str(ndoc.url), ndoc.title, authors_str, ndoc.published_at,
            ndoc.site_name, ndoc.lang, quality_str))
    
    if cur.lastrowid:
        return cur.lastrowid
    
    # Fetch ID when updated
    cur.execute("SELECT id FROM normalized_doc WHERE url=?", (str(ndoc.url),))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        raise ValueError(f"Failed to get ID for document {ndoc.url}")


def insert_sections(conn: sqlite3.Connection, doc_id: int, sections: List[Section]) -> None:
    """Insert sections for a document."""
    cur = conn.cursor()
    cur.executemany("""
      INSERT INTO section(doc_id, heading, text, page, ord) VALUES (?, ?, ?, ?, ?)
    """, [(doc_id, s.heading, s.text, s.page, s.ord) for s in sections])
    conn.commit()


def get_citations_for_question(conn: sqlite3.Connection, question_id: str, limit: int = 8) -> List[CitationRecord]:
    """Retrieves top citations for a given question_id, ordered by credibility."""
    cursor = conn.execute(
        """
        SELECT question_id, url, title, author, site_name, published, snippet, credibility, status_code, content_length, fetched_at
        FROM citations
        WHERE question_id = ?
        ORDER BY credibility DESC
        LIMIT ?
        """,
        (question_id, limit),
    )
    citations: List[CitationRecord] = []
    for row in cursor:
        citations.append(
            CitationRecord(
                question_id=row[0],
                url=HttpUrl(row[1]),
                title=row[2],
                author=row[3],
                site_name=row[4],
                published=row[5],
                snippet=row[6],
                credibility=row[7],
                status_code=row[8],
                content_length=row[9],
                fetched_at=datetime.fromisoformat(row[10]) if row[10] else None,
            )
        )
    return citations


def get_doc_by_url(conn: sqlite3.Connection, url: str) -> Optional[dict]:
    """Get a normalized document by URL."""
    cursor = conn.execute(
        "SELECT id, url, title, authors, published_at, site_name, lang, quality FROM normalized_doc WHERE url = ?",
        (url,)
    )
    row = cursor.fetchone()
    if row:
        return {
            "id": row[0],
            "url": row[1],
            "title": row[2],
            "authors": row[3].split(",") if row[3] else [],
            "published_at": row[4],
            "site_name": row[5],
            "lang": row[6],
            "quality": json.loads(row[7]) if row[7] else {}
        }
    return None


def get_sections_by_doc_id(conn: sqlite3.Connection, doc_id: int) -> List[dict]:
    """Get all sections for a document."""
    cursor = conn.execute(
        "SELECT id, heading, text, page, ord FROM section WHERE doc_id = ? ORDER BY ord",
        (doc_id,)
    )
    sections = []
    for row in cursor:
        sections.append({
            "id": row[0],
            "heading": row[1],
            "text": row[2],
            "page": row[3],
            "ord": row[4]
        })
    return sections


