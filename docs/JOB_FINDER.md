# The job finder

Reads `google_drive/job_sources_registry.csv`, visits the sources, scores every
posting it finds, and writes one HTML page with the best ones at the top.

**Python 3.9+, standard library only.** No `pip install`, no API key, no
account. The whole thing is about 2,000 lines across nine small modules.

---

## The shortest path

```bash
# 1. a working example, no network: uses the two committed snapshots
python3 tools/jobfinder.py demo
python3 tools/jobfinder.py report --run 1 --open

# 2. the real thing, Belgium and Luxembourg job boards
python3 tools/jobfinder.py crawl --countries BE,LU --categories job_board
python3 tools/jobfinder.py report --run 1 --open

# 3. keep it fresh: run 2 shows what is new since run 1
python3 tools/jobfinder.py crawl --countries BE,LU
python3 tools/jobfinder.py report --run 2
```

`report` without `--run` uses the latest run.

---

## What it actually does

```
registry CSV ──► plan ──► fetch (cached, 1 req/host/1.5 s) ──► adapters
                                                                  │
      HTML report ◄── SQLite (dedupe + history) ◄── score out of 100 ┘
```

1. **Plan.** The registry has 821 sources. A run takes a subset: by country, by
   category, by priority. LinkedIn, Indeed, Glassdoor and Google Jobs are
   filtered out at load, because their terms forbid it.
2. **Fetch.** Polite by construction: a real User-Agent naming the tool, one
   request per host at a time with a 1.5 second gap, `robots.txt` obeyed,
   responses cached on disk for 12 hours.
3. **Parse.** Four adapters, tried in order:

   | adapter | when it fires | what it gives |
   | --- | --- | --- |
   | `jsonld` | the page embeds schema.org `JobPosting` | title, employer, town, dates, full description. The best case, and most ATS platforms do this. |
   | `eurobrussels` | anchors contain `/job_display/` | the card structure of that board, employer and town included |
   | `links` | 3+ anchors look like postings | title and URL only; enough to see it exists |
   | `single` | a careers page with one role open | `<title>` and body text |

   Anything that fails to parse is reported in the "sources this run" table
   rather than silently dropped.
4. **Deduplicate.** Fingerprint is title + employer + country, folded for
   accents. Not the URL: the same job is routinely published at three URLs.
5. **Score.** See [SCORING.md](SCORING.md). Additive out of 100, with the
   arithmetic stored per posting.
6. **Report.** One self-contained HTML file. No CDN, no build step, works
   offline, readable on a phone.

---

## Commands

| command | what it does |
| --- | --- |
| `crawl` | fetch sources, score, store. `--countries BE,LU`, `--categories job_board,company`, `--priorities 1`, `--limit N`, `--offline` |
| `demo` | offline run against the two committed snapshots |
| `import` | score pages you saved by hand: `--dir ~/Downloads/jobs` |
| `report` | write `out/opportunities.html`. `--run N`, `--show-excluded`, `--open` |
| `explain` | print the arithmetic for one posting: `explain "carbon"` |
| `sources` | list what a crawl would visit before committing to it |
| `stats` | what is in the database and when each run happened |

Global: `--db path` (default `data/job_finder/opportunities.db`).

---

## When the crawler cannot reach a site

Corporate networks, some countries and most locked-down laptops block scripted
requests. The tool then reports the failure per source and carries on. Three
answers, in order of preference:

1. **Save the page and import it.**
   `Ctrl+S` on a board listing, then
   `python3 tools/jobfinder.py import --dir ~/Downloads/jobs`.
   Accepted: `.html`, `.htm`, `.mhtml` (Chrome's "single file"), `.txt`.
   Name the file after the source (`EuroBrussels.html`, or
   `company-BE-sustenuto__careers.html`) and it inherits that row's country,
   sector and language. Otherwise it lands under a generic "hand-saved" source.
2. **Paste the description.** A `.txt` whose first line is the job title and
   whose body is the posting works with the same scoring.
3. **Read the report anyway.** The ranking is unchanged; only the discovery is
   manual.

---

## Where things live

```
tools/jobfinder.py              command line
tools/serve_report.py           regenerate-on-request server for the preview
tools/job_finder/
  config.py                     every weight and threshold, documented
  score.py                      the arithmetic
  seniority.py                  what level a posting asks for, and why
  adapters.py                   page → postings
  html.py                       tiny HTML and JSON-LD reader (stdlib only)
  dates.py                      "posted 6 days ago" → a date
  fetch.py                      polite HTTP + disk cache
  crawl.py                      the pipeline
  store.py                      SQLite schema and queries
  importer.py                   hand-saved pages
  report.py                     the HTML
  tests/                        30 tests, no network
data/job_finder/
  demo/                         two committed snapshots used by `demo`
  opportunities.db              created on first run
  cache/                        raw pages, 12 hour TTL
docs/SCORING.md                 why the numbers are what they are
```

Nothing here writes to `google_drive/`, and `.gitignore` already covers
`out/*.pdf`; `out/opportunities.html` is generated and can be ignored or kept
as you prefer.

---

## Design decisions worth knowing

**Standard library only.** A job-hunting tool that needs a working `pip`
before it will open a spreadsheet is a tool that fails exactly when the
machine is locked down.

**Keywords are registry rows, not a config list.** The same CSV says where to
look and what to keep, so the two can never drift apart, and a new keyword is a
one-line change that survives a rebuild.

**SQLite, not JSON.** "New since last week" needs identity and history. JSON
files give you neither once the file is regenerated.

**Exclusions are visible.** Four conditions remove a posting entirely rather
than just lowering its score. The report has a toggle that shows them, because
a ranking that silently hides things cannot be argued with.

**Scoring is not clever.** No embeddings, no LLM, no scores that cannot be
reproduced with a calculator. Phrase counting is dumber than a language model
and much easier to trust, and the matched phrases are printed on every card so
a wrong call is visible instead of mysterious.

---

## Known limits

* **Careers pages without JSON-LD give titles only.** The `links` adapter can
  see that "Carbon Analyst — Brussels" exists but not what it says, so those
  postings score on title alone. They rank lower than they deserve.
* **Robots and terms are respected, which costs coverage.** LinkedIn and Indeed
  are excluded by design. That is most of the market.
* **Dutch-language postings are scored low on purpose.** They are not winnable
  yet with Dutch "in progress". If that changes, change one number.
* **The demo snapshot is a snapshot.** It is two pages captured on 12 November
  2026, kept so the tests and the demo do not depend on the internet.
