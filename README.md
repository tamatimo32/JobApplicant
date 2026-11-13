# JobApplicant — CV generation system

A tiny, deterministic pipeline that turns **a job description + the master
experience data** into **a one-page PDF CV that matches Thomas Chacra's
`CV_Master_Format` layout**, plus **a one-page motivation letter that matches
`ML_Master_Format`**.

No Word, no HTML, no cloud service. One Python file renders the PDF with
ReportLab, so the output is byte-reproducible and the layout can be verified
numerically against the reference.

> **Before writing any text, read [`STYLE.md`](STYLE.md).** It holds the
> applicant's standing rules: no em dashes, no naming previous employers in the
> letter prose, keep the human register. Those rules override the examples
> given further down in this file.

---

## TL;DR for an AI picking this up

```bash
pip install reportlab pymupdf fonttools pillow      # once

# 1. read the job description (URL given by the user)
# 2. copy the template folder
cp -r applications/_TEMPLATE applications/<YYYY-MM>-<employer>-<role-slug>

# 3. write applications/<slug>/content.<lang>.json   (see "Content schema")
#    + paste the posting into  applications/<slug>/job_description.<lang>.txt

# 4. write applications/<slug>/letter.<lang>.json   (see "Letter schema")

# 5. render both
python3 tools/render_cv.py     applications/<slug>/content.<lang>.json \
        "out/Thomas_Chacra_CV_<Employer>_<Role>.pdf"
python3 tools/render_letter.py applications/<slug>/letter.<lang>.json \
        "out/Thomas_Chacra_Lettre_Motivation_<Employer>_<Role>.pdf"

# 6. look at both PDFs, then hand the wording to the user for verification
```

If `render_cv.py` raises `LayoutOverflow`, the content does not fit on one page.
**Do not scale the fonts.** Cut a bullet or a line — see "Fitting the page".

---

## The job finder

The registry says where to look; the finder reads it, crawls, scores every
posting out of 100, and writes one HTML page with the best ones first.

```bash
python3 tools/jobfinder.py demo                        # offline, 42 postings
python3 tools/jobfinder.py report --run 1 --open
python3 tools/jobfinder.py crawl --countries BE,LU     # the real thing
python3 tools/jobfinder.py crawl --query energy --query internships
python3 tools/jobfinder.py verify                      # are the links still alive?
```

### Running it from PyCharm

The script fixes `sys.path` itself, so it runs from any working directory.
Two ways to set it up:

**Run configuration (recommended).** Run > Edit Configurations > `+` > Python,
then:

| Field | Value |
| --- | --- |
| Script path | `tools/jobfinder.py` |
| Parameters | `demo` |
| Working directory | the repository root |
| Python interpreter | any 3.10+; **no packages to install** |

To see the report, add a second configuration with Parameters
`report --run 1 --open`, or just right-click `out/opportunities.html`.

**PyCharm terminal.** Nothing to activate:

```bash
python3 tools/jobfinder.py demo
python3 tools/jobfinder.py report --run 1 --open
```

**One trap.** `--db` is a *global* option, so it must come **before** the
subcommand:

```bash
python3 tools/jobfinder.py --db data/job_finder/queries.db report --run 1   # correct
python3 tools/jobfinder.py report --run 1 --db data/job_finder/queries.db   # error
```

A **query** is one saved search: a listing URL plus the country, language and
sector its postings inherit. They live in `data/job_finder/queries.json`, so
"the energy page" and "the 0-2 years page" are two queries on one board rather
than two registry rows that must be kept in step.

Standard library only, no install, no API key. Scores are additive and the
arithmetic for each posting is printed in the report, so a wrong ranking is
visible rather than mysterious. Full write-up in `docs/JOB_FINDER.md`, the
formula in `docs/SCORING.md`.

Two things it will not do: scrape LinkedIn or Indeed (their terms forbid it),
and decide for you. It ranks; you read the top twelve.

### If the report lists companies instead of jobs

That was a real bug, fixed 2026-11-13. `SinglePostingAdapter` used to accept
any page with 200+ characters of text, which is every company homepage, so a
registry crawl produced one fake "posting" per company titled with its
marketing strapline. The adapter now requires a vacancy signal in the title or
near the top of the body (job, vacature, offre, sollicit, career, internship,
CDD…), and rejects `Brand | strapline` titles.

