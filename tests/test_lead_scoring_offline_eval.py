"""Real offline eval artifact for the Lead Scoring Kernel manifest.

Replaces the placeholder eval identifier `"lead_scoring_offline_eval_v1"`
that `src/lead_scoring/kernel_registry.py`'s manifest previously declared —
a string with no corresponding runnable artifact. `validate_manifest()`
(src/agency_kernel.py) requires `evals` to be non-empty for
`lifecycle="available"`, but never checked the string actually pointed to
something real; this file is that something.

Scope, deliberately narrow: this is a DETERMINISTIC eval over
`business_rules_node`'s tier-assignment logic (the one part of the pipeline
that must behave identically every run, no model variance). It does NOT
attempt to eval DeepSeek's or Claude's judgment quality — that requires a
larger labeled dataset and human-reviewed acceptance criteria, tracked as
its own follow-up (see the production-pilot plan's success metrics: scoring
accuracy / human acceptance rate). This eval's job is narrower and
achievable today: prove the deterministic business-rule thresholds that
everything else is built on don't silently drift.

Run: `python3 -m unittest tests.test_lead_scoring_offline_eval -v`
No network, no staging credentials, no DeepSeek/Claude calls.
"""
import unittest

from src.lead_scoring.graph import business_rules_node

# (score, confidence) -> expected (tier, escalate_to_claude)
# Fixture values chosen to exercise both thresholds (70 for hot, 40 for warm)
# and both escalation triggers (confidence < 0.75, tier == "hot").
_CASES = [
    # (score, confidence, expected_tier, expected_escalate)
    (95, 0.90, "hot", True),      # hot always escalates, even with high confidence
    (70, 0.95, "hot", True),      # boundary: exactly 70 is hot
    (69, 0.95, "warm", False),    # boundary: 69 is warm, not hot
    (55, 0.80, "warm", False),    # mid-warm, confident -> no escalation
    (55, 0.60, "warm", True),     # mid-warm, low confidence -> escalates
    (40, 0.90, "warm", False),    # boundary: exactly 40 is warm
    (39, 0.90, "cold", False),    # boundary: 39 is cold
    (10, 0.99, "cold", False),    # clearly cold, high confidence
    (10, 0.50, "cold", True),     # clearly cold, but low confidence still escalates
]


class LeadScoringOfflineEval(unittest.TestCase):
    def test_business_rule_tier_thresholds_are_stable(self):
        for score, confidence, expected_tier, expected_escalate in _CASES:
            with self.subTest(score=score, confidence=confidence):
                state = {"deepseek_score": {"score": score, "confidence": confidence}}
                result = business_rules_node(state)["business_rule"]
                self.assertEqual(result["tier"], expected_tier,
                                  f"score={score} confidence={confidence}")
                self.assertEqual(result["escalate_to_claude"], expected_escalate,
                                  f"score={score} confidence={confidence}")
                self.assertEqual(result["score"], score)

    def test_all_three_tiers_are_reachable(self):
        tiers_seen = {business_rules_node({"deepseek_score": {"score": s, "confidence": 0.9}})
                      ["business_rule"]["tier"] for s in (10, 55, 95)}
        self.assertEqual(tiers_seen, {"cold", "warm", "hot"})


if __name__ == "__main__":
    unittest.main()
