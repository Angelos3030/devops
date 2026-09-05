from __future__ import annotations

import unittest

from tests.ai_editor_holdout_v1 import HOLDOUT_CASES
from tests.test_ai_editor import CORPUS
from src.ai_editor.engine import EditingEngine
from src.ai_editor.model import EditPlan, Operation
from src.ai_editor.store import InMemoryEditorStore


class HoldoutCorpusIntegrityTests(unittest.TestCase):
    def test_holdout_has_at_least_300_unique_requests(self):
        self.assertGreaterEqual(len(HOLDOUT_CASES), 300)
        self.assertEqual(len(HOLDOUT_CASES), len({case.case_id for case in HOLDOUT_CASES}))
        # The same follow-up phrase may intentionally have a different expected
        # result when conversational context exists (for example, "όχι αυτή").
        semantic_inputs = {(case.message, repr(sorted(case.context.items()))) for case in HOLDOUT_CASES}
        self.assertEqual(len(HOLDOUT_CASES), len(semantic_inputs))

    def test_holdout_does_not_overlap_regression_v1(self):
        regression = {message.strip().lower() for message in CORPUS}
        overlap = [case.case_id for case in HOLDOUT_CASES if case.message.strip().lower() in regression]
        self.assertEqual(overlap, [])

    def test_required_adversarial_categories_are_present(self):
        categories = {case.category for case in HOLDOUT_CASES}
        required = {
            "phone", "hours", "business_field", "service", "palette", "media", "multi",
            "undo", "unsupported", "malformed", "xss", "prompt_injection", "code",
            "authorization", "ambiguous", "followup", "capability",
        }
        self.assertEqual(required - categories, set())

    def test_multi_operation_and_rejection_coverage(self):
        self.assertGreaterEqual(sum(len(case.operations) > 1 for case in HOLDOUT_CASES), 30)
        self.assertGreaterEqual(sum(case.reject for case in HOLDOUT_CASES), 50)
        self.assertGreaterEqual(sum(case.authorization_reject for case in HOLDOUT_CASES), 8)

    def test_expected_plans_are_valid_and_capabilities_are_enforced(self):
        capability_cases = 0
        for case in HOLDOUT_CASES:
            if case.reject or case.intent == "undo":
                continue
            edit_plan = EditPlan(
                schema_version="1.0",
                intent=case.intent,
                explanation="Synthetic holdout expectation.",
                requires_confirmation=False,
                confidence=1.0,
                operations=[Operation(op=item.op, params=item.params) for item in case.operations],
            )
            store = InMemoryEditorStore()
            store.add_client(
                case.case_id,
                {"name": "Synthetic", "services": [], "palette": "original"},
                [{"id": f"p{i}", "type": "photo"} for i in range(3)],
            )
            result = EditingEngine.execute_plan(
                case.case_id,
                edit_plan,
                store=store,
                capabilities=case.capabilities,
                persist=False,
            )
            if case.capabilities:
                capability_cases += 1
                self.assertFalse(result.success, case.case_id)
            else:
                self.assertTrue(result.success, f"{case.case_id}: {result.message}")
        self.assertGreaterEqual(capability_cases, 5)


if __name__ == "__main__":
    unittest.main()
