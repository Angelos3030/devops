"""
Αρχεία που φαίνονται «απλώς περιεχόμενο» αλλά διαβάζονται σε κάθε δημιουργία site.

Γιατί υπάρχει: το `skills/vitrina-design-system/templates/` μοιάζει με φάκελο
τεκμηρίωσης ενός skill. Είναι runtime dependency. Και δεν φαίνεται με αναζήτηση
κειμένου — η διαδρομή χτίζεται με `Path` segments, οπότε
`grep "vitrina-design-system/templates"` δίνει **μηδέν αποτελέσματα**.

Χωρίς αυτό το test, η επόμενη αναδιοργάνωση skills σβήνει τον φάκελο, τα tests
περνούν, και η γεννήτρια σπάει για κάθε ΝΕΟ πελάτη — όχι για τους υπάρχοντες,
άρα κανείς δεν το βλέπει αμέσως.
"""
import unittest
from pathlib import Path

from src import premium_generator as pg

ROOT = Path(__file__).parents[1]


class LegacyLayoutAssetsTests(unittest.TestCase):
    def test_template_dir_is_where_the_engine_looks(self):
        expected = ROOT / "skills" / "vitrina-design-system" / "templates"
        self.assertEqual(pg.TEMPLATE_DIR.resolve(), expected.resolve())
        self.assertTrue(pg.TEMPLATE_DIR.is_dir(),
                        f"runtime-critical φάκελος λείπει: {pg.TEMPLATE_DIR}")

    def test_every_declared_layout_has_its_file(self):
        """Το LAYOUTS τροφοδοτεί το /site-data και το generate_variants.
        Layout χωρίς αρχείο = 500 στη μέση της δημιουργίας."""
        missing = [name for name in pg.LAYOUTS
                   if not (pg.TEMPLATE_DIR / f"{name}.tpl.html").is_file()]
        self.assertEqual(missing, [], f"λείπουν .tpl.html: {missing}")

    def test_the_generator_actually_renders_from_them(self):
        """Απόδειξη χρήσης, όχι μόνο ύπαρξης: αν ο φάκελος μετακομίσει, αυτό σκάει."""
        html = pg.generate_variants({"name": "Δοκιμή", "type": "Υδραυλικός",
                                     "city": "Αθήνα"})
        self.assertTrue(html, "το generate_variants δεν επέστρεψε τίποτα")
        for layout, markup in html.items():
            self.assertIn(layout, pg.LAYOUTS)
            self.assertGreater(len(markup), 500, f"{layout}: ύποπτα μικρό HTML")
            self.assertNotIn("{{", markup, f"{layout}: έμειναν placeholders")


if __name__ == "__main__":
    unittest.main()
