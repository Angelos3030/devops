import unittest
from unittest.mock import patch

from src import site_copy


class SiteCopyGroundingTests(unittest.TestCase):
    @patch.object(site_copy.ai, "complete_json")
    @patch.object(site_copy.ai, "available", return_value=True)
    def test_sparse_hotel_prompt_uses_reviewed_defaults(self, _available, complete_json):
        intake = {
            "name": "Ξενοδοχείο",
            "type": "Ξενοδοχείο",
            "description": "Έχω ξενοδοχείο",
        }

        self.assertEqual(site_copy.write_copy(intake), {})
        complete_json.assert_not_called()

    @patch.object(site_copy.ai, "complete_json", return_value={
        "tagline": "Διαμονή με θέα στη θάλασσα.",
    })
    @patch.object(site_copy.ai, "available", return_value=True)
    def test_detailed_prompt_can_use_ai_copy(self, _available, complete_json):
        intake = {
            "name": "Akti",
            "type": "Ξενοδοχείο",
            "description": "Μικρό οικογενειακό ξενοδοχείο με πρωινό και θέα στη θάλασσα",
        }

        self.assertEqual(
            site_copy.write_copy(intake)["tagline"],
            "Διαμονή με θέα στη θάλασσα.",
        )
        self.assertEqual(complete_json.call_count, 2)

    @patch.object(site_copy.ai, "complete_json", return_value={
        "tagline": "Κομμώματα και περιποίηση για σκύλους και γάτες",
        "intro": "Το κομμωτήριο του σκυλάκι σας κάνει κομμώματι με ήρεμο τρόπο.",
        "services": [{
            "name": "Ξεματιάσιμο",
            "description": "Αφαίρεση νεκρού τριχώματος.",
        }],
    })
    @patch.object(site_copy.ai, "available", return_value=True)
    def test_known_malformed_professional_terms_never_reach_the_site(
        self, _available, _complete_json
    ):
        result = site_copy.write_copy({
            "name": "Pet Spa Λούνα",
            "type": "Pet grooming",
            "description": "Περιποίηση σκύλων και γατών με ραντεβού στη Γλυφάδα",
        })

        self.assertEqual(
            result["tagline"],
            "κούρεμα και περιποίηση για σκύλους και γάτες",
        )
        self.assertIn("κούρεμα", result["intro"])
        self.assertIn("του σκύλου σας", result["intro"])
        self.assertEqual(
            result["services"][0]["name"],
            "αφαίρεση νεκρού τριχώματος",
        )


if __name__ == "__main__":
    unittest.main()
