"""Polite HTTP with a disk cache.

Three rules, because this bot has a name in the User-Agent and a person behind
it: one request per host per interval, never more than a handful per run, and
an on-disk copy so re-running the scorer does not re-hammer anything.

Only the standard library is used. ``requests`` is a nicer API, but a job
search tool that needs a pip install before it will open a CSV is a worse
tool, and ``urllib`` covers redirects, TLS and headers fine.
"""

from __future__ import annotations

import gzip
import hashlib
import io
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from dataclasses import dataclass
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Optional

from . import config as C


@dataclass
class Response:
    url: str
    status: int
    text: str
    content_type: str = ""
    from_cache: bool = False
    fetched_at: Optional[datetime] = None
    error: str = ""

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 400 and not self.error


class Fetcher:
    def __init__(self, cache_dir: Path, delay: float = C.REQUEST_DELAY_SECONDS,
                 ttl_hours: int = C.CACHE_TTL_HOURS, offline: bool = False,
                 respect_robots: bool = True, verbose: bool = False):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.delay = delay
        self.ttl = timedelta(hours=ttl_hours)
        self.offline = offline
        self.respect_robots = respect_robots
        self.verbose = verbose
        self._last_hit: dict[str, float] = {}
        self._robots: dict[str, urllib.robotparser.RobotFileParser] = {}
        self.stats = {"network": 0, "cache": 0, "offline_miss": 0,
                      "blocked": 0, "errors": 0}

    # ---------------------------------------------------------------- cache
    def _key(self, url: str) -> Path:
        h = hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]
        return self.cache_dir / f"{h}.html"

    def _read_cache(self, url: str) -> Optional[Response]:
        p = self._key(url)
        if not p.exists():
            return None
        age = datetime.now() - datetime.fromtimestamp(p.stat().st_mtime)
        if age > self.ttl:
            return None
        meta = p.with_suffix(".meta")
        ctype = meta.read_text(encoding="utf-8") if meta.exists() else ""
        return Response(url=url, status=200,
                        text=p.read_text(encoding="utf-8", errors="replace"),
                        content_type=ctype, from_cache=True,
                        fetched_at=datetime.fromtimestamp(p.stat().st_mtime))

    def _write_cache(self, url: str, text: str, content_type: str) -> None:
        p = self._key(url)
        p.write_text(text, encoding="utf-8")
        p.with_suffix(".meta").write_text(content_type, encoding="utf-8")

    # --------------------------------------------------------------- robots
    def _allowed(self, url: str) -> bool:
        if not self.respect_robots:
            return True
        parts = urllib.parse.urlsplit(url)
        root = f"{parts.scheme}://{parts.netloc}"
        if root not in self._robots:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"{root}/robots.txt")
            try:
                req = urllib.request.Request(
                    f"{root}/robots.txt",
                    headers={"User-Agent": C.USER_AGENT})
                with urllib.request.urlopen(req, timeout=10) as r:
                    rp.parse(r.read().decode("utf-8", "replace").splitlines())
            except Exception:
                rp.parse([])   # no robots.txt, or unreachable: allow
            self._robots[root] = rp
        return self._robots[root].can_fetch(C.USER_AGENT, url)

    # ------------------------------------------------------------- fetch
    def get(self, url: str) -> Response:
        if any(bad in url.lower() for bad in C.NEVER_FETCH):
            self.stats["blocked"] += 1
            return Response(url=url, status=0, text="",
                            error="refused: tos_restricted domain")

        cached = self._read_cache(url)
        if cached:
            self.stats["cache"] += 1
            return cached

        if self.offline:
            self.stats["offline_miss"] += 1
            return Response(url=url, status=0, text="",
                            error="offline: no cached copy")

        if not self._allowed(url):
            self.stats["blocked"] += 1
            return Response(url=url, status=0, text="",
                            error="robots.txt disallows")

        host = urllib.parse.urlsplit(url).netloc
        wait = self.delay - (time.time() - self._last_hit.get(host, 0))
        if wait > 0:
            time.sleep(wait)

        req = urllib.request.Request(url, headers={
            "User-Agent": C.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
            "Accept-Language": "en,fr;q=0.8,nl;q=0.6",
            "Accept-Encoding": "gzip",
        })
        try:
            with urllib.request.urlopen(req, timeout=C.REQUEST_TIMEOUT) as r:
                raw = r.read()
                self._last_hit[host] = time.time()
                self.stats["network"] += 1
                if r.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
                charset = r.headers.get_content_charset() or "utf-8"
                text = raw.decode(charset, "replace")
                ctype = r.headers.get("Content-Type", "")
                self._write_cache(url, text, ctype)
                return Response(url=r.geturl(), status=r.status, text=text,
                                content_type=ctype, fetched_at=datetime.now())
        except urllib.error.HTTPError as e:
            self.stats["errors"] += 1
            return Response(url=url, status=e.code, text="",
                            error=f"HTTP {e.code}")
        except Exception as e:                                  # noqa: BLE001
            self.stats["errors"] += 1
            return Response(url=url, status=0, text="",
                            error=f"{type(e).__name__}: {e}")


    # ------------------------------------------------------------ link check
    def check(self, url: str) -> str:
        """Is this URL still there? Returns ok / redirect / gone / error.

        A HEAD request, which is cheap and does not download the page. Some
        servers reject HEAD, so a 405 or 501 is retried as a GET with the body
        thrown away. "gone" means 404 or 410: closed, not wrong.
        """
        if any(bad in url.lower() for bad in C.NEVER_FETCH):
            return "error"
        if not url.lower().startswith("http"):
            return "error"

        def _once(method: str) -> Response:
            req = urllib.request.Request(url, method=method, headers={
                "User-Agent": C.USER_AGENT,
                "Accept": "text/html,*/*;q=0.8",
            })
            try:
                with urllib.request.urlopen(req, timeout=C.REQUEST_TIMEOUT) as r:
                    return Response(url=r.geturl(), status=r.status, text="")
            except urllib.error.HTTPError as e:
                return Response(url=url, status=e.code, text="",
                                error=f"HTTP {e.code}")
            except Exception as e:                              # noqa: BLE001
                return Response(url=url, status=0, text="",
                                error=f"{type(e).__name__}")

        resp = _once("HEAD")
        if resp.status in (405, 501):
            resp = _once("GET")
        if resp.status in (200, 203, 204, 206):
            return "ok"
        if resp.status in (301, 302, 303, 307, 308):
            return "redirect"
        if resp.status in (404, 410):
            return "gone"
        return "error"


# --------------------------------------------------------------------------- #
# snapshot writer, used for the offline demo
# --------------------------------------------------------------------------- #

def save_snapshot(path: Path, url: str, html: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = f"<!-- snapshot of {url} taken {datetime.now():%Y-%m-%d %H:%M} -->\n"
    path.write_text(header + html, encoding="utf-8")
