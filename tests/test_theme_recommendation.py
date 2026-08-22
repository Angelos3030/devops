# -*- coding: utf-8 -*-
"""Οι προτάσεις theme πρέπει να ταιριάζουν στο επάγγελμα.

Το σφάλμα που φυλάει αυτό το αρχείο: ένα κομμωτήριο έβλεπε σχέδια καφετέριας.
Η αιτία δεν ήταν κακό theme — ήταν ότι η συμβατότητα δεν ήταν ποτέ ρητή, και
δύο ξεχωριστά κενά την έκρυβαν:

  · 18 από τα 58 εμπορικά themes δεν ανήκαν σε ΚΑΝΕΝΑ vertical, άρα δεν
    μπορούσαν ποτέ να προταθούν — μόνο να βρεθούν με περιήγηση.
  · 8 themes που το backend χρησιμοποιεί σε 8–18 επαγγέλματα ήταν δηλωμένα με
    ΜΙΑ κατηγορία, οπότε ένα «Κινηματογραφικό» διαβαζόταν ως «Εστίαση» από
    κομμωτήριο.

    python -m unittest tests.test_theme_recommendation -v
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import premium_generator as pg  # noqa: E402
from src import theme_compat as tc  # noqa: E402

COMPAT = tc.build(pg._TEMPLATES_BY_VERTICAL)

# Πραγματικά intake, όπως τα γράφει ο πελάτης στην αρχική.
CASES = {
    "beauty": "Έχω κομμωτήριο στη Γλυφάδα",
    "food": "Έχω ταβέρνα στη Θεσσαλονίκη",
    "dentist": "Οδοντιατρείο στο Χαλάνδρι",
    "trade": "Είμαι υδραυλικός στο Περιστέρι",
    "cafe": "Έχω καφετέρια στην παλιά πόλη",
    "rooms": "Ενοικιαζόμενα δωμάτια στην Πάρο",
}

# Themes χτισμένα σφιχτά γύρω από ένα επάγγελμα — απαγορεύεται να προταθούν
# σε άλλο.
NEVER = {
    "beauty": ["scandinavian-coffee", "klassy-cafe", "heritage-bakery", "frost-bakery",
               "counter-menu", "grecko-table", "aegean", "coast", "callout",
               "constra-build", "villa-agency", "gymso-fitness"],
    "trade": ["scandinavian-coffee", "elegance-salon", "beauty-atelier", "runway",
              "grecko-table", "aegean", "frost-bakery", "klassy-cafe"],
    "dentist": ["scandinavian-coffee", "klassy-cafe", "elegance-salon", "callout",
                "aegean", "frost-bakery", "constra-build"],
    "rooms": ["scandinavian-coffee", "klassy-cafe", "elegance-salon", "callout",
              "frost-bakery", "constra-build", "gymso-fitness"],
    "food": ["elegance-salon", "beauty-atelier", "villa-agency", "callout",
             "constra-build", "gymso-fitness", "runway"],
    "cafe": ["elegance-salon", "beauty-atelier", "villa-agency", "callout",
             "constra-build", "gymso-fitness", "runway"],
}


class VerticalExtraction(unittest.TestCase):
    def test_intake_maps_to_expected_vertical(self):
        for vertical, text in sorted(CASES.items()):
            with self.subTest(vertical=vertical):
                self.assertEqual(pg._vertical({"trade": text}), vertical,
                                 f"λάθος επάγγελμα για «{text}»")


class Relevance(unittest.TestCase):
    def test_all_recommendations_are_relevant(self):
        for vertical, text in sorted(CASES.items()):
            rec = pg.recommend_templates({"trade": text}, limit=12)
            with self.subTest(vertical=vertical):
                self.assertTrue(10 <= len(rec) <= 12,
                                f"{vertical}: {len(rec)} προτάσεις, περίμενα 10–12")
                for key in rec:
                    entry = COMPAT.get(key)
                    self.assertIsNotNone(entry, f"{key}: χωρίς δηλωμένη συμβατότητα")
                    self.assertLessEqual(
                        tc.tier(entry, vertical), 2,
                        f"{vertical}: προτάθηκε «{key}» που είναι για "
                        f"{entry['primary']} και δεν είναι γενικού σκοπού")

    def test_irrelevant_themes_never_appear(self):
        for vertical, banned in sorted(NEVER.items()):
            rec = set(pg.recommend_templates({"trade": CASES[vertical]}, limit=12))
            with self.subTest(vertical=vertical):
                leaked = sorted(rec & set(banned))
                self.assertEqual(leaked, [],
                                 f"{vertical}: διέρρευσαν άσχετα → {leaked}")

    def test_exact_matches_come_first(self):
        rec = pg.recommend_templates({"trade": CASES["beauty"]}, limit=12)
        top = rec[:3]
        for k in top:
            self.assertEqual(tc.tier(COMPAT[k], "beauty"), 0,
                             f"οι τρεις πρώτες πρέπει να είναι ακριβείς, πήρα {top}")


class SalonRegression(unittest.TestCase):
    """Το ακριβές σφάλμα που αναφέρθηκε."""

    def test_scandinavian_coffee_not_recommended_to_salon(self):
        rec = pg.recommend_templates({"trade": "Έχω κομμωτήριο στη Γλυφάδα"}, limit=12)
        self.assertNotIn("scandinavian-coffee", rec)

    def test_no_food_only_theme_for_salon(self):
        rec = pg.recommend_templates({"trade": "Έχω κομμωτήριο στη Γλυφάδα"}, limit=12)
        food_only = [k for k in rec
                     if COMPAT[k]["primary"] in ("cafe", "bakery", "food")
                     and not COMPAT[k]["generic"]]
        self.assertEqual(food_only, [], f"σχέδια εστίασης σε κομμωτήριο: {food_only}")


class Coverage(unittest.TestCase):
    def test_every_commercial_theme_is_reachable(self):
        reachable: set[str] = set()
        for vertical in pg._TEMPLATES_BY_VERTICAL:
            reachable |= set(pg.recommend_templates({"type": vertical}, limit=60))
        unreachable = sorted(set(pg.LAUNCH_REACT_TEMPLATES) - reachable)
        self.assertEqual(unreachable, [],
                         f"δεν προτείνονται πουθενά: {unreachable}")

    def test_selection_is_deterministic(self):
        a = pg.recommend_templates({"trade": CASES["beauty"]}, limit=12)
        b = pg.recommend_templates({"trade": CASES["beauty"]}, limit=12)
        self.assertEqual(a, b, "ίδιο intake πρέπει να δίνει πάντα την ίδια σειρά")


if __name__ == "__main__":
    unittest.main(verbosity=2)
