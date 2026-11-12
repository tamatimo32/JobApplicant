"""Date parsing for the handful of formats job boards actually use."""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta

_ISO = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
_DMY = re.compile(r"\b(\d{1,2})[/.](\d{1,2})[/.](\d{4})\b")
_DMON_Y = re.compile(r"\b(\d{1,2})\s+([a-z]{3,9})\.?\s+(\d{4})\b")
# "Deadline 22 November" has no year; boards drop it when it is the current one.
_DMON = re.compile(r"\b(\d{1,2})\s+([a-z]{3,9})\b")
_MON_D_Y = re.compile(r"\b([a-z]{3,9})\.?\s+(\d{1,2}),?\s+(\d{4})\b")

_MONTHS = {
    "jan": 1, "janv": 1, "januar": 1, "januari": 1,
    "feb": 2, "fev": 2, "febr": 2, "februar": 2, "februari": 2,
    "mar": 3, "mars": 3, "mrz": 3, "maart": 3, "march": 3, "märz": 3,
    "apr": 4, "avr": 4, "april": 4,
    "may": 5, "mai": 5, "mei": 5,
    "jun": 6, "juin": 6, "juni": 6,
    "jul": 7, "juil": 7, "juillet": 7, "juli": 7,
    "aug": 8, "aout": 8, "août": 8, "august": 8,
    "sep": 9, "sept": 9, "septembre": 9, "september": 9,
    "oct": 10, "octobre": 10, "oktober": 10, "okt": 10,
    "nov": 11, "novembre": 11, "november": 11,
    "dec": 12, "dec.": 12, "decembre": 12, "décembre": 12, "dezember": 12,
    "dez": 12,
}

_REL = [
    # (pattern, unit) where unit is "d", "w", "m" or None to read the number
    (re.compile(r"\b(today|aujourd'?hui|posted today|just posted)\b"), "zero"),
    (re.compile(r"\b(yesterday|hier)\b"), "one"),
    (re.compile(r"\b(\d{1,2})\s*(?:day|days|jour|jours|dag|dagen)\s+ago\b"), "d"),
    (re.compile(r"\b(\d{1,2})\s*(?:hour|hours|heure|heures|uur)\s+ago\b"), "zero"),
    (re.compile(r"\b(\d{1,2})\s*(?:week|weeks|semaine|semaines|woche|weken)\s+ago\b"), "w"),
    (re.compile(r"\b(\d{1,2})\s*(?:month|months|mois|monat|maand|maanden)\s+ago\b"), "m"),
    (re.compile(r"\bil y a (\d{1,2})\s*(jour|jours|heure|heures|semaine|semaines|mois)\b"), "fr"),
]

_DEADLINE = re.compile(
    r"\b(?:deadline|closing date|apply by|closing|date limite|"
    r"postuler avant|bewerbungsfrist|sluitingsdatum)\b[:\s]*([^\n|]{4,40})",
    re.IGNORECASE)


def parse_date(text: str, today: date | None = None) -> date | None:
    """First absolute date in the string, else a relative one, else None."""
    if not text:
        return None
    today = today or date.today()
    low = text.lower().strip()

    m = _ISO.search(low)
    if m:
        return _safe(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    m = _DMY.search(low)
    if m:
        return _safe(int(m.group(3)), int(m.group(2)), int(m.group(1)))

    m = _DMON_Y.search(low)
    if m and _month(m.group(2)):
        return _safe(int(m.group(3)), _month(m.group(2)), int(m.group(1)))

    m = _DMON.search(low)
    if m and _month(m.group(2)):
        mo, d = _month(m.group(2)), int(m.group(1))
        guess = _safe(today.year, mo, d)
        # a date more than six months behind is next year's, not this one's
        if guess and (today - guess).days > 183:
            guess = _safe(today.year + 1, mo, d)
        return guess

    m = _MON_D_Y.search(low)
    if m and _month(m.group(1)):
        return _safe(int(m.group(3)), _month(m.group(1)), int(m.group(2)))

    for pattern, unit in _REL:
        m = pattern.search(low)
        if not m:
            continue
        if unit == "zero":
            return today
        if unit == "one":
            return today - timedelta(days=1)
        if unit == "fr":
            n = int(m.group(1))
            word = m.group(2)
            if word.startswith(("semaine",)):
                return today - timedelta(days=7 * n)
            if word.startswith(("mois",)):
                return today - timedelta(days=30 * n)
            if word.startswith(("heure",)):
                return today
            return today - timedelta(days=n)
        n = int(m.group(1))
        if unit == "w":
            return today - timedelta(days=7 * n)
        if unit == "m":
            return today - timedelta(days=30 * n)
        return today - timedelta(days=n)

    return None


def parse_deadline(text: str, today: date | None = None) -> date | None:
    """The date following a word like "Deadline" or "Date limite"."""
    if not text:
        return None
    m = _DEADLINE.search(text)
    return parse_date(m.group(1), today) if m else None


def _month(token: str) -> int | None:
    token = token.lower().strip(".")
    for key, value in _MONTHS.items():
        if token.startswith(key) or key.startswith(token[:3]):
            return value
    return None


def _safe(y: int, mo: int, d: int) -> date | None:
    try:
        if not 1990 <= y <= 2100:
            return None
        return date(y, mo, d)
    except ValueError:
        return None


def days_since(d: date | None, today: date | None = None) -> int | None:
    if not d:
        return None
    return ((today or date.today()) - d).days


def stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")
