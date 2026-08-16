"""Η διόρθωση αντίθεσης αλλάζει ΜΙΑ τιμή token — τίποτε άλλο.

Το σφάλμα που κλείνει: για να αλλάξει έξι χαρακτήρες σε ένα token, ο worker
ζητούσε ολόκληρο το φύλλο στυλ ξανά. Το μοντέλο ξαναέγραφε 700 γραμμές και
μετακινούσε padding/πλάτη, φέρνοντας νέες υπερχειλίσεις σε κάθε γύρο. Το
συναλλακτικό όριο τις απέρριπτε σωστά — αλλά η αντίθεση δεν διορθωνόταν ποτέ.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.contrast_repair import (  # noqa: E402
    apply_token, contrast, parse_failure, token_value, verify,
)

CSS = """.root {
  --vt-surface: #FFFFFF;
  --vt-surface-2: #F9F9F9;
  --vt-ink: #1A1A1A;
  --vt-accent: #247cff;
  --vt-accent-ink: #247cff;
  --vt-line: #E4E4E4;
}
.timeline { display: grid; gap: 24px; padding: 40px 0; }
.timelineContent { width: 100%; max-width: 495px; }
.hero h1 { font-size: 48px; letter-spacing: -0.02em; }
"""

LOG = ("  ✗ MedicCare (original): accent-ink/surface-2 3.69<4.5\n"
       "  χαμηλότερη αντίθεση κειμένου: 3.69:1 — MedicCare (original) accent-ink/surface-2\n"
       "❌ 1 παραβάσεις του συμβολαίου")


class ContrastRepair(unittest.TestCase):
    def test_parse_is_deterministic(self) -> None:
        f = parse_failure(LOG, CSS)
        self.assertEqual(f["fg_token"], "accent-ink")
        self.assertEqual(f["bg_token"], "surface-2")
        self.assertEqual(f["fg_value"], "#247cff")
        self.assertEqual(f["bg_value"], "#F9F9F9")
        self.assertEqual(f["required"], 4.5)

    def test_contrast_math_matches_the_guard(self) -> None:
        # Το ίδιο ζεύγος που ανέφερε το spine: ~3.69:1
        self.assertAlmostEqual(contrast("#247cff", "#F9F9F9"), 3.69, delta=0.08)
        self.assertGreater(contrast("#000000", "#FFFFFF"), 20)

    # 1 ------------------------------------------------------------------
    def test_repair_cannot_modify_layout_selectors(self) -> None:
        out = apply_token(CSS, "accent-ink", "#0b3fa8")
        for line in (".timeline { display: grid; gap: 24px; padding: 40px 0; }",
                     ".timelineContent { width: 100%; max-width: 495px; }",
                     ".hero h1 { font-size: 48px; letter-spacing: -0.02em; }"):
            self.assertIn(line, out, f"άλλαξε δήλωση διάταξης/τυπογραφίας: {line}")

    # 2 ------------------------------------------------------------------
    def test_unrelated_tokens_are_byte_identical(self) -> None:
        out = apply_token(CSS, "accent-ink", "#0b3fa8")
        for tok in ("surface", "surface-2", "ink", "accent", "line"):
            self.assertEqual(token_value(out, tok), token_value(CSS, tok),
                             f"άλλαξε το άσχετο token --vt-{tok}")

    def test_diff_is_exactly_one_line(self) -> None:
        out = apply_token(CSS, "accent-ink", "#0b3fa8")
        a, b = CSS.splitlines(), out.splitlines()
        self.assertEqual(len(a), len(b))
        changed = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        self.assertEqual(len(changed), 1, f"άλλαξαν {len(changed)} γραμμές, όχι μία")
        self.assertIn("--vt-accent-ink", b[changed[0]])

    # 3 ------------------------------------------------------------------
    def test_successful_repair_reaches_required_ratio(self) -> None:
        f = parse_failure(LOG, CSS)
        ok, ratio = verify("#0b3fa8", f["bg_value"], f["required"])
        self.assertTrue(ok, f"η προτεινόμενη τιμή δίνει μόνο {ratio}:1")
        out = apply_token(CSS, f["fg_token"], "#0b3fa8")
        self.assertGreaterEqual(contrast(token_value(out, "accent-ink"),
                                         token_value(out, "surface-2")), 4.5)

    # 4 ------------------------------------------------------------------
    def test_insufficient_value_is_rejected_before_applying(self) -> None:
        f = parse_failure(LOG, CSS)
        ok, ratio = verify("#3a8dff", f["bg_value"], f["required"])
        self.assertFalse(ok, f"δέχτηκε τιμή με {ratio}:1 < 4.5")

    def test_invalid_value_never_touches_the_file(self) -> None:
        for bad in ("blue", "rgb(1,2,3)", "#12", ""):
            with self.subTest(v=bad), self.assertRaises(ValueError):
                apply_token(CSS, "accent-ink", bad)

    def test_unknown_token_raises(self) -> None:
        with self.assertRaises(ValueError):
            apply_token(CSS, "does-not-exist", "#000000")

    def test_parse_returns_none_when_not_a_contrast_failure(self) -> None:
        self.assertIsNone(parse_failure("✗ κάτι άλλο έσπασε", CSS))


if __name__ == "__main__":
    unittest.main(verbosity=2)
