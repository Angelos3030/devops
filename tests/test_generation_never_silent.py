"""Μια απορριφθείσα παραγωγή δεν επιτρέπεται να περάσει για επιδιόρθωση.

Το σφάλμα που καλύπτει: το βήμα CSS απορριπτόταν για `!important`, εξαντλούσε
τις απόπειρές του, επέστρεφε `None`, και το `_generate()` γύριζε **χωρίς να
αλλάξει τα αρχεία**. Ο βρόχος συνέχιζε πάνω σε παλιό CSS και έκαιγε όλο το
budget. Απόδειξη ότι καμία διόρθωση δεν έφτανε στον δίσκο: ίδιο `#247cff`,
ίδια 3,69:1, σε **τρία διαδοχικά τρεξίματα**.

Το επικίνδυνο δεν ήταν η αποτυχία — ήταν ότι έμοιαζε με πρόοδο.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.port_worker import _validate, PortWorkerError  # noqa: E402

REC = {"component": "MedicCare", "theme_key": "medic-care"}


def _css(body: str) -> list[dict[str, str]]:
    return [{"path": "sites/lib/templates/MedicCare.module.css", "content": body}]


class GenerationNeverSilent(unittest.TestCase):
    def test_important_is_rejected(self) -> None:
        with self.assertRaises(PortWorkerError) as cm:
            _validate(_css(".root { color: red !important; }"), REC)
        self.assertIn("!important", str(cm.exception))

    def test_clean_css_passes(self) -> None:
        ok = _validate(_css(".root { --vt-ink: #222; color: var(--vt-ink); }"), REC)
        self.assertEqual(len(ok), 1)

    def test_generate_signals_failure_instead_of_returning_none(self) -> None:
        """Το `_generate` πρέπει να επιστρέφει bool, όχι να γυρίζει σιωπηλά."""
        src = (Path(__file__).resolve().parents[1] / "src" / "port_worker.py"
               ).read_text(encoding="utf-8")
        self.assertIn('def _generate(feedback: str = "") -> bool:', src,
                      "το _generate πρέπει να δηλώνει επιτυχία/αποτυχία")
        self.assertIn('res["generation_blocked"]', src,
                      "η αποτυχία παραγωγής πρέπει να καταγράφεται στο result")
        # Καμία διαδρομή του _generate δεν τερματίζει με γυμνό `return`
        body = src[src.index('def _generate(feedback'):]
        body = body[:body.index("\n    # Guards")] if "\n    # Guards" in body else body[:4000]
        self.assertNotIn("\n            return\n", body,
                         "γυμνό return: η αποτυχία θα περνούσε ως επιδιόρθωση")

    def test_step_outcomes_are_recorded(self) -> None:
        src = (Path(__file__).resolve().parents[1] / "src" / "port_worker.py"
               ).read_text(encoding="utf-8")
        for outcome in ("SUCCESS", "VALIDATION_FAILED",
                        "GENERATION_FAILED", "BUDGET_EXHAUSTED"):
            self.assertIn(f'"{outcome}"', src, f"λείπει η κατάσταση {outcome}")
        self.assertIn('res.setdefault("generation_steps"', src,
                      "τα βήματα παραγωγής πρέπει να persistάρονται στο result.json")

    def test_css_prompt_forbids_important_explicitly(self) -> None:
        """Η απαγόρευση πρέπει να είναι ΣΤΟ βήμα CSS, όχι μόνο στην κεφαλίδα."""
        src = (Path(__file__).resolve().parents[1] / "src" / "port_worker.py"
               ).read_text(encoding="utf-8")
        step = src[src.index('_one("CSS"'):src.index('_one("CSS"') + 1400]
        self.assertIn("!important", step,
                      "το βήμα CSS δεν απαγορεύει ρητά το !important")


if __name__ == "__main__":
    unittest.main(verbosity=2)
