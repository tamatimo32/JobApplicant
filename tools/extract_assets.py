#!/usr/bin/env python3
"""
Extract the reusable brand assets (portrait + contact-bar icons) from the
reference CV so the generator never has to touch the reference PDF at runtime.

Outputs
-------
assets/photo.jpg         portrait cropped exactly as it appears in the master CV
assets/icons/*.png       pin / phone / mail / car / linkedin pictograms

Run once (idempotent):
    python3 tools/extract_assets.py
"""
from __future__ import annotations

import pathlib

import pymupdf
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
REF = ROOT / "assets" / "reference" / "CV_Master_Format.pdf"
ASSETS = ROOT / "assets"
ICONS = ASSETS / "icons"

# Portrait placement on the master page, in PDF points.
PHOTO_BOX = (46.35, 36.0, 143.0, 138.05)

# (name, x0, y0, x1, y1) in PDF points, on the 612x792 page.
ICON_BOXES = {
    "pin": (45.2, 150.9, 59.9, 164.6),
    "phone": (158.9, 150.9, 173.6, 164.6),
    "mail": (242.0, 150.9, 256.5, 164.6),
    "car": (370.7, 150.9, 385.3, 164.6),
    "linkedin": (430.6, 150.9, 446.1, 164.6),
}


def main() -> None:
    ICONS.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(REF)
    page = doc[0]

    # --- portrait: rendered at 900 dpi, then downsampled to 600 dpi JPEG ------
    # The portrait is only 96.65 pt wide on the page, so 806 px (600 dpi) is
    # more than enough for print and keeps the PDF around 250 KB instead of
    # 1.3 MB.
    pix = page.get_pixmap(dpi=900, clip=pymupdf.Rect(*PHOTO_BOX), alpha=False)
    tmp = ASSETS / "_photo_tmp.png"
    pix.save(tmp)
    im = Image.open(tmp).convert("RGB")
    target_w = 806
    im = im.resize((target_w, round(target_w * im.height / im.width)), Image.LANCZOS)
    im.save(ASSETS / "photo.jpg", quality=92, optimize=True, progressive=True)
    tmp.unlink()
    print(f"photo: {pix.width}x{pix.height} -> assets/photo.jpg "
          f"({im.width}x{im.height}, {(ASSETS / 'photo.jpg').stat().st_size // 1024} KB)")

    # --- icons ---------------------------------------------------------------
    for name, box in ICON_BOXES.items():
        ipix = page.get_pixmap(dpi=600, clip=pymupdf.Rect(*box), alpha=False)
        path = ICONS / f"{name}.png"
        ipix.save(path)
        print(f"{name}: {ipix.width}x{ipix.height} -> {path.relative_to(ROOT)}")

    # --- sanity: portrait must be ~96.65 x 102.05 pt at 4:5-ish ratio --------
    im = Image.open(ASSETS / "photo.jpg")
    print("portrait aspect (w/h):", round(im.width / im.height, 4),
          "| target:", round(96.65 / 102.05, 4))


if __name__ == "__main__":
    main()
