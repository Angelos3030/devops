from __future__ import annotations

import threading
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from src.ai_editor.model import DeepSeekSiteEditingModel, EditPlan, Operation, SiteEditingModel
from src.ai_editor.service import EditingService
from src.ai_editor.store import InMemoryEditorStore


def plan(intent: str, *operations: Operation) -> EditPlan:
    return EditPlan(
        schema_version="1.0",
        intent=intent,
        explanation="Έτοιμο.",
        requires_confirmation=False,
        confidence=1.0,
        operations=list(operations),
    )


class StaticModel(SiteEditingModel):
    def __init__(self, result: EditPlan | None):
        self.result = result

    def plan_edit(self, context, message):
        return self.result


class FakeResponse:
    def __init__(self, *, ok=True, status=200, payload=None, text=""):
        self.ok = ok
        self.status_code = status
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


class EditorIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.client_id = "client-a"
        self.store = InMemoryEditorStore()
        self.original = {
            "name": "Studio Alpha",
            "trade": "Κομμωτήριο",
            "phone": "2100000000",
            "hours": "09:00-17:00",
            "palette": "original",
            "services": [{"name": "Κούρεμα", "price": "15€"}],
        }
        self.store.add_client(
            self.client_id,
            self.original,
            [
                {"id": "p1", "type": "photo"},
                {"id": "p2", "type": "photo"},
                {"id": "p3", "type": "photo"},
            ],
        )

    def service(self, edit_plan: EditPlan | None, *, allow=True):
        return EditingService(StaticModel(edit_plan), self.store, lambda client_id: allow)

    def test_real_vertical_slice_commits_preview_and_revision(self):
        edit_plan = plan("update_phone", Operation(op="update_phone", params={"phone": "2101111111"}))
        result = self.service(edit_plan).edit(
            self.client_id, "άλλαξε το τηλέφωνο", idempotency_key="req-1", expected_version=0
        )
        self.assertTrue(result.success)
        self.assertEqual(result.content["phone"], "2101111111")
        self.assertEqual(self.store.get_content(self.client_id)["phone"], "2101111111")
        self.assertEqual(self.store.revision_count(self.client_id), 1)
        self.assertIsNotNone(result.revision_id)

    def test_operation_two_of_three_failure_rolls_back_everything(self):
        edit_plan = plan(
            "multi_edit",
            Operation(op="update_phone", params={"phone": "2101111111"}),
            Operation(op="set_palette", params={"palette": "not-a-palette"}),
            Operation(op="update_hours", params={"hours": "10:00-18:00"}),
        )
        result = self.service(edit_plan).edit(
            self.client_id, "πολλαπλή αλλαγή", idempotency_key="req-rollback", expected_version=0
        )
        self.assertFalse(result.success)
        self.assertEqual(self.store.get_content(self.client_id), self.original)
        self.assertEqual(self.store.revision_count(self.client_id), 0)

    def test_undo_restores_state_without_model_reconstruction(self):
        edit_plan = plan("update_phone", Operation(op="update_phone", params={"phone": "2101111111"}))
        self.service(edit_plan).edit(
            self.client_id, "άλλαξε τηλέφωνο", idempotency_key="req-edit", expected_version=0
        )
        undo_plan = plan("undo")
        result = self.service(undo_plan).edit(
            self.client_id, "γύρνα πίσω", idempotency_key="req-undo", expected_version=1
        )
        self.assertTrue(result.success)
        self.assertEqual(result.content, self.original)
        self.assertEqual(result.version, 2)

    def test_idempotency_prevents_duplicate_mutation_and_revision(self):
        edit_plan = plan("update_phone", Operation(op="update_phone", params={"phone": "2101111111"}))
        service = self.service(edit_plan)
        first = service.edit(self.client_id, "άλλαξε", idempotency_key="same", expected_version=0)
        second = service.edit(self.client_id, "άλλαξε", idempotency_key="same", expected_version=0)
        self.assertTrue(first.success)
        self.assertTrue(second.success)
        self.assertTrue(second.duplicate)
        self.assertEqual(self.store.revision_count(self.client_id), 1)
        self.assertEqual(self.store.get_version(self.client_id), 1)

    def test_concurrent_duplicate_submission_commits_once(self):
        edit_plan = plan("update_phone", Operation(op="update_phone", params={"phone": "2101111111"}))
        service = self.service(edit_plan)
        barrier = threading.Barrier(5)
        results = []

        def submit():
            barrier.wait()
            results.append(service.edit(
                self.client_id, "άλλαξε", idempotency_key="race", expected_version=0
            ))

        threads = [threading.Thread(target=submit) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertTrue(all(item.success for item in results))
        self.assertEqual(self.store.revision_count(self.client_id), 1)
        self.assertEqual(self.store.get_version(self.client_id), 1)

    def test_stale_revision_is_rejected(self):
        edit_plan = plan("update_phone", Operation(op="update_phone", params={"phone": "2101111111"}))
        service = self.service(edit_plan)
        self.assertTrue(service.edit(
            self.client_id, "πρώτη", idempotency_key="first", expected_version=0
        ).success)
        stale = service.edit(
            self.client_id, "δεύτερη", idempotency_key="second", expected_version=0
        )
        self.assertFalse(stale.success)
        self.assertTrue(stale.rejected)
        self.assertEqual(self.store.get_version(self.client_id), 1)

    def test_authorization_boundary_rejects_before_model_mutation(self):
        edit_plan = plan("update_phone", Operation(op="update_phone", params={"phone": "2101111111"}))
        result = self.service(edit_plan, allow=False).edit(
            "other-client", "άλλαξε", idempotency_key="idor", expected_version=0
        )
        self.assertFalse(result.success)
        self.assertTrue(result.rejected)
        self.assertEqual(self.store.get_content(self.client_id), self.original)

    def test_capability_rule_blocks_forbidden_palette(self):
        edit_plan = plan("set_palette", Operation(op="set_palette", params={"palette": "forest"}))
        result = self.service(edit_plan).edit(
            self.client_id,
            "κάνε το πράσινο",
            idempotency_key="capability",
            expected_version=0,
            capabilities={"palettes": ["original", "mono"]},
        )
        self.assertFalse(result.success)
        self.assertEqual(self.store.get_content(self.client_id), self.original)

    def test_unexpected_operation_parameter_is_rejected(self):
        edit_plan = plan(
            "update_phone",
            Operation(op="update_phone", params={"phone": "2101111111", "css": "body{}"}),
        )
        result = self.service(edit_plan).edit(
            self.client_id, "άλλαξε", idempotency_key="extra", expected_version=0
        )
        self.assertFalse(result.success)
        self.assertEqual(self.store.get_content(self.client_id), self.original)

    def test_invalid_top_level_model_output_is_rejected_by_schema(self):
        with self.assertRaises(ValidationError):
            EditPlan.model_validate({
                "schema_version": "1.0", "intent": "x", "operations": [],
                "explanation": "x", "requires_confirmation": False,
                "confidence": 1.0, "arbitrary_css": "body{}",
            })

    def test_provider_failure_changes_nothing(self):
        result = self.service(None).edit(
            self.client_id, "άλλαξε", idempotency_key="provider-down", expected_version=0
        )
        self.assertFalse(result.success)
        self.assertEqual(self.store.get_content(self.client_id), self.original)
        self.assertEqual(self.store.revision_count(self.client_id), 0)

    def test_low_confidence_changes_nothing(self):
        edit_plan = EditPlan(schema_version="1.0", intent="update_phone",
            explanation="ίσως", requires_confirmation=False, confidence=.4,
            operations=[Operation(op="update_phone", params={"phone": "2101111111"})])
        result = self.service(edit_plan).edit(
            self.client_id, "ίσως άλλαξέ το", idempotency_key="low", expected_version=0)
        self.assertFalse(result.success)
        self.assertEqual(self.store.revision_count(self.client_id), 0)

    def test_xss_and_invalid_time_are_rejected_atomically(self):
        edit_plan = plan("unsafe",
            Operation(op="update_business_field", params={"field": "tagline", "value": "<script>alert(1)</script>"}),
            Operation(op="update_hours", params={"hours": "Δευτέρα 29:99"}))
        result = self.service(edit_plan).edit(
            self.client_id, "unsafe", idempotency_key="unsafe", expected_version=0)
        self.assertFalse(result.success)
        self.assertEqual(self.store.get_content(self.client_id), self.original)

    def test_duplicate_media_indices_are_rejected(self):
        edit_plan = plan("reorder",
            Operation(op="reorder_media", params={"order": [1, 1, 2]}))
        result = self.service(edit_plan).edit(
            self.client_id, "δεύτερη πρώτη", idempotency_key="media-dup", expected_version=0)
        self.assertFalse(result.success)
        self.assertEqual(self.store.revision_count(self.client_id), 0)

    @patch("requests.post")
    def test_malformed_provider_tool_arguments_are_rejected(self, post):
        post.return_value = FakeResponse(payload={
            "choices": [{"message": {"tool_calls": [{
                "function": {"name": "edit_site", "arguments": "{not-json"}
            }]}}]
        })
        model = DeepSeekSiteEditingModel(api_key="synthetic", base_url="https://example.test")
        self.assertIsNone(model.plan_edit({}, "synthetic"))

    @patch("requests.post")
    def test_provider_plain_json_without_tool_call_is_rejected(self, post):
        post.return_value = FakeResponse(payload={
            "choices": [{"message": {"content": '{"intent":"unsafe fallback"}'}}]
        })
        model = DeepSeekSiteEditingModel(api_key="synthetic", base_url="https://example.test")
        self.assertIsNone(model.plan_edit({}, "synthetic"))


if __name__ == "__main__":
    unittest.main()
