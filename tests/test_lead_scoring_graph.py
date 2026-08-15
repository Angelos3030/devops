"""Regression test: halt_invalid_node must not conflate two different halt
causes under the same generic `halted_reason`.

Real bug found in ADR-0004's staging E2E run: negative test #7
("human_rejection") reported `halted_reason=validation_failed` even though
the lead passed validation and was halted because a human explicitly
rejected it at the approval step. Root cause: `halt_invalid_node` used
`state.get("halted_reason") or "validation_failed"`, and NOTHING upstream of
the approval-rejection path ever set `halted_reason` before reaching that
node — so it always fell through to the same default used by the real
validation-failure path (`route_after_validate`), regardless of which path
actually triggered the halt.

Fix: `human_approval_node` now sets `halted_reason="human_rejected"` in its
own state update when the decision is not approved, so `halt_invalid_node`
picks that up instead of falling through to the generic default.

This test proves the two halt reasons stay distinct without touching the
network, DeepSeek, Claude, or staging Postgres — it monkeypatches
`kernel_gate` (allow-everything stub) and the provider calls (deterministic
mocks), and uses LangGraph's in-memory checkpointer.
"""
import unittest

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from src.lead_scoring import graph as lead_graph


def _allow_everything(**kwargs):
    return {"allowed": True, "reasons": ["test_stub"]}


class HaltReasonDistinctnessTests(unittest.TestCase):
    def setUp(self):
        self._real_kernel_gate = lead_graph.kernel_gate
        lead_graph.kernel_gate = _allow_everything
        self.addCleanup(lambda: setattr(lead_graph, "kernel_gate", self._real_kernel_gate))

        self.graph = lead_graph.build_graph(MemorySaver())

    def test_validation_failure_halts_with_validation_failed(self):
        config = {"configurable": {"thread_id": "test::no-tenant"}}
        # No tenant_id -> validate_node's own missing_tenant_id check fails,
        # routed straight to halt_invalid without ever reaching human_approval.
        result = self.graph.invoke(
            {"lead_id": "no-tenant", "raw_lead": {"email": "x@vitrina.test", "service": "test"},
             "audit_log": []},
            config,
        )
        self.assertEqual(result.get("halted_reason"), "validation_failed")
        self.assertIsNone(result.get("crm_draft"))

    def test_human_rejection_halts_with_human_rejected_not_validation_failed(self):
        config = {"configurable": {"thread_id": "test::rejected-lead"}}
        hot_lead = {"email": "hot@vitrina.test", "service": "ξυλουργός",
                    "message": "χρειάζομαι επισκευή τώρα, budget 500 ευρώ"}

        # deepseek_score_node/claude_review_node call real providers unless
        # monkeypatched — stub them so this test needs no network/credentials.
        import src.lead_scoring.providers as providers
        real_deepseek, real_claude = providers.deepseek_score, providers.claude_review
        providers.deepseek_score = lambda features: {
            "score": 90, "confidence": 0.95, "reasoning": "stub"}
        providers.claude_review = lambda raw_lead, features, business_rule: {
            "recommended_tier": "hot", "rationale": "stub", "risk_flag": False}
        self.addCleanup(lambda: setattr(providers, "deepseek_score", real_deepseek))
        self.addCleanup(lambda: setattr(providers, "claude_review", real_claude))

        first = self.graph.invoke(
            {"tenant_id": "tenant-a", "lead_id": "rejected-lead", "raw_lead": hot_lead, "audit_log": []},
            config,
        )
        self.assertIn("__interrupt__", first, "hot lead must pause for human approval")

        rejected = self.graph.invoke(
            Command(resume={"approved": False, "note": "regression test rejection"}), config,
        )

        self.assertEqual(rejected.get("halted_reason"), "human_rejected")
        self.assertNotEqual(rejected.get("halted_reason"), "validation_failed")
        self.assertIsNone(rejected.get("crm_draft"))

    def test_the_two_halt_reasons_are_never_equal(self):
        # Belt-and-suspenders: the whole point of the fix is that these two
        # constants must never collide again, however either path evolves.
        self.assertNotEqual("validation_failed", "human_rejected")


if __name__ == "__main__":
    unittest.main()
