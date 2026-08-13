# -*- coding: utf-8 -*-
"""Regression για τα συστημικά ευρήματα του benchmark των 10 sites (13/8/2026).

Κάθε test εδώ αντιστοιχεί σε πραγματική αποτυχία που έφτασε σε παραγόμενο site,
όχι σε υποθετικό σενάριο. Τα κείμενα των claims είναι ΠΑΡΑΔΕΙΓΜΑΤΑ: ο έλεγχος
είναι κατηγορίας, όχι λίστας φράσεων.
"""
import unittest

from src import premium_generator as pg
from src import truth_guard


BASE = {
    "name": "Ηλεκτρολογείο Καρράς",
    "type": "Ηλεκτρολόγος",
    "city": "Καλαμαριά",
    "hours": "Δευτ.–Παρ. 08:00–18:00",
    "description": "Ηλεκτρολογικές εργασίες σε κατοικίες και επαγγελματικούς χώρους.",
    "services": [{"name": "Ηλεκτρικοί πίνακες", "description": "Αντικατάσταση παλιών πινάκων."}],
}


class TruthContract(unittest.TestCase):
    """Χωρίς απόδειξη στο intake, ο ισχυρισμός δεν επιτρέπεται να δημοσιευτεί."""

    def _scrub(self, field_value, intake=None, field="intro"):
        clean, removed = truth_guard.scrub_copy({field: field_value}, intake or BASE)
        return clean.get(field, ""), removed

    def test_experience_claim_needs_evidence(self):
        text, removed = self._scrub("Δουλεύουμε στην Καλαμαριά 15+ χρόνια στον χώρο.")
        self.assertNotIn("15", text)
        self.assertIn("tenure", {c.kind for c in removed})

    def test_decade_claim_needs_evidence(self):
        _, removed = self._scrub("Τρεις δεκαετίες δίπλα στη δική σας απόφαση.")
        self.assertIn("tenure", {c.kind for c in removed})

    def test_unquantified_tenure_is_also_a_claim(self):
        """Το μοντέλο έγραψε «Δουλεύουμε στο Περιστέρι χρόνια» μόλις του κόπηκαν οι
        αριθμοί. Η κατηγορία είναι η διάρκεια, όχι το ψηφίο."""
        for text in ("Δουλεύουμε στο Περιστέρι χρόνια και ξέρουμε τη γειτονιά.",
                     "Είμαστε εδώ χρόνια, δίπλα στους πελάτες μας.",
                     "Με πολλά χρόνια πείρα στον χώρο των εγκαταστάσεων."):
            with self.subTest(text=text[:30]):
                _, removed = self._scrub(text)
                self.assertIn("tenure", {c.kind for c in removed})

    def test_founding_year_needs_evidence(self):
        text, removed = self._scrub("Από το 1998 στη γειτονιά σας, με συνέπεια κάθε μέρα.")
        self.assertNotIn("1998", text)
        self.assertIn("founded", {c.kind for c in removed})

    def test_price_needs_evidence(self):
        text, removed = self._scrub("Όταν λέμε ότι θα κοστίσει 80 ευρώ, κοστίζει 80.")
        self.assertNotIn("80", text)
        self.assertIn("price", {c.kind for c in removed})

    def test_guarantee_needs_evidence(self):
        _, removed = self._scrub("Δίνουμε γραπτή εγγύηση σε κάθε εργασία που κάνουμε.")
        self.assertIn("guarantee", {c.kind for c in removed})

    def test_certification_award_rating_need_evidence(self):
        for text, kind in (
            ("Είμαστε πιστοποιημένοι εγκαταστάτες με πλήρη κατάρτιση.", "credential"),
            ("Βραβευμένη ομάδα για τη δουλειά της χρονιάς.", "award"),
            ("Μας βαθμολογούν 4,9/5 οι πελάτες μας.", "rating"),
            ("Πάνω από 500 πελάτες μας εμπιστεύονται κάθε χρόνο.", "counts"),
        ):
            with self.subTest(kind=kind):
                _, removed = self._scrub(text)
                self.assertIn(kind, {c.kind for c in removed})

    def test_availability_claim_needs_evidence(self):
        _, removed = self._scrub("Είμαστε διαθέσιμοι 24/7 για κάθε επείγον περιστατικό.")
        self.assertIn("availability", {c.kind for c in removed})

    def test_supported_claim_survives(self):
        """Ό,τι ΕΧΕΙ δηλώσει ο πελάτης πρέπει να επιτρέπεται — αλλιώς φτιάξαμε λογοκρισία."""
        intake = {**BASE, "description": BASE["description"] + " Δίνουμε εγγύηση 2 χρόνια στα υλικά."}
        text, removed = self._scrub("Δίνουμε εγγύηση στα υλικά που τοποθετούμε.", intake)
        self.assertIn("εγγύηση", text)
        self.assertEqual(removed, [])

    def test_fails_closed_on_unsalvageable_field(self):
        """Tagline που ολόκληρο είναι ισχυρισμός ΠΕΦΤΕΙ — δεν μπαλώνεται."""
        clean, _ = truth_guard.scrub_copy({"tagline": "30 χρόνια εμπειρίας στη γειτονιά"}, BASE)
        self.assertNotIn("tagline", clean)

    def test_safe_copy_untouched(self):
        clean, removed = truth_guard.scrub_copy(
            {"intro": "Ηλεκτρολογικές εργασίες για κατοικίες και επαγγελματικούς χώρους."}, BASE)
        self.assertEqual(removed, [])
        self.assertIn("Ηλεκτρολογικές", clean["intro"])


