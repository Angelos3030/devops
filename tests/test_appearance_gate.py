"""Η πύλη του port worker πρέπει να βλέπει ΧΡΩΜΑ, όχι μόνο δομή.

Γιατί υπάρχει: το klassy-cafe έφτασε READY_FOR_REVIEW με primary CTA σε
αντίθεση 1.00 — λευκό κείμενο σε λευκό φόντο. Πέρασε build, spine_guard,
trust_guard, templateRegistry και μηδενική υπερχείλιση, γιατί καμία από αυτές
τις πύλες δεν κοιτάζει pixel. Το `design_guard.mjs` έπιανε ακριβώς αυτό εδώ και
καιρό· ο worker απλώς δεν το έτρεχε.

Το ελάττωμα δεν ήταν το χρώμα αλλά η ΕΙΔΙΚΟΤΗΤΑ: `.root a { color: inherit }`
(0,2,0) υπερισχύει του `.heroButton` (0,1,0).
"""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class DesignGuardFlags(unittest.TestCase):
    def test_only_flag_rejects_unknown_template(self) -> None:
        """Το --only δεν πρέπει να «πετυχαίνει» σιωπηλά με άδεια λίστα."""
        proc = subprocess.run(
            ["node", "tests/design_guard.mjs", "--only", "δεν-υπάρχει-τέτοιο"],
            cwd=ROOT / "sites", capture_output=True, text=True, timeout=120,
            encoding="utf-8", errors="replace")
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)


class WorkerGate(unittest.TestCase):
    src = (ROOT / "src" / "port_worker.py").read_text(encoding="utf-8")

    def test_appearance_runs_inside_preview(self) -> None:
        self.assertIn('metrics["appearance"] = _appearance(', self.src)

    def test_appearance_blocks_acceptance(self) -> None:
        """Χωρίς αυτό, ένας υποψήφιος με αόρατο κείμενο γίνεται ACCEPTED."""
        self.assertIn("and app_ok", self.src)

    def test_appearance_fails_closed_in_result(self) -> None:
        self.assertIn('if not _app.get("passed", False):', self.src)


class ContractRules(unittest.TestCase):
    def test_prompt_lists_selfhosted_fonts_and_specificity(self) -> None:
        from src.vitrina_contract import as_prompt, extract  # noqa: PLC0415
        c = extract()
        self.assertIn("Inter", c["fonts"])
        self.assertNotIn("Poppins", c["fonts"])
        txt = as_prompt(c, "Probe")
        self.assertIn(":where(a)", txt)
        for family in ("Manrope", "Syne"):
            self.assertIn(family, txt)


if __name__ == "__main__":
    unittest.main(verbosity=2)


class StickyConstraints(unittest.TestCase):
    """Ό,τι απέρριψε ένας guard δεν επιτρέπεται να επανέλθει σε επόμενο γύρο.

    Μετρήθηκε στο klassy-cafe: ο data-binding guard έκοψε το
    `d.services[].price`, ο δεύτερος γύρος το αφαίρεσε σωστά, και ο τρίτος —
    που ζητούσε μόνο διόρθωση αντίθεσης — ξαναέγραψε ολόκληρο το αρχείο και το
    επανέφερε. Το run πέθανε στο ίδιο εύρημα από το οποίο είχε ήδη γιατρευτεί.
    """

    def test_accumulates_without_duplicates(self) -> None:
        from src.port_worker import sticky_lines  # noqa: PLC0415
        a = sticky_lines([], "[data_binding] price: 0/4\n\n")
        self.assertEqual(a, ["[data_binding] price: 0/4"])
        b = sticky_lines(a, "  [data_binding] price: 0/4  ")
        self.assertEqual(b, a, "ίδιος περιορισμός δεν διπλασιάζεται")
        c = sticky_lines(b, "[media] alt λείπει")
        self.assertEqual(c, ["[data_binding] price: 0/4", "[media] alt λείπει"])

    def test_previous_constraints_survive_new_round(self) -> None:
        src = (ROOT / "src" / "port_worker.py").read_text(encoding="utf-8")
        self.assertIn("ΜΟΝΙΜΟΙ ΠΕΡΙΟΡΙΣΜΟΙ", src)
        self.assertIn("_remember(summarize(guard_out))", src)


class RepairBase(unittest.TestCase):
    """Η επιδιόρθωση τροποποιεί το ΤΡΕΧΟΝ αρχείο, δεν το ξαναπαράγει.

    Τρία διαδοχικά runs πέθαναν στο ίδιο εύρημα (`d.services[].price`) που είχαν
    ήδη διορθώσει έναν γύρο νωρίτερα. Η αιτία δεν ήταν απειθαρχία του μοντέλου:
    κάθε γύρος έγραφε το αρχείο από την αρχή με βάση το πρωτότυπο HTML — που
    έχει τιμές — γιατί κανείς δεν του έδινε το τρέχον αρχείο. Η οδηγία «μην
    αλλάξεις τίποτε άλλο» δεν είχε αντικείμενο αναφοράς.
    """

    src = (ROOT / "src" / "port_worker.py").read_text(encoding="utf-8")

    def test_current_file_is_sent_back_on_repair(self) -> None:
        self.assertIn("ΤΟ ΤΡΕΧΟΝ ΑΡΧΕΙΟ — ΞΕΚΙΝΑ ΑΠΟ ΑΥΤΟ", self.src)
        self.assertIn('_base("jsx") if feedback else ""', self.src)
        self.assertIn('_base("css") if feedback else ""', self.src)

    def test_first_pass_has_no_base(self) -> None:
        """Στην πρώτη παραγωγή δεν υπάρχει τρέχον αρχείο — μόνο στις επιδιορθώσεις."""
        self.assertNotIn('_base("jsx"))', self.src)
