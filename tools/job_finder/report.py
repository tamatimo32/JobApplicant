"""Render the ranked result as one self-contained HTML file.

Constraints that shaped this:

* **No network.** The page must work on a phone, on a train, in a country
  where the CDN is blocked. Every byte of CSS and JS is inline.
* **No build step.** Python writes the file; double-clicking it opens it.
* **Explainable.** Each card can expand into the exact arithmetic that
  produced its score, because a ranking you cannot audit is a horoscope.
* **Readable at 380 px.** The card layout is a single column below 760 px;
  the table of sources collapses into a list.
"""

from __future__ import annotations

import html
import json
from datetime import date, datetime
from pathlib import Path

from . import config as C
from .model import Breakdown
from .store import Store

BAND_TEXT = {name: text for name, _, text in C.BANDS}
BAND_FLOOR = {name: floor for name, floor, _ in C.BANDS}


def esc(value) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def _band_counts(rows: list[dict]) -> dict[str, int]:
    out = {name: 0 for name, _, _ in C.BANDS}
    for r in rows:
        out[r.get("band") or "D"] = out.get(r.get("band") or "D", 0) + 1
    return out


def render(db_path: Path, out_path: Path, *, run_id: int | None = None,
           title: str = "Ranked opportunities",
           include_excluded: bool = False, top_n: int = C.TOP_N_FOR_HIGHLIGHTS,
           limit: int = 400) -> Path:
    store = Store(db_path)
    rows = store.ranked(limit=limit, include_excluded=include_excluded,
                        new_since_run=run_id)
    excluded_rows = store.ranked(limit=200, include_excluded=True,
                                 new_since_run=run_id)
    excluded_rows = [r for r in excluded_rows if r["excluded"]]
    stats = store.stats()

    highlights = [r for r in rows if not r["excluded"]][:top_n]
    bands = _band_counts(rows + excluded_rows)

    health: list[dict] = []
    if run_id:
        health = store.source_health(run_id)

    body = [
        _header(title, rows, stats, bands, run_id),
        _highlight_strip(highlights),
        _filters(rows),
        '<main id="list">',
        *[_card(r) for r in rows],
        "</main>",
        _sources_section(health),
        _method_section(),
        _footer(stats),
    ]

    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<style>{CSS}</style>
</head>
<body>
{''.join(body)}
<script>{JS}</script>
</body>
</html>
"""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(doc, encoding="utf-8")
    return out_path


# --------------------------------------------------------------------------- #
# sections
# --------------------------------------------------------------------------- #

def _header(title, rows, stats, bands, run_id) -> str:
    generated = datetime.now().strftime("%d %B %Y, %H:%M")
    new = sum(1 for r in rows if r.get("is_new"))
    chips = "".join(
        f'<span class="chip chip-{name.lower()}">{name} · {bands.get(name, 0)}</span>'
        for name, _, _ in C.BANDS)
    return f"""
<header class="hero">
  <div class="wrap">
    <p class="kicker">Job source registry · {stats['runs']} run(s) since {generated}</p>
    <h1>{esc(title)}</h1>
    <p class="lede">{stats['scored']} postings scored out of 100 on skills,
    seniority, location, language, employer and freshness. {len(rows)} are
    shown here; the top block is what to read first, everything below can be
    filtered.</p>
    <div class="chips">{chips}</div>
    <div class="statline">
      <div><b>{stats['scored'] - stats['excluded']}</b><span>scored and kept</span></div>
      <div><b>{new}</b><span>new this run</span></div>
      <div><b>{stats['excluded']}</b><span>excluded</span></div>
      <div><b>{stats['runs']}</b><span>runs recorded</span></div>
    </div>
  </div>
</header>"""


def _highlight_strip(highlights) -> str:
    if not highlights:
        return ""
    cards = "".join(f"""
    <a class="hi" href="{esc(r['url'])}" target="_blank" rel="noopener">
      <span class="hi-score">{r['total']}</span>
      <span class="hi-body">
        <span class="hi-title">{esc(r['title'])}</span>
        <span class="hi-meta">{esc(r['employer'])} · {esc(r['country'])}</span>
      </span>
    </a>""" for r in highlights[:6])
    return f"""
