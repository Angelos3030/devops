"""
Το intake να μη γεμίζει το site με ό,τι να 'ναι.

Αφορμή: prompt «ξενοδοχείο». Το site έβγαινε με επωνυμία «Ξενοδοχείο», παύλες
αντί για στοιχεία επικοινωνίας, και τέσσερις αριθμημένες υπηρεσίες χωρίς
περιγραφή — μία από αυτές («Πρόσφυση») δεν σήμαινε τίποτα για ξενοδοχείο.
Τρεις ανεξάρτητες αιτίες, μία εικόνα: γενικό site που θα ταίριαζε σε ξυλουργό.
"""
import unittest

from src import premium_generator as pg
from src import quick_start as qs


class PlaceholderLeakTests(unittest.TestCase):
    """Η «—» ήταν UI placeholder που γραφόταν στη βάση ως δεδομένο."""

    def test_normalize_strips_dashes_from_legacy_rows(self):
        ctx = pg.normalize({"name": "—", "type": "—", "city": "—", "phone": "—",
                            "address": "—", "email": "—", "areas": ["—"]})
        self.assertEqual(ctx["CITY"], "")
        self.assertEqual(ctx["PHONE"], "")
        self.assertEqual(ctx["ADDRESS"], "")
        self.assertEqual(ctx["EMAIL"], "")
        self.assertEqual(ctx["AREAS"], "")
        self.assertNotIn("—", ctx["NAME"])
        self.assertNotIn("—", ctx["KICKER"])

    def test_kicker_has_no_dangling_separator_without_city(self):
        ctx = pg.normalize({"name": "Θαλασσιά", "type": "Ξενοδοχείο"})
        self.assertEqual(ctx["KICKER"], "Ξενοδοχείο")

    def test_create_client_never_persists_a_dash(self):
        """Η στήλη είναι NOT NULL με default '' — η παύλα δεν χρειάστηκε ποτέ."""
        import inspect
        from src import db
        source = inspect.getsource(db.create_client)
        self.assertNotIn('"—"', source)
        self.assertIn('intake.get("city") or ""', source)


class GroundingTests(unittest.TestCase):
    """Σκέτη κατηγορία = κανένα γεγονός. Το μοντέλο τότε γεμίζει το κενό."""

    def test_bare_category_is_not_grounded(self):
        for text in ("ξενοδοχείο", "Ξενοδοχείο", "κομμωτήριο", "υδραυλικός"):
            self.assertFalse(qs._is_grounded(text, None), text)

    def test_real_description_is_grounded(self):
        self.assertTrue(
            qs._is_grounded("έχω ξενοδοχείο στην Πάρο με 12 δωμάτια και πρωινό", "Ξενοδοχείο"))

    def test_category_is_not_a_business_name(self):
        self.assertTrue(qs._is_category("Ξενοδοχείο", "Ξενοδοχείο"))
        self.assertTrue(qs._is_category("κομμωτηριο", None))
        self.assertFalse(qs._is_category("Θαλασσιά", "Ξενοδοχείο"))


class CityExtractionTests(unittest.TestCase):
    def test_trailing_words_are_not_part_of_the_city(self):
        """«στην Πάρο με 12 δωμάτια» έδινε πόλη «Πάρο με» — και ο χάρτης έψαχνε αυτό."""
        self.assertEqual(qs._guess_city("έχω ξενοδοχείο στην Πάρο με 12 δωμάτια"), "Πάρο")

    def test_two_word_places_survive(self):
        self.assertEqual(qs._guess_city("κομμωτήριο στη Νέα Σμύρνη"), "Νέα Σμύρνη")

    def test_same_place_allows_case_correction_only(self):
        self.assertTrue(qs._same_place("Πάρος", "Πάρο"))
        self.assertTrue(qs._same_place("Γέρακας", "Γέρακα"))
        self.assertFalse(qs._same_place("Πάτρα", "Πάρος"))


class ServiceQualityTests(unittest.TestCase):
    def test_reviewed_services_win_when_the_client_said_nothing(self):
        ctx = pg.normalize({"name": "Θαλασσιά", "type": "Ξενοδοχείο"})
        self.assertTrue(all(s["desc"] for s in ctx["services"]),
                        "καμία υπηρεσία δεν επιτρέπεται να μείνει χωρίς περιγραφή")

    def test_empty_description_is_filled_from_our_reviewed_copy(self):
        """Ο τίτλος ταιριάζει με δική μας ελεγμένη υπηρεσία — δεν επινοούμε κείμενο."""
        ctx = pg.normalize({"name": "Θαλασσιά", "type": "Ξενοδοχείο",
                            "services": [{"title": "Κρατήσεις", "desc": ""}]})
        self.assertTrue(ctx["services"][0]["desc"])

    def test_unknown_title_is_not_given_someone_elses_description(self):
        ctx = pg.normalize({"name": "Θαλασσιά", "type": "Ξενοδοχείο",
                            "services": [{"title": "Πρόσφυση", "desc": ""}]})
        self.assertEqual(ctx["services"][0]["desc"], "")

    def test_parser_accepts_both_shapes(self):
        cleaned = qs._clean_services([
            {"name": "Διαμονή", "desc": "Δωμάτια για επισκέπτες."},
            "Πρωινό",
            {"title": "", "desc": "χωρίς τίτλο — αγνοείται"},
        ])
        self.assertEqual(cleaned[0], {"title": "Διαμονή", "desc": "Δωμάτια για επισκέπτες."})
        self.assertEqual(cleaned[1], {"title": "Πρωινό", "desc": ""})
        self.assertEqual(len(cleaned), 2)


class GeocodingTests(unittest.TestCase):
    def test_no_location_means_no_pin(self):
        """Κενή διεύθυνση έδινε το κέντρο της Ελλάδας — καρφίτσα σε λάθος σημείο."""
        from src import meta_oauth
        calls = []
        original = meta_oauth.db.get_site_content
        meta_oauth.db.get_site_content = lambda cid: calls.append(cid) or {}
        try:
            meta_oauth._ensure_geo("test", "", "")
            meta_oauth._ensure_geo("test", "  ", None)
        finally:
            meta_oauth.db.get_site_content = original
        self.assertEqual(calls, [], "δεν πρέπει καν να ξεκινήσει η γεωκωδικοποίηση")


class VerticalTests(unittest.TestCase):
    def test_hotel_never_lands_on_the_carpenter(self):
        """Το «κρυφό fallback» που είχε ήδη χτυπήσει το φαρμακείο."""
        for text in ("Ξενοδοχείο", "ξενοδοχειο", "ενοικιαζόμενα δωμάτια", "κατάλυμα στην Πάρο"):
            intake = {"name": text, "type": text}
            self.assertEqual(pg._profession(intake), "rooms", text)
            self.assertNotIn("forge", pg.recommend_templates(intake)[:3], text)


if __name__ == "__main__":
    unittest.main()
