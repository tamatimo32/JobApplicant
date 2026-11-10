#!/usr/bin/env python3
"""
render_cv.py — build a CV that reproduces the CV_Master_Format layout exactly.

Usage
-----
    python3 tools/render_cv.py <content.json> <output.pdf>

Every template constant below (font, size, colour, x/y coordinate) was measured
from assets/reference/CV_Master_Format.pdf. Do not "eyeball" new values — change
them only after re-measuring the reference (see README.md, "How the template
was measured").

The content JSON schema is documented in README.md ("Content schema").
The renderer is single-page: it raises LayoutOverflow if the content no longer
fits, so a CV can never silently lose a bullet.
"""
from __future__ import annotations

import json
import pathlib
import sys
from dataclasses import dataclass
from typing import Sequence

from PIL import Image
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
ICONS = ROOT / "assets" / "icons"

PAGE_W, PAGE_H = 612.0, 792.0          # A4 portrait, points

# --------------------------------------------------------------------------- #
# Palette — sampled at 900 dpi from the reference PDF
# --------------------------------------------------------------------------- #
C_PRIMARY = HexColor("#156082")         # headings, dates, accent bar
C_ACCENT = HexColor("#4EA72E")          # employer names
C_LINK = HexColor("#467886")            # e-mail + LinkedIn
C_RULE = HexColor("#7F7F7F")            # rule under sidebar headings
C_SIDEBAR_HEAD = HexColor("#595959")    # sidebar headings only
C_TEXT = HexColor("#000000")
TINT = Color(241 / 255, 245 / 255, 249 / 255)   # #F1F5F9

# --------------------------------------------------------------------------- #
# Header
# --------------------------------------------------------------------------- #
ACCENT_BAR = (33.0, 36.0, 2.25, 101.82)
PHOTO = (46.35, 36.0, 96.65, 102.05)
TEXT_X = 151.58
NAME_BASE, NAME_SIZE = 57.53, 18.0
TITLE_BASE, TITLE_SIZE = 76.28, 11.0
SUMMARY_BASES = (99.03, 113.03, 127.30, 141.55)   # measured baselines
SUMMARY_SIZE, SUMMARY_LEAD = 10.0, 14.25
SUMMARY_MAX_W = 416.5            # summary box: 151.58 -> 568.0 (single Word paragraph)
SUMMARY_LINES_MAX = 4

# --------------------------------------------------------------------------- #
# Contact bar
# --------------------------------------------------------------------------- #
BAR = (36.9, 147.9, 539.1, 21.9)
BAR_RADIUS = 3.3
BAR_TEXT_BASE = 161.80
BAR_TEXT_SIZE = 9.0
BAR_ICON_TOP = 147.75                # emoji-cube top (content starts 154.1)
BAR_ICON_H = 13.8                    # emoji cube height, measured
BAR_ICON_GAP = 0.0                   # each item carries its own measured x
LINK_UNDERLINE_DY = 2.0
LINK_UNDERLINE_W = 0.45

# --------------------------------------------------------------------------- #
# Left column
# --------------------------------------------------------------------------- #
LEFT_X = 43.53
LEFT_WRAP_X = 421.5
BULLET_X = 46.28
BODY_X = 57.78
COL_RULE = (40.1, 383.0, 1.5)        # x0, width, thickness

H_BASE, H_SIZE = 187.30, 12.0
H_RULE_DY = 9.0
JOB1_BASE = 210.08

D_DATE = 12.25
D_CONTEXT = 25.50                    # title baseline -> context baseline
D_BULLET1 = 48.00                    # title baseline -> first bullet baseline
BODY_SIZE, BODY_LH = 10.0, 14.50      # 10 pt body on a 14.5 pt line (master rhythm)
D_NEXT_JOB = 26.25                   # last bullet baseline -> next title baseline
BULLET_GAP = 0.0                     # bullets are NOT extra-spaced in the master
DATE_SIZE, CONTEXT_SIZE = 8.0, 10.0

