"""Row model shared by the job-source registry modules.

Every row in the registry is either a *source* (a place that lists many
vacancies) or a *company* (one employer whose career page you check). The two
share a schema so they can live in one CSV, because the consumer of that CSV is
a scraper loop: "for each url, fetch, filter by keyword".

`size` distinguishes them in practice: a board has no size, an employer does.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional


SECTORS = {
    "energy", "water", "waste", "env_consulting", "engineering",
    "agri_food", "chemicals", "industry", "buildings", "finance",
    "public_body", "research", "transport", "pharma", "packaging",
    "software_data", "ngo", "mining", "retail", "utilities", "services",
}


@dataclass
class Row:
    category: str            # job_board | pes | public_sector | institution |
                             # big4 | company | federation | aggregator |
                             # remote | keyword
    country: str             # BE LU CH AU NZ AE EU GLOBAL
    name: str
    url: str
    listing_url: str = ""
    language: str = ""
    sector: str = ""         # employers only
    size: str = ""           # large | mid | sme  (employers only)
    what_it_lists: str = ""
    access: str = "open"     # open | login_required | api | tos_restricted
    fit: str = "medium"      # high | medium | low
    priority: int = 2        # 1 every run, 2 weekly, 3 occasionally
    notes: str = ""
    id: str = field(default="", compare=False)

    def __post_init__(self):
        if self.sector and self.sector not in SECTORS:
            raise ValueError(f"{self.name}: unknown sector {self.sector!r}")
        if self.size not in ("", "large", "mid", "sme"):
            raise ValueError(f"{self.name}: unknown size {self.size!r}")
        if self.access not in ("open", "login_required", "api", "tos_restricted"):
            raise ValueError(f"{self.name}: unknown access {self.access!r}")
        if self.fit not in ("high", "medium", "low"):
            raise ValueError(f"{self.name}: unknown fit {self.fit!r}")
        if self.priority not in (1, 2, 3):
            raise ValueError(f"{self.name}: bad priority {self.priority!r}")
        if not self.url.startswith("https://"):
            raise ValueError(f"{self.name}: url must be https:// ({self.url})")

    def as_dict(self) -> dict:
        return asdict(self)

    # ------------------------------------------------------------------ #
    # Compact constructors, so the data files stay readable as tables.
    # ------------------------------------------------------------------ #
    def __repr__(self) -> str:
        return f"<{self.category} {self.country} {self.name}>"


def company(country, name, url, sector, size, fit="medium", priority=2, note=""):
    """An employer career page. `url` is the root domain on purpose: career
    paths move when an employer changes applicant tracking system."""
    return Row(
        category="company", country=country, name=name, url=url,
        language=_lang(country), sector=sector, size=size,
        what_it_lists="Employer career page (resolve Careers from the homepage)",
        access="open", fit=fit, priority=priority,
        notes=note or "Root domain on purpose: career-page paths break on ATS migrations.",
    )


def _lang(country):
    return {
        "BE": "fr/nl/en", "LU": "fr/en", "CH": "de/fr/en",
        "AU": "en", "NZ": "en", "AE": "en/ar",
    }.get(country, "en")


def board(category, country, name, url, listing="", language="", what="",
          access="open", fit="medium", priority=2, notes=""):
    return Row(
        category=category, country=country, name=name, url=url,
        listing_url=listing, language=language, sector="", size="",
        what_it_lists=what, access=access, fit=fit, priority=priority,
        notes=notes,
    )
