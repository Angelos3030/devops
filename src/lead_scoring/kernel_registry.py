"""Registers and (per explicit, controlled, staging-only approval — see
docs/adr/0004-lead-scoring-staging-enablement.md) enables the Lead Scoring
pilot in the REAL Agency Kernel staging registry (`agent_registry` +
`agent_capabilities` + `agent_installations`, per db/migrations/
0001_agency_kernel.sql).

Two distinct, separately-callable operations, on purpose:
  - `register()` — upserts `agent_registry` + `agent_capabilities`. Safe to
    call any time; does not grant execution rights by itself.
  - `install()` / `disable()` — the explicit enablement/revocation step,
    scoped to exactly ONE dedicated synthetic staging workspace (created by
    `create_staging_workspace()`, never a real client). This is the step
    ADR-0003 deliberately left undone pending separate approval; ADR-0004
    documents that approval was given for staging only, never production.

Every function here requires VITRINA_ENV in {dev, staging} via
`src.env.require()` before opening a connection — production is structurally
unreachable (no PRODUCTION_* credentials are even read). Nothing in this
module ever reads a PRODUCTION_* credential or writes outside the dedicated
synthetic workspace created here.

Synthetic workspace convention reused from `scripts/seed_staging.py` (the
project's own existing QA-data convention, not invented here): fixed UUID in
the `aaaa000N-...` range, `qa-`-prefixed `@vitrina.test` email, Greek name
ending in "Δοκιμή" — so this row is automatically recognized as synthetic by
any existing staging tooling that already keys off that convention.
"""
from __future__ import annotations

import hashlib
import json
import os

import psycopg2
from dotenv import load_dotenv

from .. import env

load_dotenv()

AGENT_KEY = "lead_scoring_pilot"
AGENT_VERSION = "1"
CAPABILITY_KEY = "lead.capture"
CAPABILITY_VERSION = "1"


def _staging_conn_string() -> str:
    env.require(env.DEV, env.STAGING)
    url = os.environ.get("DATABASE_URL_STAGING", "")
    if not url:
        raise RuntimeError("DATABASE_URL_STAGING not set — cannot register against staging")
    return url


def manifest_dict() -> dict:
    """The real manifest this pilot registers — mirrors AgentManifest's
    contract shape (src/agency_kernel.py) as plain JSON for the registry row."""
    return {
        "agent_key": AGENT_KEY,
        "version": AGENT_VERSION,
        "name": "Lead Scoring Pilot",
        "purpose": "Score inbound leads (DeepSeek + deterministic rules), escalate to Claude "
                   "when confidence is low or risk is flagged, draft a CRM update for human approval.",
        "roi_hypothesis": "Faster, consistent lead triage reduces time-to-first-response on hot leads.",
        "success_metrics": ["time_to_first_response", "hot_lead_conversion_rate"],
        # Promoted from "draft" (ADR-0003) to "available" (ADR-0004) — staging
        # only, per explicit controlled-enablement approval. validate_manifest()
        # REQUIRES evals + revocation.procedure for "available" lifecycle; both
        # are supplied below, not skippable.
        "lifecycle": "available",
        "autonomy": "A1",
        "capabilities": [f"{CAPABILITY_KEY}@{CAPABILITY_VERSION}"],
        "permissions": ["crm.write"],
        "data_classes": ["public", "synthetic", "personal"],
        "cost": {"max_money_eur": "1", "max_tokens": 20000, "max_runtime_seconds": 300},
        # Real, runnable artifact (was a placeholder string with nothing
        # behind it): `tests/test_lead_scoring_offline_eval.py`, deterministic
        # coverage of business_rules_node's tier thresholds. Deliberately
        # narrow — does not eval DeepSeek/Claude judgment quality, which
        # needs a labeled dataset and is tracked separately as a pilot
        # success metric (human acceptance rate), not a pre-registration gate.
        "evals": ["tests/test_lead_scoring_offline_eval.py"],
        "revocation": {
            "procedure": "disable_staging.py sets agent_installations.status='disabled' for the "
                          "pilot workspace; evaluate_policy() blocks on the next call, no code change needed."
        },
    }


