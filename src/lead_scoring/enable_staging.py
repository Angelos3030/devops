#!/usr/bin/env python3
"""
Controlled staging enablement — supports docs/adr/0004-lead-scoring-staging-enablement.md.

    VITRINA_ENV=staging python -m src.lead_scoring.enable_staging

Does exactly four things, in order, all scoped to ONE dedicated synthetic
workspace (never a real client):

  1. Promotes the manifest from draft (ADR-0003) to available (this ADR) —
     register() now writes manifest_dict()'s real lifecycle value (a genuine
     bug found while wiring this up: the old INSERT hardcoded 'draft'
     regardless of the manifest content — fixed in kernel_registry.py).
  2. Creates the dedicated synthetic staging workspace
     (qa-leadscoring@vitrina.test, id=aaaa0007-...) if it doesn't exist yet —
     following scripts/seed_staging.py's own existing QA-data convention.
  3. Installs (enables) the agent for that ONE workspace only, with:
       - granted_permissions = ["crm.write"] — exactly what the manifest
         declares, nothing broader.
       - budget_limits: max_money_eur=0.50, max_tokens=5000,
         max_runtime_seconds=120 — tight, pilot-appropriate caps, not the
         manifest's own wider ceiling (max_money_eur=1/max_tokens=20000)
         which represents the theoretical maximum, not what a single
         controlled pilot run should be allowed to spend.
  4. Prints the exact resulting registry/installation/workspace state.

Refuses to run outside VITRINA_ENV in {dev, staging} (src/env.py's existing
guard). No PRODUCTION_* credential is ever read. No real client is touched.
"""
from __future__ import annotations

import sys

sys.path.insert(0, ".")

from .. import env  # noqa: E402


def main() -> None:
    env.require(env.DEV, env.STAGING)
    env.print_banner()

    from . import kernel_registry

    print("\n[1/4] Promoting manifest to lifecycle='available' (staging only)...")
    reg = kernel_registry.register()
    print(f"  {reg['agent_key']}@{reg['version']}  checksum={reg['checksum'][:12]}...")

    print("\n[2/4] Creating dedicated synthetic staging workspace (idempotent)...")
    workspace_id = kernel_registry.create_staging_workspace()
    print(f"  workspace_id={workspace_id}  email={kernel_registry.STAGING_WORKSPACE_EMAIL}")

    print("\n[3/4] Installing (enabling) agent for that ONE workspace, minimum permissions...")
    granted_permissions = ["crm.write"]  # exactly what the manifest declares — nothing broader
    budget_limits = {"max_money_eur": "0.50", "max_tokens": 5000, "max_runtime_seconds": 120}
    inst = kernel_registry.install(granted_permissions=granted_permissions, budget_limits=budget_limits)
    print(f"  status={inst['status']}  granted_permissions={inst['granted_permissions']}")
    print(f"  budget_limits={inst['budget_limits']}")

    print("\n[4/4] Exact resulting state:")
    import json
    state = kernel_registry.registry_state()
    print(json.dumps(state, indent=2, ensure_ascii=False))

    print("\nTo revoke immediately at any point:")
    print("  VITRINA_ENV=staging python -m src.lead_scoring.disable_staging")


if __name__ == "__main__":
    main()