<section class="wrap highlights">
  <h2>Start here</h2>
  <div class="hi-grid">{cards}</div>
</section>"""


def _filters(rows) -> str:
    countries = sorted({r["country"] for r in rows if r["country"]})
    bands = [b for b, _, _ in C.BANDS]
    opts = "".join(f'<option value="{esc(c)}">{esc(c)}</option>' for c in countries)
    bopts = "".join(f'<option value="{b}">Band {b}</option>' for b in bands)
    return f"""
<section class="wrap controls">
  <input id="q" type="search" placeholder="Filter by title, employer or keyword…"
         aria-label="Filter postings">
  <select id="country" aria-label="Country"><option value="">All countries</option>{opts}</select>
  <select id="band" aria-label="Band"><option value="">All bands</option>{bopts}</select>
  <label class="toggle"><input type="checkbox" id="newonly"> New this run</label>
  <label class="toggle"><input type="checkbox" id="excl"> Show excluded</label>
  <span id="count" class="count"></span>
</section>"""


def _card(r: dict) -> str:
    band = (r.get("band") or "D").lower()
    matched = [m for m in _load_json(r.get("matched"), []) if "keyword" in m]
    reasons = _load_json(r.get("reasons"), [])
    reasons = [x for x in reasons if isinstance(x, str)]
    kw = " · ".join(m["keyword"] for m in matched[:5]) or "no keyword hit"
    age = _age(r.get("posted"))
    meta = [esc(r.get("employer") or "employer unknown"), esc(r.get("country") or "?")]
    if r.get("location"):
        meta.append(esc(r["location"]))
    if age:
        meta.append(esc(age))
    if r.get("salary"):
        meta.append(esc(r["salary"]))

    badge = ""
    if r.get("is_new"):
        badge = '<span class="badge new">New</span>'
    if r.get("excluded"):
        badge += '<span class="badge off">Excluded · %s</span>' % esc(
            r.get("exclude_reason", ""))
    if r.get("adapter") == "single":
        badge += '<span class="badge soft">Title read from page heading</span>'

    bars = _bars(r, matched)

    return f"""
<article class="card band-{band}" data-country="{esc(r.get('country'))}"
         data-band="{esc(r.get('band'))}" data-new="{1 if r.get('is_new') else 0}"
         data-excluded="{1 if r.get('excluded') else 0}"
         data-text="{esc((r.get('title','') + ' ' + (r.get('employer') or '') + ' ' + kw).lower())}">
  <div class="score"><b>{r.get('total', 0)}</b><span>/100</span></div>
  <div class="body">
    <h3><a href="{esc(r.get('url'))}" target="_blank" rel="noopener">{esc(r.get('title'))}</a></h3>
    <p class="meta">{' · '.join(meta)}</p>
    <p class="kw">{esc(kw)}</p>
    <p class="verdict">{esc(BAND_TEXT.get(r.get('band'), ''))}{badge}</p>
    <details><summary>Why this score</summary>
      <div class="bars">{bars}</div>
      <pre class="audit">{esc(chr(10).join(reasons))}</pre>
    </details>
  </div>