If you still see it:

```bash
python3 tools/jobfinder.py crawl --countries BE --limit 5   # watch the output
```

Each source now prints either `N postings via <adapter>` or a reason such as
`! no vacancy list found on the page`. A company homepage is a normal cause:
the registry holds the site root, not a careers URL. Prefer the saved searches
(`--query`) or a source whose `listing_url` points at the careers page.

Two honesty features worth knowing. Postings from the demo snapshots are
labelled **Demo data · captured page** (they are real, just historical), and a
hand-written fixture would be labelled **invented** and never made clickable.
`verify` marks postings whose URL has gone 404, and a dead link stops being
clickable so a filled vacancy cannot keep looking open.

### Never invent a posting

If you add demo data, it must be **captured, not composed**. Save the page,
record its URL and date in `data/job_finder/demo/manifest.json`, and let the
adapter read it. A hand-written fixture is allowed only for a unit test, and
must be labelled `discovered_via="fixture"` so the report refuses to link it.

This is not hypothetical. A composed fixture once produced
`sustenuto.com/careers/sustainability-analyst-brussels`, a polished, plausible
URL for a vacancy that never existed. It scored 99 and sat at the top of a
report, and a reader clicked it and got a 404. The rule that came out of it:
**if nobody fetched it, the report must not present it as real.**

---

## Repository layout

```
assets/
  reference/CV_Master_Format.pdf   the CV layout contract (uploaded by the user)
  reference/ML_Master_Format.pdf   the letter layout contract (uploaded by the user)
  photo.jpg                        portrait, cropped exactly as in the master
  icons/{pin,phone,mail,car,linkedin}.png
  fonts/Aptos*.ttf                 CV body + heading substitute (see "Typography")
  fonts/Calibri-Light.ttf          letter face (real Calibri Light, metric-exact)
data/
  experience_master.json           ALL experience, in English, over-complete
tools/
  jobfinder.py                     job finder CLI   (registry CSV -> ranked HTML)
  serve_report.py                  live preview of the generated report
  job_finder/                      the finder package (docs/JOB_FINDER.md)
  render_cv.py                     CV renderer      (content JSON -> PDF)
  render_letter.py                 letter renderer  (letter JSON  -> PDF)
  extract_assets.py                rebuilds assets/photo.jpg + assets/icons/*
  compare_to_reference.py          CV regression test:     fixture vs. CV_Master_Format
  compare_letter_to_reference.py   letter regression test: fixture vs. ML_Master_Format
  fixtures/master_content.json     the master CV's own content, for the test
  fixtures/letter_content.json     the master letter's own text, for the test
docs/
  JOB_FINDER.md                    how the finder works, and its limits
  SCORING.md                       the ranking formula, in full
data/job_finder/
  demo/                            two page snapshots, so `jobfinder demo` is offline
  opportunities.db                 created on first crawl
applications/
  _TEMPLATE/                       empty content file to copy
  2026-11-ulb-enseignement-durabilite/
    content.fr.json                CV for the ULB application
    letter.fr.json                 motivation letter for the same application
    job_description_fr.txt         the posting as it was at the time
  out/                             generated PDFs (git-ignored)
```

---

## Workflow, step by step

### 1. Read the job description

The user will paste a link. Read it, then write it to
`applications/<slug>/job_description.<lang>.txt` **verbatim**. That file is the
audit trail: six months later nobody can re-open a ULB Efficy page.

Note down: language, seniority, contract type, the 5–8 phrases that recur, and
which of the master roles actually map onto them.

### 2. Choose a language

Render in the language of the posting. ULB / Belgian public bodies = French.
International companies = English. If it is ambiguous, ask.

The `content.<lang>.json` filename carries the language, and the renderer does
no translation — you do it, from `data/experience_master.json`.

### 3. Select and rewrite the content

See `content schema` below. Rules that matter:

- **Never invent a fact.** Every bullet must trace to a `bullets[].en` entry in
  `data/experience_master.json`, or to `profile` / `education`.