class VerticalClassification(unittest.TestCase):
    """Μία γενική λέξη δεν επιτρέπεται να νικήσει τη λέξη που ορίζει το επάγγελμα."""

    CASES = (
        ("trade", {"type": "Υδραυλικός", "description": "Μικρό συνεργείο υδραυλικών για βλάβες."}),
        ("garage", {"type": "Συνεργείο αυτοκινήτων", "description": "Service και επισκευές οχημάτων."}),
        ("trade", {"type": "Ηλεκτρολόγος", "description": "Ηλεκτρολογικό συνεργείο, πίνακες και βλάβες."}),
        ("pet", {"name": "Pet Spa Λούνα", "type": "Pet grooming",
                 "description": "Μπάνιο και κούρεμα για σκύλους και γάτες."}),
        ("pet", {"name": "Happy Tails", "type": "Dog grooming", "description": "Grooming για σκύλους."}),
        ("massage", {"name": "Aura Day Spa", "type": "Κέντρο μασάζ", "description": "Μασάζ και ευεξία."}),
        ("massage", {"name": "Massage Spa Athens", "type": "Μασάζ", "description": "Θεραπευτικό μασάζ."}),
        ("beauty", {"name": "Κομμωτήριο Ελένη", "type": "Κομμωτήριο", "description": "Κούρεμα και βαφή."}),
        ("dentist", {"type": "Οδοντιατρείο", "description": "Γενική οδοντιατρική."}),
        ("bakery", {"type": "Φούρνος", "description": "Ψωμί με προζύμι και πίτες."}),
    )

    def test_cases(self):
        for expected, intake in self.CASES:
            with self.subTest(intake=intake.get("type")):
                self.assertEqual(pg._vertical(intake), expected)

    def test_business_name_alone_cannot_decide(self):
        """Η επωνυμία είναι αδύναμο σήμα: «Spa» σε όνομα δεν κάνει μασάζ έναν φούρνο."""
        self.assertEqual(pg._vertical(
            {"name": "Bread Spa", "type": "Φούρνος", "description": "Ψωμί και πίτες."}), "bakery")

    def test_deterministic(self):
        intake = {"type": "Υδραυλικός", "description": "Μικρό συνεργείο υδραυλικών."}
        self.assertEqual({pg._vertical(intake) for _ in range(10)}, {"trade"})


class ThemeSelection(unittest.TestCase):
    def test_solo_practitioner_can_get_signature(self):
        intake = {"name": "Γεωργία Στεφανίδου", "type": "Λογιστικό γραφείο",
                  "description": "Λογιστικό γραφείο ενός ατόμου. Δουλεύω με ελεύθερους επαγγελματίες."}
        self.assertEqual(pg.recommend_templates(intake)[0], "signature")

    def test_organisation_does_not_get_signature_first(self):
        intake = {"name": "Αντωνίου & Σία ΑΕ", "type": "Δικηγορικό γραφείο",
                  "description": "Το γραφείο στελεχώνεται από έμπειρους νομικούς."}
        self.assertNotEqual(pg.recommend_templates(intake)[0], "signature")

    def test_trade_business_never_gets_signature(self):
        intake = {"name": "Υδραυλικά Βεργίνα", "type": "Υδραυλικός",
                  "description": "Μικρό συνεργείο υδραυλικών."}
        self.assertEqual(pg.recommend_templates(intake)[0], "callout")

    def test_selection_is_deterministic(self):
        intake = {"name": "Νίκη Αρβανίτη", "type": "Διαιτολόγος",
                  "description": "Ατομικές συνεδρίες διατροφής."}
        first = pg.recommend_templates(intake)
        for _ in range(5):
            self.assertEqual(pg.recommend_templates(intake), first)


class MediaIdentity(unittest.TestCase):
    """Stock εικόνα δεν επιτρέπεται να παρουσιαστεί ως δική του."""

    def test_no_client_photo_is_marked_illustrative(self):
        ctx = pg.normalize({"name": "Οδοντιατρείο Παπαδάκη", "type": "Οδοντιατρείο", "city": "Ηράκλειο"})
        self.assertFalse(ctx["HERO_IS_REAL"])
        self.assertTrue(ctx["MEDIA_ILLUSTRATIVE"])

    def test_client_photo_is_marked_real(self):
        ctx = pg.normalize({"name": "Κομμωτήριο Ελένη", "type": "Κομμωτήριο", "city": "Χαλάνδρι",
                            "gallery": [{"image": "https://example.com/a.jpg", "title": "Στον χώρο μας"}]})
        self.assertTrue(ctx["HERO_IS_REAL"])
        self.assertFalse(ctx["MEDIA_ILLUSTRATIVE"])


if __name__ == "__main__":
    unittest.main()
