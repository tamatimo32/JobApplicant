"""Tests for tools/ai_check.py — the letter style checker.

These exist because the first version of the checker produced a confident
"AI score" from invented weights, and a bug glued the salutation onto the
first sentence. Both are now pinned down.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

import ai_check  # noqa: E402


class ProseExtractionTest(unittest.TestCase):
    """Only body paragraphs are prose. Headings corrupt sentence statistics."""

    def test_headings_are_excluded(self):
        data = {"tagline": "a tagline without a full stop",
                "subject": "Objet : candidature sans point",
                "salutation": "Madame, Monsieur,",
                "paragraphs": ["First real sentence here. Second one follows."],
                "closing": "Cordialement,"}
        text = ai_check.letter_text(data)
        self.assertNotIn("Madame", text)
        self.assertNotIn("tagline", text)
        self.assertTrue(text.startswith("First real sentence"))

    def test_salutation_does_not_glue_to_first_sentence(self):
        data = {"salutation": "Dear Hiring Team,",
                "paragraphs": ["A permit is only worth the evidence behind it."]}
        sents = ai_check.sentences(ai_check.letter_text(data))
        self.assertEqual(sents, ["A permit is only worth the evidence behind it."])

    def test_accepts_str_and_list(self):
        data = {"paragraphs": "single string body", "closing": "Cordialement,"}
        self.assertEqual(ai_check.letter_text(data), "single string body")


class FeatureTest(unittest.TestCase):

    def test_counts_sentences_and_short_lines(self):
        f = ai_check.features(
            "One two three four five six seven. "
            "This is a considerably longer sentence that runs on for a while "
            "and keeps going well past any reasonable length.")
        self.assertEqual(f.sentences, 2)
        self.assertEqual(f.short, 1)
        self.assertGreater(f.stdev_len, 0)

    def test_detects_stock_connectives(self):
        f = ai_check.features(
            "Moreover the programme is robust. Furthermore it is holistic. "
            "Additionally we leverage synergies.")
        self.assertGreaterEqual(f.connectives, 3)

    def test_detects_cliches(self):
        f = ai_check.features(
            "I am passionate about sustainability and I am thrilled to apply.")
        self.assertGreaterEqual(f.cliches, 2)

    def test_french_is_detected(self):
        self.assertTrue(ai_check._is_french(
            "J'ai construit des indicateurs pour les équipes."))
        self.assertFalse(ai_check._is_french(
            "I have built indicators for the teams."))

    def test_no_connectives_in_plain_prose(self):
        f = ai_check.features(
            "A permit is only worth the evidence file behind it. "
            "Most of the work is the monitoring record.")
        self.assertEqual(f.connectives, 0)
        self.assertEqual(f.cliches, 0)


class BaselineTest(unittest.TestCase):

    def test_reference_letters_are_present(self):
        base = ai_check.baseline()
        self.assertIn("ML_Master_Format", base)
        self.assertIn("ML_FEAD", base)

    def test_reference_rhythm_is_not_flat(self):
        """The applicant's own letters vary a lot. That is the target."""
        for name, feats in ai_check.baseline().items():
            self.assertGreater(feats.stdev_len, 7.0,
                               f"{name} should show varied sentence length")
            self.assertEqual(feats.connectives, 0,
                             f"{name} uses no stock connectives")

    def test_reference_has_no_em_dash(self):
        for text in ai_check.REFERENCE.values():
            self.assertNotIn("\u2014", text)


class DetectorHonestyTest(unittest.TestCase):
    """The checker must never invent a pass/fail percentage."""

    def test_no_proxy_score_exists(self):
        self.assertFalse(hasattr(ai_check, "analyse"),
                         "the invented weighted 'AI %' must not come back")

    def test_llm_detector_degrades_gracefully(self):
        try:
            import llm_detector  # noqa: F401
        except ImportError:
            out = ai_check.llm_detector_score("some text")
            self.assertIsNone(out["p_llm"])
            self.assertIn("error", out)

    def test_documented_threshold_is_absent(self):
        src = (ROOT / "tools" / "ai_check.py").read_text(encoding="utf-8")
        self.assertNotIn("VERDICT", src)


if __name__ == "__main__":
    unittest.main()
