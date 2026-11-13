"""Adapters: turn one fetched page into Posting objects.

Each adapter is small and boring on purpose. If an adapter gets complicated,
the site probably publishes JSON-LD and should be handled by ``JsonLdAdapter``
instead, which is the one that survives redesigns.

Order of preference, in ``pick_adapter``: JSON-LD, then a site-specific
adapter, then the generic link heuristic, then the page itself as a single
posting (which is how an employer careers page with one open role looks).
"""

from __future__ import annotations

import re
import urllib.parse as up
from dataclasses import dataclass
from datetime import date
from typing import Optional

from . import config as C
from . import html as H
from .dates import parse_date, parse_deadline
from .model import Posting, Source, fold
from .seniority import detect


@dataclass
class Context:
    source: Source
    base_url: str
    today: date
    language: str = ""


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #

_STRONG = re.compile(
    r"\b(intern|internship|trainee|graduate|junior|analyst|consultant|"
    r"officer|assistant|advisor|adviser|specialist|engineer|researcher|"
    r"scientist|coordinator|programme manager|program manager|manager|"
    r"director|head|lead|stage|stagiaire|analyste|conseiller|ingenieur|"
    r"charge de mission|expert|associate|assistant|environment|climate|"
    r"carbon|energy|esg|durabilite|sustainability|environnement|"
    r"biodiversity|water|waste|hse|qhse|sheq|ehs|hse|compliance)\b")

_URL_POSTING = re.compile(
    r"(/job[s]?/|/job_display/|/vacanc|/career[s]?/|/offre[s]?-?d?e?mploi|"
    r"/stellenangebot|/emploi[s]?/|/positions?/|/opening|/requisition|"
    r"/job-detail|/viewjob|/detail/|/poste[s]?/|/annonce)", re.IGNORECASE)

_NOISE = re.compile(
    r"\b(login|log in|sign in|register|subscribe|newsletter|privacy|cookies?|"
    r"terms|about us|contact|faq|sitemap|search|home|back to|apply now|"
    r"save this job|email me jobs|view all|see all|read more|share|"
    r"connexion|s'inscrire|mentions legales|nous contacter|accueil)\b")


def _same_site(url: str, base: str) -> bool:
    a = up.urlsplit(url).netloc.replace("www.", "")
    b = up.urlsplit(base).netloc.replace("www.", "")
    return bool(a) and (a == b or a.endswith("." + b) or b.endswith("." + a))


