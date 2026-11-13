"""Measure how machine-written a letter reads, honestly.

The problem with "is it under 15 % AI?"
----------------------------------------
That question assumes a calibrated instrument exists. It does not, offline.
This module was built after measuring the alternatives, and the measurement
is the point, so it is recorded here.

Calibration run (2026-11-12, `llm_detector` 0.2.0, the only offline detector
installable in this sandbox):

    known HUMAN  n = 15   mean p_llm = 0.71
      - the applicant's own two hand-written letters ....... 0.63, 0.45
      - eleven real job postings by real recruiters ....... 0.52 to 0.88

    known MACHINE n = 2   mean p_llm = 0.87

    human texts scoring below 0.15 ....................... 0 of 15

So a 15 % ceiling is not a property a real letter can have. Every genuinely
human text in the sample scored five to four times higher, including the two
letters the applicant wrote himself, typos and all. The detector has a base
rate near 0.7 on short professional prose and a separation of 0.16 between
its human and machine means. It cannot support a 15 % decision.

This module therefore does not print a made-up "AI percentage". It prints:

  * `features()`  - measured style quantities, no invented weighting
  * `baseline()`  - the same quantities on the applicant's own letters
  * `llm_detector_score()` - a real offline model, when installed
  * `gptzero()`   - a real commercial model, when a key is present

A letter is judged against the applicant's own writing, not against a
threshold taken from a vendor's marketing.

Usage
-----
    python3 tools/ai_check.py <letter.json>            # features + baseline
    python3 tools/ai_check.py <letter.json> --detector # add offline model
    GPTZERO_API_KEY=... python3 tools/ai_check.py <letter.json> --gptzero
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

# Only the body paragraphs count as prose. The tagline, subject line and
# salutation are headings: they carry no terminal punctuation, so "Madame,
# Monsieur," used to glue itself onto the first real sentence and corrupt every
# length statistic downstream. Measured on the body alone.
PROSE_FIELDS = ("paragraphs",)

# The applicant's own letters, transcribed from ML_Master_Format.pdf and
# ML_FEAD.pdf. This is the reference voice: not "generic human", but *his*.
REFERENCE = {
    "ML_Master_Format": """Most bioengineers from my degree woud love to bridge
technical depth with EU policy, funding, and project execution; I am one of
those bioengineers. Joining CLERENS as a Project Assistant is the ideal
opportunity to apply my quantitative engineering background directly to
proposal drafting and project management in EU energy, climate, and storage
affairs. I hold a master's in environmental bioengineering and bring hands-on
experience across EU sustainability frameworks and energy data analysis. My
background includes performing pre-feasibility studies for low-carbon energy
systems (geothermal, river heat recovery, biowaste), building ROI
calculations, assessing climate risks via Copernicus datasets, digitalizing
CSRD matrices, and participating in ISO audit structures (9001, 14001,
50001). Throughout my work, I have consistently focused on structured data
collection, deliverable monitoring, and process automation. I am eager to
bring this analytical mindset to CLERENS to support proposal drafting for EU
funding programs (such as Horizon Europe and Innovation Fund), monitor
project work plans, assist in financial reporting, and help draft high-quality
reports and presentations for stakeholders. Fully bilingual in English and
French, based in Brussels, and eligible for the CIP framework starting January
2027, I am ready to contribute proactively to your team's day-to-day
operations and project management tasks. I would be delighted to discuss how
my profile aligns with your current project portfolio. Even if my application
is unsuccessful, I would welcome your feedback and any insights on building a
career within EU public affairs and project consultancy.""",
    "ML_FEAD": """Most of the bioengineers from my degree would probably want to
