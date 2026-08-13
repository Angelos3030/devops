"""Registers the Lead Scoring pilot into the REAL Agency Kernel staging
registry (`agent_registry` + `agent_capabilities`, per db/migrations/
0001_agency_kernel.sql) — and stops there, deliberately.

What this does:
  - Upserts one row into `agent_registry` (lifecycle='draft').
  - Links it to the ALREADY-SEEDED `lead.capture`@1 capability in
    `agent_capabilities` — no new capability_definitions row is created; the
    real catalog already has `lead.capture` ("Capture and qualify inbound
    leads", risk=medium), which is what this pilot actually does.

What this deliberately does NOT do, and why:
  - Does NOT insert into `agent_installations`. That table requires a real
    `workspace_id` FK to `clients(id)` — there is no legitimate reason for
    this pilot to touch a real client row, synthetic or otherwise, and
    `docs/25-AGENCY-KERNEL.md`'s own rollout checklist treats "enable" as a
    separate, explicitly-approved step even in staging ("Enable only after
    explicit approval; staging before production"). Without an installation
    row, `evaluate_policy()` correctly refuses to execute anything for this
    agent — that is the intended, current state, not a bug.
  - Does NOT touch `workspace_entitlements`, `clients`, or any other table.

Every function here requires VITRINA_ENV in {dev, staging} via
`src.env.require()` before opening a connection — production is structurally
unreachable (no PRODUCTION_* credentials are even read).
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
        "lifecycle": "draft",  # NOT "available" — promotion is a separate, explicit decision
        "autonomy": "A1",
        "capabilities": [f"{CAPABILITY_KEY}@{CAPABILITY_VERSION}"],
        "permissions": ["crm.write"],
        "data_classes": ["public", "synthetic", "personal"],
        "cost": {"max_money_eur": "1", "max_tokens": 20000, "max_runtime_seconds": 300},
        "evals": [],  # deliberately empty — "available" lifecycle would require these; this is "draft"
        "revocation": {},
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
            VALUES (%s, %s, %s, %s, 'draft', %s::jsonb, %s, %s)
            ON CONFLICT (agent_key, version) DO UPDATE SET
                name = EXCLUDED.name,
                purpose = EXCLUDED.purpose,
                manifest = EXCLUDED.manifest,
                manifest_checksum = EXCLUDED.manifest_checksum
            """,
            (AGENT_KEY, AGENT_VERSION, manifest["name"], manifest["purpose"],
             json.dumps(manifest), checksum, "adr-0002-lead-scoring-pilot"),
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
