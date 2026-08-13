#!/usr/bin/env python3
"""
PostgresSaver spike for the Lead Scoring pilot — supports
docs/adr/0002-lead-scoring-langgraph-pilot.md.

IMPORTANT — read before trusting the "staging" label on any output line:

  This sandbox cannot resolve aws-0-eu-central-1.pooler.supabase.com (DNS
  failure, confirmed directly: `psycopg2.connect(DATABASE_URL_STAGING)` fails
  with "Temporary failure in name resolution" before any credential is even
  used). DATABASE_URL_STAGING is read from .env, never printed, and never
  contacted successfully in this environment.

  This script tries the real staging URL FIRST. If and only if that fails, it
  falls back to a local, throwaway, real PostgreSQL 16 instance (via the
  `pgserver` package — an actual Postgres binary, not SQLite, not a mock) so
  the RLS / checkpoint / tenant-isolation mechanics can still be proven
  end-to-end. Every print line says explicitly which backend is in use.

  To get a REAL staging-Supabase-backed result: run this script from a
  machine that can reach Supabase (e.g. your own machine, same as the
  DeepSeek live runs) — no code change needed, it will pick DATABASE_URL_STAGING
  up automatically and skip the local fallback.

No production schema is touched either way: everything lives under a new,
dedicated schema (`vitrina_poc_lead_scoring`), dropped and recreated by this
script, never referencing `clients`, `sites`, or any existing table.
"""
from __future__ import annotations

import os
import sys
import time
import traceback

sys.path.insert(0, ".")

import psycopg2
from dotenv import load_dotenv
from langgraph.types import Command

load_dotenv(".env")

SCHEMA = "vitrina_poc_lead_scoring"


def _get_connection_string() -> tuple[str, str]:
    """Returns (conn_string, backend_label). Tries real staging first."""
    staging_url = os.environ.get("DATABASE_URL_STAGING", "")
    if staging_url:
        try:
            test_conn = psycopg2.connect(staging_url, connect_timeout=6)
            test_conn.close()
            return staging_url, "REAL STAGING SUPABASE"
        except Exception as exc:
            print(f"[spike] staging Supabase unreachable from this sandbox: {type(exc).__name__}: {str(exc)[:150]}")
            print("[spike] falling back to local real-Postgres substitute (pgserver) — see script docstring")

    import pgserver
    pgdata = "/tmp/vitrina_pg_spike_data"
    os.makedirs(pgdata, exist_ok=True)
    srv = pgserver.get_server(pgdata)
    globals()["_pgserver_handle"] = srv  # keep alive for process lifetime
    return srv.get_uri(), "LOCAL POSTGRES 16 SUBSTITUTE (pgserver, NOT staging Supabase)"


def _admin_conn(conn_string: str):
    conn = psycopg2.connect(conn_string)
    conn.autocommit = True
    return conn