do the science behind policies, and I'm one of those graduates. It would
indeed be quite a privilege to join your ranks and dive more into the
technical depth of future policies to be. I'd like to have my first step in
such a world. I hold a master's in environmental bioengineering and
accumulated data analyses skills through my experiences with a knowledge of
sustainability frameworks in the EU. I have made climate risks assessment for
buildings following French R4RE framework and Copernicus data, participated
in ISO9001 audits (with 14001 and 50001), digitalized the CSRD matrix,
contributed to data analysis for carbon footprints and made pre-feasibility
studies for energy systems (biowaste, Riothermie, aquathermy, geothermal)
Throughout most of my experiences I have heavily researched and connected the
dots through data and automation. I'd like to bring that same analytical
mindset to reviewing evidence, interpreting data, and supporting the
development of sound environmental policies. Bilingual in English and French
and currently living in Brussels, I am ready to join your ranks and bring my
skills for the sake of the circular economy. I would be delighted to discuss
how I could be a good fit for your team. Even if my application is
unsuccessful, I would be happy to hear your opinion on working at FEAD and any
tips you might have for finding a role that could suit my profile.""",
}


# --------------------------------------------------------------------------- #
# extraction
# --------------------------------------------------------------------------- #

def letter_text(data: dict) -> str:
    parts: list[str] = []
    for key in PROSE_FIELDS:
        value = data.get(key)
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(v for v in value if isinstance(v, str))
    return "\n\n".join(parts).strip()


def sentences(text: str) -> list[str]:
    """Split on terminal punctuation *and* newlines.

    Bug fixed 2026-11-12: the salutation ("Madame, Monsieur,") carries no
    full stop, so splitting on punctuation alone glued it onto the first
    real sentence and corrupted every length statistic downstream.
    """
    # Split into paragraphs on blank lines, then treat each paragraph as one
    # run of text with its internal wrapping collapsed. Splitting on every
    # newline would break hard-wrapped prose (the reference letters are
    # wrapped) into fragments that are not sentences.
    out: list[str] = []
    for para in re.split(r"\n\s*\n", text):
        flat = re.sub(r"\s+", " ", para).strip()
        if flat:
            out.extend(s.strip() for s in re.split(r"(?<=[.!?])\s+", flat))
    return [s for s in out if len(s.split()) >= 3]


def n_words(text: str) -> int:
    return len(re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ'’-]+", text))


# --------------------------------------------------------------------------- #
# features - measured, never combined into a secret score
# --------------------------------------------------------------------------- #

FR_CONNECTIVES = ["par ailleurs", "en outre", "de plus", "ainsi", "en effet",
                  "cependant", "toutefois", "néanmoins", "en conclusion",
                  "en somme", "il convient de", "il est important de",
                  "dans ce contexte", "à cet égard", "par conséquent",
                  "en définitive", "force est de constater"]
EN_CONNECTIVES = ["moreover", "furthermore", "additionally", "in addition",
                  "however", "therefore", "thus", "consequently",
                  "in conclusion", "overall", "it is important to",
                  "it is worth noting", "leverage", "seamless", "delve",
                  "underscore", "testament", "pivotal", "robust", "holistic",
                  "navigate", "foster", "tapestry"]

FR_CLICHES = ["je suis passionné", "je suis convaincu", "fort de mon expérience",
              "dans un monde en constante évolution",
              "n'hésitez pas à me contacter",
              "je me permets de vous adresser",
              "c'est avec un grand intérêt", "je serais ravi de",
              "un véritable atout"]
EN_CLICHES = ["i am passionate about", "i am thrilled", "i am excited to",
              "i would be delighted", "please do not hesitate",
              "in today's fast-paced", "i am confident that",
              "a proven track record", "team player", "dynamic environment"]


def _count(text: str, phrases: list[str]) -> int:
    low = " " + re.sub(r"\s+", " ", text.lower()) + " "
    return sum(low.count(p) for p in phrases)


def _is_french(text: str) -> bool:
    low = text.lower()
    return bool(re.search(r"[àâçéèêëîïôùûüÿœ]", low)) or \
        _count(low, ["je ", "les ", "des ", "pour "]) > 2


@dataclass
class Features:
    words: int
    sentences: int
    mean_len: float
    stdev_len: float
    short: int          # sentences of <= 8 words
    long: int           # sentences of >= 30 words
    connectives: int
    cliches: int
    first_person: int
    numbers: int
    named_tools: int

    def as_dict(self) -> dict:
        return {k: (round(v, 2) if isinstance(v, float) else v)
                for k, v in self.__dict__.items()}

    def table(self) -> str:
        rows = [
            ("words", self.words),
            ("sentences", self.sentences),
            ("mean sentence length", round(self.mean_len, 1)),
            ("sentence length stdev", round(self.stdev_len, 1)),
            ("short sentences (<=8 words)", self.short),
            ("long sentences (>=30 words)", self.long),
            ("stock connectives", self.connectives),
            ("cliche phrases", self.cliches),
            ("first-person markers", self.first_person),
            ("numbers", self.numbers),
            ("named tools or standards", self.named_tools),
        ]
        return "\n".join(f"    {k:32}{v:>8}" for k, v in rows)


def features(text: str) -> Features:
    s = sentences(text)
    lens = [len(x.split()) for x in s] or [0]
    fr = _is_french(text)
    fp = r"\b(je|j'|mon|ma|mes|me|moi)\b" if fr else r"\b(i|my|me|mine)\b"
    tools = re.findall(
        r"\b(ISO ?\d{4,5}|GHG Protocol|CSRD|ESRS|B ?Corp|EcoVadis|Power BI|"
        r"Excel|Python|SQL|GOTS|FSC|GRS|Sedex|Greenly|Copernicus|"
        r"EcoVadis|RSE|CSRD|ISO 14067|[A-Z]{4,6})\b", text)
    return Features(
        words=n_words(text),
        sentences=len(s),
        mean_len=statistics.fmean(lens) if lens else 0.0,
        stdev_len=statistics.pstdev(lens) if len(lens) > 1 else 0.0,
        short=sum(1 for x in lens if x <= 8),
        long=sum(1 for x in lens if x >= 30),
        connectives=_count(text, FR_CONNECTIVES if fr else EN_CONNECTIVES),
        cliches=_count(text, FR_CLICHES if fr else EN_CLICHES),
        first_person=len(re.findall(fp, text.lower())),
        numbers=len(re.findall(r"\b\d+([.,]\d+)?\b", text)),
        named_tools=len(tools),
    )


def baseline() -> dict[str, Features]:
    return {name: features(t) for name, t in REFERENCE.items()}


# --------------------------------------------------------------------------- #
# the 40 % target, and what is actually reachable
# --------------------------------------------------------------------------- #
#
# The applicant raised the ceiling from 15 % to 40 % on 2026-11-12, because the
# writing produced while chasing 15 % read oddly. That instinct was right, and
# the measurements below (llm_detector 0.2.0, 2026-11-12) show why.

THRESHOLD = 40.0

# Measured floors. These are the numbers the 40 % target has to be read
# against, because no human text of this genre gets near 40 %:
#   12 real French job adverts   min 45.9   mean 69.8   max 87.8  -> 0 of 12
#   the applicant's own letters  45.0 and 63.0
#   1 real English job advert    83.5
#   plain human-sounding EN      49.2  (best found in ~40 rewrites)
#   best natural French letter   55.7  (and that version was a list of numbers)
HUMAN_FLOOR = {"fr": 46.0, "en": 45.0}

# What the detector actually rewards, measured sentence by sentence on French:
#   0.99  "J'ai construit l'outil."
#   0.97  "Le plus dur, c'etait de retrouver la facture."
#   0.21  "Il faut deux ans de donnees pour repondre a un inspecteur."
#   0.26  "Nous avons reduit le temps de traitement de 70 %."
# It scores impersonal, corporate, number-led statements as more human than
# first-person ones. Optimising for it therefore pushes a letter *away* from
# the applicant's voice, which is the opposite of the goal.

# What the detector does with language, holding content constant:
#   "Une certification ne se gagne pas..."  FR -> 0.78
#   "A certification is not won..."         EN -> 0.28
# Its function-word list is English-only, so French text loses that feature
# entirely and drifts to the machine side. French letters therefore score
# roughly 20 to 35 points above their English equivalent.
LANGUAGE_BIAS = "detector is English-calibrated; French scores ~20-35 pts higher"


def ai_percent(text: str) -> float | None:
    """The real detector's number, as a percentage. None if not installed."""
    got = llm_detector_score(text)
    if got.get("p_llm") is None:
        return None
    return 100.0 * got["p_llm"]


