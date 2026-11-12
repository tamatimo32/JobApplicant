#!/usr/bin/env python3
"""Command line for the job finder.

    python3 tools/jobfinder.py crawl --countries BE,LU --limit 8
    python3 tools/jobfinder.py crawl --demo            # offline snapshot
    python3 tools/jobfinder.py report --open
    python3 tools/jobfinder.py explain <fingerprint>
    python3 tools/jobfinder.py sources --country BE

Run ``--help`` on any subcommand. Everything reads the registry built by
``tools/build_job_sources_csv.py``; nothing here re-implements it.
"""

from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from job_finder import config as C                      # noqa: E402
from job_finder import registry as reg                  # noqa: E402
from job_finder.crawl import crawl                      # noqa: E402
from job_finder.report import render                     # noqa: E402
from job_finder.score import KeywordIndex, score        # noqa: E402
from job_finder.store import Store                      # noqa: E402

DEFAULT_CSV = ROOT / "google_drive" / "job_sources_registry.csv"
DEFAULT_DB = ROOT / "data" / "job_finder" / "opportunities.db"
DEFAULT_CACHE = ROOT / "data" / "job_finder" / "cache"
DEFAULT_REPORT = ROOT / "out" / "opportunities.html"
DEMO_DIR = ROOT / "data" / "job_finder" / "demo"


def _csv(path: str | None) -> Path:
    p = Path(path).expanduser() if path else DEFAULT_CSV
    if not p.exists():
        sys.exit(f"registry not found: {p}\n"
                 "Build it first: python3 tools/build_job_sources_csv.py")
    return p