# --------------------------------------------------------------------------- #
# Sidebar
# --------------------------------------------------------------------------- #
PANEL_X, PANEL_W = 432.0, 143.6
PANEL_RADIUS = 4.0
PANEL_HEAD_X = 440.42
PANEL_BODY_X = 440.42
PANEL_TEXT_W = 131.5            # measured: the sidebar text box ends at ~572
PANEL_HEAD_SIZE, PANEL_HEAD_DY = 12.0, 15.35   # rect top -> heading baseline
PANEL_HEAD_DY_LANG = 13.40                     # the Languages panel uses a smaller head
PANEL_HEAD_SIZE_LANG = 11.0                    # ... and 11 pt instead of 12 pt
LANG_EXTRA_OFFSET = 3.10                       # measured gap before Languages
PANEL_RULE_DY, PANEL_RULE_INSET, PANEL_RULE_W = 18.75, 8.9, 124.3
PANEL_PAD_BOTTOM = 5.3                         # last baseline -> rect bottom
SIDEBAR_TOP, SIDEBAR_GAP = 178.3, 7.6
SIDEBAR_BOTTOM_LIMIT = 786.0

PANEL_SPECS = {
    # Each sidebar panel in the reference is measured independently:
    #   lead   = baseline-to-baseline inside the block
    #   gap    = heading baseline -> first body baseline
    #   pad    = last baseline  -> panel bottom edge
    #   ind    = left indent of the body text relative to PANEL_BODY_X
    # The reference is a hand-made Word layout, so the four panels do not share
    # one rhythm. Keeping the per-panel numbers is what makes the copy look
    # like the original.
    "text":      dict(lead=12.27, gap=21.40, pad=4.36, ind=0.00),
    "skills":    dict(lead=12.77, gap=22.25, pad=18.50, ind=0.00),
    "bullets":   dict(lead=11.75, gap=22.65, pad=13.65, ind=-1.75),
    "education": dict(lead=10.02, gap=19.50, pad=18.25, ind=-6.50),
    "languages": dict(lead=12.50, gap=23.25, pad=11.30, ind=-4.75),
}


class LayoutOverflow(RuntimeError):
    pass


class StyleViolation(RuntimeError):
    pass


EM_DASH = "\u2014"


def check_style(d: dict) -> list[str]:
    """Enforce STYLE.md §1: no em dashes in authored prose.

    The job-title separator is generated by draw_job(), not authored, so only
    the JSON's own strings are inspected here.
    """
    offenders: list[str] = []

    def walk(node, path=""):
        if isinstance(node, str):
            if EM_DASH in node:
                offenders.append(f"{path}: {node[:70]!r}")
        elif isinstance(node, dict):
            for k, v in node.items():
                if k.startswith("_"):
                    continue          # audit-trail fields are never printed
                walk(v, f"{path}.{k}" if path else k)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")

    walk({k: v for k, v in d.items()
          if k not in {"subtitle"} and not k.startswith("_")})
    return offenders


# --------------------------------------------------------------------------- #
def register_fonts() -> None:
    files = {
        "Aptos": "Aptos.ttf",
        "Aptos-Bold": "Aptos-Bold.ttf",
        "Aptos-Italic": "Aptos-Italic.ttf",
        # The master's section headings use Seaford Bold, a commercial
        # Microsoft font. Aptos Bold is a near-identical stand-in at 12 pt:
        # same cap height (8.02 pt) and 3.3 % narrower over the heading text.
        "Seaford-Bold": "Aptos-Bold.ttf",
    }
    for name, fn in files.items():
        pdfmetrics.registerFont(TTFont(name, str(FONTS / fn)))


def tw(text: str, font: str, size: float) -> float:
    return pdfmetrics.stringWidth(text, font, size)


def wrap_soft(text: str, font: str, size: float, max_w: float) -> list[str]:
    """Wrap, honouring explicit "\n" breaks authored in the content file."""
    out: list[str] = []
    for chunk in text.split("\n"):
        out.extend(wrap(chunk, font, size, max_w))
    return out


