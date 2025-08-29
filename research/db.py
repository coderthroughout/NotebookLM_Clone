from __future__ import annotations

import sqlite3
from typing import Iterable
from .models import CitationRecord


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

CREATE INDEX IF NOT EXISTS idx_citations_question ON citations(question_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_citations_unique ON citations(question_id, url);
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
                r.fetched_at,
            )
            for r in records
        ],
    )
    conn.commit()


