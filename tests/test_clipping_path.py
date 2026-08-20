"""Η διαδρομή αποκομμένου περιεχομένου: ανίχνευση, ιδιοκτησία, συναλλαγή.

Γιατί υπάρχει: το klassy-cafe έφτασε READY_FOR_REVIEW με κάρτα χάρτη 144x90 της
οποίας το περιεχόμενο ζητούσε 134px — ο σύνδεσμος «κατευθείαν οδηγίες» ήταν
κρυμμένος. Καμία πύλη δεν το είδε: όλες κοιτούσαν τι ΞΕΦΕΥΓΕΙ από το πλαίσιο,
καμία τι το πλαίσιο ΚΟΒΕΙ.

Το δεύτερο μάθημα είναι η ιδιοκτησία. Το `.mapBox` ανήκει στο κοινό `FindUs`,
που το `_validate` σωστά απαγορεύει να πειραχτεί — 60+ themes το μοιράζονται.
Συνταγή που ζητά αλλαγή εκεί είναι ανεκτέλεστη· το μοντέλο πρέπει να σταλεί
στον πλησιέστερο γονέα που του ανήκει.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.port_worker import clip_finding  # noqa: E402

SHARED = {"sel": "FindUs_mapBox", "owner": "FindUs", "themeOwner": "KlassyTable",
          "target": "KlassyTable_contactInner", "clientH": 88, "scrollH": 134,
          "hidden": 46, "axis": "ύψος", "overflow": "hidden/hidden",
          "cut": [{"text": "κατευθείαν οδηγίες ↗", "by": 43}]}


class Ownership(unittest.TestCase):
    def test_shared_component_routes_to_theme_parent(self) -> None:
        kind, text = clip_finding(SHARED, "desktop", 1440, "KlassyTable")
        self.assertEqual(kind, "SHARED_COMPONENT")
        self.assertIn("ΜΗΝ το πειράξεις", text)
        self.assertIn(".KlassyTable_contactInner", text)

    def test_shared_without_theme_parent_is_blocked(self) -> None:
        kind, _ = clip_finding({**SHARED, "target": ""}, "desktop", 1440, "KlassyTable")
        self.assertEqual(kind, "BLOCKED_SHARED_COMPONENT")

    def test_theme_owned_repairs_itself(self) -> None:
        own = {**SHARED, "sel": "KlassyTable_mapBox", "owner": "KlassyTable"}
        kind, text = clip_finding(own, "desktop", 1440, "KlassyTable")
        self.assertEqual(kind, "THEME_OWNED")
        self.assertIn(".KlassyTable_mapBox (δικό σου)", text)

    def test_evidence_is_deterministic_and_complete(self) -> None:
        _, text = clip_finding(SHARED, "desktop", 1440, "KlassyTable")
        for token in ("clientHeight: 88px", "περιεχόμενο: 134px", "κρυμμένα: 46px",
                      "overflow: hidden/hidden", "κατευθείαν οδηγίες"):
            self.assertIn(token, text)


class NeverFixByHiding(unittest.TestCase):
    """Μια «διόρθωση» που κρύβει το περιεχόμενο δεν είναι διόρθωση."""

    def test_forbids_hiding_solutions(self) -> None:
        for item in (SHARED, {**SHARED, "owner": "KlassyTable"}):
            _, text = clip_finding(item, "desktop", 1440, "KlassyTable")
            self.assertIn("ΑΠΑΓΟΡΕΥΕΤΑΙ", text)
            self.assertIn("overflow:hidden", text)
            self.assertIn("ορατό", text)


class Detection(unittest.TestCase):
    src = (ROOT / "sites" / "tests" / "shot-one.mjs").read_text(encoding="utf-8")

    def test_requires_real_cut_text(self) -> None:
        """Χωρίς πραγματικό κομμένο κείμενο δεν υπάρχει εύρημα — αλλιώς σκιές,
        transforms και ::after θα γέμιζαν τον βρόχο με φαντάσματα, όπως έκανε
        το CSS τρίγωνο του Medic Care επί τέσσερα τρεξίματα."""
        self.assertIn("if (!cut.length) continue", self.src)
        self.assertIn("if (!txt || c.children.length) continue", self.src)

    def test_ignores_intentional_truncation_and_hidden(self) -> None:
        self.assertIn("webkitLineClamp", self.src)
        self.assertIn("aria-hidden", self.src)


class Transaction(unittest.TestCase):
    def test_clipping_is_a_tracked_counter(self) -> None:
        """Διόρθωση desktop που φέρνει clipping στο mobile πρέπει να απορρίπτεται."""
        from src.repair_txn import COUNTERS, State, regressions  # noqa: PLC0415
        self.assertIn("clipped", COUNTERS)
        ok = {"renderable": True, "overflow": 0, "inner": 0, "broken": 0,
              "console": 0, "h1": 1}
        before = State(metrics={"desktop": {**ok, "clipped": 1},
                                "mobile": {**ok, "clipped": 0}}, guards={}, files={})
        after = State(metrics={"desktop": {**ok, "clipped": 0},
                               "mobile": {**ok, "clipped": 2}}, guards={}, files={})
        self.assertTrue(regressions(before, after), "το mobile χειροτέρεψε — πρέπει REJECT")


if __name__ == "__main__":
    unittest.main(verbosity=2)


class ProtrusionIsNotLoss(unittest.TestCase):
    """Προεξοχή ≠ απώλεια περιεχομένου.

    Μετρήθηκε στο clean-work: μπλε κάρτα τηλεφώνου («Χρειάζεστε βοήθεια;»)
    ακουμπισμένη σκόπιμα 20px έξω από τη γωνία της φωτογραφίας — ακριβώς όπως
    στο πρωτότυπο. Ο γονέας είχε `overflow: visible`, η σελίδα δεν κυλούσε
    οριζόντια, τίποτα δεν κρυβόταν· κι όμως ο έλεγχος την κατέγραφε ως
    υπερχείλιση και έκαιγε γύρους επιδιόρθωσης πάνω σε σχέδιο.

    Ίδιο μάθημα με το CSS τρίγωνο του Medic Care: ο έλεγχος πρέπει να μετρά
    ΑΠΡΟΣΙΤΟ περιεχόμενο, όχι γεωμετρία.
    """

    src = (ROOT / "sites" / "tests" / "shot-one.mjs").read_text(encoding="utf-8")

    def test_requires_a_clipping_ancestor_or_page_scroll(self) -> None:
        self.assertIn("for (let n = e; n; n = n.parentElement)", self.src)
        self.assertIn("document.documentElement.scrollWidth >", self.src)

    def test_real_clipping_still_reported(self) -> None:
        """Ο έλεγχος γεννήθηκε για το Frost, όπου ο γονέας ΟΝΤΩΣ έκοβε."""
        self.assertIn("'hidden' || c === 'clip'", self.src)
