"""Turn a posting into a number out of 100, with the arithmetic exposed.

Every point awarded here is recorded in ``Breakdown.reasons`` so the HTML
report can show the calculation rather than asking the reader to trust it.
"""

from __future__ import annotations

import re
from datetime import date

from . import config as C
from .model import Breakdown, Keyword, Posting, Source, fold
from .seniority import detect

# --------------------------------------------------------------------------- #
# keyword matching, built once per run
# --------------------------------------------------------------------------- #

class KeywordIndex:
    """All keyword rows, compiled, split by weight for fast matching."""

    def __init__(self, keywords: list[Keyword]):
        self.by_weight: dict[int, list[tuple[Keyword, re.Pattern]]] = {
            3: [], 2: [], 1: []}
        seen: set[tuple[str, int]] = set()
        for kw in keywords:
            key = (fold(kw.text), kw.weight)
            if key in seen or not kw.text.strip():
                continue
            seen.add(key)
            self.by_weight.setdefault(kw.weight, []).append(
                (kw, kw.pattern))

    def match(self, posting: Posting) -> list[tuple[Keyword, int]]:
        """[(keyword, count)] for every keyword that occurs, best first."""
        body = fold(posting.description[:6000])
        title = fold(posting.title)
        hits: list[tuple[Keyword, int]] = []
        for weight in (3, 2, 1):
            for kw, pattern in self.by_weight.get(weight, []):
                in_title = len(pattern.findall(title))
                in_body = len(pattern.findall(body))
                count = in_body + in_title * 2
                if count:
                    hits.append((kw, count))
        return hits


def keyword_points(hits: list[tuple[Keyword, int]], title_hits: set[str]) -> tuple[float, list[dict]]:
    """Diminishing returns: each further hit of the same weight is worth 55%
    of the one before it, evaluated per weight class.

    A posting that names three different core concepts beats one that says
    "sustainability" eleven times, which is the behaviour we want.
    """
    total = 0.0
    detail: list[dict] = []
    for weight in (3, 2, 1):
        group = [(k, n) for k, n in hits if k.weight == weight]
        if not group:
            continue
        # strong keywords first inside a weight class
        group.sort(key=lambda kn: (-kn[1], -len(kn[0].text)))
        for i, (kw, n) in enumerate(group):
            base = C.KEYWORD_BASE[weight] * (C.KEYWORD_DECAY ** i)
            # more occurrences of the same phrase add a little, capped
            repeat = min(n - 1, 3) * 1.5
            bonus = C.TITLE_BONUS[weight] if kw.text in title_hits else 0.0
            pts = base + repeat + bonus
            total += pts
            detail.append({
                "keyword": kw.text,
                "theme": kw.theme,
                "weight": weight,
                "count": n,
                "in_title": kw.text in title_hits,
                "points": round(pts, 1),
            })

    has_core = any(k.weight >= 2 for k, _ in hits)
    cap = C.MAX_KEYWORD
    if not has_core:
        cap = C.MAX_KEYWORD * C.OFFTOPIC_ONLY_CAP
    capped = min(total, cap)
    detail.append({"_subtotal": round(total, 1), "_cap": cap,
                   "_applied": round(capped, 1)})
    return capped, detail


# --------------------------------------------------------------------------- #
# the other components
# --------------------------------------------------------------------------- #

def seniority_points(p: Posting) -> tuple[int, list[str]]:
    s = p.seniority
    pts = C.SENIORITY_POINTS.get(s.level, C.SENIORITY_POINTS["unspecified"])
    reasons = [f"level {s.level}: {s.evidence}"]
    if s.years is not None:
        if s.years > C.YEARS_OVER_REACH:
            pts = min(pts, -10)
            reasons.append(f"{s.years} years asked, out of reach")
        elif s.years > C.YEARS_TOLERATED:
            pts -= 4
            reasons.append(f"{s.years} years asked, a stretch")
    return pts, reasons