def wrap_runs(runs: list[tuple[str, str]], size: float,
              max_w: float) -> list[list[tuple[str, str]]]:
    """Wrap a list of (text, font) runs, keeping run formatting per line."""
    # explode to words, remembering the font of every word
    words: list[tuple[str, str]] = []
    for text, font in runs:
        for i, w in enumerate(text.split()):
            # keep a trailing colon glued to its label ("Durabilité :")
            words.append((w, font))
    if not words:
        return []
    lines: list[list[tuple[str, str]]] = [[]]
    width = 0.0
    space = tw(" ", "Aptos", size)
    for w, font in words:
        ww = tw(w, font, size)
        if lines[-1] and width + space + ww > max_w:
            lines.append([])
            width = 0.0
        if lines[-1]:
            width += space
        lines[-1].append((w, font))
        width += ww
    # merge adjacent words sharing a font, re-adding single spaces
    merged: list[list[tuple[str, str]]] = []
    for line in lines:
        out: list[tuple[str, str]] = []
        for w, font in line:
            if out and out[-1][1] == font:
                joiner = "" if out[-1][0].endswith(":") else " "
                out[-1] = (out[-1][0] + joiner + w, font)
            else:
                out.append((w, font))
        merged.append(out)
    return merged


def wrap(text: str, font: str, size: float, max_w: float) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines, cur = [], words[0]
    for w in words[1:]:
        cand = f"{cur} {w}"
        if tw(cand, font, size) <= max_w:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def put(c: canvas.Canvas, x: float, baseline: float, text: str, font: str,
        size: float, color: Color) -> None:
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawString(x, PAGE_H - baseline, text)


def em_top_to_baseline(y_top: float, size: float) -> float:
    """Word puts the baseline 0.3 * size below the top of the em box."""
    return y_top + 0.3 * size


def panel(c: canvas.Canvas, top: float, h: float, r: float = PANEL_RADIUS) -> None:
    c.setFillColor(TINT)
    c.roundRect(PANEL_X, PAGE_H - top - h, PANEL_W, h, r, stroke=0, fill=1)


def rule(c: canvas.Canvas, x0: float, x1: float, y: float, color: Color,
         weight: float) -> None:
    c.setStrokeColor(color)
    c.setLineWidth(weight)
    c.setLineCap(0)
    c.line(x0, PAGE_H - y, x1, PAGE_H - y)


# --------------------------------------------------------------------------- #
def draw_header(c: canvas.Canvas, d: dict) -> list[str]:
    x, y, w, h = ACCENT_BAR
    c.setFillColor(C_PRIMARY)
    c.rect(x, PAGE_H - y - h, w, h, stroke=0, fill=1)

    px, py, pw, ph = PHOTO
    c.drawImage(ImageReader(str(ROOT / "assets" / "photo.jpg")),
                px, PAGE_H - py - ph, pw, ph, mask="auto")

    put(c, TEXT_X, NAME_BASE, d["name"].upper(), "Aptos-Bold", NAME_SIZE, C_TEXT)
    put(c, TEXT_X, TITLE_BASE, d["title"], "Aptos-Bold", TITLE_SIZE, C_PRIMARY)

    lines = wrap(d["summary"], "Aptos", SUMMARY_SIZE, SUMMARY_MAX_W)
    if len(lines) > SUMMARY_LINES_MAX:
        raise LayoutOverflow(
            f"summary needs {len(lines)} lines, the template has "
            f"{SUMMARY_LINES_MAX} ({SUMMARY_MAX_W} pt each). Shorten it.")
    for i, line in enumerate(lines):
        put(c, TEXT_X, SUMMARY_BASES[i], line, "Aptos", SUMMARY_SIZE, C_TEXT)
    return lines


def draw_contact_bar(c: canvas.Canvas, d: dict) -> None:
    bx, by, bw, bh = BAR
    panel(c, by, bh, BAR_RADIUS)

    for item in d["contact"]:
        tx = item["x"]                       # measured text origin
        path = ICONS / f"{item['icon']}.png"
        im = Image.open(path)
        iw = BAR_ICON_H * im.width / im.height
        ix = tx - iw - BAR_ICON_GAP
        c.drawImage(ImageReader(str(path)), ix, PAGE_H - BAR_ICON_TOP - BAR_ICON_H,
                    iw, BAR_ICON_H, mask="auto")
        color = C_LINK if item.get("link") else C_TEXT
        size = item.get("size", BAR_TEXT_SIZE)
        baseline = BAR_TEXT_BASE + item.get("dy", 0.0)
        put(c, tx, baseline, item["text"], "Aptos", size, color)
        if item.get("link"):
            width = tw(item["text"], "Aptos", size)
            rule(c, tx, tx + width, baseline + LINK_UNDERLINE_DY,
                 C_LINK, LINK_UNDERLINE_W)


