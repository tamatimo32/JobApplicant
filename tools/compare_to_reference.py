#!/usr/bin/env python3
"""
compare_to_reference.py — regression check for the CV template.

Renders tools/fixtures/master_content.json with the same engine used for real
applications and diffs the resulting text baselines against the reference PDF
(assets/reference/CV_Master_Format.pdf).

    python3 tools/compare_to_reference.py            # print the table
    python3 tools/compare_to_reference.py --fail     # exit 1 on any drift > tol

The reference was produced by Microsoft Word, so a couple of points of drift is
expected (line rounding, glyph shapes). A drift above the tolerance means a
template constant in tools/render_cv.py has been changed by accident.
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
REF = ROOT / "assets" / "reference" / "CV_Master_Format.pdf"
FIXTURE = ROOT / "tools" / "fixtures" / "master_content.json"

TOL_X, TOL_Y = 2.0, 2.0

# The contact bar is deliberately *not* at the reference x any more: the
# reference positions each label after an emoji, and we ship no emoji (the row
# is laid out from the panel edge with a dot separator). Comparing those five
# labels on x would just encode "we are not the reference", forever. Their y
# baseline is still checked.
BAR_TEXT_Y = 161.80
BAR_X_EXEMPT = True


def spans(pdf: pathlib.Path) -> list[tuple[float, float, float, str]]:
    """(baseline_y, origin_x, size, text) for every non-blank text span."""
    out = []
    doc = pymupdf.open(pdf)
    for block in doc[0].get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            for s in line["spans"]:
                t = s["text"].strip()
                if not t:
                    continue
                out.append((round(s["origin"][1], 2), round(s["origin"][0], 2),
                            round(s["size"], 2), " ".join(t.split())))
    return sorted(out)


def render_fixture() -> pathlib.Path:
    tmp = pathlib.Path(tempfile.mkdtemp()) / "fixture.pdf"
    subprocess.run([sys.executable, str(ROOT / "tools" / "render_cv.py"),
                    str(FIXTURE), str(tmp)], check=True)
    return tmp


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fail", action="store_true")
    ap.add_argument("--pdf", default=None, help="compare this PDF instead of the fixture")
    args = ap.parse_args()

    mine_pdf = pathlib.Path(args.pdf) if args.pdf else render_fixture()
    ref = spans(REF)
    mine = spans(mine_pdf)

    if args.pdf:
        print(f"{'ref_y':>8} {'my_y':>8} {'dy':>6} {'ref_x':>8} {'my_x':>8} {'dx':>6}  text")
    else:
        print(f"{'ref_y':>8} {'my_y':>8} {'dy':>6} {'ref_x':>8} {'my_x':>8} {'dx':>6}  text")

    # match greedily by (text, size) — the fixture uses the reference wording
    pool = list(ref)
    worst = 0.0
    drift = 0
    for y, x, size, text in mine:
        cands = [r for r in pool if r[3] == text]
        if not cands:
            print(f"{'':>8} {y:8.2f} {'':>6} {'':>8} {x:8.2f} {'':>6}  [new] {text[:52]}")
            continue
        r = min(cands, key=lambda r: abs(r[0] - y))
        pool.remove(r)
        dy, dx = abs(y - r[0]), abs(x - r[1])
        if BAR_X_EXEMPT and abs(y - BAR_TEXT_Y) < 0.5:
            dx = 0.0          # see BAR_TEXT_Y: x is intentional, y is not
        worst = max(worst, dy, dx)
        flag = ""
        if dy > TOL_Y or dx > TOL_X:
            drift += 1
            flag = "  <-- DRIFT"
        print(f"{r[0]:8.2f} {y:8.2f} {y - r[0]:6.2f} {r[1]:8.2f} {x:8.2f} {x - r[1]:6.2f}  "
              f"{text[:48]}{flag}")

    for r in pool:
        print(f"{r[0]:8.2f} {'':>8} {'':>6} {r[1]:8.2f} {'':>8} {'':>6}  [missing] {r[3][:48]}")

    print(f"\nmax deviation: {worst:.2f} pt   spans over tolerance: {drift}   "
          f"missing from render: {len(pool)}")
    if args.fail and (drift or worst > max(TOL_X, TOL_Y)):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
