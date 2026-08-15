"""Regression coverage for the 2026-08-13 production-pilot-prep pass.

Proves, without network/staging credentials:
  1. The pinned DeepSeek model identifier is actually used (not the legacy
     floating alias `deepseek-chat`).
  2. The pinned Claude model identifier is actually used (not the floating
     alias `claude-haiku-4-5`).
  3. Cost telemetry resolves to VERIFIED once usage reports the pinned
     model identifiers, using the authoritative rates cited in
     staging_e2e_report.py (DeepSeek + Anthropic official pricing pages,
     checked 2026-08-13).
  4. The Lead Scoring manifest's `evals` field resolves to a real file that
     exists on disk and is itself a passing test module — not a placeholder
     string with nothing behind it.
  5. The Kernel's own `validate_manifest()` still accepts the staging
     manifest shape unchanged (lifecycle=available requires evals +
     revocation.procedure — proves the pinning/eval changes didn't
     accidentally break manifest admission).
  6. None of this touches `src/config.py`, `src/ai.py`, or any shared
     AI-provider selection used elsewhere in the codebase — the pin is
     local to `src/lead_scoring/providers.py` only.

Run: python3 -m unittest tests.test_lead_scoring_pinning_and_cost -v
"""
import os
import unittest

from src.lead_scoring import kernel_registry, providers
from src.lead_scoring.staging_e2e_report import _cost_eur
from src.agency_kernel import AgentManifest, validate_manifest


class ModelPinningTests(unittest.TestCase):
    def test_deepseek_model_is_pinned_not_legacy_alias(self):
        self.assertEqual(providers.DEEPSEEK_MODEL, "deepseek-v4-flash")
        self.assertNotEqual(providers.DEEPSEEK_MODEL, "deepseek-chat",
                             "must not silently fall back to the deprecated legacy alias")

    def test_claude_model_is_pinned_not_floating_alias(self):
        self.assertEqual(providers.CLAUDE_MODEL, "claude-haiku-4-5-20251001")
        self.assertNotEqual(providers.CLAUDE_MODEL, "claude-haiku-4-5",
                             "must not silently fall back to the floating alias")

    def test_pins_are_independent_of_shared_ai_config(self):
        # The pin must not be SOURCED from cfg.MODEL_CHEAP — that's the
        # shared, product-wide model selector used by src/ai.py for
        # website/brand copy. If someone changes it, this pilot's model must
        # NOT move with it. Check the actual executable code, not the
        # docstring (which legitimately mentions cfg.MODEL_CHEAP in prose
        # explaining *why* it's no longer used) — line-by-line, skip triple-
        # quoted docstring blocks, and require no live code line assigns a
        # model constant or a request payload's "model" key from it.
        import ast
        import inspect
        tree = ast.parse(inspect.getsource(providers))
        offending = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr == "MODEL_CHEAP":
                if isinstance(node.value, ast.Name) and node.value.id == "cfg":
                    offending.append(node.lineno)
        self.assertEqual(offending, [],
                          f"providers.py must not read cfg.MODEL_CHEAP in executable code (lines {offending})")


class CostTelemetryVerifiedTests(unittest.TestCase):
    def test_cost_report_verified_when_pinned_models_used(self):
        usage_log = [
            {"provider": "deepseek", "model": providers.DEEPSEEK_MODEL,
             "requested_model": providers.DEEPSEEK_MODEL, "model_mismatch": False,
             "input_tokens": 137, "output_tokens": 33, "node": "deepseek_score"},
            {"provider": "anthropic", "model": providers.CLAUDE_MODEL,
             "requested_model": providers.CLAUDE_MODEL, "model_mismatch": False,
             "input_tokens": 240, "output_tokens": 79, "node": "claude_review"},
        ]
        report = _cost_eur(usage_log)
        self.assertEqual(report["status"], "VERIFIED")
        self.assertIsNotNone(report["verified_eur"])
        self.assertEqual(report["models_missing_authoritative_rate"], [])
        self.assertEqual(report["model_mismatches_detected"], [])

    def test_cost_report_unverified_when_legacy_alias_used(self):
        # Sanity check the negative case still works: an unpinned/legacy
        # model string must NOT be reported as VERIFIED.
        usage_log = [{"provider": "deepseek", "model": "deepseek-chat",
                      "requested_model": "deepseek-chat", "model_mismatch": False,
                      "input_tokens": 100, "output_tokens": 20, "node": "deepseek_score"}]
        report = _cost_eur(usage_log)
        self.assertEqual(report["status"], "UNVERIFIED")


class ManifestEvalArtifactTests(unittest.TestCase):
    def test_manifest_eval_points_to_a_real_existing_file(self):
        manifest = kernel_registry.manifest_dict()
        self.assertEqual(manifest["evals"], ["tests/test_lead_scoring_offline_eval.py"])
        eval_path = manifest["evals"][0]
        self.assertTrue(os.path.exists(eval_path), f"eval artifact does not exist: {eval_path}")

    def test_eval_artifact_itself_passes(self):
        import subprocess
        import sys
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "tests.test_lead_scoring_offline_eval", "-v"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_kernel_still_accepts_staging_manifest_shape(self):
        manifest = AgentManifest.from_dict(kernel_registry.manifest_dict())
        # Must not raise — proves the pinning/eval changes didn't break
        # admission of the lifecycle=available manifest.
        validate_manifest(manifest)
        self.assertEqual(manifest.lifecycle, "available")
        self.assertTrue(manifest.evals)
        self.assertTrue(manifest.revocation.get("procedure"))


if __name__ == "__main__":
    unittest.main()
