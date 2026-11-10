#!/usr/bin/env python3
"""
render_letter.py — build a motivation letter that reproduces the
ML_Master_Format layout exactly.

Usage
-----
    python3 tools/render_letter.py <letter.json> <output.pdf>

Every constant below was measured from assets/reference/ML_Master_Format.pdf
(A4, 612 x 792 pt). Do not eyeball changes — re-measure first, see README.md.

The letter is single-page; the renderer raises LayoutOverflow if the copy runs
past the signature block.
"""
from __future__ import annotations

import json
import pathlib
import sys
from dataclasses import dataclass
from typing import Sequence

from reportlab.lib.colors import Color, HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"

PAGE_W, PAGE_H = 612.0, 792.0

BLACK = HexColor("#000000")

# French typography: a narrow no-break space (U+202F) before ; : ! ? and inside
# guillemets. ReportLab's word-splitting only breaks on ASCII space, so U+202F
# keeps the pair together automatically.
NNBSP = "\u202f"


def french_spacing(text: str) -> str:
    """Apply French punctuation spacing to a line of text."""
    import re
    # «  text  »   and   text ;  text :  text !  text ?
    text = re.sub(r"« ", "«" + NNBSP, text)
    text = re.sub(r" »", NNBSP + "»", text)
    text = re.sub(r" ([;:!?])", NNBSP + r"\1", text)
    return text

# --------------------------------------------------------------------------- #
# Layout constants, in points, measured from the reference
# --------------------------------------------------------------------------- #
HEADER_X = 26.40                  # left edge of name + tagline
NAME_BASE, NAME_SIZE = 37.80, 18.0
TAGLINE_BASE, TAGLINE_SIZE = 53.04, 11.0

HEADER_RIGHT = 583.50             # right edge of the address block
PLACE_BASE, PHONE_BASE, EMAIL_BASE = 33.12, 48.48, 61.92
ADDRESS_SIZE = 11.0

RULE_Y, RULE_X0, RULE_X1, RULE_W = 77.65, 25.70, 585.70, 0.5

BODY_X = 44.40                    # left edge of every body element
BODY_RIGHT = 457.00               # justified right edge of the paragraphs
BODY_W = BODY_RIGHT - BODY_X      # 412.6

DATE_X = 476.02                   # the reference pads the date with ~174 spaces; use explicit x
DATE_BASE, DATE_SIZE = 105.74, 11.0

ADDRESSEE_BASE, ADDRESSEE_SIZE = 105.86, 14.0
SUBJECT_BASE, SUBJECT_SIZE = 120.14, 11.0

SALUTATION_BASE = 146.54
SALUTATION_SIZE = 12.0

PARA_FIRST_BASE = 173.18
PARA_SIZE, PARA_LEAD = 12.0, 14.64
PARA_GAP = 26.64                  # last baseline of a para -> first of the next

CLOSING_SIZE = 12.0
SIGNATURE_SIZE = 12.0
CLOSING_GAP = 26.64               # last paragraph baseline -> closing baseline
SIGNATURE_GAP = 26.67             # closing baseline -> signature baseline

BOTTOM_LIMIT = 730.0              # leave the last third of the page empty, as in the master


class LayoutOverflow(RuntimeError):
    pass


class StyleViolation(RuntimeError):
    pass


EM_DASH = "\u2014"

# Employers must not be named in the letter prose (STYLE.md §2).
PREVIOUS_EMPLOYERS = ("Green Stems", "BetterBusiness", "Better Business",
                      "Vertiberry", "Deplasse", "Kaspard")


def check_style(d: dict) -> list[str]:
    """Enforce STYLE.md §1 (no em dashes) and §2 (no employer names in prose)."""
    offenders: list[str] = []
    fields = ("tagline", "addressee", "subject", "salutation",
              "paragraphs", "closing")
    for field in fields:
        value = d.get(field)
        values = value if isinstance(value, list) else [value]
        for v in values:
            if not isinstance(v, str):
                continue
            if EM_DASH in v:
                offenders.append(f"{field}: em dash -> {v[:70]!r}")
            for employer in PREVIOUS_EMPLOYERS:
                if employer.lower() in v.lower():
                    offenders.append(
                        f"{field}: names previous employer {employer!r} "
                        f"(use 'mes expériences précédentes') -> {v[:60]!r}")
    return offenders


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("Calibri-Light", str(FONTS / "Calibri-Light.ttf")))


def tw(text: str, size: float) -> float:
    return pdfmetrics.stringWidth(text, "Calibri-Light", size)


