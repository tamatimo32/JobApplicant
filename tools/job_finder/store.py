"""SQLite persistence.

Why a database and not a JSON file: the point of running this weekly is change
detection. "New since last week" needs identity and history, and that is
exactly what a primary key plus a ``first_seen`` column gives you. It also
means the report can be rebuilt without re-crawling.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime
from pathlib import Path

from .model import Breakdown, Posting

SCHEMA = """
CREATE TABLE IF NOT EXISTS postings (
    fingerprint   TEXT PRIMARY KEY,
    url           TEXT NOT NULL,
    title         TEXT NOT NULL,
    employer      TEXT,
    country       TEXT,
    location      TEXT,
    language      TEXT,
    salary        TEXT,
    posted        TEXT,
    deadline      TEXT,
    description   TEXT,
    tags          TEXT,
    source_id     TEXT,
    source_name   TEXT,
    adapter       TEXT,
    seniority     TEXT,
    seniority_years INTEGER,
    first_seen    TEXT NOT NULL,
    first_run     INTEGER DEFAULT 0,
    last_seen     TEXT NOT NULL,
    active        INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS scores (
    fingerprint   TEXT PRIMARY KEY REFERENCES postings(fingerprint),
    total         INTEGER,
    band          TEXT,
    keyword       INTEGER,
    seniority     INTEGER,
    geography     INTEGER,
    language      INTEGER,
    employer      INTEGER,
    freshness     INTEGER,
    penalties     INTEGER,
    excluded      INTEGER,
    exclude_reason TEXT,
    matched       TEXT,
    reasons       TEXT,
    scored_at     TEXT
);

CREATE TABLE IF NOT EXISTS runs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    started      TEXT,
    finished     TEXT,
    label        TEXT,
    fetched      INTEGER,
    new_count    INTEGER,
    kept         INTEGER,
    notes        TEXT,
    mark         TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS source_status (
    run_id     INTEGER,
    source_id  TEXT,
    name       TEXT,
    url        TEXT,
    status     INTEGER,
    error      TEXT,
    postings   INTEGER,
    adapter    TEXT,
    ms         INTEGER,
    PRIMARY KEY (run_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_scores_total ON scores(total DESC);
CREATE INDEX IF NOT EXISTS idx_postings_country ON postings(country);
"""


def connect(path: Path | str) -> sqlite3.Connection:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


class Store:
    def __init__(self, path: Path | str):
        self.con = connect(path)

    # ------------------------------------------------------------------ runs
    def start_run(self, label: str) -> int:
        now = datetime.now().isoformat(timespec="seconds")
        cur = self.con.execute(
            "INSERT INTO runs (started, label, mark) VALUES (?, ?, ?)",
            (now, label, now))
        self.con.commit()
        return int(cur.lastrowid)

    def finish_run(self, run_id: int, fetched: int, new_count: int,
                   kept: int, notes: str = "") -> None:
        self.con.execute(
            "UPDATE runs SET finished=?, fetched=?, new_count=?, kept=?, notes=? "
            "WHERE id=?",
            (datetime.now().isoformat(timespec="seconds"), fetched, new_count,
             kept, notes, run_id))
        self.con.commit()

    def last_run_before(self, run_id: int) -> int | None:
        row = self.con.execute(
            "SELECT id FROM runs WHERE id < ? AND finished IS NOT NULL "
            "ORDER BY id DESC LIMIT 1", (run_id,)).fetchone()
        return row["id"] if row else None

    # ------------------------------------------------------------- postings
    def upsert(self, p: Posting, run_id: int) -> bool:
        """Insert or refresh. Returns True only on the insert.

        Whether a posting is *new* is a question about runs, answered by
        ``ranked(new_since_run=…)`` from ``first_run``; this method answers the
        narrower question "have I stored this before at all".
        """
        now = datetime.now().isoformat(timespec="seconds")
        existing = self.con.execute(
            "SELECT first_run FROM postings WHERE fingerprint=?",
            (p.fingerprint,)).fetchone()
        if existing:
            self.con.execute(
                """UPDATE postings SET url=?, title=?, employer=?, country=?,
                   location=?, language=?, salary=?, posted=?, deadline=?,
                   description=?, tags=?, source_id=?, source_name=?,
                   adapter=?, seniority=?, seniority_years=?, last_seen=?,
                   active=1 WHERE fingerprint=?""",
                (p.url, p.title, p.employer, p.country, p.location, p.language,
                 p.salary, _d(p.posted), _d(p.deadline), p.description[:8000],
                 json.dumps(p.tags, ensure_ascii=False), p.source_id,
                 p.source_name, p.adapter, p.seniority.level,
                 p.seniority.years, now, p.fingerprint))
            self.con.commit()
            return False
        self.con.execute(
            """INSERT INTO postings (fingerprint, url, title, employer, country,
               location, language, salary, posted, deadline, description, tags,
               source_id, source_name, adapter, seniority, seniority_years,
               first_seen, first_run, last_seen, active)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1)""",
            (p.fingerprint, p.url, p.title, p.employer, p.country, p.location,
             p.language, p.salary, _d(p.posted), _d(p.deadline),
             p.description[:8000], json.dumps(p.tags, ensure_ascii=False),
             p.source_id, p.source_name, p.adapter, p.seniority.level,
             p.seniority.years, now, run_id, now))
        self.con.commit()
        return True

    def save_score(self, fingerprint: str, b: Breakdown) -> None:
        self.con.execute(
            """INSERT INTO scores (fingerprint, total, band, keyword, seniority,
               geography, language, employer, freshness, penalties, excluded,
               exclude_reason, matched, reasons, scored_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(fingerprint) DO UPDATE SET
                 total=excluded.total, band=excluded.band,
                 keyword=excluded.keyword, seniority=excluded.seniority,
                 geography=excluded.geography, language=excluded.language,
                 employer=excluded.employer, freshness=excluded.freshness,
                 penalties=excluded.penalties, excluded=excluded.excluded,
                 exclude_reason=excluded.exclude_reason,
                 matched=excluded.matched, reasons=excluded.reasons,
                 scored_at=excluded.scored_at""",
            (fingerprint, b.total, b.band, b.keyword, b.seniority, b.geography,
             b.language, b.employer, b.freshness, b.penalties, int(b.excluded),
             b.exclude_reason, json.dumps(b.matched, ensure_ascii=False),
             json.dumps(b.reasons, ensure_ascii=False),
             datetime.now().isoformat(timespec="seconds")))
        self.con.commit()

    def log_source(self, run_id: int, source_id: str, name: str, url: str,
                   status: int, error: str, postings: int, adapter: str,
                   ms: int) -> None:
        self.con.execute(
            """INSERT OR REPLACE INTO source_status
               (run_id, source_id, name, url, status, error, postings, adapter, ms)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (run_id, source_id, name, url, status, error, postings, adapter, ms))
        self.con.commit()

    # --------------------------------------------------------------- reading
    def ranked(self, limit: int | None = None, include_excluded: bool = False,
               new_since_run: int | None = None) -> list[dict]:
        where = ["1=1"]
        params: list = []
        if not include_excluded:
            where.append("s.excluded = 0")
        sql = f"""
            SELECT p.*,
                   s.total, s.band,
                   s.keyword      AS s_keyword,
                   s.seniority    AS s_seniority,
                   s.geography    AS s_geography,
                   s.language     AS s_language,
                   s.employer     AS s_employer,
                   s.freshness    AS s_freshness,
                   s.penalties    AS s_penalties,
                   s.excluded, s.exclude_reason, s.matched, s.reasons,
                   s.scored_at
            FROM postings p JOIN scores s USING (fingerprint)
            WHERE {' AND '.join(where)}
            ORDER BY s.total DESC, p.posted DESC
        """
        if limit:
            sql += " LIMIT ?"
            params.append(limit)
        rows = [dict(r) for r in self.con.execute(sql, params)]
        if new_since_run is not None:
            # "new" means first seen during this run. The first run therefore
            # flags everything, which is the truth.
            rows = [r for r in rows]
            for r in rows:
                r["is_new"] = r.get("first_run") == new_since_run
        return rows

    def stats(self) -> dict:
        one = lambda q: self.con.execute(q).fetchone()[0]  # noqa: E731
        return {
            "postings": one("SELECT COUNT(*) FROM postings"),
            "scored": one("SELECT COUNT(*) FROM scores"),
            "excluded": one("SELECT COUNT(*) FROM scores WHERE excluded=1"),
            "runs": one("SELECT COUNT(*) FROM runs"),
        }

    def source_health(self, run_id: int) -> list[dict]:
        return [dict(r) for r in self.con.execute(
            "SELECT * FROM source_status WHERE run_id=? ORDER BY error DESC, name",
            (run_id,))]


def _d(value: date | None) -> str | None:
    return value.isoformat() if value else None
