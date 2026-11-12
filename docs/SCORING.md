# The scoring system, in full

The report answers one question: **of everything the registry can find, which
twelve should I read first?** That is a ranking problem, not a search problem,
and it needs a rule that is simple enough to argue with.

Every score is out of 100 and additive. Open any card in the report, press
"why this score", and the arithmetic for that specific posting is printed. The
numbers below live in `tools/job_finder/config.py`; this document explains why
they are what they are.

```
total = keyword + seniority + location + language + employer + freshness + penalties
        (35)      (20)        (15)       (10)       (12)       (8)         (−)
```

Clamped to 0–100. Nothing is normalised after the fact, so a 99 means the same
thing in every run and two runs can be compared honestly.

---

## 1. Keyword relevance, 35 points

The largest component, because fit to the actual work should beat prestige.
Keywords come from the CV and the M.Sc., as 173 rows in the registry, each
carrying a weight:

| weight | meaning | example |
| --- | --- | --- |
| 3 | core, the CV names it | sustainability analyst, CSRD, GHG Protocol, LCA, double materiality, B Corp, EcoVadis, Power BI, bilan carbone |
| 2 | likely fit | environmental compliance, energy efficiency, ISO 14001, waste management, stakeholder engagement |
| 1 | adjacent, mostly noise | environment, climate, biodiversity, reporting |

**First hit:** 13 points for a weight-3 keyword, 7 for weight-2, 3 for
weight-1.

**Diminishing returns:** each further keyword of the same weight is worth 55%
of the one before. Six core concepts beat one core concept repeated six times.

**Title bonus:** +9 when a core keyword appears in the job title, because that
is what the job actually is. A "Sustainability Analyst" whose description never
says "sustainability" is still a sustainability analyst.

**Off-topic cap:** a posting with no weight-2 or weight-3 keyword at all is
capped at 5 points (15% of 35). "Environment" appearing in a marketing job is
not a signal.

Worked example, from the demo:

```
+23.5  sustainability analyst   (weight 3, in title)
+ 7.2  double materiality       (weight 3)
+ 3.9  GHG Protocol             (weight 3)
+ 2.2  EcoVadis                 (weight 3)
+ 1.2  Power BI                 (weight 3)
+ 0.7  B Corp                   (weight 3)
        raw 38.9, capped at 35
```

## 2. Seniority fit, 20 points

| what the posting asks | points |
| --- | --- |
| graduate, junior, assistant, 0–2 years | **20** |
| internship or traineeship | 14 |
| no level stated | 13 |
| mid, 3–5 years | 8 |
| senior, lead, manager | −6 |
| head, director, partner, chief | −20 |

The candidate has roughly two years of internships and a first job. A role
asking for six years is a different person, and no amount of matching keywords
makes it writable.

Level is read from the title first, then from the body ("junior", "entry
level", "0 to 2 years"), and **a stated number of years overrides the title**:
"Senior Analyst, 0–2 years" is a junior role with an inflated name. Both
mistakes are common, in opposite directions.

3 years asked → −4 points, a stretch. More than 5 → −12 and excluded.

## 3. Location, 15 points

| | points | why |
| --- | --- | --- |
| Belgium | 15 | lives there, no permit needed |
| Luxembourg | 13 | commutable, same languages |
| Switzerland | 11 | relocation, strong market, high cost |
| UAE | 10 | relocation, large ESG build-out |
| Australia | 9 | relocation, visa |
| New Zealand | 9 | relocation, visa |
| remote | 12 | location independent |
| anywhere else | 2 | outside the six |

The six countries are in scope, so five of them lose very little. Someone
reading this in Brussels might prefer to reweight Belgium to 25; that is one
number in `config.py`.

## 4. Language, 10 points

| posting language | points |
| --- | --- |
| English | 10 |
| French | 10 |
| unknown | 8 |
| Dutch | 3 |
| German | 1 |

Bilingual FR/EN is the CV's strongest line, and Dutch is "in progress" rather
than fluent, so a Dutch-language posting is a real barrier even in Brussels.
Posting a job in Dutch in Belgium is common enough that this fires often, and
that is the point: those are not roles this CV can win yet.

Separately, a posting that explicitly *demands* fluent Dutch takes a −10
penalty on top, and fluent German −4.

## 5. Employer type, 12 points

| sector | points | | sector | points |
| --- | --- | --- | --- | --- |
| environmental consulting | 12 | | institutions | 8 |
| energy | 10 | | finance | 7 |
| water | 10 | | services | 7 |
| waste | 10 | | chemicals | 7 |
| public bodies | 9 | | industry | 7 |
| research | 9 | | transport | 6 |
| utilities | 9 | | pharma | 6 |
| agri-food | 8 | | packaging | 6 |
| engineering | 8 | | retail | 5 |
| buildings | 8 | | mining | 4 |
| NGOs | 5 | | software / data | 6 |

Small consultancies score highest deliberately: in a twelve-person practice one
junior does the carbon footprint, the CSRD gap analysis and the dashboard,
which is this CV almost exactly. At a large employer the same junior does one
narrow slice.

+2 when the employer was named in the registry, because those rows were chosen
on purpose rather than scraped from a board.

## 6. Freshness, 8 points

| age | points |
| --- | --- |
| today | 8 |
| a week | 7 |
| two weeks | 5 |
| a month | 2 |
| two months or more | 0 |
| no date on the page | 4 |

Small on purpose. An old posting is not a bad posting, it is a likely filled
one.

## 7. Penalties, and exclusions

| trigger | penalty |
| --- | --- |
| unpaid | −12 |
| commission-only or freelance-only | −15, **excluded** |
| senior wording in the title | −8 |
| more than 5 years asked | −12, **excluded** |
| fluent Dutch required | −10 |
| fluent German required | −4 |
| deadline has passed | −25, **excluded** |
| recruiter posting hiding the client | −4 |
| registry row whose domain was never confirmed | −2 |
| executive title | **excluded** |

Excluded means removed from the main list, not down-ranked. Four things earn
that: a role you cannot get (senior or 6+ years), a role that does not pay
(commission only), a role that has closed, and a role at the top of an
organisation. The toggle in the report shows what was removed and why, because
a ranking that silently hides things is worse than no ranking.

---

## Bands

| band | score | label |
| --- | --- | --- |
| A | 75+ | apply now |
| B | 60–74 | strong match |
| C | 45–59 | worth a look |
| D | below 45 | low priority |

## What this deliberately does not do

* **It does not read the posting properly.** It counts phrases. A posting
  that says "sustainability" in a paragraph about how the company was founded
  scores as if the job were about it. The report compensates by showing which
  keywords matched, so a wrong score is visible rather than mysterious.
* **It does not know about visa sponsorship.** "Visa support provided" and
  "must have the right to work in Australia" are different postings and score
  the same.
* **It does not know your preferences** beyond the six countries and the two
  languages. If you would rather never work in finance, change one number in
  `config.py` and every score moves accordingly.
* **It is not a substitute for reading.** The top band means "read this
  first", not "apply".

## Tuning it for yourself

Everything lives in `tools/job_finder/config.py`. The three that change results
most:

```python
COUNTRY_POINTS = {"BE": 15, ...}      # how much location matters
KEYWORD_DECAY = 0.55                   # how fast extra keywords stop helping
SENIORITY_POINTS = {"graduate": 20, ...}  # how strict about level
```

After a change, re-run `python3 -m unittest discover -s tools/job_finder/tests
-t tools` to confirm the arithmetic still adds up and that the documented
behaviour (junior beats senior, French beats Dutch, fresh beats stale) still
holds.
