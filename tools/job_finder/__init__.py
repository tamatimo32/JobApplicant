"""Read the job-source registry, collect postings, rank them, render a report.

The registry (``google_drive/job_sources_registry.csv``) says *where* to look
and *what* to keep. This package turns that into a ranked, browsable HTML page.

Pipeline::

    registry  ->  planner  ->  fetch (cached)  ->  adapters  ->  score
              ->  sqlite store  ->  report.html

Only two things are opinionated: the scoring weights in ``config.py`` and the
arithmetic in ``score.py``. Both are documented, and every score the report
shows can be reproduced by hand with ``jobfinder explain <id>``.
"""

__version__ = "1.0.0"
