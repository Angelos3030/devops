"""Κάθε σκουπίδι που μπορεί να γυρίσει μοντέλο -> NO_WRITE, ποτέ εγγραφή.

Το μετρημένο περιστατικό: `json.loads("")` σε 4/4 κλήσεις, επειδή τα reasoning
tokens κατανάλωσαν όλο το budget των 400 και το σώμα βγήκε άδειο. Το fail-closed
δούλεψε — έλειπε μόνο η διάγνωση και το επαρκές budget.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.contrast_repair import (  # noqa: E402
    NO_WRITE, apply_token, contrast, parse_response, token_value, verify,
)

CSS = (".root {\n  --vt-surface-2: #F9F9F9;\n  --vt-accent-ink: #247cff;\n"
       "  --vt-ink: #1A1A1A;\n}\n.timeline { display: grid; gap: 24px; }\n")


class ContrastResponse(unittest.TestCase):
    def _no_write(self, raw, needle=""):
        value, err = parse_response(raw)
        self.assertIsNone(value, f"δέχτηκε τιμή από {raw!r}")
        self.assertTrue(err, "λείπει δομημένο σφάλμα")
        if needle:
            self.assertIn(needle, err)

    # 1 · 2 --------------------------------------------------------------
    def test_empty_and_whitespace_content(self) -> None:
        for raw in ("", None, "   ", "\n\t  \n"):
            with self.subTest(raw=repr(raw)):
                self._no_write(raw, "άδειο")

    # 3 ------------------------------------------------------------------
    def test_malformed_json(self) -> None:
        for raw in ('{"value": ', "not json at all", '{"value" "#000000"}', "[1,2,3]"):
            with self.subTest(raw=raw):
                self._no_write(raw)

    # 4 ------------------------------------------------------------------
    def test_missing_or_wrong_typed_fields(self) -> None:
        self._no_write('{"why": "ξέχασα την τιμή"}', "value")
        self._no_write('{"value": 16711680}', "συμβολοσειρά")
        self._no_write('{"value": null}', "συμβολοσειρά")
        self._no_write('{"value": "cornflowerblue"}', "hex")
        self._no_write('{"value": "rgb(11,63,168)"}', "hex")

    # 5 ------------------------------------------------------------------
    def test_valid_json_failing_wcag_does_not_write(self) -> None:
        value, err = parse_response('{"value": "#3a8dff"}')
        self.assertEqual(value, "#3a8dff")   # έγκυρο σχήμα…
        ok, ratio = verify(value, "#F9F9F9", 4.5)
        self.assertFalse(ok, f"…αλλά {ratio}:1 < 4.5 — δεν πρέπει να γραφτεί")

    # 6 ------------------------------------------------------------------
    def test_passing_candidate_mutates_exactly_one_line(self) -> None:
        value, err = parse_response('{"value": "#0b3fa8", "why": "σκουρότερο μπλε"}')
        self.assertEqual(err, "")
        ok, ratio = verify(value, "#F9F9F9", 4.5)
        self.assertTrue(ok, f"{ratio}:1")
        out = apply_token(CSS, "accent-ink", value)
        a, b = CSS.splitlines(), out.splitlines()
        changed = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        self.assertEqual(len(changed), 1)
        self.assertIn("--vt-accent-ink", b[changed[0]])
        self.assertEqual(token_value(out, "surface-2"), "#F9F9F9")
        self.assertEqual(token_value(out, "ink"), "#1A1A1A")
        self.assertIn(".timeline { display: grid; gap: 24px; }", out)
        self.assertGreaterEqual(contrast(value, "#F9F9F9"), 4.5)

    def test_no_write_constant_is_used(self) -> None:
        src = (Path(__file__).resolve().parents[1] / "src" / "port_worker.py"
               ).read_text(encoding="utf-8")
        self.assertIn("cr.NO_WRITE", src)
        # Η στενή κλήση χρησιμοποιεί το ΦΘΗΝΟ, μη-reasoning μοντέλο με μικρό
        # budget: το reasoning μοντέλο επέστρεφε κενό content και στα 1500.
        self.assertIn("ask_cheap(", src)
        self.assertIn("self._pass1_model", src)
        self.assertIn("max_tokens=300", src)
        self.assertNotIn("max_tokens=1500", src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
