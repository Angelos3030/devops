"""Η αντιστοίχιση vertical→demo πρέπει να είναι ΣΗΜΑΣΙΟΛΟΓΙΚΑ έγκυρη.

Γιατί υπάρχει: το `music` αντιστοιχίστηκε στο `salon` επειδή το κομμωτήριο έχει
τα πλουσιότερα πεδία του demoData. Ο έλεγχος περνούσε — υπήρχε ρητή εγγραφή —
και το αποτέλεσμα ήταν εικονίδια μουσικής (νότα, βιντεοκάμερα) πάνω από
«Κούρεμα & styling», με τιμές κομμωτηρίου σε theme μουσικού.

Συντακτικά έγκυρο, σημασιολογικά παράλογο.

Το βαθύτερο λάθος ήταν η ΣΕΙΡΑ των κριτηρίων: πρώτα «ποιο demo έχει αρκετά
δεδομένα;» και μετά «ταιριάζει;». Πλούσια αλλά άσχετα δεδομένα είναι χειρότερα
από φτωχά αλλά σωστά — κρύβουν τα πραγματικά ελαττώματα του theme πίσω από τον
θόρυβο της αναντιστοιχίας. Το ίδιο μάθημα με το ιατρικό theme πάνω σε
φωτογραφίες κουζίνας, σε άλλη μορφή.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.port_worker import (  # noqa: E402
    DEMO_FAMILY, VERTICAL_DEMO, VERTICAL_FAMILY,
    DemoMappingMissing, DemoSemanticallyUnsupported, demo_for,
)


class CompatiblePairs(unittest.TestCase):
    def test_same_family_mappings_pass(self) -> None:
        for vertical, expected in (("medical", "physician"), ("fitness", "gym"),
                                   ("beauty", "salon"), ("property", "realestate"),
                                   ("food", "taverna"), ("trades", "plumber")):
            with self.subTest(vertical=vertical):
                self.assertEqual(demo_for({"verticals": [vertical]}), expected)

    def test_every_accepted_mapping_shares_a_family(self) -> None:
        """Καμία εγγραφή του πίνακα δεν επιτρέπεται να περνά κατά λάθος."""
        for vertical, demo in VERTICAL_DEMO.items():
            fam = VERTICAL_FAMILY.get(vertical)
            if fam is None:
                continue                      # ρητά απορριπτόμενο, ελέγχεται πιο κάτω
                                              # noqa: E116
            self.assertEqual(DEMO_FAMILY.get(demo), fam,
                             f"{vertical}->{demo}: ασύμβατες οικογένειες")


class SemanticMismatch(unittest.TestCase):
    def test_music_to_salon_is_rejected(self) -> None:
        with self.assertRaises(DemoSemanticallyUnsupported) as cm:
            demo_for({"verticals": ["music"]})
        self.assertIn("DEMO_SEMANTICALLY_UNSUPPORTED", str(cm.exception))

    def test_content_to_farm_is_rejected(self) -> None:
        with self.assertRaises(DemoSemanticallyUnsupported):
            demo_for({"verticals": ["content"]})

    def test_richness_never_overrides_mismatch(self) -> None:
        """Το salon έχει τα περισσότερα πεδία· δεν του δίνει κανένα δικαίωμα."""
        from src.vitrina_contract import availability  # noqa: PLC0415
        counts = {b: sum(m["count"] for m in availability(b)["arrays"].values())
                  for b in ("salon", "plumber", "farm")}
        self.assertGreaterEqual(counts["salon"], counts["plumber"],
                                "η υπόθεση του test άλλαξε: το salon δεν είναι πια πλουσιότερο")
        with self.assertRaises(DemoSemanticallyUnsupported):
            demo_for({"verticals": ["music"]})


class FailClosed(unittest.TestCase):
    def test_unknown_vertical_fails_closed(self) -> None:
        for bogus in (["blockchain"], ["unknown"], [], [None]):
            with self.subTest(v=bogus), self.assertRaises(DemoMappingMissing):
                demo_for({"verticals": bogus})

    def test_no_silent_fallback_demo(self) -> None:
        """Ούτε salon, ούτε farm, ούτε carpenter ως εφεδρεία."""
        for bogus in ("music", "content", "blockchain"):
            with self.subTest(v=bogus):
                try:
                    demo_for({"verticals": [bogus]})
                except DemoMappingMissing:
                    continue
                self.fail(f"το «{bogus}» πήρε demo χωρίς σημασιολογική βάση")

    def test_semantic_error_is_a_mapping_error(self) -> None:
        """Ο υπάρχων χειρισμός (BLOCKED) πρέπει να συνεχίσει να πιάνει και τα δύο."""
        self.assertTrue(issubclass(DemoSemanticallyUnsupported, DemoMappingMissing))


if __name__ == "__main__":
    unittest.main(verbosity=2)
