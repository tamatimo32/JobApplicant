"""Read the two halves of the registry CSV: places to look, and keywords.

The CSV is the contract with ``tools/build_job_sources_csv.py``. Keep them in
step: if a column is renamed there, this module fails loudly rather than
silently scoring everything zero.
"""

from __future__ import annotations

import csv
from pathlib import Path

from .model import Keyword, Source

REQUIRED = ("id", "category", "country", "name", "url", "access")


class RegistryError(ValueError):
    pass


def _int(value: str, default: int = 3) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def load(path: Path | str) -> tuple[list[Source], list[Keyword]]:
    path = Path(path)
    if not path.exists():
        raise RegistryError(
            f"registry not found: {path}\n"
            "build it with:  python3 tools/build_job_sources_csv.py")
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            raise RegistryError(f"registry is missing columns: {missing}")
        rows = list(reader)

    sources: list[Source] = []
    keywords: list[Keyword] = []
    for r in rows:
        if r.get("category") == "keyword":
            kw = _keyword(r)
            if kw:
                keywords.append(kw)
            continue
        sources.append(Source(
            id=r.get("id", "").strip(),
            name=r.get("name", "").strip(),
            category=r.get("category", "").strip(),
            country=r.get("country", "").strip().upper().replace("ANY", ""),
            url=r.get("url", "").strip(),
            listing_url=(r.get("listing_url") or "").strip(),
            language=(r.get("language") or "").strip().lower()[:2],
            sector=(r.get("sector") or "").strip(),
            size=(r.get("size") or "").strip(),
            access=(r.get("access") or "open").strip(),
            fit=(r.get("fit") or "").strip(),
            priority=_int(r.get("priority"), 3),
            verified=(r.get("verified") or "").strip(),
            notes=(r.get("notes") or "").strip(),
        ))
    return sources, keywords


def _keyword(row: dict) -> Keyword | None:
    text = (row.get("name") or "").strip()
    if not text:
        return None
    notes = row.get("notes") or ""
    theme, weight = "", 2
    for part in notes.split(";"):
        part = part.strip()
        if part.startswith("theme="):
            theme = part[6:]
        elif part.startswith("weight="):
            weight = _int(part[7:], 2)
    if not theme:
        theme = (row.get("what_it_lists") or "").replace("theme:", "").strip()
    return Keyword(
        theme=theme or "general",
        text=text,
        language=(row.get("language") or "").strip().lower()[:2],
        weight=weight,
        source=(row.get("fit") or ""),
    )


# --------------------------------------------------------------------------- #
# query selection: "a run" is a subset of the registry
# --------------------------------------------------------------------------- #

def select(sources: list[Source], *, countries: list[str] | None = None,
           categories: list[str] | None = None, priorities: list[int] | None = None,
           names: list[str] | None = None, max_countries: list[str] | None = None,
           include_restricted: bool = False) -> list[Source]:
    out = []
    for s in sources:
        if not include_restricted and s.access in {"tos_restricted", "login_required"}:
            continue
        if countries and s.country not in countries and s.category != "remote":
            continue
        if categories and s.category not in categories:
            continue
        if priorities and s.priority not in priorities:
            continue
        if names and not any(n.lower() in s.name.lower() for n in names):
            continue
        out.append(s)
    out.sort(key=lambda s: (s.priority, -s.fit_rank, s.country, s.name))
    return out


def fit_rank(source: Source) -> int:
    return {"high": 3, "medium": 2, "low": 1}.get(source.fit, 2)


# make the property available without importing a function name into callers
Source.fit_rank = property(lambda self: {"high": 3, "medium": 2, "low": 1}.get(self.fit, 2))