- **Retailor, don't translate literally.** The master data says "Built
  automated Excel and Power BI tools supporting ESG and environmental reporting
  workflows"; for a teaching-and-sustainability role that becomes "Conçoit des
  tableaux de bord Power BI et des outils Excel automatisés consolidant les
  données durabilité" — same fact, angled at the posting.
- **5 roles max, 1–3 bullets each.** The page has room for ~12 bullets total.
- **Mirror the posting's vocabulary** where it is truthful (e.g. the ULB posting
  says "transition socio-écologique", "multi-acteurs", "parcours durabilité").
- **No em dashes and no previous-employer names in letter prose.** See
  `STYLE.md`. Check with
  `grep -n '—' applications/<slug>/content.*.json applications/<slug>/letter.*.json`.
- **The summary is 1 to 4 lines** at 10 pt across 416.5 pt (4 is the reference).
  A shorter summary lifts the contact bar automatically, so do not pad it out.
  Anything over 4 lines is refused.
- **Verification status.** The user asked to review every CV. Leave
  `"_source.verification_status"` in place and, in the chat reply, list every
  bullet that is *not* a verbatim reuse of an already-approved line.

### 4. Write the letter

See "Letter schema". The letter is **justified** (as in the master) and the
renderer reproduces Word's line breaking by allowing a small per-gap
compression — that is what makes the line breaks land on the same words as
`ML_Master_Format`. Do not remove `JUSTIFY_COMPRESSION`.

When `"typography": "fr"`, French punctuation spacing is applied
automatically: a narrow no-break space (U+202F) before `; : ! ?` and inside
`« »`. That is correct French typography; keep it.

### 5. Render and look at it

```bash
python3 tools/render_cv.py     applications/<slug>/content.fr.json out/<cv>.pdf
python3 tools/render_letter.py applications/<slug>/letter.fr.json  out/<ml>.pdf
python3 -c "import pymupdf; pymupdf.open('out/<cv>.pdf')[0].get_pixmap(dpi=150).save('/tmp/p.png')"
```

Always *look* at the PNG. The numbers can be perfect while something is ugly.

### 6. Deliver

- Keep both PDFs in `out/`.
- Upload a copy to the user's Google Drive folder
  `1nI7MBzOW5I-5DxKmZG23v8WGq5hW5Ctf` (`google_drive` connector → `upload_file`).
- Present the PDF in the chat.

---

## Content schema

`applications/<slug>/content.<lang>.json`

```jsonc
{
  "_source": {                       // free-form, but keep it: it is the audit trail
    "job": "...", "url": "...", "language": "fr", "date": "YYYY-MM-DD",
    "sources": ["..."], "verification_status": "PENDING USER VERIFICATION"
  },

  "name":    "Thomas Chacra",
  "subtitle": "internal PDF metadata only",
  "title":   "one line, <= 1 line at 11 pt bold across 430 pt",

  // EXACTLY 4 lines. The renderer wraps at 416.5 pt and refuses more.
  // Author it as one string; line breaks are computed.
  "summary": "...",


  // The contact bar ships as TEXT ONLY, no emoji. `icon` is optional legacy:
  // older content files carry it and the renderer ignores it, so you do not
  // have to strip it. `x` is likewise ignored -- the row is laid out
  // automatically from the panel's left edge with a "·" separator, because the
  // master's x values are "after an emoji we no longer draw". Keep the five
  // items to roughly the master's lengths or the row will not fit.
  "contact": [
    {"text": "1000 Bruxelles, Belgique"},
    {"text": "+32 485315276"},
    {"text": "thomaschacra@gmail.com", "link": true},
    {"text": "Permis B"},
    {"text": "www.linkedin.com/in/thomas-chacra/", "link": true, "size": 7.0}
  ],

  "experience_heading": "EXPÉRIENCE PROFESSIONNELLE",

  "experience": [                    // 5 max; the renderer flows them and checks fit
    {
      "title":    "Sustainability Adviser",      // black, bold
      "employer": "Green Stems Products",        // green, bold
      "dates":    "Sept. 2026 – Aujourd'hui",    // small, primary blue
      "context":  "Packaging compostable …",     // italic one-liner
      "bullets":  ["…", "…"]                     // 1–3, wrapped at 363.7 pt
    }
  ],

  "sidebar": [                       // order matters; 5 panels is the design
    {
      "heading": "Compétences clés",
      "type": "text",                // free paragraphs; "\n" = hard break;
      "paras": ["Label : text …"]    // "Label :" renders bold automatically
    },
    {"heading": "Informatique & Data", "type": "skills",
     "lines": ["Power BI, Excel / Power Query,", "SQL, Python, Power Automate"]},
    {"heading": "Soft skills", "type": "bullets",
     "items": ["Esprit analytique", "Rigueur et autonomie", "Communication"]},
    {"heading": "Formation", "type": "education",
     "items": [{"lines": ["M.Sc. …", "Université libre de Bruxelles (ULB)"]}]},
    {"heading": "Langues", "type": "languages",
     "items": [["Français", "Bilingue"], ["Anglais", "Bilingue"], ["Néerlandais", "En cours"]]}
  ]
}
```

