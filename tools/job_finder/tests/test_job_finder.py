"""Tests for the job finder.

Run with:  python3 -m unittest discover -s tools/job_finder/tests -t tools

No pytest, no network, no fixtures that are not in the repo. The point is that
a collaborator can check the ranking maths without installing anything.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from job_finder import config as C                        # noqa: E402
from job_finder import dates, report, seniority           # noqa: E402
from job_finder.adapters import Context, extract_postings  # noqa: E402
from job_finder.crawl import fingerprint                   # noqa: E402
from job_finder.fetch import Fetcher                       # noqa: E402
from job_finder.importer import match_source               # noqa: E402
from job_finder.model import Keyword, Posting, Source, fold  # noqa: E402
from job_finder.score import (KeywordIndex, band_for, keyword_points,  # noqa: E402
                              score)
from job_finder.store import Store                         # noqa: E402

DEMO = ROOT / "data" / "job_finder" / "demo"

CORE = [  # the keywords the CV really cares about
    Keyword("sustainability", "sustainability analyst", "en", 3, "role"),
    Keyword("sustainability", "double materiality", "en", 3, "skill"),
    Keyword("carbon", "ghg protocol", "en", 3, "skill"),
    Keyword("carbon", "bilan carbone", "fr", 3, "role"),
    Keyword("reporting", "csrd", "en", 3, "skill"),
    Keyword("reporting", "esrs", "en", 3, "skill"),
    Keyword("lca", "life cycle assessment", "en", 3, "skill"),
    Keyword("lca", "iso 14067", "en", 3, "skill"),
    Keyword("data", "power bi", "en", 3, "tool"),
    Keyword("certification", "b corp", "en", 3, "skill"),
    Keyword("certification", "ecovadis", "en", 3, "skill"),
    Keyword("adjacent", "environment", "en", 1, "degree"),
]


def a_posting(**kw) -> Posting:
    base = dict(url="https://example.org/job/1", title="Sustainability Analyst",
                employer="Test", country="BE", language="en",
                description="CSRD reporting, GHG Protocol inventories and "
                            "double materiality work for SME clients.")
    base.update(kw)
    return Posting(**base)


class WeightsTest(unittest.TestCase):
    def test_components_sum_to_one_hundred(self):
        total = (C.MAX_KEYWORD + C.MAX_SENIORITY + C.MAX_GEOGRAPHY +
                 C.MAX_LANGUAGE + C.MAX_EMPLOYER + C.MAX_FRESHNESS)
        self.assertEqual(total, 100)

    def test_bands_cover_zero(self):
        self.assertEqual(band_for(0), "D")
        self.assertEqual(band_for(100), "A")
        floors = [f for _, f, _ in C.BANDS]
        self.assertEqual(floors, sorted(floors, reverse=True))


class FoldTest(unittest.TestCase):
    def test_accents_collapse(self):
        self.assertEqual(fold("Toitū Envirocare"), fold("Toitu Envirocare"))
        self.assertEqual(fold("Möbius"), "mobius")

    def test_fingerprint_is_stable_across_accents(self):
        self.assertEqual(fingerprint("Analyste ESG", "Möbius", "BE"),
                         fingerprint("analyste esg", "Mobius", "be"))


class SeniorityTest(unittest.TestCase):
    def test_levels(self):
        cases = {
            "Junior Analyst": "graduate",
            "Sustainability Intern": "intern",
            "Senior Manager, Climate": "senior",
            "Head of Sustainability": "exec",
            "Carbon Consultant": "unspecified",
        }
        for title, expected in cases.items():
            with self.subTest(title=title):
                self.assertEqual(seniority.detect(title).level, expected)

    def test_zero_years_is_not_three_years(self):
        self.assertEqual(seniority.min_years("0-2 years of experience"), 0)
        self.assertEqual(seniority.min_years("No prior experience required"), 0)
        self.assertEqual(seniority.min_years("3-5 years"), 3)

    def test_years_override_an_inflated_title(self):
        s = seniority.detect("Junior Analyst", "You have 8 years of experience.")
        self.assertEqual(s.level, "senior")


class DateTest(unittest.TestCase):
    today = date(2026, 11, 12)

    def test_relative(self):
        self.assertEqual(dates.parse_date("Posted today", self.today), self.today)
        self.assertEqual(dates.parse_date("Posted 6 days ago", self.today),
                         self.today - timedelta(days=6))

    def test_absolute_and_missing_year(self):
        self.assertEqual(dates.parse_date("2026-11-04", self.today),
                         date(2026, 11, 4))
        self.assertEqual(dates.parse_date("Deadline 22 November", self.today),
                         date(2026, 11, 22))
        # a date just behind us is next year's
        self.assertEqual(dates.parse_date("4 January", self.today),
                         date(2027, 1, 4))

    def test_nonsense_is_none(self):
        self.assertIsNone(dates.parse_date("as soon as possible", self.today))


class KeywordScoringTest(unittest.TestCase):
    def setUp(self):
        self.index = KeywordIndex(CORE)

    def test_title_beats_body(self):
        title_hit = self.index.match(a_posting(title="Sustainability Analyst"))
        body_hit = self.index.match(a_posting(
            title="Officer",
            description="We need a sustainability analyst urgently."))
        p1, _ = keyword_points(title_hit, {"sustainability analyst"})
        p2, _ = keyword_points(body_hit, set())
        self.assertGreater(p1, p2)

    def test_diminishing_returns(self):
        once = self.index.match(a_posting(description="CSRD"))
        many = self.index.match(a_posting(description="CSRD " * 20))
        p1, _ = keyword_points(once, set())
        p2, _ = keyword_points(many, set())
        self.assertLess(p2 - p1, 4 * len(many))

    def test_capped_at_the_maximum(self):
        body = "CSRD ESRS GHG Protocol double materiality EcoVadis B Corp " * 3
        hits = self.index.match(a_posting(description=body))
        pts, _ = keyword_points(hits, set())
        self.assertLessEqual(pts, C.MAX_KEYWORD)

    def test_offtopic_only_is_penalised(self):
        off = self.index.match(a_posting(
            title="Marketing Coordinator", description="environment"))
        on = self.index.match(a_posting())
        self.assertLess(keyword_points(off, set())[0],
                        keyword_points(on, set())[0])


class ScoreTest(unittest.TestCase):
    def setUp(self):
        self.index = KeywordIndex(CORE)
        self.today = date(2026, 11, 12)
        self.source = Source("c1", "Test", "company", "BE", "https://x.be", "",
                             "en", "env_consulting", "sme", "open", "high", 1,
                             "yes", "")

    def test_total_matches_the_parts(self):
        b = score(a_posting(posted=self.today), self.source, self.index,
                  self.today)
        parts = (b.keyword + b.seniority + b.geography + b.language +
                 b.employer + b.freshness + b.penalties)
        self.assertEqual(b.total, max(0, min(100, parts)))

    def test_every_point_is_traceable(self):
        b = score(a_posting(posted=self.today), self.source, self.index,
                  self.today)
        self.assertTrue(any("keyword relevance" in r for r in b.reasons))
        self.assertTrue(any("penalties" in r for r in b.reasons))

    def test_senior_role_scores_below_junior_role(self):
        junior = score(a_posting(title="Junior Sustainability Analyst"),
                       self.source, self.index, self.today)
        senior = score(a_posting(title="Senior Sustainability Analyst"),
                       self.source, self.index, self.today)
        self.assertGreater(junior.total, senior.total)

    def test_fluent_dutch_is_a_penalty_in_belgium(self):
        fr = score(a_posting(title="Analyste durabilite", language="fr"),
                   self.source, self.index, self.today)
        nl = score(a_posting(title="Duurzaamheidsanalist", language="nl"),
                   self.source, self.index, self.today)
        self.assertGreater(fr.total, nl.total)

    def test_unpaid_internship_is_penalised(self):
        paid = score(a_posting(title="ESG Intern"), self.source, self.index,
                     self.today)
        unpaid = score(a_posting(title="ESG Intern",
                                 description="CSRD reporting. Unpaid, six months."),
                       self.source, self.index, self.today)
        self.assertGreater(paid.total, unpaid.total)

    def test_exclusion_for_out_of_reach_experience(self):
        b = score(a_posting(title="Environmental Compliance Manager",
                            description="You have 9 years of experience."),
                  self.source, self.index, self.today)
        self.assertTrue(b.excluded)
        self.assertIn("year", b.exclude_reason)

    def test_stale_postings_lose_points(self):
        fresh = score(a_posting(posted=self.today), self.source, self.index,
                      self.today)
        old = score(a_posting(posted=self.today - timedelta(days=90)),
                    self.source, self.index, self.today)
        self.assertGreater(fresh.total, old.total)

    def test_outside_the_six_countries_scores_low(self):
        be = score(a_posting(country="BE"), self.source, self.index, self.today)
        uk = score(a_posting(country="UK"), self.source, self.index, self.today)
        self.assertGreater(be.total, uk.total)


class AdapterTest(unittest.TestCase):
    def ctx(self, source=None, base="https://example.org/jobs"):
        return Context(source=source or Source(
            "s", "Board", "job_board", "BE", "https://example.org", "",
            "en", "", "", "open", "high", 1, "", ""),
            base_url=base, today=date(2026, 11, 12), language="en")

    def test_jsonld_is_preferred(self):
        html = """<html><body>
        <script type="application/ld+json">
        {"@type":"JobPosting","title":"Junior Carbon Analyst",
         "hiringOrganization":{"name":"Acme"},
         "datePosted":"2026-11-01",
         "jobLocation":{"address":{"addressLocality":"Brussels",
                                   "addressCountry":"BE"}},
         "description":"<p>GHG Protocol.</p>"}
        </script></body></html>"""
        postings, adapter = extract_postings(html, self.ctx())
        self.assertEqual(adapter, "jsonld")
        self.assertEqual(postings[0].title, "Junior Carbon Analyst")
        self.assertEqual(postings[0].employer, "Acme")
        self.assertEqual(postings[0].country, "BE")
        self.assertEqual(postings[0].posted, date(2026, 11, 1))

    def test_eurobrussels_cards(self):
        path = DEMO / "eurobrussels-environment.html"
        ctx = Context(Source("job_board-BE-eurobrussels", "EuroBrussels",
                             "job_board", "BE", "https://www.eurobrussels.com",
                             "https://www.eurobrussels.com/jobs/environment",
                             "en", "", "", "open", "high", 1, "", ""),
                      base_url="https://www.eurobrussels.com/jobs/environment",
                      today=date(2026, 11, 12), language="en")
        postings, adapter = extract_postings(path.read_text(), ctx)
        self.assertEqual(adapter, "eurobrussels")
        self.assertEqual(len(postings), 20)
        named = [p for p in postings if p.employer and p.employer != "EuroBrussels"]
        self.assertGreaterEqual(len(named), 19)
        titles = [p.title for p in postings]
        self.assertIn("Junior Analyst - Renewable Fuels", titles)

    def test_empty_page_is_not_a_crash(self):
        postings, adapter = extract_postings("", self.ctx())
        self.assertEqual(postings, [])


class FetchPolitenessTest(unittest.TestCase):
    def test_restricted_domains_are_refused_locally(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Fetcher(Path(tmp), offline=False, respect_robots=False)
            for url in ("https://www.linkedin.com/jobs/view/1",
                        "https://be.indeed.com/viewjob?jk=1"):
                r = f.get(url)
                self.assertFalse(r.ok)
                self.assertIn("refused", r.error.lower())
            self.assertEqual(f.stats["network"], 0)

    def test_offline_never_touches_the_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Fetcher(Path(tmp), offline=True)
            r = f.get("https://example.org/jobs")
            self.assertIn("offline", r.error)
            self.assertEqual(f.stats["network"], 0)


class StoreTest(unittest.TestCase):
    def test_upsert_is_idempotent_and_flags_new(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(Path(tmp) / "t.db")
            run = store.start_run("first")
            p = a_posting()
            p.fingerprint = fingerprint(p.title, p.employer, p.country)
            self.assertTrue(store.upsert(p, run))
            self.assertFalse(store.upsert(p, run))
            store.finish_run(run, 1, 1, 1)
            run2 = store.start_run("second")
            self.assertFalse(store.upsert(p, run2))
            store.save_score(p.fingerprint, score(
                p, None, KeywordIndex(CORE), date(2026, 11, 12)))
            store.finish_run(run2, 0, 0, 0)
            run3 = store.start_run("third")
            store.upsert(p, run3)
            rows = store.ranked(new_since_run=run3)
            self.assertEqual(len(rows), 1)
            self.assertFalse(rows[0]["is_new"])


class ImporterTest(unittest.TestCase):
    def test_matching_a_saved_file_to_its_row(self):
        sources = [Source("company-BE-sustenuto-formerly-betterbusiness",
                          "Sustenuto (formerly BetterBusiness)", "company",
                          "BE", "https://sustenuto.com", "", "fr", "env_consulting",
                          "sme", "open", "high", 1, "yes", "")]
        for name in ("company-BE-sustenuto__careers.html",
                     "Sustenuto (formerly BetterBusiness).html",
                     "ESG role at Sustenuto.txt"):
            with self.subTest(name=name):
                self.assertEqual(match_source(Path(name), sources).id,
                                 "company-BE-sustenuto-formerly-betterbusiness")


class QueryTest(unittest.TestCase):
    """Saved searches: the registry says which sites, a query says which search."""

    def test_the_shipped_queries_load(self):
        from job_finder import queries as Q
        qs = Q.load(ROOT / "data" / "job_finder" / "queries.json")
        self.assertTrue(qs)
        for q in qs:
            self.assertTrue(q.url.startswith("https://"), q.id)
            self.assertTrue(q.country, f"{q.id} needs a country")
            self.assertTrue(q.sector, f"{q.id} needs a sector")

    def test_a_query_becomes_a_source(self):
        from job_finder import queries as Q
        qs = Q.load(ROOT / "data" / "job_finder" / "queries.json")
        src = qs[0].as_source()
        self.assertEqual(src.listing_url, src.url)
        self.assertEqual(src.access, "open")
        self.assertEqual(src.category, "job_board")
        self.assertTrue(src.id.startswith("query-") or src.id == qs[0].id)

    def test_selection_by_id_board_and_label(self):
        from job_finder import queries as Q
        qs = Q.load(ROOT / "data" / "job_finder" / "queries.json")
        one = Q.select(qs, ["eurobrussels-energy"])
        self.assertEqual(len(one), 1)
        by_board = Q.select(qs, ["EuroBrussels"])
        self.assertEqual(len(by_board), len(qs))
        by_label = Q.select(qs, ["intern"])
        self.assertGreaterEqual(len(by_label), 1)

    def test_unknown_query_is_an_error_not_a_silent_empty_run(self):
        from job_finder import queries as Q
        qs = Q.load(ROOT / "data" / "job_finder" / "queries.json")
        with self.assertRaises(SystemExit):
            Q.select(qs, ["no-such-query"])


class CaptureFidelityTest(unittest.TestCase):
    """Every committed snapshot must be captured, never composed.

    The manifest is the receipt: it records the URL and capture date of each
    file, and this test checks the files and the manifest still agree.
    """

    def setUp(self):
        import json
        self.manifest = json.loads(
            (DEMO / "manifest.json").read_text(encoding="utf-8"))

    def test_every_snapshot_is_in_the_manifest(self):
        on_disk = {p.name for p in DEMO.glob("*.html")}
        listed = set(self.manifest["files"])
        self.assertEqual(on_disk, listed,
                         "a captured page without a manifest entry, or the "
                         "reverse: where did this file come from?")

    def test_every_manifest_entry_records_provenance(self):
        for name, meta in self.manifest["files"].items():
            with self.subTest(name=name):
                self.assertTrue(meta["url"].startswith("https://"))
                self.assertIn("captured", self.manifest)
                self.assertGreater(meta["postings"], 0)

    def test_snapshots_carry_real_job_ids_and_nothing_invented(self):
        """Each file must hold as many distinct ids as the manifest claims."""
        import re
        for name, meta in self.manifest["files"].items():
            with self.subTest(name=name):
                text = (DEMO / name).read_text(encoding="utf-8")
                ids = set(re.findall(r"job_display/(\d+)", text))
                self.assertEqual(len(ids), meta["postings"])

    def test_the_fabricated_sustenuto_fixture_is_gone(self):
        """It must not come back. This is the URL a reader clicked."""
        for path in DEMO.glob("*.html"):
            text = path.read_text(encoding="utf-8").lower()
            self.assertNotIn("sustainability-analyst-brussels", text)
            self.assertNotIn("quantis.com/careers", text)


class ProvenanceTest(unittest.TestCase):
    """A demonstration must never be able to pass itself off as live data.

    This is the regression test for the bug that shipped a fabricated URL to
    the top of a report: a hand-written fixture was scored, rendered, and read
    as a real vacancy.
    """

    def _report(self, via_values):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        db = Path(tmp.name) / "t.db"
        store = Store(db)
        run = store.start_run("t")
        index = KeywordIndex(CORE)
        source = Source("s", "Board", "job_board", "BE", "https://x", "",
                        "en", "env_consulting", "sme", "open", "high", 1,
                        "yes", "")
        for i, via in enumerate(via_values):
            p = a_posting(title=f"Junior Carbon Analyst {i}", url=f"https://x/{i}")
            p.fingerprint = fingerprint(p.title, p.employer, p.country)
            p.discovered_via = via
            store.upsert(p, run)
            store.save_score(p.fingerprint, score(p, source, index,
                                                  date(2026, 11, 12)))
        store.finish_run(run, 1, len(via_values), len(via_values))
        out = report.render(db, Path(tmp.name) / "r.html", run_id=run)
        return out.read_text()

    def test_a_snapshot_report_is_bannered_and_keeps_real_links(self):
        """A snapshot is historical, not invented: the URLs did exist."""
        html = self._report(["snapshot", "snapshot"])
        self.assertIn("not a live crawl", html)
        self.assertIn("captured page", html.lower())
        # the anchor survives, because the page really was there
        self.assertEqual(html.count("<h3><a href="), 2)

    def test_a_fixture_report_is_bannered_and_never_linked(self):
        """The regression test. A hand-written URL must never be clickable."""
        html = self._report(["fixture", "fixture"])
        self.assertIn("invented", html.lower())
        self.assertIn("invented posting", html)
        self.assertEqual(html.count("<h3><a href="), 0)

    def test_live_postings_are_linked_and_not_bannered(self):
        html = self._report(["crawl", "crawl"])
        self.assertNotIn("not a live crawl", html)
        self.assertNotIn("invented", html.lower())
        self.assertIn("<h3><a href=", html)

    def test_a_mixed_report_warns_about_the_demo_rows(self):
        html = self._report(["crawl", "fixture"])
        self.assertIn("invented demo data", html.lower())
        # the real one stays clickable, the invented one does not
        self.assertEqual(html.count("<h3><a href="), 1)

    def test_default_provenance_is_crawl(self):
        self.assertEqual(a_posting().discovered_via, "crawl")


class InactiveTest(unittest.TestCase):
    """A posting the last crawl did not see is closed, and must fall out."""

    def test_inactive_postings_are_hidden_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(Path(tmp) / "t.db")
            run = store.start_run("r")
            p = a_posting()
            p.fingerprint = fingerprint(p.title, p.employer, p.country)
            store.upsert(p, run)
            store.save_score(p.fingerprint, score(p, None, KeywordIndex(CORE),
                                                  date(2026, 11, 12)))
            store.finish_run(run, 1, 1, 1)
            self.assertEqual(len(store.ranked()), 1)

            # a later run marks it gone
            run2 = store.start_run("r2")
            store.finish_run(run2, 0, 0, 0)
            store.con.execute("UPDATE postings SET active=0")
            store.con.commit()

            self.assertEqual(len(store.ranked()), 0)
            self.assertEqual(len(store.ranked(include_inactive=True)), 1)


class LinkCheckTest(unittest.TestCase):
    def test_link_status_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(Path(tmp) / "t.db")
            run = store.start_run("r")
            p = a_posting()
            p.fingerprint = fingerprint(p.title, p.employer, p.country)
            store.upsert(p, run)
            self.assertEqual(len(store.needing_link_check()), 1)

            store.mark_link(p.fingerprint, "gone")
            self.assertEqual(store.link_summary()["gone"], 1)
            self.assertEqual(len(store.needing_link_check()), 0)

    def test_a_dead_link_can_be_hidden_from_the_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "t.db"
            store = Store(db)
            run = store.start_run("r")
            for i, status in enumerate(["ok", "gone"]):
                p = a_posting(title=f"Analyst {i}", url=f"https://x/{i}")
                p.fingerprint = fingerprint(p.title, p.employer, p.country)
                store.upsert(p, run)
                store.save_score(p.fingerprint, score(p, None, KeywordIndex(CORE),
                                                      date(2026, 11, 12)))
                store.mark_link(p.fingerprint, status)
            store.finish_run(run, 1, 2, 2)

            both = report.render(db, Path(tmp) / "a.html", run_id=run)
            self.assertEqual(both.read_text().count('class="card '), 2)
            one = report.render(db, Path(tmp) / "b.html", run_id=run,
                                hide_dead=True)
            self.assertEqual(one.read_text().count('class="card '), 1)


class ReportTest(unittest.TestCase):
    def test_report_is_self_contained(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "t.db"
            store = Store(db)
            run = store.start_run("t")
            index = KeywordIndex(CORE)
            source = Source("s", "Board", "job_board", "BE", "https://x", "",
                            "en", "env_consulting", "sme", "open", "high", 1,
                            "yes", "")
            for i, title in enumerate(["Junior Carbon Analyst",
                                       "Senior Climate Director"]):
                p = a_posting(title=title, url=f"https://x/{i}")
                p.fingerprint = fingerprint(p.title, p.employer, p.country)
                store.upsert(p, run)
                store.save_score(p.fingerprint, score(p, source, index,
                                                      date(2026, 11, 12)))
            store.finish_run(run, 1, 2, 2)
            out = report.render(db, Path(tmp) / "r.html", run_id=run)
            html = out.read_text()
            self.assertIn("<style>", html)
            self.assertNotIn("http://cdn", html)
            self.assertNotIn("<link rel=\"stylesheet\"", html)
            self.assertIn("Junior Carbon Analyst", html)
            self.assertIn("How the number is made", html)


if __name__ == "__main__":
    unittest.main(verbosity=2)


class DemoCommandTest(unittest.TestCase):
    """The documented `demo` command must work with no arguments.

    Bug (2026-11-13): `python3 tools/jobfinder.py demo` printed
    "No sources matched that selection." The demo matched registry ids
    ("job_board-BE-eurobrussels") against snapshot filenames
    ("eurobrussels-energy"), two namespaces that never overlap. It now
    pairs through the manifest, and falls back to building sources from
    the saved queries that produced each capture.
    """

    def _run(self, *argv):
        sys.path.insert(0, str(ROOT / "tools"))
        import jobfinder

        return jobfinder.main(list(argv))

    def test_bare_demo_selects_every_capture(self):
        sys.path.insert(0, str(ROOT / "tools"))
        import jobfinder
        from job_finder import queries as Q

        sources = [q.as_source() for q in Q.load(jobfinder.DEFAULT_QUERIES)]
        picked = jobfinder._demo_sources(sources)
        self.assertTrue(picked, "manifest pairing found no captures")
        self.assertEqual(len(picked), 4)

    def test_demo_pairs_on_manifest_not_names(self):
        sys.path.insert(0, str(ROOT / "tools"))
        import jobfinder
        from job_finder.model import Source

        bogus = Source(
            id="job_board-BE-eurobrussels", name="EuroBrussels",
            category="job_board", country="BE",
            url="https://www.eurobrussels.com",
            listing_url="https://www.eurobrussels.com/jobs/environment",
            language="en", sector="public", size="sme", access="open",
            fit="high", priority=1, verified="", notes="")
        # The old prefix rule would have matched nothing; the manifest does
        # not know this id either, so the result must be empty, not a crash.
        self.assertEqual(jobfinder._demo_sources([bogus]), [])

    def test_demo_run_end_to_end(self):
        import tempfile
        from pathlib import Path as P

        with tempfile.TemporaryDirectory() as tmp:
            db = P(tmp) / "demo.db"
            # --db is a global option and must precede the subcommand
            self.assertEqual(self._run("--db", str(db), "demo"), 0)
            self.assertTrue(db.exists(), "demo did not write to --db")


class HomepageIsNotAVacancyTest(unittest.TestCase):
    """A company homepage must not become a "posting" named after its tagline.

    Bug (2026-11-13): the applicant reported that the report listed company
    names instead of job titles. SinglePostingAdapter matched any page with
    200+ characters of text, which is every homepage, so a registry crawl
    produced one fake posting per company titled with its marketing strapline.
    """

    def _ctx(self, url="https://www.example.be"):
        from datetime import date
        return Context(
            source=Source(
                id="company-BE-example", name="Example", category="company",
                country="BE", url=url, listing_url="", language="nl",
                sector="env_consulting", size="large", access="open",
                fit="high", priority=1, verified="", notes=""),
            base_url=url, language="nl", today=date(2026, 11, 13))

    HOMEPAGE = """
    <html><head><title>Aquafin | Water zuiveren voor een betere wereld</title>
    </head><body>
    <nav><a href="/nl/over-ons">Over ons</a><a href="/nl/diensten">Diensten</a>
    <a href="/nl/contact">Contact</a></nav>
    <h1>Welkom bij Aquafin</h1>
    <p>Wij zuiveren het afvalwater van meer dan 6 miljoen Vlamingen en dragen
    zo bij aan een gezonde leefomgeving. Onze 1.900 medewerkers werken dagelijks
    aan innovatieve oplossingen voor waterzuivering, klimaatadaptatie en
    circulaire economie. Ontdek onze projecten, onze aanpak en de kansen die
    wij bieden. Wij investeren in onderzoek en in duurzame technologie.</p>
    </body></html>"""

    VACANCY = """
    <html><head><title>Milieudeskundige waterzuivering - Aquafin</title></head>
    <body><h1>Milieudeskundige waterzuivering</h1>
    <p>Wij zoeken een milieudeskundige voor onze waterzuiveringsinstallaties in
    Vlaanderen. Je volgt de milieuvergunningen op, analyseert meetgegevens en
    rapporteert aan de overheid. Voltijds contract van onbepaalde duur.</p>
    <p>Solliciteer via onze website. Vereist: master milieuwetenschappen.</p>
    </body></html>"""

    def test_homepage_produces_no_posting(self):
        postings, adapter = extract_postings(self.HOMEPAGE, self._ctx())
        self.assertEqual(postings, [],
                         "a homepage must never become a posting")
        self.assertEqual(adapter, "no-adapter")

    def test_real_vacancy_still_parses(self):
        postings, adapter = extract_postings(self.VACANCY, self._ctx())
        self.assertEqual(adapter, "single")
        self.assertEqual(len(postings), 1)
        self.assertIn("Milieudeskundige", postings[0].title)

    def test_title_never_equals_employer_name(self):
        """The reported symptom: titles that were company names."""
        postings, _ = extract_postings(self.HOMEPAGE, self._ctx())
        for p in postings:
            self.assertNotEqual(fold(p.title), fold(p.employer))


class CareersPageDiscoveryTest(unittest.TestCase):
    """A crawl must reach the careers page when the registry gives a site root.

    Bug (2026-11-13): the applicant reported that `crawl` returned website
    names rather than job offers. Most registry rows have no listing_url, so
    the crawler fetched homepages, and two defects hid the vacancies behind
    them:
      1. nothing followed the careers link on the homepage;
      2. the link heuristic required 4+ word anchor text, which is almost
         never how a Dutch or French vacancy is titled ("Stagiair
         duurzaamheid", "Data analist energie").
    """

    HOME = """<html><head><title>Aquafin - Water zuiveren</title></head><body>
    <nav><a href="/nl/over-ons">Over ons</a>
    <a href="/nl/werken-bij-ons">Werken bij Aquafin</a>
    <a href="/nl/contact">Contact</a></nav>
    <p>Aquafin zuivert afvalwater voor 6 miljoen Vlamingen met 1.900
    medewerkers en investeert in klimaat en duurzaamheid.</p></body></html>"""

    CAREERS = """<html><head><title>Vacatures - Aquafin</title></head><body>
    <ul>
    <li><a href="/nl/vacatures/1001">Milieudeskundige waterzuivering</a></li>
    <li><a href="/nl/vacatures/1002">Ingenieur klimaatadaptatie</a></li>
    <li><a href="/nl/vacatures/1003">Data analist energie</a></li>
    <li><a href="/nl/vacatures/1004">Stagiair duurzaamheid</a></li>
    </ul></body></html>"""

    def _ctx(self, base):
        from datetime import date
        return Context(
            source=Source(
                id="company-TEST-aquafin", name="Aquafin", category="company",
                country="BE", url="https://www.aquafin.be", listing_url="",
                language="nl", sector="env_consulting", size="large",
                access="open", fit="high", priority=1, verified="", notes=""),
            base_url=base, language="nl", today=date(2026, 11, 13))

    def test_careers_link_is_found(self):
        from job_finder.adapters import find_careers_url
        from job_finder import html as H

        url = find_careers_url(H.parse(self.HOME), "https://www.aquafin.be")
        self.assertEqual(url, "https://www.aquafin.be/nl/werken-bij-ons")

    def test_job_alert_link_is_not_mistaken_for_the_listing(self):
        from job_finder.adapters import find_careers_url
        from job_finder import html as H

        page = H.parse("""<html><body>
        <a href="/nl/careers/job-alert">Job alert</a>
        <a href="/nl/werken-bij-ons">Werken bij Aquafin</a>
        </body></html>""")
        self.assertEqual(find_careers_url(page, "https://www.aquafin.be"),
                         "https://www.aquafin.be/nl/werken-bij-ons")

    def test_homepage_itself_yields_nothing(self):
        postings, adapter = extract_postings(self.HOME, self._ctx(
            "https://www.aquafin.be"))
        self.assertEqual(postings, [])
        self.assertEqual(adapter, "no-adapter")

    def test_short_dutch_titles_are_recognised(self):
        """Two-word titles were being dropped by the 4-word rule."""
        postings, adapter = extract_postings(
            self.CAREERS, self._ctx("https://www.aquafin.be/nl/werken-bij-ons"))
        self.assertEqual(adapter, "links")
        self.assertEqual(len(postings), 4)
        titles = {p.title for p in postings}
        self.assertIn("Stagiair duurzaamheid", titles)
        self.assertIn("Data analist energie", titles)
        self.assertIn("Milieudeskundige waterzuivering", titles)

    def test_no_posting_is_named_after_its_company(self):
        postings, _ = extract_postings(
            self.CAREERS, self._ctx("https://www.aquafin.be/nl/werken-bij-ons"))
        for p in postings:
            self.assertNotIn("aquafin", fold(p.title))


class PreviewSetupTest(unittest.TestCase):
    """`jobfinder.py demo` and `serve_report.py` must agree on the database.

    Bug (2026-11-13): demo wrote data/job_finder/opportunities.db while the
    server defaulted to demo.db, so "run demo, then serve" always produced
    "Report could not be built".
    """

    def test_server_defaults_to_the_database_demo_writes(self):
        tools = ROOT / "tools"
        sys.path.insert(0, str(tools))
        import jobfinder

        src = (tools / "serve_report.py").read_text(encoding="utf-8")
        self.assertIn("opportunities.db", src,
                      "serve_report must default to the db `demo` writes")
        self.assertNotIn('"demo.db"', src,
                         "serve_report still defaults to demo.db")
        self.assertTrue(str(jobfinder.DEFAULT_DB).endswith("opportunities.db"))

    def test_generated_database_is_gitignored(self):
        ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("data/job_finder/opportunities.db", ignored)