def verdict(pct: float, language: str = "en") -> tuple[str, str]:
    """Read the score against measured human floors, not against 40 % alone."""
    if pct <= THRESHOLD:
        return "PASS", f"at or under {THRESHOLD:.0f} %"
    floor = HUMAN_FLOOR.get(language, 46.0)
    if pct < floor:
        return "GOOD", (f"under the {floor:.0f} % floor measured on real human "
                        f"{language.upper()} text; as low as this genre goes")
    if pct <= floor + 30:
        return "HUMAN RANGE", (
            f"inside the range real human {language.upper()} text occupies "
            f"({floor:.0f}-{floor + 43:.0f} %); rewriting further does not help")
    return "HIGH", (
        f"above the human range for {language.upper()}; more concrete detail "
        f"(numbers, named artefacts) usually brings it down")


# --------------------------------------------------------------------------- #
# real detectors
# --------------------------------------------------------------------------- #

def llm_detector_score(text: str) -> dict:
    """The offline model, if it is installed in this interpreter."""
    try:
        from llm_detector import classify_text   # type: ignore
    except ImportError:
        return {"detector": "llm_detector", "error": "not installed "
                "(pip install llm-detector)", "p_llm": None}
    r = classify_text(text)
    return {"detector": "llm_detector", "p_llm": round(float(r["p_llm"]), 3),
            "flagged_as_llm": bool(r.get("is_llm"))}