def _clean_title(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip(" -|–—·•\n\t")
    # boards suffix the employer and the city; cut at the first separator
    for sep in (" | ", " – ", " — ", " · "):
        if sep in text and len(text.split(sep)[0]) > 12:
            text = text.split(sep)[0]
            break
    return text.strip()


def _looks_like_posting(anchor: H.Anchor, base: str) -> bool:
    href = up.urljoin(base, anchor.href)
    if not href.startswith("http"):
        return False
    if not _same_site(href, base) and not _URL_POSTING.search(href):
        return False
    text = (anchor.text or "").strip()
    if len(text) < 8 or len(text) > 160:
        return False
    if _NOISE.search(fold(text)) and not _STRONG.search(fold(text)):
        return False
    if _URL_POSTING.search(href) and _STRONG.search(fold(text)):
        return True
    # long, sentence-like anchors are usually cards
    return bool(_STRONG.search(fold(text))) and len(text.split()) >= 4


# --------------------------------------------------------------------------- #
# adapters
# --------------------------------------------------------------------------- #

class JsonLdAdapter:
    """schema.org JobPosting. Highest precision, so it runs first."""

    name = "jsonld"

    def match(self, page: H.Page) -> bool:
        return bool(H.job_postings(page))

    def parse(self, page: H.Page, ctx: Context) -> list[Posting]:
        out: list[Posting] = []
        for item in H.job_postings(page, ctx.base_url):
            title = _clean_title(item["title"])
            if not title:
                continue
            url = item["url"] or ctx.base_url
            p = Posting(
                url=url,
                title=title,
                raw_title=item["title"],
                employer=item["employer"] or ctx.source.name,
                # the posting states its own country; trust it over the source,
                # because one careers page can advertise several countries
                country=_country_code(item["location"]) or ctx.source.country,
                location=item["location"],
                language=(item["language"] or ctx.language)[:2],
                salary=item["salary"],
                description=item["description"] or "",
                posted=parse_date(item["date_posted"], ctx.today),
                deadline=parse_date(item["valid_through"], ctx.today),
                source_id=ctx.source.id,
                source_name=ctx.source.name,
                adapter=self.name,
            )
            if item.get("remote") and "remote" not in fold(p.location):
                p.location = (p.location + ", remote").strip(", ")
            p.seniority = detect(p.title, p.description)
            out.append(p)
        return out


class EuroBrusselsAdapter:
    """EuroBrussels cards: the title anchor, then employer, town and a blurb.

    The link slug looks tempting but drops stop words ("Compassion in World
    Farming" becomes ``Compassion_in_World_Farming`` while the title loses its
    "and"), so word counts do not line up. Read the surrounding markup instead
    and fall back to the slug only for the employer.
    """

    name = "eurobrussels"

    def match(self, page: H.Page) -> bool:
        return any("/job_display/" in a.href for a in page.anchors)

    def parse(self, page: H.Page, ctx: Context) -> list[Posting]:
        cards = _eurobrussels_cards(page.text)
        out, seen = [], set()
        for a in page.anchors:
            if "/job_display/" not in a.href or a.href in seen:
                continue
            seen.add(a.href)
            title = _clean_title(a.text)
            card = (cards.get(a.text) or cards.get(fold(a.text))
                    or cards.get(title) or cards.get(fold(title)) or {})
            employer = _titlecase(card.get("employer", ""))
            town = card.get("location", "")
            p = Posting(
                url=up.urljoin(ctx.base_url, a.href), title=title,
                raw_title=a.text, employer=employer or ctx.source.name,
                country=ctx.source.country or _country_code(town),
                location=town, language="en",
                description=card.get("blurb", ""),
                posted=parse_date(card.get("posted", ""), ctx.today),
                deadline=parse_deadline(card.get("deadline", ""), ctx.today),
                source_id=ctx.source.id, source_name=ctx.source.name,
                adapter=self.name,
            )
            p.seniority = detect(p.title)
            out.append(p)
        return out


_EURO_POSTED = re.compile(
    r"^(posted\s+(today|yesterday|\d+\s+\w+\s+ago)|\d+\s+days?\s+left|"
    r"deadline\s+[^\n]+|saved!?|save this job)$", re.IGNORECASE)
# a card can carry a posted line and a deadline line; keep both, the posted
# one is what freshness scoring needs and the deadline is what "gone" needs
_EURO_DEADLINE = re.compile(r"^(deadline\s+.*|\d+\s+days?\s+left)$", re.I)
# "Europe" contains "eur", so match a currency amount, not the letters.
_EURO_SALARY = re.compile(r"(€\s?[\d.,]+|\bEUR\s?[\d.,]+|"
                          r"\b\d[\d.,]*\s*(?:€|EUR)\b|\bsalary\b|"
                          r"\bper (?:year|month|annum)\b)", re.IGNORECASE)


_EURO_TAGS = re.compile(r"^([A-Z][A-Za-z &/().'-]+){2,}$")


def _looks_like_title(candidate: str, nxt: str) -> bool:
    return (10 <= len(candidate) <= 160
            and not _EURO_POSTED.match(candidate)
            and not _EURO_SALARY.search(candidate)
            and not candidate.endswith((".", ":", ";"))
            and (" " in candidate or len(candidate) > 12)
            and 2 <= len(nxt) <= 90
            and not nxt.endswith(".")
            and not _EURO_POSTED.match(nxt))


def _eurobrussels_cards(text: str) -> dict[str, dict]:
    """Group the page text into cards, keyed by title (raw and folded).

    A card is read in a fixed order, which is how both saved pages are laid
    out: title, employer, optional town, optional salary, optional blurb and
    tags, then the posted and deadline lines, which always come last and are
    what freshness and "is this still open" depend on. The card ends at the
    first line after the dates that looks like a new title.
    """
    lines = [ln.strip() for ln in text.split("\n")]
    lines = [ln for ln in lines if ln]
    out: dict[str, dict] = {}
    i = 0
    while i < len(lines) - 1:
        candidate, nxt = lines[i], lines[i + 1]
        if not _looks_like_title(candidate, nxt):
            i += 1
            continue

        location, salary, blurb = "", "", ""
        j = i + 2
        if j < len(lines) and len(lines[j]) <= 40 and not _special(lines[j]):
            location = lines[j]
            j += 1
        if j < len(lines) and _EURO_SALARY.search(lines[j]) and lines[j] != location:
            salary = lines[j]
            j += 1
        if j < len(lines) and not _special(lines[j]) and len(lines[j]) >= 40:
            blurb = lines[j]
            j += 1
            # tags run straight on from the blurb in the saved markup
            while j < len(lines) and not _special(lines[j]) \
                    and not _looks_like_title(lines[j],
                                              lines[j + 1] if j + 1 < len(lines) else ""):
                j += 1

        posted = deadline = ""
        while j < len(lines) and _special(lines[j]):
            line = lines[j]
            if _EURO_DEADLINE.match(line):
                deadline = line
            elif line.lower().startswith(("posted", "just posted")):
                posted = line
            j += 1
        # A card always carries a date or two; if the walk consumed the whole
        # page it has run away, so treat this candidate as prose and move on.
        if not posted and not deadline and not salary:
            i += 1
            continue

        d = {"employer": nxt, "location": location, "posted": posted,
             "deadline": deadline, "blurb": blurb, "salary": salary}
        out.setdefault(candidate, d)
        out.setdefault(fold(candidate), d)
        i = max(j, i + 1)
    return out


def _special(line: str) -> bool:
    """A line that is metadata rather than prose."""
    return bool(_EURO_POSTED.match(line) or _EURO_SALARY.search(line))


class LinkListAdapter:
    """The fallback for any board: follow posting-shaped anchors."""

    name = "links"

    def match(self, page: H.Page) -> bool:
        return self._count(page) >= 3

    def _count(self, page: H.Page) -> int:
        return sum(1 for a in page.anchors if _looks_like_posting(a, self.base))

    def parse(self, page: H.Page, ctx: Context) -> list[Posting]:
        self.base = ctx.base_url
        out, seen = [], set()
        for a in page.anchors:
            if not _looks_like_posting(a, ctx.base_url):
                continue
            url = up.urljoin(ctx.base_url, a.href)
            key = fold(_clean_title(a.text))
            if url in seen or key in seen:
                continue
            seen.add(url)
            seen.add(key)
            title = _clean_title(a.text)
            p = Posting(
                url=url, title=title, raw_title=a.text,
                employer=ctx.source.name, country=ctx.source.country,
                language=ctx.language, source_id=ctx.source.id,
                source_name=ctx.source.name, adapter=self.name,
                description="",
            )
            p.seniority = detect(title)
            out.append(p)
        return out


class SinglePostingAdapter:
    """A careers page with exactly one open role, or a direct posting URL.

    The title comes from the page ``<title>``, which is almost always right,
    and the body text becomes the description so keyword scoring still works.
    """

    name = "single"

    # Signals that a page is actually advertising a vacancy rather than being
    # a company homepage. Before 2026-11-13 this adapter matched *any* page
    # with 200+ characters of text, which is every homepage on the internet,
    # so a crawl of the registry produced one fake "posting" per company
    # titled with its marketing strapline ("Aquafin | Water zuiveren voor een
    # betere wereld"). That is what made the report read as a list of
    # companies instead of vacancies.
    _JOB_WORDS = (
        "job", "jobs", "vacanc", "vacature", "offre", "emploi", "stelle",
        "position", "career", "carriere", "sollicit", "apply", "recruit",
        "hiring", "traineeship", "internship", "stage", "cdd", "cdi",
        "full-time", "part-time", "voltijds", "deeltijds",
    )

    def match(self, page: H.Page) -> bool:
        text = page.text or ""
        if len(text) < 200:
            return False
        title = fold(page.title or "")
        body = fold(text[:4000])
        # A vacancy page names the role and usually says how to apply.
        has_role_word = any(w in title for w in self._JOB_WORDS) or \
            any(w in body for w in self._JOB_WORDS)
        if not has_role_word:
            return False
        # A homepage title is usually "Brand | strapline". A job page title
        # is usually the role, often followed by the employer.
        if "|" in (page.title or "") and not any(
                w in title for w in self._JOB_WORDS):
            return False
        return True

    def parse(self, page: H.Page, ctx: Context) -> list[Posting]:
        title = _clean_title(page.title)
        employer = ctx.source.name
        if " at " in title.lower():
            head, _, tail = title.partition(" at ")
            title, employer = _clean_title(head), _clean_title(tail)
        p = Posting(
            url=ctx.base_url, title=title or ctx.source.name,
            raw_title=page.title, employer=employer,
            country=ctx.source.country,
            location=page.meta.get("og:locality", ""),
            language=ctx.language,
            description=H.strip_tags(page.text)[:6000],
            source_id=ctx.source.id, source_name=ctx.source.name,
            adapter=self.name,
        )
        p.seniority = detect(p.title, p.description)
        return [p]


ADAPTERS = [JsonLdAdapter(), EuroBrusselsAdapter(), LinkListAdapter(),
            SinglePostingAdapter()]


def pick_adapter(page: H.Page, base_url: str):
    LinkListAdapter.base = base_url      # set before match() is called
    for adapter in ADAPTERS:
        try:
            if adapter.match(page):
                return adapter
        except Exception:                                      # noqa: BLE001
            continue
    return None


_COUNTRY_CODES = {
    "belgium": "BE", "luxembourg": "LU", "switzerland": "CH",
    "australia": "AU", "new zealand": "NZ", "united arab emirates": "AE",
    "be": "BE", "lu": "LU", "ch": "CH", "au": "AU", "nz": "NZ", "ae": "AE",
    "belgique": "BE", "belgie": "BE", "luxemburg": "LU", "suisse": "CH",
    "schweiz": "CH", "uae": "AE", "vereinigte arabische emirate": "AE",
}


def _country_code(location: str) -> str:
    tail = fold(location).split(",")[-1].strip()
    return _COUNTRY_CODES.get(tail, "")


def _titlecase(text: str) -> str:
    """Capitalise an employer name without destroying acronyms.

    "BDEW" and "ECOS" are how these organisations write themselves; "Bdew" is
    how a naive capitaliser writes them.
    """
    small = {"of", "and", "the", "for", "de", "du", "des", "la", "le", "les",
             "den", "der", "und", "von", "van", "in", "on", "&"}
    out = []
    for i, word in enumerate(text.split()):
        if sum(c.isupper() for c in word) >= 2:
            out.append(word)                       # keep acronyms
        elif i and word.lower() in small:
            out.append(word.lower())
        else:
            out.append("-".join(p[:1].upper() + p[1:]
                                for p in word.split("-")))
    return " ".join(out)


def extract_postings(html_text: str, ctx: Context) -> tuple[list[Posting], str]:
    """(postings, adapter_name). Never raises; a bad page yields nothing."""
    try:
        page = H.parse(html_text)
    except Exception:                                          # noqa: BLE001
        return [], "error"
    if not page.anchors and not page.text and not page.ld_json:
        return [], "empty"

    adapter = pick_adapter(page, ctx.base_url)
    if adapter is None:
        return [], "no-adapter"
    try:
        postings = adapter.parse(page, ctx)
    except Exception:                                          # noqa: BLE001
        return [], f"{adapter.name}-error"

    out = []
    for p in postings[:C.MAX_POSTINGS_PER_SOURCE]:
        if not p.title:
            continue
        p.deadline = p.deadline or parse_deadline(page.text[:4000], ctx.today)
        if not p.country:
            p.country = ctx.source.country
        out.append(p)
    return out, adapter.name
