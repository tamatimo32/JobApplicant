#!/usr/bin/env python3
"""Serve the generated report on 0.0.0.0 so the preview works.

Usage:  python3 tools/serve_report.py [--port 8000] [--db data/job_finder/…]
It regenerates the HTML on every request, so a crawl followed by a refresh
shows the new ranking without restarting anything.
"""

from __future__ import annotations

import argparse
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from job_finder.report import render      # noqa: E402
from job_finder.store import Store        # noqa: E402


def make_handler(db: Path, title: str):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):                                 # noqa: N802
            path = self.path.split("?")[0]
            if path not in ("/", "/index.html", "/opportunities.html"):
                self.send_error(404)
                return
            try:
                store = Store(db)
                row = store.con.execute("SELECT MAX(id) AS id FROM runs").fetchone()
                run_id = row["id"] if row else None
                out = render(db, ROOT / "out" / "opportunities.html",
                             run_id=run_id, title=title)
                body = out.read_bytes()
            except Exception as exc:                      # noqa: BLE001
                body = (f"<h1>Report could not be built</h1><pre>{exc}</pre>"
                        "<p>Run <code>python3 tools/jobfinder.py demo</code> first "
                        f"(it writes {db}).</p>"
                        "</p>").encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt, *args):
            sys.stderr.write("  " + fmt % args + "\n")

    return Handler


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    # Must match jobfinder.py's DEFAULT_DB. It used to default to demo.db
    # while `jobfinder.py demo` wrote opportunities.db, so the documented
    # "run demo, then serve" sequence always showed an empty/erroring report.
    ap.add_argument("--db",
                    default=str(ROOT / "data" / "job_finder" / "opportunities.db"))
    ap.add_argument("--title", default="Ranked opportunities")
    args = ap.parse_args()

    handler = make_handler(Path(args.db), args.title)
    srv = ThreadingHTTPServer(("0.0.0.0", args.port), handler)
    print(f"serving {args.db} on http://0.0.0.0:{args.port}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