def draw_main_heading(c: canvas.Canvas, text: str) -> None:
    put(c, LEFT_X, H_BASE, text.upper(), "Seaford-Bold", H_SIZE, C_PRIMARY)
    rule(c, COL_RULE[0], COL_RULE[0] + COL_RULE[1], H_BASE + H_RULE_DY,
         C_PRIMARY, COL_RULE[2])


@dataclass
class Job:
    title: str
    employer: str
    dates: str
    context: str
    bullet_lines: list[list[str]]

    @property
    def n_lines(self) -> int:
        return sum(len(b) for b in self.bullet_lines)


def prepare_job(raw: dict) -> Job:
    body_w = LEFT_WRAP_X - BODY_X
    return Job(
        title=raw["title"],
        employer=raw["employer"],
        dates=raw["dates"],
        context=raw["context"],
        bullet_lines=[wrap(b, "Aptos", BODY_SIZE, body_w) for b in raw["bullets"]],
    )


def job_advance(job: Job) -> float:
    """Title baseline -> next title baseline."""
    # last bullet's last line is at  D_BULLET1 + (n_lines-1)*BODY_LH
    #                              + (n_bullets-1)*(D_BULLET-BODY_LH)
    n_lines = job.n_lines
    n_bul = len(job.bullet_lines)
    span = (n_lines - 1) * BODY_LH + max(0, n_bul - 1) * BULLET_GAP
    return D_BULLET1 + span + D_NEXT_JOB


def draw_job(c: canvas.Canvas, job: Job, base: float) -> None:
    put(c, LEFT_X, base, job.title, "Aptos-Bold", BODY_SIZE, C_TEXT)
    x = LEFT_X + tw(job.title, "Aptos-Bold", BODY_SIZE)
    put(c, x, base, " \u2014 ", "Aptos", BODY_SIZE, C_TEXT)
    x += tw(" \u2014 ", "Aptos", BODY_SIZE)
    put(c, x, base, job.employer, "Aptos-Bold", BODY_SIZE, C_ACCENT)

    put(c, LEFT_X, base + D_DATE, job.dates, "Aptos-Bold", DATE_SIZE, C_PRIMARY)
    put(c, LEFT_X, base + D_CONTEXT, job.context, "Aptos-Italic", CONTEXT_SIZE, C_TEXT)

    y = base + D_BULLET1
    for idx, lines in enumerate(job.bullet_lines):
        if idx:
            y += BULLET_GAP
        put(c, BULLET_X, y, "\u2022", "Aptos", BODY_SIZE, C_TEXT)
        for line in lines:
            put(c, BODY_X, y, line, "Aptos", BODY_SIZE, C_TEXT)
            y += BODY_LH
    return


