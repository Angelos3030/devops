"""Το κοινό FindUs πρέπει να αμύνεται μόνο του σε στενό δοχείο.

Γιατί υπάρχει: το FindUs ήταν grid `minmax(280px, 1fr) 1.25fr` που στοιβαζόταν
μόνο μέσω media query — δηλαδή όταν στένευε το VIEWPORT. Το πραγματικό πρόβλημα
ήταν το ΔΟΧΕΙΟ. Μετρημένα, σε πλάτος οθόνης 1440:

    theme            FindUs   στήλες           χάρτης    περιεχόμενο  κομμένα
    gymso-fitness    531px    280px + 107px    107x67    142px        77px
    villa-agency     555px    280px + 131px    131x82    139px        59px
    klassy-cafe      568px    280px + 144px    144x90    134px        46px

Τρία themes, ένα σφάλμα. Κάθε theme που φώλιαζε το component σε στενή στήλη
έκρυβε τον σύνδεσμο οδηγιών — και το `_validate` σωστά απαγόρευε στο μοντέλο να
διορθώσει κοινό component, οπότε η διόρθωση ανά theme ήταν και ανεκτέλεστη.

Ο έλεγχος συμπεριφοράς σε πραγματικό browser ζει στο
`sites/tests/findus_layout.mjs`. Εδώ φυλάσσεται μόνο το συμβόλαιο του CSS, ώστε
η προστασία να μη φύγει σιωπηλά σε κάποιο μελλοντικό restyle.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "sites" / "lib" / "templates" / "FindUs.module.css").read_text(encoding="utf-8")
WRAP = CSS[CSS.index(".wrap {"):CSS.index("}", CSS.index(".wrap {"))]
MAPBOX = CSS[CSS.index(".mapBox {"):CSS.index("}", CSS.index(".mapBox {"))]


class ContainerDefence(unittest.TestCase):
    def test_wrap_wraps_instead_of_forcing_two_columns(self) -> None:
        self.assertIn("flex-wrap: wrap", WRAP)
        self.assertNotIn("grid-template-columns", WRAP,
                         "το grid δεν στοιβάζεται όταν στενεύει το δοχείο, μόνο το viewport")

    def test_children_can_shrink_and_reflow(self) -> None:
        self.assertRegex(CSS, r"\.info \{[^}]*flex: 1 1 \d+px")
        self.assertRegex(CSS, r"\.mapBox \{[^}]*flex: [\d.]+ 1 \d+px")

    def test_map_has_a_floor_height(self) -> None:
        """Το aspect-ratio βγάζει ύψος ΑΠΟ το πλάτος: στενή στήλη = κοντό κουτί.
        Το περιεχόμενο του mapHolder μετρήθηκε στα ~142px."""
        m = re.search(r"min-height:\s*(\d+)px", MAPBOX)
        self.assertIsNotNone(m, "ο χάρτης χωρίς ελάχιστο ύψος ξανακρύβει το περιεχόμενό του")
        self.assertGreaterEqual(int(m.group(1)), 150)


class NoForbiddenWorkarounds(unittest.TestCase):
    """Η αποκοπή δεν λύνεται κρύβοντας — ο κανόνας που δόθηκε και στο μοντέλο."""

    def test_no_content_removal_or_shrinking(self) -> None:
        for banned in ("display: none", "visibility: hidden"):
            self.assertNotIn(banned, MAPBOX)
        for size in re.findall(r"font-size:\s*([\d.]+)rem", CSS):
            self.assertGreaterEqual(float(size), 0.7, "γραμματοσειρά συρρικνωμένη για να χωρέσει")

    def test_map_keeps_rounded_clipping_only(self) -> None:
        """Το overflow:hidden στο .mapBox προϋπήρχε για τις στρογγυλές γωνίες του
        iframe — δεν προστέθηκε ως «λύση» και συνοδεύεται από min-height."""
        self.assertIn("border-radius", MAPBOX)
        self.assertIn("min-height", MAPBOX)


class SharedComponentStaysShared(unittest.TestCase):
    def test_no_theme_specific_selectors_leaked_in(self) -> None:
        """Ένα κοινό component που ξέρει ονόματα themes δεν είναι πια κοινό."""
        for theme in ("Klassy", "Gymso", "Villa", "Medic", "Frost"):
            self.assertNotIn(theme, CSS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
