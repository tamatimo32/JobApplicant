# JobApplicant — CV generation system

A tiny, deterministic pipeline that turns **a job description + the master
experience data** into **a one-page PDF CV that matches Thomas Chacra's
`CV_Master_Format` layout**.

No Word, no HTML, no cloud service. One Python file renders the PDF with
ReportLab, so the output is byte-reproducible and the layout can be verified
numerically against the reference.

---

## TL;DR for an AI picking this up

```bash
pip install reportlab pymupdf fonttools pillow      # once

# 1. read the job description (URL given by the user)
# 2. copy the template folder
cp -r applications/_TEMPLATE applications/<YYYY-MM>-<employer>-<role-slug>

# 3. write applications/<slug>/content.<lang>.json   (see "Content schema")
#    + paste the posting into  applications/<slug>/job_description.<lang>.txt

# 4. render
python3 tools/render_cv.py applications/<slug>/content.<lang>.json \
        "out/Thomas_Chacra_CV_<Employer>_<Role>.pdf"

# 5. look at the PDF, then hand the bullets to the user for verification
```

If `render_cv.py` raises `LayoutOverflow`, the content does not fit on one page.
**Do not scale the fonts.** Cut a bullet or a line — see "Fitting the page".

---

## Repository layout

```
assets/
  reference/CV_Master_Format.pdf   the layout contract (uploaded by the user)
  photo.jpg                        portrait, cropped exactly as in the master
  icons/{pin,phone,mail,car,linkedin}.png
  fonts/Aptos*.ttf                 body + heading substitute (see "Typography")
data/
  experience_master.json           ALL experience, in English, over-complete
tools/
  render_cv.py                     the renderer  (content JSON -> PDF)
  extract_assets.py                rebuilds assets/photo.jpg + assets/icons/*
  compare_to_reference.py          regression test: fixture vs. the master PDF
  fixtures/master_content.json     the master CV's own content, for the test
applications/
  _TEMPLATE/                       empty content file to copy
  2026-11-ulb-enseignement-durabilite/
    content.fr.json                what was sent for the ULB application
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
- **The summary is exactly 4 lines** at 10 pt across 416.5 pt. The renderer
  enforces this.
- **Verification status.** The user asked to review every CV. Leave
  `"_source.verification_status"` in place and, in the chat reply, list every
  bullet that is *not* a verbatim reuse of an already-approved line.

### 4. Render and look at it

```bash
python3 tools/render_cv.py applications/<slug>/content.fr.json out/<name>.pdf
python3 -c "import pymupdf; pymupdf.open('out/<name>.pdf')[0].get_pixmap(dpi=150).save('/tmp/p.png')"
```

Always *look* at the PNG. The numbers can be perfect while something is ugly.

### 5. Deliver

- Keep the PDF in `out/`.
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


  // Each item: icon in {pin,phone,mail,car,linkedin}, text, x (left edge of the
  // TEXT, measured from the master), optional link/href styling, optional size.
  // Do not change the x values unless you re-measure the master.
  "contact": [
    {"icon": "pin",   "text": "1000 Bruxelles, Belgique", "x": 59.78},
    {"icon": "phone", "text": "+32 485315276",            "x": 173.58},
    {"icon": "mail",  "text": "thomaschacra@gmail.com",   "x": 258.35, "link": true},
    {"icon": "car",   "text": "Permis B",                 "x": 385.15},
    {"icon": "linkedin", "text": "www.linkedin.com/in/thomas-chacra/",
                         "x": 449.95, "link": true, "size": 7.0}
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

## Fitting the page

The renderer draws top-down and raises `LayoutOverflow` at two points:

1. the summary needs more than 4 lines;
2. the experience column runs past y = 780 pt, or the sidebar past 786 pt.

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

### Regression test

```bash
python3 tools/compare_to_reference.py
```

It renders `tools/fixtures/master_content.json` (the master CV's own content)
and diffs every text baseline against the reference PDF. Current state:
**max deviation 5.2 pt on a 792 pt page, no structural differences**. If you
change a constant and this gets worse, you broke something.

---

## Typography

| Role | Reference font | What we ship | Why |
| --- | --- | --- | --- |
| Body, job titles, dates, sidebar | **Aptos** | real `Aptos.ttf`, `Aptos-Bold.ttf`, `Aptos-Italic.ttf` | extracted from the master, identical metrics |
| Section headings ("EXPÉRIENCE…") | **Seaford Bold** | `Aptos-Bold` (aliased as `Seaford-Bold`) | Seaford is a commercial Microsoft font, not redistributable |

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
- [ ] PDF metadata: title = `CV — <name>`, subject = the posting reference.
- [ ] Text is selectable and the file is < 500 KB.

---

## Legal / privacy notes

- `assets/photo.jpg` and the icons come from the user's own CV.
- Aptos is distributed by Microsoft; the TTFs here were extracted from the
  user's own document for the sole purpose of reproducing it. Do not publish
  this repo's `assets/fonts/` separately.
- `data/experience_master.json` contains personal data (phone, e-mail,
  employers). Keep the repository private.
