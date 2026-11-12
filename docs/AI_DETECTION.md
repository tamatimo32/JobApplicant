# AI-detection: what the 15 % target actually measures

The applicant asked (2026-11-12) that motivation letters score **no more than
15 % AI-detected**, verified with a checker. This note records what happened
when that was tested, because the answer changed the approach.

Short version: **the 15 % ceiling is not achievable by any genuinely written
letter, and the number a detector returns for these letters cannot be used as
an acceptance test.** Here is the evidence.

---

## 1. No detector service is reachable

The sandbox has outbound access to GitHub, PyPI and `*.pythonhosted.org` only.

| Route | Result |
| --- | --- |
| GPTZero, ZeroGPT, Sapling, Copyleaks, Originality.ai APIs | unreachable (`000`) |
| HuggingFace model hub (pretrained detector weights) | unreachable |
| PyPI package `gptzero` | installs fine, but it is a thin HTTP client for the unreachable API |
| PyPI package `llm-detector` | **works offline**, ships its own model artifacts, 6.5 MB |

So the only instrument available is `llm-detector`. It is a research-grade
statistical classifier: lexical diversity, punctuation patterns, repetition,
and cross-tokenizer divergence. It is not GPTZero, and it is not calibrated on
French.

## 2. The instrument was tested against text of known authorship

Fifteen texts known to be human and two known to be machine-written:

| Group | Texts | `p_llm` |
| --- | --- | --- |
| The applicant's own two letters (`ML_Master_Format`, `ML_FEAD`) | 2 | **0.63**, **0.45** |
| Real recruiter-written job postings | 13 | 0.52 to 0.88 |
| Deliberately templated machine prose | 2 | 0.87, 0.88 |

```
known HUMAN   n = 15   mean p_llm = 0.71
known MACHINE n = 2    mean p_llm = 0.87
human texts scoring below 0.15:  0 of 15
```

The two letters the applicant wrote **himself**, typos and all, score 0.63 and
0.45. One of them is flagged as machine-written. Every single recruiter job
posting is flagged too.

The model has a base rate near 0.7 on short professional prose and a gap of
0.16 between its human and machine means. It cannot support a threshold
decision at 15 %. Reporting "12.4 % AI" from it would be a fabricated number.

## 3. Why this is expected, not surprising

Detectors are trained on long documents. A 230-word letter is roughly the
length of the *training example*, not the *test document*; there is not enough
signal. Commercial vendors say the same thing privately and publish accuracy
figures on essays of 500+ words. A one-page letter is out of distribution for
all of them.

There is also a base-rate problem. Recruiter postings and hand-written letters
share the features these models flag: formal register, long noun phrases,
topic repetition within a paragraph. Those are properties of *business writing*,
not of machine generation.

## 4. What is used instead

`tools/ai_check.py` reports measured style quantities next to the applicant's
own two letters, side by side:

```
                                       this letter   ML_Master   ML_FEAD
    mean sentence length                     19.25       26.67     26.67
    sentence length stdev                     8.52        8.77     13.84
    short sentences (<=8 words)                  1           0         0
    stock connectives                            0           0         0
    cliche phrases                               0           1         1
    first-person markers                        11          13        17
```

**The test is proximity to his own voice, not a vendor threshold.** A letter
that matches his hand-written rhythm is, by construction, as human as the
reference it is measured against. The specific things we push toward:

- sentence-length stdev above ~8 (his letters: 8.8 and 13.8). Flat rhythm is
  the single clearest machine tell and the easiest to fix;
- at least one very short sentence;
- zero stock connectives (`de plus`, `en outre`, `moreover`, `furthermore`)
  and zero cliché phrases;
- first-person markers at or above his baseline;
- concrete numbers and named standards in every letter.

`ai_check.py --detector` will still run `llm-detector` if it is installed, and
`--gptzero` will call the real thing if a `GPTZERO_API_KEY` is ever provided.
Both are reported as instrumentation, never as pass/fail.

## 5. What to tell the applicant

If a recruiter's screen demands "under 15 %", the honest answer is that the
figure is not reproducible: the same letter will come back at 4 % from one
vendor and 60 % from another, and both will also flag the job advert itself.
The defensible position is that the letters are written in his own voice,
match his own reference letters structurally, and contain no templated
language. That is what was optimised, and it is checkable.

## 6. Reproducing

```bash
python3 tools/ai_check.py applications/<slug>/letter.fr.json
python3 tools/ai_check.py applications/<slug>/letter.fr.json --detector
pip install llm-detector          # only needed for --detector
```