Sidebar block types: `text`, `skills`, `bullets`, `education`, `languages`.
Anything else raises.

---

## Letter schema

`applications/<slug>/letter.<lang>.json`

```jsonc
{
  "typography": "fr",          // "fr" turns on French punctuation spacing; "en" = off

  "name":    "THOMAS CHACRA",  // upper-case, 18 pt
  "tagline": "one line",       // 11 pt, under the name
  "place":   "Bruxelles, Belgique",
  "phone":   "+32 485 31 52 76",
  "email":   "thomaschacra@gmail.com",
  "date":    "10/11/2026",

  "addressee": "À l'attention de …, offre … — ULB.",   // 14 pt
  "subject":   "Objet : … — Thomas Chacra",            // 11 pt
  "salutation": "Madame, Monsieur,",                   // 12 pt

  "paragraphs": ["…", "…"],    // 12 pt, justified, blank line between
  "closing":   "Cordialement,",
  "signature": "Thomas Chacra"
}
```

### Length: keep it short

**Target 220 to 300 words, four paragraphs.** The applicant asked for shorter
letters on 2026-11-10, after the first four applications ran to 350 to 372
words. Shorter reads better, and it matches the master, which leaves a third of
the page empty. Do not fill the page just because the page exists.

The four paragraphs, in this order:

1. **The hook and why this job.** One idea about the work itself, then the
   posting's own subject matter named precisely.
2. **The evidence.** Two or three concrete things, with the tools named. This is
   the only dense paragraph.
3. **The honest gap and the logistics.** Say plainly what you have not done yet,
   then languages, location, availability. Reviewers trust the letter more when
   it admits a limit, and postings often ask for a specific confirmation here
   (relocation, office presence, start date).
4. **A one-sentence close.**

`render_letter.py` will accept up to 380 words, but that is a ceiling, not a
target. If a letter passes 300 words, cut a sentence rather than shaving words.

### The house style these letters share

The reference (`ML_Master_Format.pdf`, for Clerens) and the earlier one
(`ML_FEAD.pdf`) are built on the same skeleton, and it works. Keep it:

1. **Open with a hook, never with "Je".** The reference opens *"Most
   bioengineers from my degree would love to bridge technical depth with EU
   policy… I am one of those bioengineers."* The FEAD letter uses the same
   move. It reframes the application as a natural consequence of who you are.
