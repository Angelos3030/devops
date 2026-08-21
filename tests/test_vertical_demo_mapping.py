"""Το QA σενάριο πρέπει ΠΑΝΤΑ να ταιριάζει με το vertical που δοκιμάζεται.

Γιατί υπάρχει: ο port worker απέδιδε το `medic-care` με τα προεπιλεγμένα demo
δεδομένα — δηλαδή έκρινε ιατρικό theme πάνω σε **φωτογραφίες κουζίνας**
ξυλουργού, με «Η Κλινική μας» πάνω από ντουλάπες. Κάθε μέτρηση εικόνων, ύψους
και υπερχείλισης γινόταν σε λάθος περιεχόμενο.

Το επικίνδυνο δεν είναι το λάθος σενάριο· είναι ότι το QA μπορεί να βγει
**πράσινο** πάνω σε λάθος σενάριο. Γι' αυτό: χωρίς ρητή αντιστοίχιση, τίποτα
δεν αποδίδεται.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.port_worker import VERTICAL_DEMO, DemoMappingMissing, demo_for  # noqa: E402


class VerticalDemoMapping(unittest.TestCase):
    def test_required_mappings(self) -> None:
        # ΠΡΟΣΟΧΗ: τα `content` και `music` ΔΕΝ είναι πλέον έγκυρα. Είχαν
        # αντιστοιχιστεί με κριτήριο τον πλούτο των δεδομένων και παρήγαγαν
        # εικονίδια μουσικής πάνω από «Κούρεμα & styling». Βλ.
        # tests/test_demo_semantics.py.
        for vertical, expected in (("medical", "physician"), ("food", "taverna"),
                                   ("beauty", "salon"), ("fitness", "gym"),
                                   ("property", "realestate"), ("trades", "plumber")):
            with self.subTest(vertical=vertical):
                self.assertEqual(demo_for({"verticals": [vertical]}), expected)

    def test_first_mapped_vertical_wins(self) -> None:
        # Το frost-bakery δηλώνει ["food", "retail"] — παίρνει το πρώτο.
        self.assertEqual(demo_for({"verticals": ["food", "retail"]}), "taverna")

    def test_unknown_vertical_fails_closed(self) -> None:
        with self.assertRaises(DemoMappingMissing) as cm:
            demo_for({"verticals": ["underwater-basket-weaving"]})
        self.assertIn("DEMO_MAPPING_MISSING", str(cm.exception))

    def test_empty_verticals_fails_closed(self) -> None:
        with self.assertRaises(DemoMappingMissing):
            demo_for({"verticals": []})
        with self.assertRaises(DemoMappingMissing):
            demo_for({})

    def test_never_falls_back_to_generic(self) -> None:
        """Καμία διαδρομή δεν επιστρέφει carpenter/generic για άγνωστο vertical."""
        # ΠΡΟΣΟΧΗ: τα `content` και `music` ΕΧΟΥΝ πλέον αντιστοίχιση
        # (content->farm, music->salon). Άγνωστο σημαίνει πραγματικά άγνωστο.
        for bogus in (["unknown"], ["blockchain"], ["", None], ["Content"],
                      ["music"], ["content"]):
            with self.subTest(v=bogus), self.assertRaises(DemoMappingMissing):
                demo_for({"verticals": bogus})

    def test_mapped_demos_exist_in_demo_data(self) -> None:
        """Κάθε τιμή του VERTICAL_DEMO πρέπει να υπάρχει πραγματικά."""
        src = (Path(__file__).resolve().parents[1] / "sites" / "lib" / "demoData.js"
               ).read_text(encoding="utf-8")
        for vertical, biz in VERTICAL_DEMO.items():
            with self.subTest(vertical=vertical):
                self.assertIn(f"\n  {biz}: {{", src,
                              f"το demo '{biz}' δεν υπάρχει στο demoData.js")


if __name__ == "__main__":
    unittest.main(verbosity=2)
