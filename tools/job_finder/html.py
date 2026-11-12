"""A tiny HTML reader and the JSON-LD reader, on the standard library alone.

``html.parser`` is slow but correct and always present. We only need three
things from a page: the ``<title>``, anchors with their text, and the
machine-readable job posting block that most job boards now embed. That last
one is the prize, because it is structured and does not depend on class names
that change whenever a site redesigns.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser

_BLOCK = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6",
          "section", "article", "ul", "ol", "table", "header", "footer"}
_SKIP = {"script", "style", "noscript", "svg", "template"}


@dataclass
class Anchor:
    href: str
    text: str


@dataclass
class Page:
    title: str = ""
    anchors: list[Anchor] = field(default_factory=list)
    text: str = ""
    ld_json: list[dict] = field(default_factory=list)
    meta: dict[str, str] = field(default_factory=dict)


class _Reader(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.page = Page()
        self._skip_depth = 0
        self._in_title = False
        self._anchor: Anchor | None = None
        self._anchor_depth = 0
        self._ld_buffer: list[str] = []
        self._in_ld = False
        self._text_parts: list[str] = []

    # ---------------------------------------------------------------- tags
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in _SKIP:
            self._skip_depth += 1
            if tag == "script" and a.get("type") == "application/ld+json":
                self._in_ld = True
                self._ld_buffer = []
            return
        if tag == "title":
            self._in_title = True
        elif tag == "a" and a.get("href"):
            self._anchor = Anchor(href=a["href"], text="")
            self._anchor_depth = 1
        elif tag == "meta":
            name = a.get("name") or a.get("property") or ""
            content = a.get("content") or ""
            if name and content:
                self.page.meta[name.lower()] = content
        if tag in _BLOCK:
            self._text_parts.append("\n")

    def handle_endtag(self, tag):
        if tag in _SKIP:
            if tag == "script" and self._in_ld:
                self._flush_ld()
                self._in_ld = False
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if tag == "title":
            self._in_title = False
        elif tag == "a" and self._anchor:
            self._anchor.text = re.sub(r"\s+", " ", self._anchor.text).strip()
            if self._anchor.text:
                self.page.anchors.append(self._anchor)
            self._anchor = None
        if tag in _BLOCK:
            self._text_parts.append("\n")

    # ---------------------------------------------------------------- data
    def handle_data(self, data):
        if self._skip_depth:
            if self._in_ld:
                self._ld_buffer.append(data)
            return
        if self._in_title:
            self.page.title += data
        if self._anchor is not None:
            self._anchor.text += data
        self._text_parts.append(data)

    def _flush_ld(self):
        blob = "".join(self._ld_buffer).strip()
        if not blob:
            return
        try:
            data = json.loads(blob)
        except json.JSONDecodeError:
            return
        for item in data if isinstance(data, list) else [data]:
            if isinstance(item, dict):
                self.page.ld_json.append(item)
                graph = item.get("@graph")
                if isinstance(graph, list):
                    self.page.ld_json.extend(
                        g for g in graph if isinstance(g, dict))

    def close(self):
        super().close()
        self.page.title = re.sub(r"\s+", " ", self.page.title).strip()
        text = "".join(self._text_parts)
        text = re.sub(r"[ \t\r\xa0]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n", text)
        self.page.text = text.strip()


def parse(html: str) -> Page:
    reader = _Reader()
    try:
        reader.feed(html)
        reader.close()
    except Exception:                                          # noqa: BLE001
        pass
    return reader.page


# --------------------------------------------------------------------------- #
# JSON-LD JobPosting
# --------------------------------------------------------------------------- #

def job_postings(page: Page, base_url: str = "") -> list[dict]:
    """Every schema.org JobPosting on the page, flattened to plain fields."""
    out = []
    for item in page.ld_json:
        types = item.get("@type")
        types = types if isinstance(types, list) else [types]
        if "JobPosting" not in types:
            continue
        out.append({
            "title": _text(item.get("title") or item.get("name")),
            "description": _text(item.get("description")),
            "date_posted": _text(item.get("datePosted")),
            "valid_through": _text(item.get("validThrough")),
            "employment_type": _text(item.get("employmentType")),
            "url": _abs(_text(item.get("url")), base_url),
            "employer": _org(item.get("hiringOrganization")),
            "location": _location(item.get("jobLocation")),
            "remote": bool(item.get("jobLocationType")),
            "salary": _salary(item.get("baseSalary")),
            "language": _text(item.get("inLanguage")),
        })
    return out


def _text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return strip_tags(value)
    if isinstance(value, dict):
        return _text(value.get("name") or value.get("value") or "")
    if isinstance(value, list):
        return ", ".join(_text(v) for v in value if v)
    return str(value)


def _org(value) -> str:
    if isinstance(value, dict):
        return _text(value.get("name"))
    return _text(value)


def _location(value) -> str:
    if isinstance(value, list):
        value = value[0] if value else None
    if not isinstance(value, dict):
        return _text(value)
    addr = value.get("address") if isinstance(value.get("address"), dict) else {}
    parts = [addr.get("addressLocality"), addr.get("addressRegion"),
             addr.get("addressCountry")]
    if isinstance(parts[-1], dict):
        parts[-1] = parts[-1].get("name") or parts[-1].get("addressCountry")
    return ", ".join(str(p) for p in parts if p)


def _salary(value) -> str:
    if not isinstance(value, dict):
        return _text(value)
    cur = value.get("currency") or ""
    v = value.get("value")
    if isinstance(v, dict):
        lo, hi, unit = v.get("minValue"), v.get("maxValue"), v.get("unitText") or ""
        if lo and hi:
            return f"{lo}-{hi} {cur} {unit}".strip()
        single = v.get("value")
        if single:
            return f"{single} {cur} {unit}".strip()
    return _text(v)


_TAG = re.compile(r"<[^>]+>")


def strip_tags(html: str) -> str:
    if not html:
        return ""
    html = re.sub(r"(?i)<(br|/p|/li|/div|/h[1-6])\s*/?>", "\n", html)
    text = _TAG.sub(" ", html)
    text = (text.replace("&nbsp;", " ").replace("&amp;", "&")
                .replace("&lt;", "<").replace("&gt;", ">")
                .replace("&quot;", '"').replace("&#39;", "'")
                .replace("&rsquo;", "\u2019").replace("&ndash;", "-"))
    text = re.sub(r"[ \t\r\xa0]+", " ", text)
    return re.sub(r"\n\s*\n+", "\n", text).strip()


def _abs(url: str, base: str) -> str:
    if not url:
        return ""
    if url.startswith("http"):
        return url
    import urllib.parse as up
    return up.urljoin(base, url)
