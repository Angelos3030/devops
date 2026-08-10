import unittest
from unittest.mock import patch

from src import premium_generator as pg
from src import quick_start


class VerticalRoutingTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
