"""Import postings from pages saved by hand.

Why this exists: many desktops sit behind a proxy that blocks scripts, and
some boards simply cannot be crawled politely. A person can still open the
page, hit "save as", and drop the file in a folder. This turns that folder
into ranked postings, using exactly the same adapters as the crawler.

Two shapes are accepted:

* **Saved pages.** ``Save page as → Webpage, complete`` in Firefox, or
  ``Ctrl+S`` in Chrome. ``.html`` or ``.mhtml``.
* **Pasted text.** A ``.txt`` holding a board listing or a single description.
  The filename decides which source it belongs to.

File naming, either::

    <source-id>.html          job_board-BE-eurobrussels.html
    <source-id>__anything.html

Anything without a recognisable source id is matched on the source name
(``EuroBrussels.html``), and failing that is treated as a posting discovered on
the fallback board ``inbox``.
"""

from __future__ import annotations

import email
import re
from datetime import date
from pathlib import Path

from . import html as H
from .adapters import Context, extract_postings
from .model import Keyword, Posting, Source
from .score import KeywordIndex, score
from .seniority import detect

INBOX = Source(
    id="inbox", name="Hand-saved posting", category="job_board", country="",
    url="", listing_url="", language="", sector="", size="", access="open",
    fit="medium", priority=2, verified="", notes="imported from a saved page")


def _mhtml_text(raw: bytes) -> str:
    """Unpack a Chrome .mhtml into the HTML part."""
    msg = email.message_from_bytes(raw)
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            payload = part.get_payload(decode=True) or b""
            charset = part.get_content_charset() or "utf-8"
            return payload.decode(charset, "replace")
    return raw.decode("utf-8", "replace")


def _read(path: Path) -> str:
    raw = path.read_bytes()
    if path.suffix.lower() in {".mhtml", ".mht"}:
        return _mhtml_text(raw)
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def match_source(path: Path, sources: list[Source]) -> Source | None:
    stem = path.stem
    for s in sources:
        if stem == s.id or stem.startswith(s.id):
            return s
    folded = re.sub(r"[^a-z0-9]+", "", stem.lower())
    # "Sustenuto (formerly BetterBusiness).html" and "EU Affairs Manager at
    # Sustenuto.html" both belong to that row
    for s in sources:
        core = re.sub(r"\s*\(.*?\)", "", s.name).strip()
        key = re.sub(r"[^a-z0-9]+", "", core.lower())
        if key and len(key) > 4 and key in folded:
            return s
    for s in sources:
        if re.sub(r"[^a-z0-9]+", "", s.name.lower()) == folded:
            return s
    # "EuroBrussels-page-2" -> EuroBrussels
    for s in sources:
        key = re.sub(r"[^a-z0-9]+", "", s.name.lower())
        if key and key in folded:
            return s
    return None


def import_dir(folder: Path, sources: list[Source], keywords: list[Keyword],
               today: date | None = None) -> list[tuple[Posting, object, Source]]:
    """[(posting, breakdown, source)] for everything importable in *folder*."""
    today = today or date.today()
    index = KeywordIndex(keywords)
    out: list[tuple[Posting, object, Source]] = []

    for path in sorted(Path(folder).glob("*")):
        if path.suffix.lower() not in {".html", ".htm", ".mhtml", ".mht", ".txt"}:
            continue
        path = path.resolve()
        source = match_source(path, sources) or INBOX
        text = _read(path)

        if path.suffix.lower() == ".txt":
            postings = [_from_text(text, path, source, today)]
        else:
            ctx = Context(source=source, base_url=source.target or path.as_uri(),
                          today=today, language=source.language
                          if len(source.language) == 2 else "")
            postings, _adapter = extract_postings(text, ctx)
            if not postings:
                postings = [_from_text(text, path, source, today)]

        for p in postings:
            # a file:// URL carries no country, and a posting with no country
            # is scored as if it were abroad, so inherit the source's
            if not p.country:
                p.country = source.country
            p.discovered_via = "import"

        for p in postings:
            if not p.title:
                continue
            p.seniority = detect(p.title, p.description)
            b = score(p, source, index, today)
            out.append((p, b, source))
    return out


def _from_text(text: str, path: Path, source: Source, today: date) -> Posting:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    title = lines[0][:160] if lines else path.stem.replace("-", " ")
    body = H.strip_tags("\n".join(lines[1:]))[:6000] if len(lines) > 1 else ""
    # a file:// URL carries no country, and a posting with no country is
    # scored as if it were abroad, so fall back to the source's own country
    p = Posting(
        url=source.target or path.as_uri(), title=title, raw_title=title,
        employer=source.name if source is not INBOX else "",
        country=source.country, language=source.language
        if len(source.language) == 2 else "",
        description=body, source_id=source.id, source_name=source.name,
        adapter=f"import:{path.suffix.lstrip('.')}",
    )
    p.seniority = detect(p.title, p.description)
    return p