def register(dry_run: bool = False) -> dict:
    """Idempotent upsert into agent_registry + agent_capabilities. Returns the
    registered row's checksum. Never touches agent_installations/clients."""
    manifest = manifest_dict()
    checksum = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()

    if dry_run:
        return {"agent_key": AGENT_KEY, "version": AGENT_VERSION, "checksum": checksum, "dry_run": True}

    conn = psycopg2.connect(_staging_conn_string())
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO agent_registry
                (agent_key, version, name, purpose, lifecycle, manifest, manifest_checksum, registered_by)
            VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s)
            ON CONFLICT (agent_key, version) DO UPDATE SET
                name = EXCLUDED.name,
                purpose = EXCLUDED.purpose,
                lifecycle = EXCLUDED.lifecycle,
                manifest = EXCLUDED.manifest,
                manifest_checksum = EXCLUDED.manifest_checksum
            """,
            (AGENT_KEY, AGENT_VERSION, manifest["name"], manifest["purpose"], manifest["lifecycle"],
             json.dumps(manifest), checksum, "adr-0004-lead-scoring-staging-enablement"),
        )
        cur.execute(
            """
            INSERT INTO agent_capabilities (agent_key, agent_version, capability_key, capability_version)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            (AGENT_KEY, AGENT_VERSION, CAPABILITY_KEY, CAPABILITY_VERSION),
        )
        conn.commit()
    finally:
        conn.close()

    return {"agent_key": AGENT_KEY, "version": AGENT_VERSION, "checksum": checksum, "dry_run": False}


def fetch_registered_manifest():
    """Reads back the manifest actually stored in agent_registry (not the
    local manifest_dict() function) and validates it through the real
    AgentManifest.from_dict() — proving the registry round-trip, not just
    reconstructing the manifest from memory. Raises if register() hasn't
    been run yet."""
    from ..agency_kernel import AgentManifest  # local import avoids a cycle at module load

    conn = psycopg2.connect(_staging_conn_string())
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT manifest FROM agent_registry WHERE agent_key = %s AND version = %s",
            (AGENT_KEY, AGENT_VERSION),
        )
        row = cur.fetchone()
        if not row:
            raise RuntimeError(
                f"{AGENT_KEY}@{AGENT_VERSION} not found in agent_registry — run register() first"
            )
        return AgentManifest.from_dict(row[0])
    finally:
        conn.close()


# --- Dedicated synthetic staging workspace (never a real client) ---------
STAGING_WORKSPACE_ID = "aaaa0007-0000-4000-8000-000000000007"  # next free id after seed_staging.py's aaaa0001-0006
STAGING_WORKSPACE_EMAIL = "qa-leadscoring@vitrina.test"


def create_staging_workspace() -> str:
    """Idempotent insert of ONE dedicated synthetic client row, following the
    exact convention scripts/seed_staging.py already uses for QA data (fixed
    uuid range, qa- email prefix, @vitrina.test domain, Greek 'Δοκιμή' name)
    so existing staging tooling recognizes it as synthetic automatically.
    Never touches any other client row."""
    conn = psycopg2.connect(_staging_conn_string())
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO clients (id, name, business_type, city, status, email, phone, plan)
            VALUES (%s, %s, %s, %s, 'trial', %s, %s, 'starter')
            ON CONFLICT (id) DO NOTHING
            """,
            (STAGING_WORKSPACE_ID, "Lead Scoring Δοκιμή", "ξυλουργός", "Αθήνα",
             STAGING_WORKSPACE_EMAIL, "2100000007"),
        )
        conn.commit()
    finally:
        conn.close()
    return STAGING_WORKSPACE_ID


def install(*, granted_permissions: list[str], budget_limits: dict) -> dict:
    """The explicit enablement step. Scoped to STAGING_WORKSPACE_ID only —
    never accepts an arbitrary workspace_id, so this function cannot
    accidentally enable the agent for a real client no matter how it's
    called. Minimum permissions: pass only what the manifest actually
    declares (['crm.write']), not a broader set."""
    env.require(env.DEV, env.STAGING)
    conn = psycopg2.connect(_staging_conn_string())
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO agent_installations
                (workspace_id, agent_key, agent_version, status, granted_permissions,
                 budget_limits, installed_by)
            VALUES (%s, %s, %s, 'enabled', %s::jsonb, %s::jsonb, %s)
            ON CONFLICT (workspace_id, agent_key, agent_version) DO UPDATE SET
                status = 'enabled',
                granted_permissions = EXCLUDED.granted_permissions,
                budget_limits = EXCLUDED.budget_limits,
                updated_at = now(),
                revoked_at = NULL,
                revocation_reason = NULL
            """,
            (STAGING_WORKSPACE_ID, AGENT_KEY, AGENT_VERSION,
             json.dumps(granted_permissions), json.dumps(budget_limits),
             "adr-0004-lead-scoring-staging-enablement"),
        )
        conn.commit()
    finally:
        conn.close()
    return {"workspace_id": STAGING_WORKSPACE_ID, "status": "enabled",
            "granted_permissions": granted_permissions, "budget_limits": budget_limits}


