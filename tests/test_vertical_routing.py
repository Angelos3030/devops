import unittest
from unittest.mock import patch

from src import premium_generator as pg
from src import quick_start


class VerticalRoutingTests(unittest.TestCase):
    def test_real_world_descriptions_cover_all_vertical_families(self):
        cases = [
            ("Παραδοσιακή ταβέρνα στην Καλαμάτα", "food", "warmth"),
            ("Καφετέρια στη Μάνη με brunch", "cafe", "counter-menu"),
            ("Οικογενειακός φούρνος με ψωμί ημέρας", "bakery", "bakery-editorial"),
            ("Οδοντιατρείο με αισθητική οδοντιατρική", "dentist", "clinic-triage"),
            ("Καρδιολόγος με ιατρείο στο Χαλάνδρι", "doctor", "clinic-triage"),
            ("Φαρμακείο Μαρία στον Γέρακα", "pharmacy", "quiet"),
            ("Κέντρο αισθητικής με laser αποτρίχωση", "aesthetics", "beauty-atelier"),
            ("Κέντρο μασάζ και wellness", "massage", "living"),
            ("Νυχάδικο για μανικιούρ και πεντικιούρ", "beauty", "beauty-atelier"),
            ("Ανθοπωλείο με λουλούδια και δώρα", "retail", "bento"),
            ("Δικηγορικό γραφείο οικογενειακού δικαίου", "professional", "marble"),
            ("Ξυλουργείο για κουζίνες και ντουλάπες", "wood", "forge"),
            ("Υδραυλικός 24 ώρες στην Αθήνα", "trade", "callout"),
            ("Ηλεκτρολόγος στον Πειραιά", "trade", "callout"),
            ("Ενοικιαζόμενα δωμάτια στη Νάξο", "rooms", "aegean"),
            ("Γυμναστήριο και personal training", "gym", "volt"),
            ("Συνεργείο αυτοκινήτων και βουλκανιζατέρ", "garage", "motor"),
            ("Παραγωγός ελαιόλαδου στη Μεσσηνία", "farm", "terra"),
        ]
        for description, expected_vertical, expected_first in cases:
            with self.subTest(description=description):
                intake = {"type": "Άλλο", "description": description}
                self.assertEqual(pg._vertical(intake), expected_vertical)
                self.assertEqual(pg.recommend_templates(intake)[0], expected_first)

    def test_pharmacy_is_not_treated_as_fashion_retail(self):
        intake = {"type": "Άλλο", "description": "Φαρμακείο Μαρία στον Γέρακα"}
        templates = pg.recommend_templates(intake)
        self.assertEqual(templates[0], "quiet")
        self.assertNotIn("runway", templates)

    def test_carpenter_starts_with_craft_not_fashion_gallery(self):
        intake = {
            "type": "Άλλο",
            "description": "Ξυλουργικό εργαστήριο με κουζίνες και ντουλάπες",
        }
        templates = pg.recommend_templates(intake)
        self.assertEqual(templates[0], "forge")
        self.assertNotIn("runway", templates)

    def parse_without_ai(self, text):
        with patch.object(quick_start.ai, "available", return_value=False):
            return quick_start.parse(text)

    def test_lowercase_cafe_in_mani(self):
        intake = self.parse_without_ai("έχω καφετέρια στην μάνη")
        self.assertEqual(intake["type"], "Καφετέρια")
        self.assertEqual(intake["city"], "μάνη")
        self.assertEqual(pg._vertical(intake), "cafe")

    def test_cafe_never_receives_bakery_first_party_themes(self):
        templates = pg.recommend_templates({
            "type": "Καφετέρια", "city": "Μάνη",
            "description": "καφές, ροφήματα και snacks",
        })
        bakery_only = {"bakery-editorial", "morning-journal",
                       "microbakery-lab", "heritage-bakery"}
        self.assertFalse(bakery_only.intersection(templates))
        self.assertEqual(templates[0], "counter-menu")

    def test_bakery_keeps_bakery_themes_and_copy(self):
        intake = self.parse_without_ai("έχω φούρνο στη μάνη")
        self.assertEqual(pg._vertical(intake), "bakery")
        self.assertEqual(pg.recommend_templates(intake)[0], "bakery-editorial")
        data = pg.normalize(intake)
        self.assertTrue(any("ψωμί" in item["title"].lower()
                            for item in data["services"]))

    def test_cafe_default_copy_has_no_bakery_claim(self):
        data = pg.normalize({"type": "Καφετέρια", "city": "Μάνη"})
        combined = " ".join(
            [item["title"] + " " + item["desc"] for item in data["services"]]
            + [item["p"] for item in data["story"]]
        ).lower()
        self.assertNotIn("φούρν", combined)
        self.assertNotIn("ψωμί", combined)

    def test_dentist_with_aesthetic_service_keeps_medical_theme(self):
        intake = self.parse_without_ai(
            "έχω οδοντιατρείο στην Αθήνα με αισθητική οδοντιατρική"
        )
        self.assertEqual(intake["type"], "Οδοντιατρείο")
        self.assertEqual(pg._vertical(intake), "dentist")
        self.assertEqual(pg.recommend_templates(intake)[0], "clinic-triage")

    def test_nail_studio_does_not_route_to_dentist(self):
        intake = self.parse_without_ai("έχω νυχάδικο στον Γέρακα")
        self.assertEqual(intake["type"], "Νυχάδικο")
        self.assertEqual(pg._vertical(intake), "beauty")
        self.assertEqual(pg.recommend_templates(intake)[0], "beauty-atelier")

    def test_describe_structure_match_twelve_for_salon(self):
        text = ("Έχω κομμωτήριο στο Περιστέρι, γυναίκες και άντρες, θέλω online "
                "ραντεβού, τιμοκατάλογο και κάτι μοντέρνο αλλά όχι πολύ φανταχτερό.")
        intake = self.parse_without_ai(text)
        self.assertEqual(intake["type"], "Κομμωτήριο")
        self.assertEqual(intake["city"], "Περιστέρι")
        self.assertTrue(intake["booking"])
        self.assertTrue(intake["pricing"])
        self.assertIn("online-booking", intake["features"])
        templates = pg.recommend_templates(intake)
        self.assertEqual(len(templates), 12)
        self.assertEqual(templates[0], "price-first")
        self.assertIn("beauty-atelier", templates[:4])
        self.assertEqual(len(templates), len(set(templates)))

    def test_unapproved_capability_does_not_replace_trade_anchor(self):
        intake = self.parse_without_ai(
            "Είμαι υδραυλικός στην Αθήνα και θέλω έλεγχο περιοχής και διαθεσιμότητας"
        )
        self.assertEqual(pg.recommend_templates(intake)[0], "callout")

    def test_no_photo_request_stays_with_approved_professional_themes(self):
        intake = self.parse_without_ai(
            "Έχω δικηγορικό γραφείο στο Χαλάνδρι, δεν έχω φωτογραφίες και θέλω minimal site"
        )
        templates = pg.recommend_templates(intake)
        self.assertIn("quiet", templates[:4])
        self.assertNotIn("type-specimen", templates)

    def test_sparse_hotel_prompt_gets_hospitality_copy_without_fake_facts(self):
        data = pg.normalize({"name": "Ξενοδοχείο", "type": "Ξενοδοχείο"})
        combined = " ".join(
            [data["TAGLINE"], data["STORY_TITLE"], data["CTA_TITLE"]]
            + [item["title"] + " " + item["desc"] for item in data["services"]]
            + [item["p"] for item in data["story"]]
        ).lower()
        self.assertEqual(pg._vertical({"type": "Ξενοδοχείο"}), "rooms")
        self.assertIn("διαμον", combined)
        self.assertIn("φιλοξεν", combined)
        self.assertNotIn("ένας άνθρωπος που ακούει", combined)
        self.assertNotIn("υπηρεσίες καθαρισμού", combined)
        self.assertEqual(data["PHONE"], "")
        self.assertEqual(data["PHONE_INTL"], "")
        self.assertEqual(data["CITY"], "")
        self.assertEqual(data["HOURS"], "")
        self.assertEqual(data["reviews"], [])

    def test_placeholder_contact_values_are_not_rendered_as_business_facts(self):
        data = pg.normalize({
            "name": "Ξενοδοχείο", "type": "Ξενοδοχείο",
            "city": "—", "phone": "—", "hours": "—",
        })
        self.assertEqual(data["CITY"], "")
        self.assertEqual(data["PHONE"], "")
        self.assertEqual(data["HOURS"], "")


if __name__ == "__main__":
    unittest.main()
