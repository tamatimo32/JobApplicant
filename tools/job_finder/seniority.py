"""Work out what level a posting is asking for, and why.

Kept separate from scoring because it is the part most likely to be wrong, and
the report shows the evidence next to the score so mistakes are visible.
"""

from __future__ import annotations

import re

from .model import Seniority, fold

# Ordered: the first pattern that matches the title wins. Order matters,
# "Senior Sustainability Intern" is a senior trap, not an internship.
_TITLE_RULES = [
    ("exec", r"\b(head|director|chief|vp|vice president|managing partner|"
             r"principal|partner|general manager|ceo|cto|cfo|founder)\b"),
    ("senior", r"\b(senior|sr\.?|lead|manager|team leader|experienced|"
               r"expert|specialist iii|consultant ii|advisor iii)\b"),
    ("intern", r"\b(intern|internship|trainee|stagiaire|stage|apprentice)\b"),
    ("graduate", r"\b(junior|graduate|entry level|assistant|analyst i|"
                 r"officer i|associate i|starter)\b"),
]

_YEARS = [
    re.compile(r"(?<![0-9])([0-9]{1,2})\s*(?:\+|plus)?\s*(?:to|-|–)?\s*"
               r"(?:[0-9]{1,2})?\s*\+?\s*years?"),
    re.compile(r"minimum\s+of\s+([0-9]{1,2})\s*years?"),
    re.compile(r"at least\s+([0-9]{1,2})\s*years?"),
]

# "0-2 years" means 0 is acceptable, so the minimum is what counts.
_RANGE = re.compile(r"([0-9]{1,2})\s*(?:to|-|–)\s*([0-9]{1,2})\s*\+?\s*years?")

_NEGATIVE = re.compile(r"\b(no|without|not)\b")


def min_years(text: str) -> int | None:
    """The smallest number of years of experience a posting demands.

    Careful about the two traps: "0-2 years" asks for nothing, and
    "no prior experience required" contains a year-like phrase that must not
    be read as a requirement.
    """
    t = fold(text)
    if re.search(r"\b(no|without|not)\b[^.]{0,40}years?", t):
        return 0
    if re.search(r"\bno (prior |previous )?(professional )?experience\b", t):
        return 0
    if re.search(r"\b(0|zero)[- ]to[- ]([0-2])[- ]years?\b", t):
        return 0

    found: list[int] = []
    for m in _RANGE.finditer(t):
        found.append(int(m.group(1)))
    for m in _YEARS:
        for g in m.finditer(t):
            if g.group(1).isdigit():
                found.append(int(g.group(1)))
    real = [f for f in found if f <= 30]
    if not real:
        return None
    return min(real)


def detect(title: str, description: str = "") -> Seniority:
    t = fold(title)
    d = fold(description)
    years = min_years(description) if description else None

    level, evidence = "", ""
    for name, pattern in _TITLE_RULES:
        m = re.search(pattern, t)
        if m and m.group(0).strip():
            level, evidence = name, f'title says "{m.group(0).strip()}"'
            break

    if not level:
        # The body sometimes states the level when the title does not.
        if re.search(r"\b(junior|graduate scheme|entry level|"
                     r"0 to 2 years|first experience)\b", d):
            level, evidence = "graduate", "body says junior or entry level"
        elif re.search(r"\b(senior|5\+ years|seven years|eight years)\b", d):
            level, evidence = "senior", "body asks for senior experience"
        else:
            level, evidence = "unspecified", "no explicit level"

    # Years trump the title: "Senior Analyst, 0-2 years" is a junior role with
    # an inflated name, and vice versa.
    if years is not None:
        if years <= 2:
            level = "graduate"
            evidence = f"{years} years or fewer asked"
        elif years >= 6 and level in {"graduate", "unspecified", "intern"}:
            level = "senior"
            evidence = f"{years} years asked"

    return Seniority(level=level, years=years, evidence=evidence)
