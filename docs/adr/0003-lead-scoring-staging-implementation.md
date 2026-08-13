# ADR-0003: Lead Scoring — real staging implementation and comparison

**Status:** Implemented, not yet executed against staging (network-blocked
from the build sandbox — same limitation documented in ADR-0002; hand-off
required, see "Run this" below)
**Date:** 2026-08-13
**Builds on:** [0002-lead-scoring-langgraph-pilot.md](0002-lead-scoring-langgraph-pilot.md) (Accepted, staging-verified)

## What changed from the isolated pilot

The isolated pilot (`research/langgraph-poc/lead-scoring/`) used mocked
DeepSeek/Claude calls and an in-memory Kernel manifest stand-in. This is the
real version, in `src/lead_scoring/`:

| | Pilot (`research/langgraph-poc/lead-scoring/`) | Real (`src/lead_scoring/`) |
|---|---|---|
| DeepSeek | `_mock_deepseek_score()` | `providers.deepseek_score()` — real HTTP call, `DEEPSEEK_API_KEY`, JSON mode |
| Claude | `_mock_claude_review()` | `providers.claude_review()` — real `anthropic.Anthropic().messages.create()`, `ANTHROPIC_API_KEY`/`MODEL_CHEAP` from `src/config.py` |
| Kernel manifest | in-memory `AgentManifest` stand-in | read back from the REAL `agent_registry` row via `kernel_registry.fetch_registered_manifest()` — proves the registry round-trip, not just reconstructed from memory |
| Kernel installation | in-memory `{"status": "enabled", ...}` | read from the REAL `agent_installations` table via `kernel_registry.fetch_installation()` — returns `{}` since no row exists (see below) |
| Capability key | invented `lead.score`/`crm.draft` | the REAL, already-seeded `lead.capture`@1 (`db/migrations/0001_agency_kernel.sql`) — no new capability_definitions rows created |
| Checkpoint DB | throwaway schema, dropped every run | `vitrina_lead_scoring_runtime` schema in staging, persistent across runs |

## Deliberate incompleteness: no `agent_installations` row

`kernel_registry.register()` writes to `agent_registry` and `agent_capabilities`
only. It does **not** create an `agent_installations` row, because that table
requires a real `workspace_id` FK to `clients(id)` — there's no legitimate
reason for a pilot to touch a real (or synthetic) client row, and
`docs/25-AGENCY-KERNEL.md`'s own rollout checklist treats "enable" as a
separate, explicitly-approved step even in staging: *"Enable only after
explicit approval; staging before production."*

Consequence: running `run_staging_pilot.py` today will hit the real
`evaluate_policy()` and get correctly blocked at the first Kernel-gated node
(`deepseek_score`) with `blockers=['installation:missing']`. **This is the
expected, correct result of this step** — proof the fail-closed gate holds
against the real registry, not a bug. Enabling a real installation (to let a
lead actually flow end-to-end) is intentionally left as a separate decision.

## What's verified now vs. what awaits a real run

This build sandbox has no network route to Supabase, DeepSeek, or Anthropic's
API (same DNS-level block documented in ADR-0002 — confirmed directly, not
assumed). What I could verify here, without network:

- All modules import cleanly (no syntax/wiring errors): `providers.py`,
  `kernel_registry.py`, `graph.py`, `run_staging_pilot.py`.
- Pure business logic, tested directly against real functions (not
  hypothetically): `validate_node` → `enrich_classify_node` →
  `business_rules_node` → routing functions, confirmed **no PII field
  (`email`, `message`) reaches the DeepSeek-bound `features` dict**, and
  routing (`hot` tier + risk flag → `human_approval`, rejected approval →
  `halt_invalid`) is correct.

What requires your machine to actually confirm (same hand-off pattern as
ADR-0002's staging proof and the earlier DeepSeek live runs):

1. Real DeepSeek scoring call succeeds and returns a parseable score.
2. Real Claude review call succeeds on an escalated lead.
3. `kernel_registry.register()` succeeds against real staging and the
   manifest round-trips through `fetch_registered_manifest()` correctly.
4. The expected `installation:missing` block actually occurs (confirms the
   deliberate gap above holds in practice, not just in the code).
5. `PostgresSaver` against the new `vitrina_lead_scoring_runtime` schema
   persists correctly (same mechanic already proven in ADR-0002, on a new
   schema this time).

## Run this

```powershell
cd greek-smb-agent
$env:VITRINA_ENV="staging"
python -m src.lead_scoring.run_staging_pilot
```

Expected final output block: a `PermissionError` caught and reported as
"Kernel blocked execution (EXPECTED on a fresh run)" with
`blockers=['installation:missing']`. Anything else — a silent success, an
unrelated crash, or a different blocker — should come back to me before
treating this as validated.

## Comparison: custom state machine vs. LangGraph — real implementation

Structural facts, measured directly from the code that now exists (not
projected):

| Dimension | Custom (extrapolated from `social_engine.py`, per ADR-0002) | LangGraph (measured, real implementation) |
|---|---|---|
| Lines/complexity | Estimated 250-350 lines for state-machine plumbing alone (ADR-0002) | `src/lead_scoring/graph.py`: 246 lines total, including all business logic, Kernel gate wiring, and provider calls — orchestration wiring itself (node/edge declarations) is ~35 of those lines |
| Real provider integration cost | N/A (no prior implementation to compare) | `providers.py`: 108 lines for both DeepSeek and Claude clients combined, isolated from graph/orchestration code — swappable without touching `graph.py` |
| Kernel integration | Would need bespoke policy-check calls scattered through custom code, no enforced pattern | Every gated node calls the same `kernel_gate()` helper (14 lines) — one call shape reused 3 times, reading the REAL registry each time |
| Testability | Same concern as ADR-0002: DB required to test anything | Confirmed directly in this session: `validate_node`, `enrich_classify_node`, `business_rules_node`, and all routing functions tested with zero DB/network dependency — pure function calls, real assertions, real pass |
| Failure modes newly surfaced by building the real version | N/A | The Kernel's `installation:missing` block is itself a *discovered* failure mode this exercise forces you to confront explicitly (who enables agents, when, under what approval) — a custom implementation could easily skip this check silently and fail open instead of closed |

**Token cost and real timing:** cannot be measured from this sandbox (no
network). Once you run `run_staging_pilot.py`, the real DeepSeek/Claude calls
will report token usage in their raw API responses — worth capturing before
this pilot is considered fully closed out. Not fabricating numbers here.

**Maintenance burden:** unchanged from ADR-0002's assessment — one runtime
pattern (`kernel_gate()` + `RetryPolicy` + checkpointer) reusable across the
~6 planned domain graphs, versus re-deriving Kernel-check placement and retry
logic per workflow.

## No CRM connected, no production write, no production credential

- `crm_draft_node` returns `status="DRAFT_ONLY_NOT_WRITTEN"` — no code path in
  `src/lead_scoring/` calls any CRM API.
- `kernel_registry.py` and `run_staging_pilot.py` both call
  `env.require(env.DEV, env.STAGING)` before opening any connection — the
  project's own existing guard, not a new one. `PRODUCTION_*` credentials are
  never read by this package.
- `DATABASE_URL_STAGING` is read from `.env`, never logged or printed.