2. **Paragraph 2 = the evidence.** Concrete, one breath: what you did, with
   named frameworks and tools. This is the only paragraph allowed to be dense.
   Describe *where* generically ("dans mes expériences précédentes", "dans mon
   poste actuel"): see `STYLE.md` §2. Employer names belong in the CV.
3. **Paragraph 3 = why this employer.** Name their actual organs and projects
   (for ULB: reACT, SAGE, ARES, TRAN-F201), not generic praise.
4. **Paragraph 4 = the logistics** (languages, availability, eligibility).
5. **Paragraph 5 = a warm close** that offers a conversation and invites
   feedback even on rejection. Both reference letters do this; it reads as
   confident rather than needy.
6. 220–300 words, four paragraphs. See "Length: keep it short" above. The master
   leaves a third of the page empty, so resist filling it.
   `render_letter.py` raises `LayoutOverflow` past y = 730 pt.

Rules of thumb taken from the user's own guidance note
("Contenu d'une bonne lettre de motivation - FR"):

- one A4 page, clear paragraphs, short sentences;
- do not re-narrate the CV — reference it;
- do not start the first sentence with "je";
- start sentences with different words.

## Two traps that produce "misaligned" text

Both of these look like a formatting accident in Word. Neither is. Both are
now guarded, and both guards are exercised by the suite below.

### 1. Justification leaks into the next line (the letter)

`render_letter.py` justifies every body line except a paragraph's last one.
ReportLab's `setWordSpace()` emits a bare `Tw` operator, and per the PDF spec
`Tw` is **unbounded**: it lives in the page graphics state and survives the
`ET` that closes the text object. So the *first unjustified line drawn after a
justified one* silently inherits that word spacing. In the ABB letter this made
the last line of paragraph 2 render 32 pt wider than the measure, and
"…familiar ground." hung past the right margin in Word and every viewer.

The letter is **not** built as a table; it is absolutely positioned text lines.

Guards:

- `reset_spacing()` emits `0 Tc 0 Tw` at the start of every draw, and again
  after each justified line. Do not add a code path that draws text without it.
- `layout_paragraphs()` rejects a paragraph whose final line is wider than the
  measure. `wrap()` deliberately allows `JUSTIFY_COMPRESSION` so a *justified*
  line can be squeezed like Word does, but a last line is never justified, so
  it gets no allowance. If the allowance is what squeezed the final word on,
  the line really is too wide: reword the sentence.
- `assert_inside_margins()` re-opens the finished PDF and fails if any body
  word crosses `BODY_RIGHT`.

### 2. Anything drawn after a resized image inherits its transform

Also worth knowing, same class of bug: if you ever `drawImage` between text
calls, remember ReportLab has already emitted a `cm` for it. Draw all images
(only the photo, now) before the text, or wrap them.

### 3. A 3-line summary used to slide under the bar (fixed)

The bar's y was a constant measured from the reference, whose summary is 4
lines. With a 3-line summary the last line ended ~14 pt above the bar and the
page read as if the text had run into it, while the experience block still
started at a fixed `JOB1_BASE`, leaving a hole right under the bar.

The bar now floats: `bar_geometry(summary_lines)` lifts it by
`BAR_RISE_PER_SPARED_LINE` for each line the summary does not use, so the gap
between the summary and the bar is constant. **A 1 to 4-line summary is
therefore fine**, and you do not need to pad a 3-line summary out to 4 lines.

### 4. The contact-bar backdrop was the sidebar's (fixed)

`draw_contact_bar()` used to call `panel()`, which is hard-wired to the
sidebar's `PANEL_X` / `PANEL_W` (432.0 / 143.6). The bar therefore only ever
had a pale rectangle under its last item. It now draws its own `roundRect` from
`BAR = (x, top, width, height)`. Note `BAR` is a **box**, not `(x, y, w)`: the
third element is a width.

---

## Fitting the page

The renderer draws top-down and raises `LayoutOverflow` at two points:

1. the summary needs more than 4 lines;
2. the experience column runs past y = 780 pt, or the sidebar past 786 pt;
3. the title runs past x = 575 (check with `tw(title, "Aptos-Bold", 11)` first,
   it is cheaper than a failed render);
4. a `skills` block contains a key other than `heading` / `type` / `lines`
   (anything else, a `note` for instance, would be silently dropped);
5. the letter addressee would overprint the date, i.e. it ends past
   `DATE_X - 12` = 464 pt. Keep the addressee short ("To the Hiring Team, ABB
   Electrification Distribution Solutions.") and let the subject line carry
   the posting reference.

Fixes, in order of preference:

1. delete the weakest bullet;
2. shorten a bullet so it loses a wrapped line (a bullet costs 14.5 pt per line);
3. drop the 5th role (the master itself keeps 5; 4 is fine for a niche posting);
4. shorten the summary.

**Never** change font sizes or leading to squeeze content in. The whole point is
that every CV looks identical.

---

## How the template was measured

Everything in `render_cv.py` under "Layout constants" is a measurement, not a
guess. To re-derive any of it:

```bash
python3 - <<'PY'
import pymupdf
p = pymupdf.open('assets/reference/CV_Master_Format.pdf')[0]
for b in p.get_text('dict')['blocks']:
    if b['type'] == 0:
        for l in b['lines']:
            for s in l['spans']:
                print(round(s['origin'][0],2), round(s['origin'][1],2),
                      s['size'], s['font'], repr(s['text'][:50]))
PY
```

`origin` is the **text baseline** in PDF points, from the top-left of a
612 × 792 pt A4 page — which is why the renderer stores baselines, not tops.

Key measurements (page = 612 × 792 pt):

| Element | Value |
| --- | --- |
| Left margin / text column | 36.0 / 43.53 pt, wraps at 421.5 |
| Bullet marker / bullet text | 46.28 / 57.78 pt |
| Body text | Aptos 10 pt, leading 14.5 pt (word-wrapped lines *and* between bullets) |
| Job title baseline → date | 12.25 pt |
| Job title baseline → context | 25.50 pt |
| Job title baseline → first bullet | 48.00 pt |
| Last bullet → next job title | 26.25 pt |
| Header: name / title / summary | 18 pt @ y 57.53 · 11 pt @ y 76.28 · 10 pt @ y 99.03 (+14.25/line) |
| Contact bar | rounded rect (36.9, 147.9) 539.1 × 21.9, r 3.3, text baseline 161.80 |
| Icons | 13.8 pt tall, 2 pt before their text |
| Sidebar panel | x 432.0, width 143.6, radius 4.0, fill `#F1F5F9` |
| Sidebar heading | Aptos-Bold 12 pt (Languages: 11 pt) `#595959` @ rect_top + 15.35 |
| Sidebar rule | `#7F7F7F` 1.25 pt, inset 8.9, at rect_top + 18.75 |
| Main heading | 12 pt `#156082` @ y 187.30, rule 1.5 pt at y 196.3, 40.1 → 423.1 |

Colours sampled at 900 dpi: primary `#156082`, employer green `#4EA72E`,
link `#467886`, sidebar heading `#595959`, panel `#F1F5F9`.

### Letter measurements

`ML_Master_Format.pdf` is also A4 (612 × 792 pt). Everything is **Calibri
Light** — nothing is bold, including the addressee line.

| Element | Value |
| --- | --- |
| Header left/right | name at x 26.40, y 37.80 (18 pt) · tagline y 53.04 (11 pt) |
| Address block | right-aligned to x 583.50, baselines 33.12 / 48.48 / 61.92 (11 pt) |
| Rules | two rectangles at y 77.4–77.9: 25.70→457.40 and 457.90→585.70 (0.5 pt) |
| Body left edge | x 44.40 for every element |
| Justified right edge | x 457.00 (measure = 412.60 pt) |
| Date | x 476.02, y 105.74 (11 pt) |
| Addressee / Subject | y 105.86 (14 pt) / y 120.14 (11 pt) |
| Salutation | y 146.54 (12 pt) |
| Body | 12 pt, leading 14.64, paragraph gap 26.64 |
| Closing / signature | +26.64 / +26.67 after the last paragraph (12 pt) |

### Regression tests

```bash
python3 tools/compare_to_reference.py          # CV
python3 tools/compare_letter_to_reference.py   # letter
```

CV: renders `tools/fixtures/master_content.json` (the master CV's own content)
and diffs every text baseline against the reference. Current state:
**max deviation 5.17 pt on a 792 pt page, 30 spans over tolerance, 10 missing**.
The contact-bar labels are compared on `y` only: their `x` deliberately no
longer matches the reference, which positions each label after an emoji.

Letter: renders `tools/fixtures/letter_content.json`, checks every header
element glyph-accurately and each body paragraph for identical line count,
identical text and identical first baseline. Current state:
**max deviation 0.24 pt; 33/33 lines break on the same words.**

If you change a constant and these get worse, you broke something.

**A clean tree still exits 1 on `--fail` for the CV.** The CV master mixes
12.25 pt and 14.5 pt leading, so a handful of sidebar spans sit 1–5 pt apart and
pymupdf also splits some adjacent spans, which the comparator reports as
`[missing]`. Baseline is: **max deviation 5.17 pt, 30 spans over tolerance,
10 missing** — verify you did not *worsen* those three numbers rather than
expecting a zero exit. A run with those figures is green.
The letter harness (`--fail`, exit 0) has no such caveat and is the stricter of
the two; treat any movement there as a real regression.

---

## Typography

| Role | Reference font | What we ship | Why |
| --- | --- | --- | --- |
| Body, job titles, dates, sidebar | **Aptos** | real `Aptos.ttf`, `Aptos-Bold.ttf`, `Aptos-Italic.ttf` | extracted from the master, identical metrics |
| Section headings ("EXPÉRIENCE…") | **Seaford Bold** | `Aptos-Bold` (aliased as `Seaford-Bold`) | Seaford is a commercial Microsoft font, not redistributable |
| Motivation letters | **Calibri Light** | real `Calibri-Light.ttf` | metric-exact: body line widths match the reference to < 0.1 pt |

Seaford Bold was verified to be a near-perfect stand-in: cap height **8.02 pt
vs 7.89 pt** at 12 pt, and **3.3 % narrower** over the heading string. Side by
side the difference is invisible at 100 %.

If a real `Seaford-Bold.ttf` is ever obtained, drop it in `assets/fonts/` and
point `register_fonts()` at it — nothing else changes.

Icons are the emoji bitmaps lifted from the reference at 600 dpi
(`tools/extract_assets.py`), so they match exactly. They are *raster*: do not
scale them beyond 13.8 pt.

---

## Accessibility / quality checklist before sending

- [ ] One page, nothing below y = 780 pt.
- [ ] `summary` is 4 lines, no orphan word on line 4.
- [ ] No bullet widows (a single word on its own line) — reword to avoid.
- [ ] Employer names present in the posting are spelled exactly as the employer
      spells them.
- [ ] French typography: non-breaking space before `: ; ! ?` is *not* emulated —
      the master does not use it either. Keep `'` as a straight apostrophe, as
      in the master.
- [ ] Dates consistent (`Sept. 2026 – Aujourd'hui`, en dash with spaces).
- [ ] PDF metadata: title = `CV — <name>` / `Lettre de motivation — <name>`,
      subject = the posting reference.
- [ ] Text is selectable and the file is < 500 KB.
- [ ] French letters: punctuation spacing present (` :`, ` ;`, `« … »`).
- [ ] The contact bar carries no emoji: it is text plus a "·" separator, and
      the page holds exactly one image (the photo). `assert_no_icons()` checks
      both on the finished PDF.
- [ ] No body line crosses x = 457. `assert_inside_margins()` checks the
      finished letter, and `layout_paragraphs()` checks the last line of every
      paragraph before drawing.
- [ ] No em dash anywhere in the prose (`grep -n '—'`); only the CV's structural
      `Title — Employer` separator may contain one.
- [ ] The letter does not name previous employers; it says "mes expériences
      précédentes" or similar.
- [ ] The `skills` sidebar blocks carry only `heading` / `type` / `lines`;
      a `note` key is rejected by the renderer (it used to vanish silently).
- [ ] The title fits: it must end before x = 575, otherwise `LayoutOverflow`.
- [ ] The letter is 220 to 300 words and four paragraphs (see "Length: keep it
      short"); a long letter is the commonest way these go wrong.
- [ ] Register is professional, not chatty: medium sentences (mean 18-22 words,
      almost none over 30), no rhetorical questions, no performed honesty, no
      invented numbers. See `STYLE.md` §3.
- [ ] No AI tells: "passionné par", "fort de mon expérience", "je suis convaincu
      que", or three-item lists in every sentence.
- [ ] The letter and the CV tell the same story with the same job titles.

## Legal / privacy notes

- `assets/photo.jpg` and the icons come from the user's own CV.
- Aptos is distributed by Microsoft; the TTFs here were extracted from the
  user's own document for the sole purpose of reproducing it. Do not publish
  this repo's `assets/fonts/` separately.
- `data/experience_master.json` contains personal data (phone, e-mail,
  employers). Keep the repository private.
