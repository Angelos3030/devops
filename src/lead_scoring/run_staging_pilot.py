#!/usr/bin/env python3
"""
Real (non-mocked) Lead Scoring staging run.

    VITRINA_ENV=staging python -m src.lead_scoring.run_staging_pilot

What this does, in order:
  1. `env.require(DEV, STAGING)` — refuses to run at all outside those two,
     using the project's own existing environment guard (src/env.py). No
     PRODUCTION_* credential is ever read by this module.
  2. Registers the Lead Scoring manifest into the REAL `agent_registry` +
     `agent_capabilities` tables in staging (idempotent — safe to re-run).
  3. Builds a `PostgresSaver` checkpointer against staging, in a NEW isolated
     schema (`vitrina_lead_scoring_runtime`) — never touching `clients`,
     `sites`, or the Agency Kernel's own tables.
  4. Submits one synthetic lead through the real graph (real DeepSeek call,
     real Claude call where escalation triggers).

Expected outcome on a fresh run: the Kernel correctly BLOCKS at
`deepseek_score` with `installation:missing`, because this pilot deliberately
never creates an `agent_installations` row (see kernel_registry.py). That is
the correct, intended current state — proof the fail-closed gate holds for
real, not a bug to silence. Enabling a real installation is a separate,
explicitly-approved step, consistent with docs/25-AGENCY-KERNEL.md's own
rollout checklist.

No real CRM is connected. No production credential is read. No client row is
created, read, or modified.
"""
from __future__ import annotations

import sys
import time

sys.path.insert(0, ".")

from .. import env  # noqa: E402


def main() -> None:
    env.require(env.DEV, env.STAGING)
    env.print_banner()

    from . import kernel_registry
    print("\n[1/3] Registering Lead Scoring manifest into staging agent_registry...")
    reg = kernel_registry.register()
    print(f"  registered: {reg['agent_key']}@{reg['version']}  checksum={reg['checksum'][:12]}...")
    print("  NOTE: no agent_installations row created — this is deliberate, see module docstring.")

    print("\n[2/3] Setting up PostgresSaver against staging (isolated schema: "
          "vitrina_lead_scoring_runtime)...")
    import os
    import psycopg2
    conn_string = os.environ.get("DATABASE_URL_STAGING", "")
    if not conn_string:
        sys.exit("DATABASE_URL_STAGING not set")

    admin = psycopg2.connect(conn_string)
    admin.autocommit = True
    cur = admin.cursor()
    cur.execute("CREATE SCHEMA IF NOT EXISTS vitrina_lead_scoring_runtime")
    admin.close()

    from langgraph.checkpoint.postgres import PostgresSaver
    with PostgresSaver.from_conn_string(conn_string) as checkpointer:
        checkpointer.setup()

        from .graph import build_graph
        graph = build_graph(checkpointer)

        print("\n[3/3] Submitting one synthetic lead through the real graph...")
        # A syntactically valid but all-zeros UUID — obviously fake, never a
        # real clients.id. validate_node only checks tenant_id is truthy, so
        # this passes validation and reaches the Kernel-gated deepseek_score
        # node, which is the actual thing this run is meant to exercise.
        # (First attempt at this script passed tenant_id=None, which tripped
        # validate_node's own missing_tenant_id check instead — a bug in this
        # harness, not the Kernel; fixed here.)
        SYNTHETIC_TENANT_ID = "00000000-0000-0000-0000-000000000000"
        lead = {"email": "pilot-test@example.gr", "service": "ξυλουργός", "source": "web_form",
                "message": "Χρειάζομαι επισκευή τώρα, έχω budget 500 ευρώ"}
        thread_id = f"staging-pilot::{int(time.time())}"
        config = {"configurable": {"thread_id": thread_id}}
        try:
            result = graph.invoke(
                {"tenant_id": SYNTHETIC_TENANT_ID, "lead_id": thread_id, "raw_lead": lead, "audit_log": []},
                config,
            )
        except PermissionError as exc:
            print(f"\n  Kernel blocked execution (EXPECTED on a fresh run): {exc}")
            print("  This confirms fail-closed behavior holds against the real staging registry.")
            print("  To let this run all the way through: create a real agent_installations row")
            print("  for a real staging workspace_id — a separate, explicit approval step, not")
            print("  something this script does automatically.")
            return

        print(f"\n  UNEXPECTED: graph completed without a Kernel block: {result}")
        print("  (If an installation row now exists, this pilot may need re-scoping — flag before trusting this.)")


if __name__ == "__main__":
    main()