# Word's justifier will *compress* a line slightly to keep an extra word on it.
# The reference letter shows this: "…bridge technical depth with EU policy," is
# 420.87 pt of natural text forced into the 412.6 pt measure (‑0.64 pt per
# gap). Allowing the same compression is what makes our line breaks land on the
# same words as the master.
JUSTIFY_COMPRESSION = 0.75        # pt of shrink allowed per inter-word gap


def wrap(text: str, size: float, max_w: float) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines, cur = [], words[0]
    for w in words[1:]:
        cand = f"{cur} {w}"
        gaps = cand.count(" ")
        # a line fits if it ends up at or under the measure, or if the
        # overhang can be absorbed by squeezing the gaps
        if tw(cand, size) <= max_w + gaps * JUSTIFY_COMPRESSION:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def reset_spacing(c: canvas.Canvas) -> None:
    """Clear character and word spacing in the page graphics state.

    ReportLab's `setWordSpace` emits a bare `Tw` operator, which the PDF spec
    says is *unbounded*: it lives in the page state and survives the `ET` that
    ends the text object. So a justified line leaves a non-zero word space
    behind, and the next `drawString` (an unjustified last line, the date, the
    signature) silently inherits it. That is what pushed the last line of body
    paragraph 2 past the right margin ("...familiar ground." widened by 32 pt).
    Every draw path now clears it first.
    """
    # Canvas exposes no public setter for the *page* state (setWordSpace only
    # exists on a text object), so emit the operators directly.
    c._code.append("0 Tc 0 Tw")


def draw(c: canvas.Canvas, x: float, baseline: float, text: str, size: float,
         right_align_to: float | None = None, justify_to: float | None = None,
         french: bool = True) -> None:
    """Draw one line. The reference letters are fully justified, so every line
    except the last of a paragraph is stretched to BODY_RIGHT."""
    reset_spacing(c)
    if french:
        text = french_spacing(text)
    c.setFont("Calibri-Light", size)
    c.setFillColor(BLACK)
    y = PAGE_H - baseline

    if right_align_to is not None:
        c.drawRightString(right_align_to, y, text)
        return

    if justify_to is not None and " " in text:
        natural = tw(text, size)
        gaps = text.count(" ")
        extra = (justify_to - BODY_X - natural) / gaps if gaps else 0.0
        if abs(extra) > 0.01:
            t = c.beginText(BODY_X, y)
            t.setFont("Calibri-Light", size)
            t.setFillColor(BLACK)
            t.setWordSpace(extra)
            t.textOut(text)
            c.drawText(t)
            reset_spacing(c)
            return

    c.drawString(x, y, text)


def assert_inside_margins(pdf_path: str) -> None:
    """Post-render check: no body line may cross BODY_RIGHT.

    Catches both of the ways this has gone wrong: a non-zero word space leaking
    in from a justified line, and a paragraph whose last line was allowed to
    overhang because `wrap` used its compression allowance. Deliberately scoped
    to the body band, because the header block (name, address, date) is
    right-aligned to a different edge.
    """
    try:
        import pymupdf
    except ImportError:  # pragma: no cover
        print("  (pymupdf not installed: skipping the margin check)")
        return
    doc = pymupdf.open(pdf_path)
    page = doc[0]
    lo, hi = PARA_FIRST_BASE - 20.0, BOTTOM_LIMIT
    bad = []
    for w in page.get_text("words"):
        x0, y0, x1, _ = w[:4]
        # y in pymupdf is measured from the top; baselines here are top-down too
        if lo <= y0 <= hi and x0 >= BODY_X - 1.0 and x1 > BODY_RIGHT + 0.5:
            bad.append((round(x1, 1), w[4]))
    if bad:
        raise LayoutOverflow(
            "text crosses the right margin at x = "
            f"{BODY_RIGHT:.1f} pt: {bad[:6]}. Two known causes: a word space "
            "leaking out of a justified line (see reset_spacing), or a "
            "paragraph whose last line was squeezed onto one line too many.")


@dataclass
class Para:
    lines: list[str]


def layout_paragraphs(paras: list[str]) -> list[Para]:
    """Wrap each paragraph, then check its last line.

    `wrap` allows JUSTIFY_COMPRESSION so that a *justified* line may end a
    fraction of a point past the measure, the way Word does it. The last line of
    a paragraph is not justified, so it gets no such allowance: if the
    compression allowance is what let the final word onto that line, the line
    really is too wide and would overhang the right margin. ("...is familiar
    ground." was 415.89 pt in a 412.6 pt measure, i.e. 3.3 pt into the margin.)
    """
    out = []
    for p in paras:
        lines = wrap(p, PARA_SIZE, BODY_W)
        last = tw(lines[-1], PARA_SIZE)
        if last > BODY_W + 0.01:
            raise LayoutOverflow(
                f"the last line of a paragraph is {last:.2f} pt wide, past the "
                f"{BODY_W:.2f} pt measure by {last - BODY_W:.2f} pt, and a last "
                f"line is never justified so it cannot be squeezed: {lines[-1]!r}. "
                f"Reword the sentence to change where it breaks.")
        out.append(Para(lines))
    return out


