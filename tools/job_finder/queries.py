"""Saved searches.

The registry answers "which sites exist". A query answers "which search to run
on that site", and carries the context the page itself does not state: which
country the postings belong to, what language they are in, which sector the
employer sits in.

Without this, a crawl of a board with filters could only guess, and a posting
found under /jobs/energy inherited whatever the registry row said, which is
nothing.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .model import Source


@dataclass
class Query:
    id: str
    url: str
    label: str = ""
    board: str = ""
    country: str = ""
    language: str = ""
    sector: str = ""
    size: str = ""
    why: str = ""
    source_id: str = ""

    def as_source(self) -> Source:
        """A synthetic registry row, so the crawler needs no special case."""
        return Source(
            id=self.source_id or f"query-{self.id}",
            name=self.label or self.board or self.id,
            category="job_board",
            country=(self.country or "").upper(),
            url=self.url,
            listing_url=self.url,
            language=(self.language or "")[:2],
            sector=self.sector,
            size=self.size,
            access="open",
            fit="high",
            priority=1,
            verified="yes",
            notes=self.why,
        )


def load(path: Path | str) -> list[Query]:
    path = Path(path)
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    out: list[Query] = []
    for raw in data.get("queries", []):
        if not raw.get("url"):
            continue
        out.append(Query(
            id=raw.get("id") or raw["url"],
            url=raw["url"],
            label=raw.get("label", ""),
            board=raw.get("board", ""),
            country=raw.get("country", ""),
            language=raw.get("language", ""),
            sector=raw.get("sector", ""),
            size=raw.get("size", ""),
            why=raw.get("why", ""),
            source_id=raw.get("source_id", ""),
        ))
    return out


def select(queries: list[Query], wanted: list[str] | None) -> list[Query]:
    """Filter by id, board or a label substring. No arguments means all."""
    if not wanted:
        return queries
    out, missing = [], []
    for name in wanted:
        key = name.strip().lower()
        hits = [q for q in queries
                if key in {q.id.lower(), q.board.lower()}
                or key in q.label.lower() or key in q.id.lower()]
        if not hits:
            missing.append(name)
        out.extend(h for h in hits if h not in out)
    if missing:
        known = ", ".join(q.id for q in queries)
        raise SystemExit(f"unknown query: {', '.join(missing)}\nknown: {known}")
    return out
