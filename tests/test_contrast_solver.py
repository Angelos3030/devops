"""Η διόρθωση αντίθεσης είναι αριθμητική, όχι γνωμοδοτική.

Μετρήθηκε σε τέσσερα τρεξίματα: το μοντέλο γέμιζε ΚΑΘΕ budget με reasoning
(300→300, 1000→1000 tokens), `finish_reason: length`, `content` πάντα κενό.
Η εργασία όμως είναι κλειστού τύπου — «σκούρυνε μέχρι 4,5:1» — και λύνεται
ακριβώς, επαναλήψιμα και δωρεάν.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.contrast_repair import (  # noqa: E402
    apply_token, contrast, solve, to_hsl, token_value,
)

CSS = (".root {\n  --vt-surface-2: #F9F9F9;\n  --vt-accent-ink: #247cff;\n"
       "  --vt-ink: #1A1A1A;\n  --vt-accent: #247cff;\n}\n"
       ".timeline { display: grid; gap: 24px; }\n.hero h1 { font-size: 48px; }\n")


class DeterministicContrast(unittest.TestCase):
    # A + το γνωστό περιστατικό Medic Care -------------------------------
    def test_medic_care_case_darkens_to_threshold(self) -> None:
        value, err = solve("#247cff", "#F9F9F9", 4.5)
        self.assertEqual(err, "")
        self.assertGreaterEqual(contrast(value, "#F9F9F9"), 4.5)

    # B ------------------------------------------------------------------
    def test_lightens_against_dark_background(self) -> None:
        value, err = solve("#333333", "#111111", 4.5)
        self.assertEqual(err, "")
        self.assertGreaterEqual(contrast(value, "#111111"), 4.5)
        # φώτισε, δεν σκούρυνε
        self.assertGreater(to_hsl(value)[2], to_hsl("#333333")[2])

    # C ------------------------------------------------------------------
    def test_already_passing_pair_is_no_change(self) -> None:
        value, err = solve("#000000", "#FFFFFF", 4.5)
        self.assertIsNone(value)
        self.assertIn("NO_CHANGE", err)

    # D ------------------------------------------------------------------
    def test_minimal_change(self) -> None:
        """Δεν πέφτει σε μαύρο/λευκό όταν υπάρχει κοντινότερη λύση."""
        value, _ = solve("#247cff", "#F9F9F9", 4.5)
        self.assertNotIn(value.lower(), ("#000000", "#ffffff"))
        before, after = to_hsl("#247cff"), to_hsl(value)
        self.assertAlmostEqual(before[0], after[0], delta=1.0)   # ίδια απόχρωση
        self.assertAlmostEqual(before[1], after[1], delta=0.05)  # ίδιος κορεσμός
        self.assertLess(before[2] - after[2], 0.30, "υπερβολική αλλαγή φωτεινότητας")

    # E ------------------------------------------------------------------
    def test_unrelated_tokens_byte_identical(self) -> None:
        value, _ = solve("#247cff", "#F9F9F9", 4.5)
        out = apply_token(CSS, "accent-ink", value)
        for tok in ("surface-2", "ink", "accent"):
            self.assertEqual(token_value(out, tok), token_value(CSS, tok))
        self.assertIn(".timeline { display: grid; gap: 24px; }", out)
        self.assertIn(".hero h1 { font-size: 48px; }", out)
        changed = [i for i, (x, y) in enumerate(zip(CSS.splitlines(), out.splitlines())) if x != y]
        self.assertEqual(len(changed), 1)

    # F ------------------------------------------------------------------
    def test_impossible_and_invalid_input_no_write(self) -> None:
        # Κατώφλι πέρα από το εφικτό εύρος
        value, err = solve("#808080", "#7F7F7F", 21.0)
        self.assertIsNone(value)
        self.assertTrue(err)
        for bad in ("blue", "#12", "", "rgb(0,0,0)"):
            with self.subTest(v=bad):
                self.assertIsNone(solve(bad, "#FFFFFF", 4.5)[0])
                self.assertIsNone(solve("#000000", bad, 4.5)[0])

    # G ------------------------------------------------------------------
    def test_deterministic_output(self) -> None:
        runs = {solve("#247cff", "#F9F9F9", 4.5)[0] for _ in range(6)}
        self.assertEqual(len(runs), 1, f"μη ντετερμινιστικό: {runs}")

    def test_no_model_tokens_are_spent(self) -> None:
        src = (Path(__file__).resolve().parents[1] / "src" / "port_worker.py"
               ).read_text(encoding="utf-8")
        head = src[src.index("def _contrast_only_fix"):src.index("def port_source")]
        self.assertIn("cr.solve(", head)
        self.assertNotIn("ask_cheap", head, "η διαδρομή καλεί ακόμη μοντέλο")
        self.assertNotIn("chat.ask", head)
        self.assertIn('"model_tokens": 0', head)


if __name__ == "__main__":
    unittest.main(verbosity=2)
