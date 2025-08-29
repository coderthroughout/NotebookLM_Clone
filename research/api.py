from __future__ import annotations

import sqlite3
from typing import List, Tuple


def get_top_citations(db_path: str, question_id: str, limit: int = 8) -> List[Tuple[str, str, float, str]]:
    """Return list of (title, url, credibility, snippet) sorted by credibility desc."""
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute(
            """
            SELECT title, url, credibility, snippet
            FROM citations
            WHERE question_id = ?
            ORDER BY credibility DESC
            LIMIT ?
            """,
            (question_id, limit),
        )
        rows = cur.fetchall()
        return [(r[0] or "", r[1], float(r[2] or 0.0), r[3] or "") for r in rows]
    finally:
        conn.close()


