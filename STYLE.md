# Standing rules for written content

These are the applicant's own instructions. They override any stylistic habit
of the model, and they apply to **every** CV and letter from now on.

Read this file before writing `content.<lang>.json` or `letter.<lang>.json`.

---

## 1. Never use em dashes

No `—` anywhere in text the applicant will send: CV summary, bullets, sidebar,
letter paragraphs, subject line, addressee line.

This is not a preference about typography. Em dashes have become a tell for
machine-written text, and the applicant does not want to sound machine-written.

Do not swap the em dash for an en dash, a double hyphen, or a spaced hyphen
either. **Rewrite the sentence so no dash is needed.** That is almost always
better prose anyway:

| Instead of | Write |
| --- | --- |
| `l'analyse technique — carbone, énergie, données ESG — et la traduction` | `l'analyse technique (carbone, énergie, données ESG) et la traduction` |
| `un jury mixte — un exercice de pédagogie` | `un jury mixte, un exercice de pédagogie` |
| `offre 2026/129CDD — ULB` | `offre 2026/129CDD, ULB` |

Preferred substitutes, in order: recast the clause, commas, a colon, brackets.

### One deliberate exception

The line that introduces a job in the CV is `Title — Employer` and that
separator is part of the master layout (`CV_Master_Format.pdf`), rendered by
`render_cv.py`. It is structural, not prose, and it stays. If the applicant
ever asks for that separator to go as well, change it there and nowhere else.

Check before every delivery:

```bash
grep -n '—' applications/<slug>/content.*.json applications/<slug>/letter.*.json
```

The only acceptable hit is the rendered job-title separator, which is generated
by the renderer and never typed into the JSON.

---

## 2. Do not name previous employers in the letter's prose

In a motivation letter, do not write "Chez BetterBusiness, j'ai…" or
"At Vertiberry, I…".

Refer to the experience generically:

- French: "lors de mes expériences précédentes", "dans mon expérience en
  conseil", "au cours de mes années de recherche", "dans un précédent poste".
- English: "in my previous experiences", "in my consulting work", "during my
  research years", "in a previous role".

Reasons this works better:

- the reader does not know those companies, so the names cost attention and
  buy nothing;
- naming a competitor or a small unknown firm can only invite comparisons;
- it keeps the letter about the applicant and the addressee, not about a list.

**Employer names still belong in the CV**, where the recruiter expects them.
This rule is about the letter's prose only.

When the employer *is* the point (for instance a role that is a direct
continuation of one of them), say so without the name: "dans mon poste actuel
d'adviseur durabilité".

---

## 3. Keep the human register

The applicant explicitly liked the tone produced so far and asked for it to be
kept. That means:

- first person, plain words, no corporate gloss;
- one opinion or small admission is welcome ("un chiffre ne suffit pas");
- sentence lengths should vary. Some short. Some longer, provided they stay
  readable;
- concrete nouns and numbers beat adjectives. "ISO 14067" is worth more than
  "solide expertise";

Avoid the tells:

- "passionné par", "je suis convaincu que", "fort de mon expérience de",
  "dans un monde en constante évolution";
- English: "I am passionate about", "leverage", "seamless", "delve",
  "in today's fast-paced world", "I am thrilled to";
- three-item lists in every sentence. One is fine, in one place;
- starting consecutive sentences with the same word, especially "Je";
- closing with "n'hésitez pas à me contacter". The applicant's own letters end
  by inviting a conversation and, unusually, by welcoming feedback even on
  rejection. Keep that move, it reads as confident rather than desperate.

A useful test before delivering: read one paragraph out loud. If it could not
have been said by a person in a conversation, rewrite it.

---

## 4. Everything already true from README still applies

Layout fidelity, one page, `LayoutOverflow` instead of shrinking fonts,
verification flags, French punctuation spacing. See `README.md`.

---

## 4. No emoji, no icon images

The contact bar on the CV carries **text only**, separated by a middle dot
(`·`). The emoji bitmaps that the original master used (pin, phone, mail, car,
LinkedIn) are no longer drawn. Reasons: they are raster, they render
inconsistently across viewers, and they date the document.

`tools/render_cv.py` enforces this: `assert_no_icons()` fails the render if the
page holds any image besides `assets/photo.jpg`. The `icon` key in a content
file is ignored, so old files keep working.

**The photo stays.** "No images" means no emoji; the applicant's portrait is
part of the template.

### Sidebar headings are one line, so keep them short

A sidebar heading is drawn once at 12 pt and never wrapped. A long one does not
error usefully: it runs straight through the rounded edge of the panel. The
Amazon CV shipped `Stakeholders & communication` (172.3 pt wide) into a panel
that only offers 129.2 pt, and the text was sliced off at the page edge.

`tools/render_cv.py` now measures every sidebar heading before drawing it and
raises `LayoutOverflow` when it does not fit with 6 pt to spare. Keep headings
to two words where possible (`Stakeholder work`, not `Stakeholders and
communication`). The same limit applies to `Languages`, which renders its
heading at 11 pt.

## 5. No tables in the letter

The motivation letter is absolute-positioned text lines, not a table, and it
must stay that way. If a line looks "misaligned" (a word hanging past the right
margin), the cause is in the renderer, not the content: see the "Two traps"
section of `README.md`. Never fix it by adding a table, a column, or manual
spaces.

## 6. Motivation letters stay short

**220 to 300 words, four paragraphs.** The four letters written before
2026-11-10 ran to 350 to 372 words; the applicant asked for shorter ones. Aim
for the lower half of the range.

What this means in practice: one dense evidence paragraph, not two. Cut any
sentence that only restates the CV. A one-sentence close is enough. The page
stays two-thirds full and that is correct, not an oversight.

The detailed four-paragraph structure is in `README.md`, under
"Length: keep it short".
