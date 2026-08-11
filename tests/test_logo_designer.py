import unittest
from unittest.mock import patch

from src import logo_designer
from src.logo_designer import generate_logo_drafts


class LogoDesignerTests(unittest.TestCase):
    def test_returns_three_distinct_routes(self):
        drafts = generate_logo_drafts("Οδοντιατρείο Μαρία", "Οδοντιατρείο")
        self.assertEqual([d["id"] for d in drafts], ["monogram", "emblem", "wordmark"])
        self.assertEqual(len({d["svg"] for d in drafts}), 3)
        self.assertTrue(all('viewBox="0 0 640 240"' in d["svg"] for d in drafts))

    def test_escapes_business_data(self):
        drafts = generate_logo_drafts('<script>alert("x")</script>', "Καφέ & bar")
        joined = "".join(d["svg"] for d in drafts)
        self.assertNotIn("<script>", joined)
        self.assertIn("&lt;script&gt;", joined)

    def test_medical_and_beauty_use_different_palettes(self):
        medical = generate_logo_drafts("Α", "Οδοντιατρείο")[0]["svg"]
        beauty = generate_logo_drafts("Α", "Κέντρο αισθητικής")[0]["svg"]
        self.assertNotEqual(medical, beauty)

    def test_workspace_uses_database_business_type(self):
        with patch.object(logo_designer.db, "get_site_content", return_value={}):
            name, trade = logo_designer._workspace_identity(
                {"name": "Ιατρείο Μαρία", "business_type": "Οδοντιατρείο"},
                "client-1",
            )
        self.assertEqual(name, "Ιατρείο Μαρία")
        self.assertEqual(trade, "Οδοντιατρείο")

    def test_approval_replaces_only_older_logo_assets(self):
        assets = [
            {"id": "old-logo", "type": "logo"},
            {"id": "photo-1", "type": "photo"},
            {"id": "new-logo", "type": "logo"},
        ]
        with patch.object(logo_designer.auth, "require_client_access",
                          return_value={"name": "Νέα Nails", "type": "Νύχια"}), \
             patch.object(logo_designer.db, "get_site_content", return_value={}), \
             patch.object(logo_designer.db, "upload_to_storage",
                          return_value="https://assets.example/logo.svg") as upload, \
             patch.object(logo_designer.db, "save_client_asset",
                          return_value="new-logo"), \
             patch.object(logo_designer.db, "get_client_assets", return_value=assets), \
             patch.object(logo_designer.db, "delete_client_asset") as delete:
            result = logo_designer.approve_logo_draft(
                "client-1", "emblem", "Bearer owner")

        self.assertTrue(result["approved"])
        self.assertEqual(upload.call_args.args[3], "image/svg+xml")
        delete.assert_called_once_with("client-1", "old-logo")


if __name__ == "__main__":
    unittest.main()
