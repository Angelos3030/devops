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
        complete_json.assert_called_once()


if __name__ == "__main__":
    unittest.main()