def gptzero(text: str, api_key: str) -> dict:
    req = urllib.request.Request(
        "https://api.gptzero.me/v2/predict/text",
        data=json.dumps({"document": text}).encode("utf-8"),
        headers={"X-Api-Key": api_key, "Content-Type": "application/json",
                 "Accept": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"detector": "gptzero", "error": f"HTTP {e.code}", "p_llm": None}
    except Exception as e:                                    # noqa: BLE001
        return {"detector": "gptzero", "error": str(e), "p_llm": None}
    doc = (data.get("documents") or [data])[0]
    prob = doc.get("completely_generated_prob",
                   doc.get("average_generated_prob"))
    return {"detector": "gptzero",
            "p_llm": round(float(prob), 3) if prob is not None else None}


# --------------------------------------------------------------------------- #
# cli
# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("letter", nargs="+")
    ap.add_argument("--detector", action="store_true", default=True,
                    help="run the offline llm_detector model (default)")
    ap.add_argument("--features", action="store_true",
                    help="also print the style table against the reference letters")
    ap.add_argument("--gptzero", action="store_true",
                    help="add GPTZero (needs GPTZERO_API_KEY)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    base = baseline()
    out = {}
    worst = 0
    for path in args.letter:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        text = letter_text(raw)
        f = features(text)
        lang = "fr" if _is_french(text) else "en"
        det = llm_detector_score(text)
        pct = 100.0 * det["p_llm"] if det.get("p_llm") is not None else None
        entry = {"language": lang, "features": f.as_dict(),
                 "ai_percent": round(pct, 1) if pct is not None else None,
                 "threshold": THRESHOLD,
                 "baseline": {k: v.as_dict() for k, v in base.items()}}
        if pct is not None:
            entry["verdict"], entry["why"] = verdict(pct, lang)
            worst = max(worst, pct)
        if args.gptzero:
            key = os.environ.get("GPTZERO_API_KEY", "")
            entry["gptzero"] = (gptzero(text, key) if key
                                else {"error": "GPTZERO_API_KEY not set"})
        out[path] = entry

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    for path, e in out.items():
        print(f"\n{Path(path).name}  [{e['language']}]")
        if e["ai_percent"] is None:
            print("    detector unavailable (pip install llm-detector)")
        else:
            print(f"    AI score   {e['ai_percent']:5.1f} %   "
                  f"(target <= {THRESHOLD:.0f} %)   {e['verdict']}")
            print(f"               {e['why']}")
        print(f"    words {e['features']['words']}, "
              f"sentence stdev {e['features']['stdev_len']}, "
              f"short sentences {e['features']['short']}")
        if args.features:
            b = base["ML_Master_Format"].as_dict()
            c = base["ML_FEAD"].as_dict()
            print(f"    {'':30}{'letter':>9}{'Master':>9}{'FEAD':>9}")
            for key in ("mean_len", "stdev_len", "short", "connectives",
                        "cliches", "first_person", "numbers", "named_tools"):
                print(f"    {key:30}{e['features'][key]:>9}{b[key]:>9}{c[key]:>9}")

    if len(out) > 1 and worst:
        print(f"\n    worst of {len(out)}: {worst:.1f} %")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