def _split(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [v.strip().upper() for v in value.split(",") if v.strip()]


# --------------------------------------------------------------------------- #
# commands
# --------------------------------------------------------------------------- #

def cmd_crawl(args) -> int:
    sources, keywords = reg.load(_csv(args.csv))
    chosen = reg.select(
        sources,
        countries=_split(args.countries),
        categories=[c.strip() for c in args.categories.split(",")] if args.categories else None,
        priorities=[int(p) for p in args.priorities.split(",")] if args.priorities else None,
        names=[n.strip() for n in args.name.split(",")] if args.name else None,
        include_restricted=args.include_restricted,
    )
    if getattr(args, "demo", False):
        # the demo runs only sources we actually have a snapshot for
        snapshots = {p.stem for p in DEMO_DIR.glob("*.html")} if DEMO_DIR.exists() else set()
        chosen = [s for s in chosen
                  if s.id in snapshots or any(s.id.startswith(k) for k in snapshots)]
        keywords = keywords or []
    if not chosen:
        print("No sources matched that selection.")
        return 2
    print(f"{len(chosen)} sources selected, {len(keywords)} keywords loaded")
    store = Store(Path(args.db))
    report = crawl(chosen, keywords, store, Path(args.cache),
                   offline=args.offline, limit=args.limit,
                   label=args.label or "", verbose=not args.quiet,
                   snapshot_dir=DEMO_DIR if getattr(args, "demo", False) else None)
    for line in report.lines():
        print(line)
    print(f"database: {args.db}")
    print(f"next: python3 tools/jobfinder.py report --run {report.run_id}")
    return 0


def cmd_report(args) -> int:
    store = Store(Path(args.db))
    run_id = args.run
    if run_id is None:
        row = store.con.execute(
            "SELECT MAX(id) AS id FROM runs").fetchone()
        run_id = row["id"] if row else None
    out = render(Path(args.db), Path(args.out), run_id=run_id,
                 title=args.title, include_excluded=args.show_excluded,
                 top_n=args.top, limit=args.limit)
    print(f"wrote {out}")
    if args.open:
        webbrowser.open(out.resolve().as_uri())
    return 0


def cmd_explain(args) -> int:
    store = Store(Path(args.db))
    rows = store.con.execute(
        "SELECT p.*, s.* FROM postings p JOIN scores s USING (fingerprint) "
        "WHERE p.fingerprint LIKE ? OR p.title LIKE ? LIMIT 1",
        (f"{args.fingerprint}%", f"%{args.fingerprint}%")).fetchall()
    if not rows:
        print("nothing matched")
        return 1
    r = dict(rows[0])
    r["excluded"] = bool(r.get("excluded"))
    print(f"{r['title']}\n{r['employer'] or '?'} · {r['country'] or '?'} · {r['url']}\n")
    print(f"TOTAL {r['total']}/100  band {r['band']}"
          f"{'  EXCLUDED: ' + r['exclude_reason'] if r['excluded'] else ''}\n")
    import json
    for line in json.loads(r["reasons"] or "[]"):
        print(" ", line)
    return 0


def cmd_sources(args) -> int:
    sources, keywords = reg.load(_csv(args.csv))
    chosen = reg.select(sources, countries=_split(args.country),
                        categories=[args.category] if args.category else None,
                        priorities=[args.priority] if args.priority else None)
    print(f"{len(chosen)} sources, {len(keywords)} keywords\n")
    for s in chosen:
        flag = {"open": " ", "login_required": "L",
                "api": "A", "tos_restricted": "X"}.get(s.access, "?")
        print(f"{flag} {s.country:2} {s.category:13} {s.name[:34]:34} {s.target[:58]}")
    return 0


def cmd_demo(args) -> int:
    """Run the crawler against the committed snapshot, fully offline."""
    return cmd_crawl(argparse.Namespace(
        csv=args.csv, countries=args.countries, categories=None, priorities=None,
        name=None, include_restricted=False, demo=True, offline=True,
        limit=None, label="demo", quiet=False, db=args.db, cache=args.cache))


def cmd_import(args) -> int:
    """Score pages saved by hand, using the same adapters as the crawler."""
    from job_finder.importer import import_dir
    from job_finder.crawl import fingerprint

    sources, keywords = reg.load(_csv(args.csv))
    folder = Path(args.dir).expanduser()
    if not folder.is_dir():
        sys.exit(f"not a folder: {folder}")
    items = import_dir(folder, sources, keywords)
    if not items:
        print(f"nothing importable in {folder} "
              "(accepted: .html .htm .mhtml .txt)")
        return 1

    store = Store(Path(args.db))
    run_id = store.start_run(args.label or f"import {folder.name}")
    new = kept = 0
    for posting, breakdown, source in items:
        posting.fingerprint = fingerprint(posting.title, posting.employer,
                                          posting.country)
        is_new = store.upsert(posting, run_id)
        store.save_score(posting.fingerprint, breakdown)
        new += int(is_new)
        kept += int(not breakdown.excluded)
    store.finish_run(run_id, len(items), new, kept, notes=f"import {folder}")
    print(f"imported {len(items)} postings ({new} new, {kept} kept) "
          f"from {folder}\nrun {run_id}")
    print(f"next: python3 tools/jobfinder.py report --run {run_id}")
    return 0


def cmd_stats(args) -> int:
    store = Store(Path(args.db))
    print(store.stats())
    runs = store.con.execute(
        "SELECT id, started, label, fetched, new_count, kept FROM runs "
        "ORDER BY id DESC LIMIT 8").fetchall()
    for r in runs:
        print(f"  run {r['id']:>3} {r['started']} {r['label'][:18]:18} "
              f"{r['fetched'] or 0} pages, {r['new_count'] or 0} new, "
              f"{r['kept'] or 0} kept")
    return 0


# --------------------------------------------------------------------------- #
# argument parsing
# --------------------------------------------------------------------------- #

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="jobfinder",
        description="Crawl the job-source registry, rank the postings, render "
                    "an HTML report.")
    p.add_argument("--db", default=str(DEFAULT_DB), help="SQLite database path")
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("crawl", help="fetch sources and score postings")
    c.add_argument("--csv", help="registry CSV (default: google_drive/…)")
    c.add_argument("--countries", help="comma separated, e.g. BE,LU")
    c.add_argument("--categories", help="e.g. job_board,company")
    c.add_argument("--priorities", help="e.g. 1 or 1,2")
    c.add_argument("--name", help="substring match on source name")
    c.add_argument("--limit", type=int, help="stop after N sources")
    c.add_argument("--label", help="label stored with the run")
    c.add_argument("--offline", action="store_true",
                   help="use the cache only, no network")
    c.add_argument("--demo", action="store_true",
                   help="crawl the committed demo snapshot")
    c.add_argument("--include-restricted", action="store_true",
                   help="include login and tos_restricted sources (still not fetched)")
    c.add_argument("--quiet", action="store_true")
    c.add_argument("--cache", default=str(DEFAULT_CACHE))
    c.set_defaults(func=cmd_crawl)

    r = sub.add_parser("report", help="render the HTML report")
    r.add_argument("--run", type=int, help="run id for the 'new' flags")
    r.add_argument("--out", default=str(DEFAULT_REPORT))
    r.add_argument("--title", default="Ranked opportunities")
    r.add_argument("--top", type=int, default=C.TOP_N_FOR_HIGHLIGHTS)
    r.add_argument("--limit", type=int, default=400)
    r.add_argument("--show-excluded", action="store_true")
    r.add_argument("--open", action="store_true", help="open in the browser")
    r.set_defaults(func=cmd_report)

    e = sub.add_parser("explain", help="print the arithmetic for one posting")
    e.add_argument("fingerprint", help="fingerprint prefix, or part of the title")
    e.set_defaults(func=cmd_explain)

    s = sub.add_parser("sources", help="list what a crawl would visit")
    s.add_argument("--csv")
    s.add_argument("--country")
    s.add_argument("--category")
    s.add_argument("--priority", type=int)
    s.set_defaults(func=cmd_sources)

    d = sub.add_parser("demo", help="offline run against the committed snapshot")
    d.add_argument("--csv")
    d.add_argument("--countries")
    d.add_argument("--db", default=str(ROOT / "data" / "job_finder" / "demo.db"))
    d.add_argument("--cache", default=str(DEFAULT_CACHE))
    d.set_defaults(func=cmd_demo)

    i = sub.add_parser("import", help="score pages saved by hand from a folder")
    i.add_argument("--dir", required=True, help="folder of saved .html/.txt files")
    i.add_argument("--csv")
    i.add_argument("--label")
    i.set_defaults(func=cmd_import)

    t = sub.add_parser("stats", help="what is in the database")
    t.set_defaults(func=cmd_stats)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
