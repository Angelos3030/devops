from __future__ import annotations

import unittest
from unittest.mock import patch

from src import social_engine


class SocialEngineTests(unittest.TestCase):
    def test_create_draft_is_approval_first(self):
        with patch("src.social_engine.db.save_post", return_value="post-1") as save:
            post_id = social_engine.create_draft("client-1", "  Καλημέρα!  ", targets=["facebook"])
        self.assertEqual(post_id, "post-1")
        self.assertEqual(save.call_args.args[:2], ("client-1", "Καλημέρα!"))
        self.assertEqual(save.call_args.kwargs["status"], "pending_approval")
        self.assertTrue(save.call_args.kwargs["approval_required"])

    def test_invalid_target_is_rejected(self):
        with self.assertRaises(ValueError):
            social_engine.clean_targets(["facebook", "tiktok"])

    @patch("src.social_engine.db.finish_post")
    @patch("src.social_engine.publisher.publish")
    def test_missing_approval_is_blocked(self, publish, finish):
        result = social_engine.process_post({
            "id": "post-1", "client_id": "client-1", "caption": "Text",
            "targets": ["facebook"], "approval_required": True,
        })
        self.assertFalse(result["ok"])
        self.assertEqual(result["blocked"], "approval_required")
        publish.assert_not_called()
        self.assertEqual(finish.call_args.kwargs["status"], "pending_approval")

    @patch("src.social_engine.db.save_publish_log")
    @patch("src.social_engine.db.finish_post")
    @patch("src.social_engine.publisher.publish")
    def test_partial_success_retries_only_failed_network(self, publish, finish, _log):
        publish.return_value = {
            "results": {
                "facebook": {"ok": True, "post_id": "fb-123"},
                "instagram": {"ok": False, "error": "temporary"},
            }
        }
        post = {
            "id": "post-1", "client_id": "client-1", "caption": "Text",
            "targets": ["facebook", "instagram"], "attempts": 0, "max_attempts": 3,
            "approved_at": "2026-08-06T00:00:00Z",
        }
        result = social_engine.process_post(post)
        self.assertFalse(result["ok"])
        self.assertEqual(publish.call_args.args[3], ["facebook", "instagram"])
        self.assertEqual(finish.call_args.kwargs["status"], "scheduled")
        self.assertEqual(finish.call_args.kwargs["fb_post_id"], "fb-123")

        publish.reset_mock()
        finish.reset_mock()
        publish.return_value = {"results": {"instagram": {"ok": True, "media_id": "ig-456"}}}
        post.update({"attempts": 1, "fb_post_id": "fb-123"})
        result = social_engine.process_post(post)
        self.assertTrue(result["ok"])
        self.assertEqual(publish.call_args.args[3], ["instagram"])
        self.assertEqual(finish.call_args.kwargs["status"], "published")
        self.assertEqual(finish.call_args.kwargs["fb_post_id"], "fb-123")
        self.assertEqual(finish.call_args.kwargs["ig_post_id"], "ig-456")

    @patch("src.social_engine.db.save_publish_log")
    @patch("src.social_engine.db.finish_post")
    @patch("src.social_engine.publisher.publish")
    def test_dry_run_never_marks_published(self, publish, finish, _log):
        publish.return_value = {"dry_run": True, "results": {"facebook": {"dry_run": True}}}
        post = {
            "id": "post-1", "client_id": "client-1", "caption": "Text",
            "targets": ["facebook"], "attempts": 0, "approved_at": "2026-08-06T00:00:00Z",
        }
        result = social_engine.process_post(post, dry_run=True)
        self.assertTrue(result["ok"])
        self.assertEqual(finish.call_args.kwargs["status"], "scheduled")


if __name__ == "__main__":
    unittest.main()