</article>"""


def _bars(r, matched) -> str:
    parts = [
        ("Keywords", r.get("s_keyword", 0), C.MAX_KEYWORD),
        ("Seniority", r.get("s_seniority", 0), C.MAX_SENIORITY),
        ("Location", r.get("s_geography", 0), C.MAX_GEOGRAPHY),
        ("Employer", r.get("s_employer", 0), C.MAX_EMPLOYER),
        ("Language", r.get("s_language", 0), C.MAX_LANGUAGE),
        ("Freshness", r.get("s_freshness", 0), C.MAX_FRESHNESS),
        ("Penalties", r.get("s_penalties", 0), 25),
    ]
    out = []
    for label, value, ceiling in parts:
        value = int(value or 0)
        pct = max(0, min(100, round(100 * value / ceiling)))
        cls = "neg" if value < 0 else "pos"
        out.append(
            f'<div class="bar"><span class="lbl">{esc(label)}</span>'
            f'<span class="track"><i class="{cls}" style="width:{pct}%"></i></span>'
            f'<span class="val">{value:+d}</span></div>')
    return "".join(out)


def _sources_section(health: list[dict]) -> str:
    if not health:
        return ""
    ok = sum(1 for h in health if not h.get("error"))
    rows = "".join(
        f'<tr class="{"bad" if h.get("error") else ""}">'
        f'<td>{esc(h.get("name"))}</td>'
        f'<td>{esc(h.get("adapter") or "—")}</td>'
        f'<td>{h.get("postings", 0)}</td>'
        f'<td>{esc(h.get("error") or "ok")}</td></tr>'
        for h in health)
    return f"""
<section class="wrap sources">
  <h2>Sources this run <small>{ok} of {len(health)} answered</small></h2>
  <p class="note">A source that errors is not a dead end, it is a note to check
  by hand. Blocked means robots.txt said no, and that is respected.</p>
  <div class="tablewrap"><table>
    <thead><tr><th>Source</th><th>Adapter</th><th>Postings</th><th>Result</th></tr></thead>
    <tbody>{rows}</tbody>
  </table></div>
</section>"""


def _method_section() -> str:
    rows = "".join(
        f"<tr><td>{esc(label)}</td><td>{mx}</td><td>{esc(why)}</td></tr>"
        for label, mx, why in [
            ("Keyword relevance", C.MAX_KEYWORD,
             "CV and degree keywords, weighted 3/2/1, with diminishing returns "
             "and a bonus when a core term is in the job title"),
            ("Seniority fit", C.MAX_SENIORITY,
             "graduate level scores highest, senior and executive are negative"),
            ("Location", C.MAX_GEOGRAPHY,
             "Belgium 15, Luxembourg 13, Switzerland 11, UAE 10, Australia and "
             "New Zealand 9, remote 12"),
            ("Language", C.MAX_LANGUAGE,
             "English and French 10, Dutch 3, German 1"),
            ("Employer type", C.MAX_EMPLOYER,
             "small consultancies and energy or water utilities score highest"),
            ("Freshness", C.MAX_FRESHNESS,
             "linear from 8 points today to 0 at 60 days"),
            ("Penalties", -25,
             "unpaid, commission-only, senior wording, fluent Dutch or German, "
             "deadline passed"),
        ])
    return f"""
<section class="wrap method">
  <h2>How the number is made</h2>
  <p class="note">Additive, out of 100, clamped at zero. Nothing is hidden:
  open any card and the arithmetic is printed for that posting.
  Full write-up in <code>docs/SCORING.md</code>.</p>
  <div class="tablewrap"><table>
    <thead><tr><th>Component</th><th>Max</th><th>Rule</th></tr></thead>
    <tbody>{rows}</tbody>
  </table></div>
  <p class="note">Excluded, not merely down-ranked: executive roles, anything
  asking for more than five years, commission-only work, and passed deadlines.
  Exclusions can be shown with the toggle above.</p>
</section>"""


def _footer(stats) -> str:
    return f"""
<footer class="wrap">
  <p>Generated {datetime.now():%d %B %Y at %H:%M} by
  <code>tools/job_finder</code>. {stats['postings']} postings in the database,
  {stats['scored']} scored. Scores are advice, not verdicts: read the posting
  before deciding.</p>