def build(d: dict, out_path: str) -> None:
    bad = check_style(d)
    if bad:
        raise StyleViolation(
            "STYLE.md violation in this letter:\n  " + "\n  ".join(bad))
    register_fonts()
    c = canvas.Canvas(out_path, pagesize=(PAGE_W, PAGE_H))
    c.setTitle(f"Lettre de motivation — {d.get('signature', '')}".strip())
    c.setAuthor(d.get("signature", ""))
    c.setSubject(d.get("subject", ""))
    c.setCreator("JobApplicant / render_letter.py")

    # ---- header ----------------------------------------------------------
    draw(c, HEADER_X, NAME_BASE, d["name"], NAME_SIZE, french=False)
    draw(c, HEADER_X, TAGLINE_BASE, d["tagline"], TAGLINE_SIZE,
         french=d.get("typography") == "fr")
    draw(c, 0, PLACE_BASE, d["place"], ADDRESS_SIZE, right_align_to=HEADER_RIGHT, french=False)
    draw(c, 0, PHONE_BASE, d["phone"], ADDRESS_SIZE, right_align_to=HEADER_RIGHT, french=False)
    draw(c, 0, EMAIL_BASE, d["email"], ADDRESS_SIZE, right_align_to=HEADER_RIGHT, french=False)

    c.setStrokeColor(BLACK)
    c.setLineWidth(RULE_W)
    c.setLineCap(0)
    c.line(RULE_X0, PAGE_H - RULE_Y, RULE_X1, PAGE_H - RULE_Y)

    # ---- date / addressee / subject -------------------------------------
    # The reference "right aligns" the date by padding it with ~174 spaces.
    # Reproduce the visual result with an explicit x instead.
    draw(c, DATE_X, DATE_BASE, d["date"].strip(), DATE_SIZE, french=False)
    # The date sits to the right of the addressee on the same baseline block.
    # A long addressee used to overprint it, silently: fail instead.
    addr_w = tw(french_spacing(d["addressee"]) if d.get("typography") == "fr"
                else d["addressee"], ADDRESSEE_SIZE)
    if BODY_X + addr_w > DATE_X - 12.0:
        raise LayoutOverflow(
            f'the addressee runs into the date: it ends at x={BODY_X + addr_w:.1f}, '
            f'past the limit x={DATE_X - 12.0:.1f} (DATE_X minus a 12 pt gutter). '
            f'Shorten it.')
    draw(c, BODY_X, ADDRESSEE_BASE, d["addressee"], ADDRESSEE_SIZE,
         french=d.get("typography") == "fr")
    draw(c, BODY_X, SUBJECT_BASE, d["subject"], SUBJECT_SIZE,
         french=d.get("typography") == "fr")

    # ---- salutation ------------------------------------------------------
    draw(c, BODY_X, SALUTATION_BASE, d["salutation"], SALUTATION_SIZE,
         french=d.get("typography") == "fr")

    # ---- body ------------------------------------------------------------
    paras = layout_paragraphs(d["paragraphs"])
    y = PARA_FIRST_BASE
    for i, para in enumerate(paras):
        if i:
            y += PARA_GAP
        for j, line in enumerate(para.lines):
            last = j == len(para.lines) - 1
            draw(c, BODY_X, y, line, PARA_SIZE,
                 justify_to=None if last else BODY_RIGHT)
            if not last:
                y += PARA_LEAD
    last_body = y

    # ---- closing ---------------------------------------------------------
    closing_y = last_body + CLOSING_GAP
    signature_y = closing_y + SIGNATURE_GAP
    if signature_y > BOTTOM_LIMIT:
        raise LayoutOverflow(
            f"the letter runs to {signature_y:.0f} pt (limit {BOTTOM_LIMIT:.0f}). "
            "Cut a sentence — the master letter leaves a third of the page empty.")
    draw(c, BODY_X, closing_y, d["closing"], CLOSING_SIZE)
    draw(c, BODY_X, signature_y, d["signature"], SIGNATURE_SIZE)

    c.showPage()
    c.save()
    assert_inside_margins(out_path)


def main(argv: Sequence[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    with open(argv[1], encoding="utf-8") as fh:
        build(json.load(fh), argv[2])
    print(f"wrote {argv[2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