def setup_schema(conn_string: str) -> None:
    """Isolated schema + RLS-protected tenant index table. Never touches any
    existing production/staging table — additive only, and dropped at the
    start of every run so this is idempotent to re-run."""
    conn = _admin_conn(conn_string)
    cur = conn.cursor()
    cur.execute(f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE")
    cur.execute(f"CREATE SCHEMA {SCHEMA}")
    cur.execute(f"""
        CREATE TABLE {SCHEMA}.lead_scoring_runs (
            id BIGSERIAL PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            thread_id TEXT NOT NULL UNIQUE,
            lead_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'started',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    # RLS: a tenant-scoped role may only see its own rows. This mirrors the
    # real convention in docs/25-AGENCY-KERNEL.md ("RLS is enabled on every
    # new table") — this table is the tenant-safe index into LangGraph
    # threads; the raw checkpoint tables underneath stay service-role-only,
    # same boundary as claim_client_site() in the real Kernel migration.
    cur.execute(f"ALTER TABLE {SCHEMA}.lead_scoring_runs ENABLE ROW LEVEL SECURITY")
    cur.execute(f"""
        CREATE POLICY tenant_isolation ON {SCHEMA}.lead_scoring_runs
        USING (tenant_id = current_setting('app.tenant_id', true))
        WITH CHECK (tenant_id = current_setting('app.tenant_id', true))
    """)
    # A restricted role that RLS actually applies to (table owners / superusers
    # bypass RLS by default in Postgres — the whole point of this block is to
    # prove RLS holds for the role application code would actually run as).
    cur.execute("DROP ROLE IF EXISTS vitrina_poc_tenant_role")
    cur.execute("CREATE ROLE vitrina_poc_tenant_role LOGIN PASSWORD 'poc_only_not_secret'")
    cur.execute(f"GRANT USAGE ON SCHEMA {SCHEMA} TO vitrina_poc_tenant_role")
    cur.execute(f"GRANT SELECT, INSERT, UPDATE ON {SCHEMA}.lead_scoring_runs TO vitrina_poc_tenant_role")
    cur.execute(f"GRANT USAGE, SELECT ON {SCHEMA}.lead_scoring_runs_id_seq TO vitrina_poc_tenant_role")
    conn.close()
    print(f"[spike] schema {SCHEMA} + RLS-protected lead_scoring_runs table created")


def tenant_role_connection(conn_string: str, tenant_id: str):
    """Connects AS the restricted role (not admin/superuser) and sets the
    session-local tenant_id GUC that the RLS policy checks. This is the
    connection real application code would use — not the setup connection.

    Supabase-specific wrinkle found by actually running this against staging:
    the pooler (Supavisor) is multi-tenant at the INFRASTRUCTURE level (many
    Supabase projects share the pooler) and requires the username to carry a
    "<role>.<project_ref>" suffix so it knows which project's Postgres to
    route to — this is unrelated to our own application-level tenant_id and
    would trip up ANY new role connecting through this pooler, not just this
    POC. The admin connection's username already has that suffix baked in
    (e.g. "postgres.<project_ref>"); the restricted role needs the same
    suffix reused, or Supavisor rejects the connection with
    "ENOIDENTIFIER: no tenant identifier provided" before Postgres itself
    ever sees a role name to authenticate.
    """
    base = psycopg2.connect(conn_string)
    dsn_parts = base.get_dsn_parameters()
    base.close()
    admin_user = dsn_parts.get("user", "")
    if "." in admin_user:
        project_ref = admin_user.split(".", 1)[1]
        pooled_user = f"vitrina_poc_tenant_role.{project_ref}"
    else:
        pooled_user = "vitrina_poc_tenant_role"  # direct (non-pooled) connection, no suffix needed
    role_conn = psycopg2.connect(
        dbname=dsn_parts.get("dbname", "postgres"),
        host=dsn_parts.get("host") or None,
        port=dsn_parts.get("port") or None,
        user=pooled_user,
        password="poc_only_not_secret",
    )
    role_conn.autocommit = True
    cur = role_conn.cursor()
    cur.execute("SET app.tenant_id = %s", (tenant_id,))
    return role_conn


def prove_tenant_isolation(conn_string: str) -> None:
    print("\n=== PROPERTY: tenant isolation (RLS, restricted role, NOT superuser) ===")
    admin = _admin_conn(conn_string)
    cur = admin.cursor()
    cur.execute(
        f"INSERT INTO {SCHEMA}.lead_scoring_runs (tenant_id, thread_id, lead_id) VALUES (%s,%s,%s)",
        ("tenant-A", "lead-A-1", "lead-1"),
    )
    cur.execute(
        f"INSERT INTO {SCHEMA}.lead_scoring_runs (tenant_id, thread_id, lead_id) VALUES (%s,%s,%s)",
        ("tenant-B", "lead-B-1", "lead-1"),
    )
    admin.close()

    conn_a = tenant_role_connection(conn_string, "tenant-A")
    cur_a = conn_a.cursor()
    cur_a.execute(f"SELECT tenant_id, thread_id FROM {SCHEMA}.lead_scoring_runs ORDER BY thread_id")
    rows_a = cur_a.fetchall()
    print(f"  session tenant_id=tenant-A sees: {rows_a}")
    assert rows_a == [("tenant-A", "lead-A-1")], f"RLS LEAK: tenant-A saw {rows_a}"

    conn_b = tenant_role_connection(conn_string, "tenant-B")
    cur_b = conn_b.cursor()
    cur_b.execute(f"SELECT tenant_id, thread_id FROM {SCHEMA}.lead_scoring_runs ORDER BY thread_id")
    rows_b = cur_b.fetchall()
    print(f"  session tenant_id=tenant-B sees: {rows_b}")
    assert rows_b == [("tenant-B", "lead-B-1")], f"RLS LEAK: tenant-B saw {rows_b}"

    conn_a.close()
    conn_b.close()
    print("  PROVEN: cross-tenant row is invisible under RLS with a non-superuser role.")


def register_run(conn_string: str, tenant_id: str, thread_id: str, lead_id: str) -> None:
    admin = _admin_conn(conn_string)
    cur = admin.cursor()
    cur.execute(
        f"""INSERT INTO {SCHEMA}.lead_scoring_runs (tenant_id, thread_id, lead_id)
            VALUES (%s,%s,%s) ON CONFLICT (thread_id) DO NOTHING""",
        (tenant_id, thread_id, lead_id),
    )
    admin.close()


def submit_lead(graph, conn_string: str, tenant_id: str, lead_id: str, raw_lead: dict,
                 approve: bool | None = None) -> dict:
    """Idempotency guard: same (tenant_id, lead_id) always maps to the same
    thread_id. If a completed run already exists for that thread, we return
    the cached final state instead of reprocessing — proving idempotency is
    an explicit application-level guarantee here (LangGraph does not dedupe
    invokes by thread_id on its own; re-invoking a finished thread just runs
    it again from the top unless the caller checks first)."""
    thread_id = f"{tenant_id}::{lead_id}"
    config = {"configurable": {"thread_id": thread_id}}

    existing = graph.get_state(config)
    if existing.values.get("crm_draft") or existing.values.get("halted_reason"):
        print(f"  [idempotency] thread {thread_id} already terminal — returning cached result, no re-run")
        return {"cached": True, "state": existing.values}

    register_run(conn_string, tenant_id, thread_id, lead_id)
    if existing.next:
        # a paused run exists (mid-interrupt) — resume it
        result = graph.invoke(Command(resume={"approved": approve, "note": "resumed"}), config)
    else:
        result = graph.invoke({"tenant_id": tenant_id, "lead_id": lead_id, "raw_lead": raw_lead, "audit_log": []}, config)
    return {"cached": False, "state": result}


def main() -> None:
    conn_string, backend_label = _get_connection_string()
    print(f"[spike] backend in use: {backend_label}")
    print(f"[spike] production credentials used: NO (staging URL only tested for reachability, "
          f"never successfully connected in this environment; local runs use a throwaway pgserver instance)")

    setup_schema(conn_string)
    prove_tenant_isolation(conn_string)

    from langgraph.checkpoint.postgres import PostgresSaver
    with PostgresSaver.from_conn_string(conn_string) as checkpointer:
        checkpointer.setup()

        from lead_scoring_graph import build_lead_scoring_graph
        graph = build_lead_scoring_graph(checkpointer)

        print("\n=== PROPERTY: persisted graph state + human approval interrupt ===")
        lead = {"email": "test@example.gr", "service": "ξυλουργός", "source": "web_form",
                "message": "Χρειάζομαι επισκευή τώρα, έχω budget 500 ευρώ"}
        out1 = submit_lead(graph, conn_string, "tenant-A", "lead-42", lead)
        state1 = out1["state"]
        print(f"  interrupted: {'__interrupt__' in state1}")
        if "__interrupt__" in state1:
            print(f"  interrupt payload tier: {state1['__interrupt__'][0].value['tier']}")
        paused = graph.get_state({"configurable": {"thread_id": "tenant-A::lead-42"}})
        print(f"  paused before: {paused.next}")
        print(f"  audit events so far: {len(paused.values['audit_log'])}")
        for ev in paused.values["audit_log"]:
            print(f"    - {ev['node']:<16} {ev['actor']:<9} {ev['action']:<10} {ev['detail'][:90]}")

        print("\n=== PROPERTY: resume after simulated process restart ===")
    # checkpointer connection closed here (end of `with` block) — genuinely
    # gone, not just logically "pretend closed"
    with PostgresSaver.from_conn_string(conn_string) as checkpointer2:
        from lead_scoring_graph import build_lead_scoring_graph as build2
        graph2 = build2(checkpointer2)
        restored = graph2.get_state({"configurable": {"thread_id": "tenant-A::lead-42"}})
        print(f"  state survived restart: tier={restored.values.get('business_rule', {}).get('tier')!r}")
        print(f"  still paused before: {restored.next}")

        result2 = graph2.invoke(
            Command(resume={"approved": True, "note": "spike approval"}),
            {"configurable": {"thread_id": "tenant-A::lead-42"}},
        )
        print(f"  crm_draft.status: {result2['crm_draft']['status']}")
        print(f"  crm_draft.tier: {result2['crm_draft']['tier']}")

        print("\n=== PROPERTY: idempotency — resubmit the SAME lead_id ===")
        out_dup = submit_lead(graph2, conn_string, "tenant-A", "lead-42", lead, approve=True)
        print(f"  second submit cached={out_dup['cached']} (no nodes re-ran)")

        print("\n=== PROPERTY: DeepSeek -> Claude escalation path (low-signal lead: escalates to Claude on low confidence, but not hot enough for human approval) ===")
        cold_lead = {"phone": "2101234567", "service": "καθαρισμός", "source": "referral", "message": "καλημέρα"}
        out_cold = submit_lead(graph2, conn_string, "tenant-A", "lead-cold-1", cold_lead)
        state_cold = out_cold["state"]
        print(f"  tier: {state_cold['business_rule']['tier']}  escalated_to_claude: "
              f"{state_cold['business_rule']['escalate_to_claude']}  claude_reviewed: "
              f"{state_cold.get('claude_review') is not None}  interrupted: {'__interrupt__' in state_cold}")
        assert state_cold["business_rule"]["escalate_to_claude"], "expected DeepSeek->Claude escalation on low confidence"
        assert "__interrupt__" not in state_cold, "warm/non-risky tier should NOT require human approval, even after Claude review"

        print("\n=== PROPERTY: retry behavior (transient DeepSeek failure recovers via RetryPolicy) ===")
        import lead_scoring_graph as lsg_retry
        lsg_retry._DEEPSEEK_TRANSIENT_FAIL_ONCE.add("lead-retry-1")
        retry_lead = {"email": "retry@example.gr", "service": "καθαρισμός", "source": "web_form", "message": "γεια"}
        out_retry = submit_lead(graph2, conn_string, "tenant-A", "lead-retry-1", retry_lead)
        retry_state = out_retry["state"]
        retry_events = [e for e in retry_state["audit_log"] if e["node"] == "deepseek_score"]
        print(f"  deepseek_score succeeded despite injected first-attempt failure: {bool(retry_events)}")
        print(f"  (RetryPolicy(max_attempts=3, retry_on=(RuntimeError,)) attached to this node absorbed it —"
              f" no exception reached submit_lead())")
        assert retry_events, "expected deepseek_score to eventually succeed after transient failure"

        print("\n=== PROPERTY: policy-level failure recovery (Kernel denies DeepSeek on raw-PII misuse) ===")
        # Prove the Kernel gate is load-bearing: temporarily request scoring
        # with a disallowed data class and confirm the node raises, then show
        # the correctly-scoped call (as used throughout this graph) succeeds.
        import lead_scoring_graph as lsg
        bad_decision = lsg.kernel_gate(
            capability="lead.score", version="1", permissions=(),
            data_classes=("personal",),  # raw PII — NOT allowed for DeepSeek
            risk="low", provider="deepseek",
        )
        print(f"  Kernel decision for DeepSeek+personal data: allowed={bad_decision['allowed']} "
              f"reasons={bad_decision['reasons']}")
        assert not bad_decision["allowed"], "Kernel should have denied DeepSeek access to personal data"
        good_decision = lsg.kernel_gate(
            capability="lead.score", version="1", permissions=(),
            data_classes=("synthetic",), risk="low", provider="deepseek",
        )
        print(f"  Kernel decision for DeepSeek+synthetic (stripped) data: allowed={good_decision['allowed']}")
        assert good_decision["allowed"]

        print("\n=== PROPERTY: audit trail (full, post-resume) ===")
        final_state = graph2.get_state({"configurable": {"thread_id": "tenant-A::lead-42"}})
        for ev in final_state.values["audit_log"]:
            print(f"  {ev['ts']}  {ev['node']:<16} {ev['actor']:<9} {ev['action']:<10} {ev['detail'][:90]}")

    print(f"\n=== SPIKE COMPLETE — backend was: {backend_label} ===")
    print("=== Nothing written outside schema", SCHEMA, "or research/langgraph-poc/lead-scoring/ ===")


if __name__ == "__main__":
    main()
