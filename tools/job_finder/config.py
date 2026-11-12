"""Every tunable number in the ranking, in one file.

The score is additive out of 100 and deliberately simple enough to check by
hand. The reasoning for each weight is in ``docs/SCORING.md``; this file is the
source of truth the code reads.

Design rules that the numbers encode
------------------------------------
1. **Fit to the work beats prestige.** Keyword relevance is the largest
   component. A carbon analyst at a 12-person consultancy outscores a
   sustainability *communications* role at a name-brand bank.
2. **A title you cannot get is not a good match.** Seniority is a strong
   positive down the scale and a penalty up it. Nothing is scored "10/10"
   while requiring six years of experience.
3. **Geography is a fact, not a preference.** Belgium is the anchor; the other
   five countries are in scope, so they lose only a little. Outside the six is
   a heavy penalty unless the role is remote.
4. **Language is a gate, not a bonus.** A Dutch-language role is not a fit
   with Dutch "in progress" and is penalised accordingly.
5. **Freshness is small.** Old does not mean bad, it means likely filled.
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# component maxima: these sum to exactly 100
# --------------------------------------------------------------------------- #

MAX_KEYWORD = 35
MAX_SENIORITY = 20
MAX_GEOGRAPHY = 15
MAX_LANGUAGE = 10
MAX_EMPLOYER = 12
MAX_FRESHNESS = 8

assert MAX_KEYWORD + MAX_SENIORITY + MAX_GEOGRAPHY + MAX_LANGUAGE + \
    MAX_EMPLOYER + MAX_FRESHNESS == 100

# --------------------------------------------------------------------------- #
# keyword relevance
# --------------------------------------------------------------------------- #

# A keyword of weight 3 is "core" (sustainability consultant, carbon analyst,
# LCA, CSRD reporting). Diminishing returns stop a posting that mentions
# "environment" forty times from beating one that names the actual job.
KEYWORD_DECAY = 0.55

# Points awarded for the first hit of a given weight, before decay.
KEYWORD_BASE = {3: 13.0, 2: 7.0, 1: 3.0}

# Extra points when a core keyword appears in the *title*, not the body.
# Titles are what a recruiter and a candidate both read first.
TITLE_BONUS = {3: 9.0, 2: 3.0, 1: 0.0}

# An off-topic keyword (weight 1) matching in a posting that has no core
# keyword at all is noise, not signal. Cap those rows.
OFFTOPIC_ONLY_CAP = 0.15   # fraction of MAX_KEYWORD

# --------------------------------------------------------------------------- #
# seniority
# --------------------------------------------------------------------------- #

# Points by the level the posting asks for. The candidate has roughly two
# years of internships and a first job, so "graduate" is the bullseye.
SENIORITY_POINTS = {
    "graduate": 20,      # 0-2 years, junior analyst, assistant, trainee scheme
    "intern": 14,        # eligible, but a step back and usually unpaid
    "mid": 8,            # 3-5 years: reachable with a strong letter
    "unspecified": 13,   # unknown is mildly better than a bad guess
    "senior": -6,
    "exec": -20,
}

# A stated minimum above this is out of reach regardless of the title.
YEARS_OVER_REACH = 5
YEARS_TOLERATED = 3      # 3 years asked is a stretch, 5 is a different person

# --------------------------------------------------------------------------- #
# geography
# --------------------------------------------------------------------------- #

ANCHOR_COUNTRY = "BE"
COUNTRY_POINTS = {
    "BE": 15,   # where the candidate lives and is authorised to work
    "LU": 13,   # commutable-ish, same languages
    "CH": 11,   # relocation, higher cost of living, strong market
    "AE": 10,   # relocation, tax-free, large ESG build-out
    "AU": 9,    # relocation, visa needed
    "NZ": 9,    # relocation, visa needed
}
OUTSIDE_POINTS = 2
REMOTE_POINTS = 12          # remote is location-independent

# --------------------------------------------------------------------------- #
# language
# --------------------------------------------------------------------------- #

# The candidate is bilingual FR/EN and learning NL.
LANGUAGE_POINTS = {"en": 10, "fr": 10, "nl": 3, "de": 1, "": 8}
# A French-language role in Flanders is still fine; a Dutch-language role is
# not, and it is the language that decides, not the country.

# --------------------------------------------------------------------------- #
# employer type
# --------------------------------------------------------------------------- #

# Small sustainability practices are the best realistic entry point: one
# junior does everything, so the CV's breadth is the point.
EMPLOYER_SECTOR_POINTS = {
    "env_consulting": 12,
    "energy": 10,
    "water": 10,
    "waste": 10,
    "public_body": 9,
    "research": 9,
    "utilities": 9,
    "agri_food": 8,
    "engineering": 8,
    "buildings": 8,
    "institution": 8,
    "finance": 7,
    "services": 7,
    "chemicals": 7,
    "industry": 7,
    "transport": 6,
    "pharma": 6,
    "packaging": 6,
    "retail": 5,
    "mining": 4,
    "ngo": 5,
    "software_data": 6,
}
EMPLOYER_SECTOR_DEFAULT = 6

# extra points when the employer was named in the registry (we chose it on
# purpose), vs. a posting found on a board we did not curate
REGISTRY_EMPLOYER_BONUS = 2

# --------------------------------------------------------------------------- #
# freshness
# --------------------------------------------------------------------------- #

# Age in days -> points. Linear between the anchors, clamped at the ends.
FRESHNESS_ANCHORS = [(0, 8), (7, 7), (14, 5), (30, 2), (60, 0)]
FRESHNESS_UNKNOWN = 4       # no date on the page: assume average, not stale

# --------------------------------------------------------------------------- #
# penalties
# --------------------------------------------------------------------------- #

PENALTY = {
    "unpaid": -12,           # an unpaid internship is a real cost to the candidate
    "commission_only": -15,
    "senior_title": -8,      # "Senior"/"Head"/"Lead" in the title
    "years_over_reach": -12,
    "dutch_required": -10,
    "german_required": -4,
    "outside_scope": -6,
    "deadline_passed": -25,  # almost certainly gone; kept only for the archive
    "staffing_agency": -4,   # second-hand postings hide the real employer
    "unverified_source": -2,  # registry row whose domain was inferred
}

# Hard exclusions: not "scored low", removed. Each must be defensible.
EXCLUDE_IF = {
    "commission_only": True,
    "deadline_passed": True,
    "seniority_exec": True,
    "years_over_reach": True,
}

# --------------------------------------------------------------------------- #
# bands and output
# --------------------------------------------------------------------------- #

BANDS = [
    ("A", 75, "Apply now"),
    ("B", 60, "Strong match"),
    ("C", 45, "Worth a look"),
    ("D", 0, "Low priority"),
]

MIN_SCORE_TO_SHOW = 0
TOP_N_FOR_HIGHLIGHTS = 12

# --------------------------------------------------------------------------- #
# crawling manners
# --------------------------------------------------------------------------- #

USER_AGENT = "JobApplicant-finder/1.0 (personal job search; contact: owner of repo)"
REQUEST_DELAY_SECONDS = 1.5      # between requests to the same host
REQUEST_TIMEOUT = 20
CACHE_TTL_HOURS = 12             # re-fetch a page only after this
MAX_PAGES_PER_SOURCE = 3
MAX_POSTINGS_PER_SOURCE = 80

# Sources we must never touch, regardless of what the registry says.
NEVER_FETCH = ("linkedin.", "indeed.", "glassdoor.", "google.com/jobs")

# Which canonical sector an employer name maps to, when the registry row was
# itself a job board and carries no sector.