def disable(reason: str = "manual revocation") -> dict:
    """Immediate revocation — requirement #9 (must be disable-able
    immediately). Idempotent; safe to call even if never installed."""
    env.require(env.DEV, env.STAGING)
    conn = psycopg2.connect(_staging_conn_string())
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE agent_installations
            SET status = 'disabled', revoked_at = now(), revocation_reason = %s, updated_at = now()
            WHERE workspace_id = %s AND agent_key = %s AND agent_version = %s
            """,
            (reason, STAGING_WORKSPACE_ID, AGENT_KEY, AGENT_VERSION),
        )
        affected = cur.rowcount
        conn.commit()
    finally:
        conn.close()
    return {"workspace_id": STAGING_WORKSPACE_ID, "status": "disabled", "rows_affected": affected}


def registry_state() -> dict:
    """Exact current registry/installation state, for the enablement report."""
    conn = psycopg2.connect(_staging_conn_string())
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT lifecycle, manifest_checksum, registered_at FROM agent_registry "
            "WHERE agent_key = %s AND version = %s",
            (AGENT_KEY, AGENT_VERSION),
        )
        reg = cur.fetchone()
        cur.execute(
            "SELECT status, granted_permissions, budget_limits, installed_at, updated_at "
            "FROM agent_installations WHERE workspace_id = %s AND agent_key = %s AND agent_version = %s",
            (STAGING_WORKSPACE_ID, AGENT_KEY, AGENT_VERSION),
        )
        inst = cur.fetchone()
        cur.execute("SELECT id, name, email, status FROM clients WHERE id = %s", (STAGING_WORKSPACE_ID,))
        ws = cur.fetchone()
    finally:
        conn.close()
    return {
        "registry": {"lifecycle": reg[0], "checksum": reg[1][:16], "registered_at": str(reg[2])} if reg else None,
        "installation": ({"status": inst[0], "granted_permissions": inst[1], "budget_limits": inst[2],
                           "installed_at": str(inst[3]), "updated_at": str(inst[4])} if inst else None),
        "workspace": {"id": ws[0], "name": ws[1], "email": ws[2], "status": ws[3]} if ws else None,
    }


def fetch_installation(workspace_id: str | None) -> dict:
    """Reads the real agent_installations row for (workspace_id, AGENT_KEY,
    AGENT_VERSION), if any. Returns {} (→ Kernel blocks with
    'installation:missing') when workspace_id is None or no row exists — this
    pilot never creates that row itself, by design (see module docstring)."""
    if not workspace_id:
        return {}
    conn = psycopg2.connect(_staging_conn_string())
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT status, granted_permissions, budget_limits
            FROM agent_installations
            WHERE workspace_id = %s AND agent_key = %s AND agent_version = %s
            """,
            (workspace_id, AGENT_KEY, AGENT_VERSION),
        )
        row = cur.fetchone()
        if not row:
            return {}
        status, granted_permissions, budget_limits = row
        return {"status": status, "granted_permissions": granted_permissions, "budget_limits": budget_limits}
    finally:
        conn.close()
