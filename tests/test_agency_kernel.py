import unittest
from decimal import Decimal

from src.agency_kernel import (
    AgentManifest,
    CostEnvelope,
    KernelValidationError,
    TaskRequest,
    VersionedRef,
    admit_manifest,
    build_action_queue_item,
    capability_matrix,
    evaluate_policy,
)


def manifest(**overrides):
    raw = {
        "agent_key": "website.qa",
        "version": "1",
        "name": "Website QA",
        "purpose": "Verify website quality before release",
        "roi_hypothesis": "Catch regressions before they cost leads",
        "success_metrics": ["escaped_regressions"],
        "lifecycle": "available",
        "autonomy": "A1",
        "capabilities": ["website.qa@1"],
        "permissions": ["content.publish"],
        "data_classes": ["public", "repository", "synthetic"],
        "cost": {"max_money_eur": "1", "max_tokens": 1000,
                 "max_runtime_seconds": 300},
        "evals": ["tests/test_website_qa.py"],
        "revocation": {"procedure": "disable installations, then revoke version"},
        "entrypoint": "src.website_qa:run",
    }
    raw.update(overrides)
    return AgentManifest.from_dict(raw)


class ManifestTests(unittest.TestCase):
    def test_valid_manifest_is_admitted(self):
        candidate = manifest()
        admit_manifest(candidate, [])
        self.assertEqual(str(candidate.agent), "website.qa@1")

    def test_roi_and_metric_are_mandatory(self):
        with self.assertRaisesRegex(KernelValidationError, "ROI"):
            manifest(roi_hypothesis="", success_metrics=[])

    def test_duplicate_purpose_is_rejected(self):
        current = manifest()
        candidate = manifest(agent_key="website.qa.copy", version="1")
        with self.assertRaisesRegex(KernelValidationError, "Purpose already owned"):
            admit_manifest(candidate, [current])

    def test_overlap_requires_admission_dimension(self):
        with self.assertRaisesRegex(KernelValidationError, "Overlapping functionality"):
            manifest(overlaps_with=["website.builder@1"],
                     separation_reasons=["different name"])


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.manifest = manifest()
        self.capability = VersionedRef("website.qa", "1")
        self.installation = {
            "status": "enabled",
            "granted_permissions": ["content.publish"],
            "budget_limits": {"max_money_eur": "1", "max_tokens": 1000,
                              "max_runtime_seconds": 300},
        }

    def decide(self, task=None, **changes):
        installation = {**self.installation, **changes}
        return evaluate_policy(
            manifest=self.manifest,
            installation=installation,
            entitlements=[self.capability],
            enabled_dependencies=[],
            task=task or TaskRequest(capability=self.capability),
        )

    def test_disabled_installation_is_blocked(self):
        decision = self.decide(status="disabled")
        self.assertFalse(decision.allowed)
        self.assertIn("installation:disabled", decision.reasons)

    def test_missing_entitlement_is_blocked(self):
        decision = evaluate_policy(
            manifest=self.manifest, installation=self.installation,
            entitlements=[], enabled_dependencies=[],
            task=TaskRequest(capability=self.capability),
        )
        self.assertFalse(decision.allowed)
        self.assertIn("capability_not_entitled", decision.reasons)

    def test_deepseek_personal_data_is_blocked(self):
        task = TaskRequest(capability=self.capability,
                           data_classes=frozenset({"personal"}), provider="deepseek")
        decision = self.decide(task)
        self.assertFalse(decision.allowed)
        self.assertIn("deepseek_data_policy", decision.reasons)

    def test_production_write_requires_approval(self):
        task = TaskRequest(capability=self.capability,
                           requested_permissions=frozenset({"content.publish"}))
        decision = self.decide(task)
        self.assertTrue(decision.allowed)
        self.assertTrue(decision.requires_approval)
        self.assertEqual(decision.effective_approval_policy, "client")

    def test_budget_is_enforced(self):
        task = TaskRequest(capability=self.capability,
                           budget=CostEnvelope(max_money_eur=Decimal("2")))
        decision = self.decide(task)
        self.assertFalse(decision.allowed)
        self.assertIn("money_budget_exceeded", decision.reasons)


class ContractTests(unittest.TestCase):
    def test_capability_override_denies_plan_grant(self):
        resolved = capability_matrix(
            [{"capability_key": "website.qa", "capability_version": "1"}],
            [{"capability_key": "website.qa", "capability_version": "1",
              "status": "denied", "source": "manual"}],
        )
        self.assertEqual(resolved, {})

    def test_action_queue_contract_is_versioned(self):
        item = build_action_queue_item({
            "task_id": "task-1", "workspace_id": "workspace-1",
            "agent_key": "website.qa", "agent_version": "1",
            "capability_key": "website.qa", "capability_version": "1",
            "needs_approval": True,
        })
        self.assertEqual(item["schema_version"], "1.0")
        self.assertTrue(item["needs_approval"])
        self.assertEqual(item["agent"]["key"], "website.qa")


if __name__ == "__main__":
    unittest.main()
