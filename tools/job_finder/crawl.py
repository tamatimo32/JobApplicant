"""Crawl a set of registry sources, score what comes back, store the result."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from . import config as C
from . import registry as reg
from . import html as H
from .adapters import (Context, extract_postings, find_careers_url)
from .fetch import Fetcher
from .model import Keyword, Posting, Source, fold
from .score import KeywordIndex, score
from .seniority import detect
from .store import Store


@dataclass
class RunReport:
    run_id: int = 0
    fetched: int = 0
    postings: int = 0
    new: int = 0
    kept: int = 0
    excluded: int = 0
    log: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def lines(self) -> list[str]:
        out = [f"run {self.run_id}: {self.fetched} pages, {self.postings} postings, "
               f"{self.new} new, {self.kept} kept, {self.excluded} excluded"]
        return out


def fingerprint(title: str, employer: str, country: str) -> str:
    """Identity for deduplication.

    Title plus employer plus country, not the URL, because the same posting is
    routinely published at three URLs (board, ATS, employer site). Folded so
    "Möbius" and "Mobius" collapse, which is the same accent bug as before.
    """
    blob = "|".join([fold(title), fold(employer), fold(country)])
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()[:16]


def crawl(sources: list[Source], keywords: list[Keyword], store: Store,
          cache_dir: Path, *, offline: bool = False, limit: int | None = None,
          label: str = "", verbose: bool = True,
          snapshot_dir: Path | None = None) -> RunReport:
    run_id = store.start_run(label or f"run {date.today()}")
    report = RunReport(run_id=run_id)
    fetcher = Fetcher(cache_dir, offline=offline, verbose=verbose)
    index = KeywordIndex(keywords)
    today = date.today()
    seen: set[str] = set()

    for i, source in enumerate(sources[:limit] if limit else sources, 1):
        started = time.time()
        url = source.target
        if verbose:
            print(f"[{i}/{len(sources)}] {source.name}  {url}")
        snapshot = None
        if snapshot_dir:
            exact = Path(snapshot_dir) / f"{source.id}.html"
            # A query's synthetic id is "query-<id>"; its capture is named
            # after the query. Fall back to a prefix match so a renamed
            # registry row still finds its page.
            plain = source.id.removeprefix("query-")
            candidates = [f"{plain}.html", f"{source.id}.html"]
            for name in candidates:
                if (Path(snapshot_dir) / name).exists():
                    snapshot = Path(snapshot_dir) / name
                    break
            if snapshot is None:
                snapshot = next(
                    (q for q in sorted(Path(snapshot_dir).glob("*.html"))
                     if plain.startswith(q.stem) or q.stem.startswith(plain)),
                    None)
        if snapshot is not None:
            from .fetch import Response
            resp = Response(url=url, status=200,
                            text=snapshot.read_text(encoding="utf-8"),
                            content_type="text/html; charset=utf-8")
            print(f"        (snapshot {snapshot.name})" if verbose else "", end="\n")
        else:
            resp = fetcher.get(url)
        ms = int((time.time() - started) * 1000)

        if not resp.ok:
            report.log.append({"source": source.name, "error": resp.error,
                               "status": resp.status})
            store.log_source(run_id, source.id, source.name, url, resp.status,
                             resp.error, 0, "", ms)
            if verbose:
                print(f"        ! {resp.error}")
            continue

        report.fetched += 1
        # the registry cell can hold "fr/nl/en"; a posting has one language
        lang = source.language if len(source.language) == 2 else ""
        ctx = Context(source=source, base_url=resp.url or url, today=today,
                      language=lang)
        postings, adapter = extract_postings(resp.text, ctx)

        # A registry row with no listing_url points at a site root, and a root
        # sells the company rather than its vacancies. When the first parse
        # finds nothing, look for the careers page and try that before giving
        # up. This is what stops a crawl from returning company names.
        followed = ""
        if not postings and not snapshot:
            page = H.parse(resp.text) if resp.ok else None
            careers = find_careers_url(page, ctx.base_url) if page else ""
            if careers and careers != url:
                followed = careers
                if verbose:
                    print(f"        -> careers page {careers}")
                resp2 = fetcher.get(careers)
                if resp2.ok:
                    report.fetched += 1
                    ctx2 = Context(source=source, base_url=resp2.url or careers,
                                   today=today, language=lang)
                    postings, adapter = extract_postings(resp2.text, ctx2)
                    resp = resp2
        # remember whether these came from a committed snapshot or the live
        # site, so the report can never present a snapshot as a real vacancy
        via = "snapshot" if snapshot is not None else "crawl"

        kept_here = 0
        dropped = 0
        for p in postings:
            # A job offer is never titled with the name of the company that
            # posted it. When that happens the "posting" is really the
            # company homepage, which reads as a website name in the report
            # and carries no information. Refuse those outright rather than
            # ranking them.
            if fold(p.title) == fold(p.employer) or not p.title.strip():
                dropped += 1
                continue
            if not p.country:
                p.country = source.country
            p.discovered_via = via
            p.fingerprint = fingerprint(p.title, p.employer, p.country)
            if p.fingerprint in seen:
                continue
            seen.add(p.fingerprint)
            if not p.seniority.level:
                p.seniority = detect(p.title, p.description)
            b = score(p, source, index, today)
            is_new = store.upsert(p, run_id)
            store.save_score(p.fingerprint, b)
            report.postings += 1
            report.new += int(is_new)
            if b.excluded:
                report.excluded += 1
            else:
                report.kept += 1
                kept_here += 1

        store.log_source(run_id, source.id, source.name, followed or url,
                         resp.status, "", len(postings), adapter, ms)
        if dropped and verbose:
            print(f"        ! dropped {dropped} item(s) titled with the "
                  f"company name")
        if verbose:
            if postings:
                print(f"        {len(postings)} postings via {adapter}"
                      f"{'  [cached]' if resp.from_cache else ''}")
            else:
                # Say why a page produced nothing. "no-adapter" now usually
                # means the page looked like a homepage rather than a
                # vacancy list, which is the normal outcome for a company
                # whose careers link was never captured in the registry.
                reason = {
                    "no-adapter": "no vacancy list or posting found on the page",
                    "empty": "page had no readable text (JavaScript-only?)",
                    "error": "could not parse the HTML",
                }.get(adapter, f"adapter {adapter}")
                print(f"        ! {reason}{'  [cached]' if resp.from_cache else ''}")

    # anything not seen this run is no longer advertised
    store.con.execute(
        "UPDATE postings SET active=0 WHERE last_seen < (SELECT mark FROM runs WHERE id=?)",
        (run_id,))
    store.con.commit()
    store.finish_run(run_id, report.fetched, report.new, report.kept,
                     notes=f"adapters: {fetcher.stats}")
    return report