def draw_sidebar(c: canvas.Canvas, blocks: list[dict]) -> float:
    top = SIDEBAR_TOP
    for block in blocks:
        kind = block["type"]
        if kind not in PANEL_SPECS:
            raise ValueError(f"unknown sidebar block type: {kind}")
        spec = PANEL_SPECS[kind]
        lead, gap_after_head = spec["lead"], spec["gap"]
        pad, ind = spec["pad"], spec["ind"]

        # The Languages heading is drawn 11 pt (not 12) in the reference.
        head_base = top + (PANEL_HEAD_DY_LANG if kind == "languages" else PANEL_HEAD_DY)
        rows: list[tuple[float, float, str, str, float, Color]] = []
        y = head_base + gap_after_head

        if kind == "text":
            for para in block["paras"]:
                for chunk in para.split("\n"):
                    # "Label : text" -> the label renders bold, the rest regular
                    label, sep, rest = chunk.partition(" : ")
                    runs = []
                    if sep:
                        runs.append((label + " :", "Aptos-Bold"))
                        runs.append((rest, "Aptos"))
                    else:
                        runs.append((chunk, "Aptos"))
                    for line_runs in wrap_runs(runs, 8.0, PANEL_TEXT_W):
                        rows.append((y, PANEL_BODY_X, line_runs, 8.0))
                        y += lead
            y -= lead
        elif kind == "skills":
            # authored one line per entry — never re-wrapped
            for line in block["lines"]:
                rows.append((y, PANEL_BODY_X, [(line, "Aptos")], 9.0))
                y += lead
            y -= lead
        elif kind == "bullets":
            for item in block["items"]:
                rows.append((y, PANEL_BODY_X + 2.25, [("\u2022", "Aptos")], 8.0))
                rows.append((y, PANEL_BODY_X + 6.0, [(item, "Aptos")], 8.0))
                y += lead
            y -= lead
        elif kind == "education":
            for item in block["items"]:
                for i, line in enumerate(item["lines"]):
                    rows.append((y, PANEL_BODY_X + 5.25,
                                 [(line, "Aptos-Bold" if i == 0 else "Aptos")], 7.0))
                    y += lead
                y += 0.0
            y -= lead
        elif kind == "languages":
            for lang, level in block["items"]:
                rows.append((y, PANEL_BODY_X + 4.75, [(lang, "Aptos")], 8.0))
                rows.append((y, PANEL_BODY_X + 61.3, [(level, "Aptos")], 8.0))
                y += lead
            y -= lead

        block_top = top + (LANG_EXTRA_OFFSET if kind == "languages" else 0.0)
        rect_h = (y - block_top) + pad
        panel(c, block_top, rect_h)
        rule(c, PANEL_X + PANEL_RULE_INSET, PANEL_X + PANEL_RULE_INSET + PANEL_RULE_W,
             block_top + PANEL_RULE_DY, C_RULE, 1.25)
        put(c, PANEL_HEAD_X, head_base, block["heading"], "Aptos-Bold",
            PANEL_HEAD_SIZE_LANG if kind == "languages" else PANEL_HEAD_SIZE,
            C_SIDEBAR_HEAD)
        for base, x, runs, size in rows:
            cx = x
            for i, (text, font) in enumerate(runs):
                put(c, cx, base, text, font, size, C_TEXT)
                # a run that is followed by another run keeps its trailing space
                cx += tw(text + (" " if i < len(runs) - 1 else ""), font, size)

        top = block_top + rect_h + SIDEBAR_GAP
    return top - SIDEBAR_GAP


def build(d: dict, out_path: str) -> None:
    bad = check_style(d)
    if bad:
        raise StyleViolation(
            "em dash found in authored text (see STYLE.md §1):\n  "
            + "\n  ".join(bad))
    register_fonts()
    c = canvas.Canvas(out_path, pagesize=(PAGE_W, PAGE_H))
    c.setTitle(f"CV \u2014 {d['name']}")
    c.setAuthor(d["name"])
    c.setSubject(d.get("subtitle", ""))
    c.setCreator("JobApplicant / render_cv.py")

    draw_header(c, d)
    draw_contact_bar(c, d)
    draw_main_heading(c, d["experience_heading"])

    jobs = [prepare_job(j) for j in d["experience"]]
    base = JOB1_BASE
    last_bottom = base
    for job in jobs:
        draw_job(c, job, base)
        base += job_advance(job)
        last_bottom = base - D_NEXT_JOB

    sidebar_bottom = draw_sidebar(c, d["sidebar"])

    if last_bottom > sidebar_bottom + 4 and sidebar_bottom > SIDEBAR_BOTTOM_LIMIT:
        raise LayoutOverflow("sidebar overflows the page")
    if last_bottom > 780:
        raise LayoutOverflow(
            f"experience column runs to {last_bottom:.1f} pt (limit 780). "
            "Remove a bullet or shorten the text.")

    c.showPage()
    c.save()


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