</footer>"""


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #

def _load_json(raw, fallback):
    if not raw:
        return fallback
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return fallback


def _age(posted) -> str:
    if not posted:
        return ""
    try:
        d = date.fromisoformat(posted)
    except ValueError:
        return ""
    days = (date.today() - d).days
    if days <= 0:
        return "posted today"
    if days == 1:
        return "posted yesterday"
    if days < 30:
        return f"posted {days} days ago"
    return f"posted {days // 30} month(s) ago"


# --------------------------------------------------------------------------- #
# CSS and JS, inline by design
# --------------------------------------------------------------------------- #

CSS = """
:root{
  --ink:#14171c; --ink-soft:#5b6270; --line:#e3e6ec; --bg:#f6f7f9;
  --card:#fff; --a:#0f9d6b; --b:#2f7ed8; --c:#c08a17; --d:#8b8f98;
  --neg:#c2453f; --accent:#12324f;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,
  "Helvetica Neue",Arial,sans-serif}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px}
a{color:inherit}
h1,h2,h3{line-height:1.2;margin:0}
small{font-weight:400;color:var(--ink-soft)}

.hero{background:var(--accent);color:#fff;padding:40px 0 30px}
.kicker{text-transform:uppercase;letter-spacing:.12em;font-size:11px;
  opacity:.72;margin:0 0 10px}
.hero h1{font-size:clamp(26px,4.4vw,40px);letter-spacing:-.02em}
.lede{max-width:62ch;opacity:.86;margin:12px 0 18px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:22px}
.chip{font-size:12px;padding:4px 10px;border-radius:999px;background:#ffffff17;
  border:1px solid #ffffff2e}
.statline{display:flex;gap:26px;flex-wrap:wrap;
  border-top:1px solid #ffffff24;padding-top:16px}
.statline div{display:flex;flex-direction:column}
.statline b{font-size:22px}
.statline span{font-size:12px;opacity:.7}

.highlights{padding:34px 0 6px}
.highlights h2{font-size:15px;text-transform:uppercase;letter-spacing:.1em;
  color:var(--ink-soft);margin-bottom:14px}
.hi-grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}
.hi{display:flex;gap:12px;align-items:center;background:var(--card);
  border:1px solid var(--line);border-radius:12px;padding:12px 14px;
  text-decoration:none;transition:transform .12s ease, box-shadow .12s ease}
.hi:hover{transform:translateY(-2px);box-shadow:0 6px 18px #14171c14}
.hi-score{font-weight:700;font-size:20px;color:var(--a);min-width:38px}
.hi-body{display:flex;flex-direction:column;min-width:0}
.hi-title{font-weight:600;font-size:14px;overflow:hidden;text-overflow:ellipsis;
  white-space:nowrap}
.hi-meta{font-size:12px;color:var(--ink-soft);overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}

.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;
  padding:26px 20px 18px;position:sticky;top:0;background:var(--bg);
  z-index:5;border-bottom:1px solid var(--line)}
.controls input[type=search]{flex:1 1 260px;min-width:0}
.controls input,.controls select{font:inherit;padding:9px 12px;border-radius:9px;
  border:1px solid var(--line);background:#fff;color:var(--ink)}
.toggle{display:flex;gap:6px;align-items:center;font-size:14px;color:var(--ink-soft)}
.count{font-size:13px;color:var(--ink-soft);margin-left:auto}

.card{display:flex;gap:18px;background:var(--card);border:1px solid var(--line);
  border-left:4px solid var(--d);border-radius:12px;padding:16px 18px;
  margin:12px 0;transition:box-shadow .12s ease}
.card:hover{box-shadow:0 4px 16px #14171c0f}
.card.band-a{border-left-color:var(--a)}
.card.band-b{border-left-color:var(--b)}
.card.band-c{border-left-color:var(--c)}
.card.off{opacity:.6}
.score{min-width:64px;text-align:center;display:flex;flex-direction:column;
  justify-content:center}
.score b{font-size:26px;letter-spacing:-.02em}
.score span{font-size:11px;color:var(--ink-soft)}
.body{min-width:0;flex:1}
.card h3{font-size:17px;font-weight:650}
.card h3 a{text-decoration:none}
.card h3 a:hover{text-decoration:underline}
.meta{margin:4px 0 6px;font-size:13px;color:var(--ink-soft)}
.kw{margin:0;font-size:12px;color:var(--a);font-weight:600}
.verdict{margin:8px 0 0;font-size:13px;display:flex;gap:8px;flex-wrap:wrap;
  align-items:center}
.badge{font-size:11px;padding:2px 8px;border-radius:999px;background:var(--bg);
  border:1px solid var(--line);color:var(--ink-soft)}
.badge.new{background:#0f9d6b1a;border-color:#0f9d6b55;color:#0b7a53;font-weight:600}
.badge.off{background:#c2453f14;border-color:#c2453f44;color:#a4342f}

details{margin-top:10px}
summary{cursor:pointer;font-size:13px;color:var(--ink-soft)}
.bars{display:grid;gap:5px;margin:12px 0 8px}
.bar{display:grid;grid-template-columns:96px 1fr 40px;gap:10px;
  align-items:center;font-size:12px}
.bar .lbl{color:var(--ink-soft)}
.bar .track{background:var(--bg);border-radius:4px;height:8px;overflow:hidden}
.bar i{display:block;height:100%;border-radius:4px;background:var(--b)}
.bar i.neg{background:var(--neg)}
.bar .val{text-align:right;font-variant-numeric:tabular-nums}
.audit{background:var(--bg);border:1px solid var(--line);border-radius:8px;
  padding:10px 12px;font-size:12px;line-height:1.55;overflow-x:auto;
  white-space:pre-wrap;color:var(--ink-soft)}

.sources,.method{padding:34px 0}
.sources h2,.method h2{font-size:18px;margin-bottom:6px}
.note{font-size:13px;color:var(--ink-soft);max-width:70ch}
.tablewrap{overflow-x:auto;margin-top:12px}
table{border-collapse:collapse;width:100%;font-size:13px;background:#fff;
  border:1px solid var(--line);border-radius:10px}
th,td{text-align:left;padding:8px 12px;border-bottom:1px solid var(--line)}
th{font-size:11px;text-transform:uppercase;letter-spacing:.08em;
  color:var(--ink-soft);font-weight:600}
tr.bad td{background:#c2453f0a}
footer{padding:30px 20px 60px;font-size:12px;color:var(--ink-soft)}
code{background:#00000008;padding:1px 5px;border-radius:4px;font-size:.92em}
.hide{display:none !important}

@media (max-width:760px){
  .hero{padding:28px 0 22px}
  .card{flex-direction:row;gap:12px;padding:14px}
  .score{min-width:50px}
  .score b{font-size:21px}
  .controls{position:static;padding:18px 20px}
  .count{margin-left:0}
  .bar{grid-template-columns:80px 1fr 34px}
}
@media print{
  .controls,.highlight-strip{display:none}
  .card{break-inside:avoid;box-shadow:none}
}
"""

JS = """
(function(){
  const q=document.getElementById('q'),
        c=document.getElementById('country'),
        b=document.getElementById('band'),
        n=document.getElementById('newonly'),
        e=document.getElementById('excl'),
        cards=[...document.querySelectorAll('.card')],
        count=document.getElementById('count');

  function apply(){
    const term=q.value.trim().toLowerCase();
    let shown=0;
    cards.forEach(card=>{
      const okText=!term||card.dataset.text.includes(term);
      const okC=!c.value||card.dataset.country===c.value;
      const okB=!b.value||card.dataset.band===b.value;
      const okN=!n.checked||card.dataset.new==='1';
      const okE=e.checked||card.dataset.excluded!=='1';
      const vis=okText&&okC&&okB&&okN&&okE;
      card.classList.toggle('hide',!vis);
      if(vis) shown++;
    });
    count.textContent=shown+' shown';
  }
  [q,c,b,n,e].forEach(el=>{
    el.addEventListener(el.tagName==='INPUT'&&el.type==='checkbox'?'change':'input',apply);
    el.addEventListener('change',apply);
  });
  apply();
})();
"""
