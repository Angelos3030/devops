"""Ο solver πρέπει να ψάχνει ΚΑΙ ΤΙΣ ΔΥΟ κατευθύνσεις φωτεινότητας.

Γιατί υπάρχει: το clean-work (υδραυλικός) απέτυχε με τρία ζεύγη κηρυγμένα
«αδύνατα» — λευκό κείμενο πάνω σε ανοιχτό γαλάζιο #7cb8eb. Η παλιά ευρετική
έλεγε «φόντο πιο σκούρο από το κείμενο; φώτισε το κείμενο», οπότε έστελνε το
λευκό να γίνει πιο λευκό. Σκούρο κείμενο στο ίδιο φόντο δίνει ~10:1.

Το δεύτερο μάθημα ήταν το κόστος: μία διόρθωση ανά γύρο σήμαινε ότι τέσσερις
παραβάσεις κατανάλωναν και τους τέσσερις γύρους — 27 λεπτά — και το theme
σταματούσε στο 4.48 έναντι 4.5. Ο solver δεν κοστίζει tokens· δεν υπάρχει λόγος
να δουλεύει ένα ζεύγος τη φορά.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.contrast_repair import contrast, parse_failures, solve, to_hsl  # noqa: E402


class BothDirections(unittest.TestCase):
    def test_white_on_light_background_darkens(self) -> None:
        """Το ακριβές ζεύγος που κόλλησε το clean-work."""
        value, err = solve("#ffffff", "#7cb8eb", 4.5)
        self.assertIsNotNone(value, err)
        self.assertGreaterEqual(contrast(value, "#7cb8eb"), 4.5)

    def test_dark_on_dark_background_lightens(self) -> None:
        value, err = solve("#1c1f24", "#2a2a2a", 4.5)
        self.assertIsNotNone(value, err)
        self.assertGreaterEqual(contrast(value, "#2a2a2a"), 4.5)

    def test_hue_survives_both_directions(self) -> None:
        for fg, bg in (("#e5e50f", "#4f83d1"), ("#4f83d1", "#ffffff")):
            with self.subTest(fg=fg):
                value, _ = solve(fg, bg, 4.5)
                self.assertIsNotNone(value)
                self.assertAlmostEqual(to_hsl(fg)[0], to_hsl(value)[0], delta=1.0)

    def test_still_fails_closed_when_truly_impossible(self) -> None:
        """Καμία αποδυνάμωση: αν όντως δεν υπάρχει λύση, δεν γράφεται τίποτα."""
        value, err = solve("#808080", "#808080", 21.0)
        self.assertIsNone(value)
        self.assertIn("αδύνατο", err)

    def test_prefers_the_smaller_move(self) -> None:
        """Όταν λύνουν και οι δύο κατευθύνσεις, κερδίζει η κοντινότερη."""
        value, _ = solve("#6e6e6e", "#9a9a9a", 3.0)
        self.assertIsNotNone(value)
        self.assertLess(to_hsl(value)[2], to_hsl("#6e6e6e")[2] + 0.5)


class AllViolationsAtOnce(unittest.TestCase):
    CSS = (".root {\n  --vt-ink-soft: #6a6a6a;\n  --vt-surface-2: #fffafa;\n"
           "  --vt-on-accent: #ffffff;\n  --vt-accent: #7cb8eb;\n}\n")

    def test_collects_every_failing_pair(self) -> None:
        log = ("  ✗ CleanService: on-accent/accent 2.12 < 4.5\n"
               "  ✗ CleanService: ink-soft/surface-2 4.48 < 4.5\n")
        found = parse_failures(log, self.CSS)
        self.assertEqual({f["fg_token"] for f in found}, {"on-accent", "ink-soft"})

    def test_empty_log_yields_nothing(self) -> None:
        self.assertEqual(parse_failures("όλα καλά", self.CSS), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)


class ConvergesInPlace(unittest.TestCase):
    """Η διόρθωση χρώματος δεν επιτρέπεται να καίει γύρους του μοντέλου.

    Μετρήθηκε στο clean-work: αφού πέρασαν τα τέσσερα ζεύγη κειμένου,
    εμφανίστηκε `line/surface 1.19 < 1.2` — μία εκατοστή κάτω από το όριο. Κάθε
    τέτοιο κύμα κόστιζε ένα ολόκληρο ξαναγράψιμο JSX+CSS (~7 λεπτά) επειδή ο
    solver έτρεχε μία φορά ανά γύρο. Είναι αριθμητικός και δωρεάν: πρέπει να
    συγκλίνει επί τόπου.
    """

    src = (ROOT / "src" / "port_worker.py").read_text(encoding="utf-8")

    def test_repeats_until_clean(self) -> None:
        self.assertIn("for _ in range(CONTRAST_PASSES):", self.src)
        self.assertIn('_run(["node", "tests/spine_guard.mjs"]', self.src)

    def test_bounded_so_oscillation_cannot_hang(self) -> None:
        import src.port_worker as pw  # noqa: PLC0415
        self.assertGreaterEqual(pw.CONTRAST_PASSES, 2)
        self.assertLessEqual(pw.CONTRAST_PASSES, 10)

    def test_stops_when_a_pass_changes_nothing(self) -> None:
        """Αλλιώς ένα άλυτο ζεύγος θα ξανατρέχε τον guard μέχρι το φράγμα."""
        self.assertIn("if not _contrast_pass(failures, css_path, res):", self.src)
