"""Plain data types. No I/O, no scoring, so both are easy to test."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field, asdict
from datetime import date
from typing import Optional


# --------------------------------------------------------------------------- #
# text helpers, shared by scoring and by the keyword matcher
# --------------------------------------------------------------------------- #

_PUNCT = re.compile(r"[^a-z0-9+&/. ]+")
_SPACE = re.compile(r"\s+")


def fold(text: str) -> str:
    """Lowercase, strip accents, drop punctuation, collapse whitespace.

    ``Toitū Envirocare`` and ``Toitu Envirocare`` must match the same keyword,
    which is exactly the bug that broke the registry ids earlier.
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = text.replace("\u2019", "'").replace("\u2013", "-").replace("\u2014", "-")
    text = _PUNCT.sub(" ", text)
    return _SPACE.sub(" ", text).strip()


def phrase_re(pattern: str) -> re.Pattern:
    """Word-boundary regex for a folded keyword phrase."""
    words = [re.escape(w) for w in phrase_tokens(pattern)]
    body = r"[\s\-/]+".join(words) if words else r"(?!)"
    return re.compile(rf"(?<![a-z0-9]){body}(?![a-z0-9])")


def phrase_tokens(phrase: str) -> list[str]:
    return [w for w in fold(phrase).split(" ") if w]


# --------------------------------------------------------------------------- #
# seniority
# --------------------------------------------------------------------------- #

LEVELS = ["intern", "graduate", "mid", "senior", "exec"]
LEVEL_RANK = {name: i for i, name in enumerate(LEVELS)}


@dataclass
class Seniority:
    level: str = "unspecified"   # one of LEVELS or "unspecified"
    years: Optional[int] = None  # minimum years requested, when stated
    evidence: str = ""           # the phrase that decided it, for the report

    @property
    def rank(self) -> int:
        if self.level == "unspecified":
            return LEVEL_RANK["graduate"]
        return LEVEL_RANK[self.level]


# --------------------------------------------------------------------------- #
# a posting, as an adapter produced it
# --------------------------------------------------------------------------- #

@dataclass
class Posting:
    url: str
    title: str
    employer: str = ""
    country: str = ""            # ISO-ish: BE, LU, CH, AU, NZ, AE, or ""
    location: str = ""
    language: str = ""           # en / fr / nl / de / ""
    salary: str = ""
    posted: Optional[date] = None
    deadline: Optional[date] = None
    description: str = ""
    tags: list[str] = field(default_factory=list)

    # provenance
    source_id: str = ""
    source_name: str = ""
    adapter: str = ""
    raw_title: str = ""

    # computed later
    seniority: Seniority = field(default_factory=Seniority)
    fingerprint: str = ""

    def text(self, limit: int = 6000) -> str:
        """Title-present-first text blob for keyword matching."""
        head = " ".join([self.title, " ".join(self.tags)])
        body = (self.description or "")[:limit]
        return f"{head} {head} {body}"  # title twice: it counts more

    def as_dict(self) -> dict:
        d = asdict(self)
        d["posted"] = self.posted.isoformat() if self.posted else None
        d["deadline"] = self.deadline.isoformat() if self.deadline else None
        return d


# --------------------------------------------------------------------------- #
# a registry row, reduced to what the crawler needs
# --------------------------------------------------------------------------- #

@dataclass
class Source:
    id: str
    name: str
    category: str
    country: str
    url: str
    listing_url: str
    language: str
    sector: str
    size: str
    access: str
    fit: str
    priority: int
    verified: str
    notes: str

    @property
    def target(self) -> str:
        """The URL actually fetched: the listing page when we have one."""
        return self.listing_url or self.url

    @property
    def is_employer(self) -> bool:
        return self.category in {"company", "federation", "big4"}


@dataclass
class Keyword:
    theme: str
    text: str
    language: str
    weight: int      # 3 core, 2 likely, 1 adjacent
    source: str

    @property
    def pattern(self) -> re.Pattern:
        return phrase_re(self.text)


# --------------------------------------------------------------------------- #
# scoring output
# --------------------------------------------------------------------------- #

@dataclass
class Breakdown:
    """One scored posting. Every field is an integer number of points.

    The six parts sum to ``total``; ``penalties`` is already folded in, and is
    kept separately only so the report can show a strikethrough.
    """

    keyword: int = 0
    seniority: int = 0
    geography: int = 0
    language: int = 0
    employer: int = 0
    freshness: int = 0
    penalties: int = 0
    total: int = 0
    band: str = ""
    matched: list[dict] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    excluded: bool = False
    exclude_reason: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def parts(self) -> list[tuple[str, int, int]]:
        """(label, points, maximum) in report order."""
        return [
            ("Keyword relevance", self.keyword, 35),
            ("Seniority fit", self.seniority, 20),
            ("Location", self.geography, 15),
            ("Employer type", self.employer, 12),
            ("Language", self.language, 10),
            ("Freshness", self.freshness, 8),
        ]
