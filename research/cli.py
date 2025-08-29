from __future__ import annotations

import argparse
from rich.console import Console
from rich.table import Table

from .db import init_db, upsert_citations
from .pipeline import run_research
from .api import get_top_citations


def main():
    parser = argparse.ArgumentParser(description="Run web research and store citations")
    parser.add_argument("question_id", help="Unique question id")
    parser.add_argument("query", nargs="?", help="Search query (omit when using --show-top)")
    parser.add_argument("--db", dest="db_path", default="citations.db", help="SQLite DB path")
    parser.add_argument("--k", dest="top_k", type=int, default=8, help="Top sources to keep")
    parser.add_argument("--provider", dest="provider", choices=["serpapi", "ddg"], default="serpapi", help="Search provider")
    parser.add_argument("--hl", dest="hl", default="en", help="Interface language (SerpAPI)")
    parser.add_argument("--gl", dest="gl", default="us", help="Geolocation (SerpAPI)")
    parser.add_argument("--cred-threshold", dest="cred_threshold", type=float, default=0.5, help="Minimum credibility")
    parser.add_argument("--show-top", dest="show_top", type=int, default=0, help="Print top N citations and exit")

    args = parser.parse_args()
    console = Console()

    if args.show_top:
        console.rule(f"[bold]Top Citations[/bold] • {args.question_id}")
        rows = get_top_citations(args.db_path, args.question_id, args.show_top)
        table = Table(title="Top Citations")
        table.add_column("Cred", justify="right")
        table.add_column("Title")
        table.add_column("URL")
        for title, url, cred, snippet in rows:
            table.add_row(f"{cred:.2f}", title or "(no title)", url)
        console.print(table)
        console.print(f"[green]{len(rows)} citations from {args.db_path}[/green]")
        return

    if not args.query:
        console.print("[red]Error: query is required unless using --show-top[/red]")
        return

    console.rule(f"[bold]Research[/bold] • {args.query}")
    citations = run_research(
        args.question_id,
        args.query,
        top_k=args.top_k,
        provider=args.provider,
        hl=args.hl,
        gl=args.gl,
        cred_threshold=args.cred_threshold,
    )

    conn = init_db(args.db_path)
    upsert_citations(conn, citations)

    table = Table(title="Saved Citations")
    table.add_column("Cred", justify="right")
    table.add_column("Title")
    table.add_column("URL")

    for c in citations:
        table.add_row(f"{c.credibility:.2f}", c.title or "(no title)", str(c.url))

    console.print(table)
    console.print(f"[green]Saved {len(citations)} citations to {args.db_path}[/green]")


if __name__ == "__main__":
    main()


