#!/usr/bin/env python3
"""
compare_letter_to_reference.py — regression check for the motivation-letter template.

Renders tools/fixtures/letter_content.json (the reference letter's own text) and
compares it against assets/reference/ML_Master_Format.pdf.

Paragraphs are compared a *paragraph* at a time (line count + baselines +
concatenated text) because Word's and ReportLab's greedy line-breakers can
disagree by one word on a line. Every other element is compared glyph-accurate.

    python3 tools/compare_letter_to_reference.py
    python3 tools/compare_letter_to_reference.py --fail     # exit 1 on drift
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import tempfile

import pymupdf

ROOT = pathlib.Path(__file__).resolve().parent.parent
REF = ROOT / "assets" / "reference" / "ML_Master_Format.pdf"
FIXTURE = ROOT / "tools" / "fixtures" / "letter_content.json"

TOL = 1.5
PARA_TOP = 160.0          # below this baseline, the page is body paragraphs


def spans(pdf: pathlib.Path) -> list[tuple[float, float, float, str]]:
    out = []
    for block in pymupdf.open(pdf)[0].get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            for s in line["spans"]:
                t = " ".join(s["text"].split())
                if t:
                    out.append((round(s["origin"][1], 2), round(s["origin"][0], 2),
                                round(s["size"], 2), t))
    return sorted(out)


def paragraphs(spans_: list[tuple[float, float, float, str]]) -> list[list]:
    """Group body lines into paragraphs using the 14.64 pt leading."""
    body = [s for s in spans_ if s[0] > PARA_TOP]
    paras: list[list] = []
    for s in sorted(body, key=lambda s: s[0]):
        if paras and abs(s[0] - paras[-1][-1][0] - 14.64) < 0.6:
            paras[-1].append(s)
        else:
            paras.append([s])
    return paras


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fail", action="store_true")
    ap.add_argument("--pdf", default=None)
    args = ap.parse_args()

    if args.pdf:
        mine = pathlib.Path(args.pdf)
    else:
        tmp = pathlib.Path(tempfile.mkdtemp()) / "letter.pdf"
        subprocess.run([sys.executable, str(ROOT / "tools" / "render_letter.py"),
                        str(FIXTURE), str(tmp)], check=True)
        mine = tmp

    ref_all = spans(REF)
    my_all = spans(mine)

    # ---------- 1. everything above the body: glyph-accurate -----------------
    ref_head = [s for s in ref_all if s[0] <= PARA_TOP]
    my_head = [s for s in my_all if s[0] <= PARA_TOP]
    worst = 0.0
    drift = 0
    print("== header / date / addressee / subject / salutation ==")
    pool = list(ref_head)
    for y, x, size, text in my_head:
        c = [r for r in pool if r[3] == text]
        if not c:
            print(f"  [new] y={y:7.2f} x={x:7.2f} {text[:52]!r}")
            continue
        r = min(c, key=lambda r: abs(r[0] - y))
        pool.remove(r)
        dy, dx = abs(y - r[0]), abs(x - r[1])
        worst = max(worst, dy, dx)
        bad = dy > TOL or dx > TOL
        drift += bad
        print(f"  dy={y - r[0]:+6.2f} dx={x - r[1]:+6.2f}  {text[:56]!r}"
              f"{'   <-- DRIFT' if bad else ''}")
    for r in pool:
        print(f"  [missing] y={r[0]:7.2f} {r[3][:56]!r}")

    # ---------- 2. body paragraphs: count + baselines + text ----------------
    ref_paras = paragraphs(ref_all)
    my_paras = paragraphs(my_all)
    print(f"\n== body: {len(ref_paras)} paragraphs in reference, "
          f"{len(my_paras)} rendered ==")
    for i in range(max(len(ref_paras), len(my_paras))):
        rp = ref_paras[i] if i < len(ref_paras) else None
        mp = my_paras[i] if i < len(my_paras) else None
        if not rp or not mp:
            print(f"  para {i}: MISSING on one side")
            drift += 1
            continue
        r_text = " ".join(s[3] for s in rp)
        m_text = " ".join(s[3] for s in mp)
        dy = abs(mp[0][0] - rp[0][0])
        worst = max(worst, dy)
        ok = r_text == m_text and len(rp) == len(mp) and dy <= TOL
        drift += not ok
        print(f"  para {i}: lines {len(rp)}/{len(mp)}  first-baseline "
              f"{rp[0][0]:.2f} -> {mp[0][0]:.2f} (d={mp[0][0] - rp[0][0]:+.2f})  "
              f"{'OK' if ok else 'DIFF'}")
        if r_text != m_text:
            print(f"      text differs")

    print(f"\nmax deviation: {worst:.2f} pt   problem areas: {drift}")
    if args.fail and drift:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