def geography_points(p: Posting, sector_remote: bool = False) -> tuple[int, list[str]]:
    if sector_remote or "remote" in fold(p.location + " " + p.title):
        return C.REMOTE_POINTS, ["location is remote"]
    if not p.country:
        return C.COUNTRY_POINTS.get(C.ANCHOR_COUNTRY) - 4, ["country unknown"]
    if p.country in C.COUNTRY_POINTS:
        pts = C.COUNTRY_POINTS[p.country]
        note = "anchor country" if p.country == C.ANCHOR_COUNTRY else "in scope"
        return pts, [f"{p.country}: {note}"]
    return C.OUTSIDE_POINTS, [f"{p.country} is outside the six target countries"]


def language_points(p: Posting) -> tuple[int, list[str]]:
    lang = (p.language or "").lower()[:2]
    pts = C.LANGUAGE_POINTS.get(lang, C.LANGUAGE_POINTS[""])
    label = {"en": "English", "fr": "French", "nl": "Dutch", "de": "German"}.get(lang, "unknown")
    return pts, [f"posting language: {label}"]


def employer_points(source: Source | None, posting: Posting) -> tuple[int, list[str]]:
    sector = (source.sector if source else "") or ""
    if sector:
        pts = C.EMPLOYER_SECTOR_POINTS.get(sector, C.EMPLOYER_SECTOR_DEFAULT)
        reasons = [f"sector {sector}"]
        if source and source.is_employer:
            pts += C.REGISTRY_EMPLOYER_BONUS
            reasons.append("named employer in the registry")
        return min(pts, C.MAX_EMPLOYER), reasons

    # A posting found on a board: guess from the text.
    t = fold(posting.title + " " + posting.description[:800])
    if re.search(r"\bconsultanc|consulting|advisory\b", t):
        return C.EMPLOYER_SECTOR_POINTS["services"], ["looks like a consultancy"]
    if re.search(r"\b(ngo|non-profit|not for profit|charity|foundation)\b", t):
        return C.EMPLOYER_SECTOR_POINTS["ngo"], ["looks like an NGO"]
    if re.search(r"\b(university|institute|research centre|research center)\b", t):
        return C.EMPLOYER_SECTOR_POINTS["research"], ["looks like a research body"]
    if re.search(r"\b(commission|agency|ministry|authority|parliament)\b", t):
        return C.EMPLOYER_SECTOR_POINTS["public_body"], ["looks like a public body"]
    return C.EMPLOYER_SECTOR_DEFAULT, ["employer type inferred from text"]


def _freshness_curve(days: int) -> int:
    anchors = C.FRESHNESS_ANCHORS
    if days <= anchors[0][0]:
        return anchors[0][1]
    for (d0, v0), (d1, v1) in zip(anchors, anchors[1:]):
        if d0 <= days <= d1:
            span = d1 - d0 or 1
            return round(v0 + (v1 - v0) * (days - d0) / span)
    return anchors[-1][1]


def freshness_points(p: Posting, today: date) -> tuple[int, list[str]]:
    if not p.posted:
        return C.FRESHNESS_UNKNOWN, ["no posted date found"]
    days = (today - p.posted).days
    if days < 0:
        days = 0
    return _freshness_curve(days), [f"posted {days} days ago"]


# --------------------------------------------------------------------------- #
# penalties and exclusions
# --------------------------------------------------------------------------- #

_UNPAID = re.compile(r"\b(unpaid|no salary|not remunerated|non-remunerate|"
                     r"volunteer (position|role)|benevolat|sans remuneration)\b")
_COMMISSION = re.compile(r"\b(commission only|100% commission|"
                         r"self-employed|freelance only|commission-based)\b")
_DUTCH = re.compile(r"\b(dutch|nederlands|nederlandstalig)\b[^.]{0,60}"
                    r"\b(fluent|native|required|mandatory|essential|mother tongue)\b")
_GERMAN = re.compile(r"\b(german|deutsch)\b[^.]{0,60}"
                     r"\b(fluent|native|required|mandatory|essential|mother tongue)\b")
_AGENCY = re.compile(r"\b(recruitment agency|staffing agency|"
                     r"we are recruiting on behalf of|our client is)\b")


def penalties_for(p: Posting, breakdown_level: str) -> tuple[int, list[str], list[str]]:
    """(points, reasons, exclusion reasons)."""
    blob = fold(p.title + " " + p.description[:4000])
    points = 0
    reasons: list[str] = []
    excluded: list[str] = []

    def hit(name: str, why: str, exclude_key: str | None = None) -> None:
        nonlocal points
        points += C.PENALTY[name]
        reasons.append(f"{why} ({C.PENALTY[name]:+d})")
        if exclude_key and C.EXCLUDE_IF.get(exclude_key):
            excluded.append(why)

    if _UNPAID.search(blob):
        hit("unpaid", "unpaid position")
    if _COMMISSION.search(blob):
        hit("commission_only", "commission-only or freelance-only", "commission_only")
    if _DUTCH.search(blob):
        hit("dutch_required", "fluent Dutch required")
    if _GERMAN.search(blob):
        hit("german_required", "fluent German required")
    if _AGENCY.search(blob):
        hit("staffing_agency", "posting is written by a recruiter on behalf of a client")

    if p.seniority.level == "exec":
        excluded.append("executive role (head, director or partner)")
        if C.EXCLUDE_IF.get("seniority_exec"):
            reasons.append("executive title")
    elif re.search(r"\b(senior|lead|head|principal)\b", fold(p.title)):
        hit("senior_title", "senior wording in the title")

    if p.seniority.years is not None and p.seniority.years > C.YEARS_OVER_REACH:
        points += C.PENALTY["years_over_reach"]
        reasons.append(f"{p.seniority.years} years of experience asked "
                       f"({C.PENALTY['years_over_reach']:+d})")
        if C.EXCLUDE_IF.get("years_over_reach"):
            excluded.append(f"{p.seniority.years} years of experience asked")

    if p.deadline and p.deadline < date.today():
        hit("deadline_passed", "deadline has passed", "deadline_passed")

    return points, reasons, excluded


# --------------------------------------------------------------------------- #
# assemble
# --------------------------------------------------------------------------- #

def band_for(total: int) -> str:
    for name, floor, _ in C.BANDS:
        if total >= floor:
            return name
    return C.BANDS[-1][0]


def score(posting: Posting, source: Source | None, index: KeywordIndex,
          today: date) -> Breakdown:
    # always re-detect: an adapter may have run before the description was
    # filled in, and seniority is what decides the exclusions
    posting.seniority = detect(posting.title, posting.description)

    b = Breakdown()
    hits = index.match(posting)
    title_hits = {kw.text for kw, _ in hits
                  if kw.pattern.search(fold(posting.title))}

    kw_raw, detail = keyword_points(hits, title_hits)
    b.keyword = int(round(kw_raw))
    b.matched = detail

    b.seniority, sr = seniority_points(posting)
    b.geography, gr = geography_points(posting)
    b.language, lr = language_points(posting)
    b.employer, er = employer_points(source, posting)
    b.freshness, fr = freshness_points(posting, today)

    pen, pr, excl = penalties_for(posting, posting.seniority.level)
    if source and source.verified == "no":
        pen += C.PENALTY["unverified_source"]
        pr.append("registry row was inferred, domain unconfirmed "
                  f"({C.PENALTY['unverified_source']:+d})")
    b.penalties = pen

    raw = (b.keyword + b.seniority + b.geography + b.language +
           b.employer + b.freshness + b.penalties)
    b.total = max(0, min(100, raw))
    b.band = band_for(b.total)

    if excl:
        b.excluded = True
        b.exclude_reason = "; ".join(dict.fromkeys(excl))

    b.reasons = (
        [f"keyword relevance {b.keyword}/35"] +
        [f"  + {d['points']:g} {d['keyword']} (weight {d['weight']}"
         f"{', in title' if d.get('in_title') else ''})"
         for d in [x for x in detail if "keyword" in x][:6]] +
        (["  " + f"raw subtotal {detail[-1]['_subtotal']:g}, capped at "
                  f"{detail[-1]['_cap']:g}"] if detail and "_subtotal" in detail[-1]
         else []) +
        [f"seniority {b.seniority:+d}"] + [f"  {r}" for r in sr] +
        [f"location {b.geography:+d}"] + [f"  {r}" for r in gr] +
        [f"language {b.language:+d}"] + [f"  {r}" for r in lr] +
        [f"employer {b.employer:+d}"] + [f"  {r}" for r in er] +
        [f"freshness {b.freshness:+d}"] + [f"  {r}" for r in fr] +
        [f"penalties {b.penalties:+d}"] + [f"  {r}" for r in pr]
    )
    return b
