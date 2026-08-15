# ADR-0005: Lead Scoring — limited production pilot plan

**Status:** Plan only. Nothing in this document has been executed.
**Date:** 2026-08-13
**Builds on:** [0004-lead-scoring-staging-enablement.md](0004-lead-scoring-staging-enablement.md)
(verdict: READY FOR LIMITED PRODUCTION PILOT, staging-confirmed 2026-08-13).
**Scope:** This is a plan. It does not enable production. Every step below
requires a separate, explicit go-ahead before being run, per standing
instruction.

## 0. What changed since ADR-0004, before this plan was written

Per the four pre-production controls requested, all four are now done and
verified in staging:

1. **Models pinned.** `src/lead_scoring/providers.py` now defaults to
   `DEEPSEEK_MODEL=deepseek-v4-flash` and `CLAUDE_MODEL=claude-haiku-4-5-20251001`
   — explicit identifiers, not the floating aliases `deepseek-chat` /
   `claude-haiku-4-5`. Both independently overridable via env var
   (`DEEPSEEK_MODEL_CHEAP`, `LEAD_SCORING_CLAUDE_MODEL`), deliberately
   decoupled from `cfg.MODEL_CHEAP` so a future site-copy/brand-caption model
   change elsewhere in the codebase can't silently change this pilot's
   behavior or cost.
2. **DeepSeek mapping verified, not assumed.** Confirmed against DeepSeek's
   own official changelog (api-docs.deepseek.com/updates, 2026-04-24 entry):
   `deepseek-chat` was an intentional legacy alias for DeepSeek-V4-Flash's
   non-thinking mode, scheduled for discontinuation 2026-07-24 (already
   past). Pinning to `deepseek-v4-flash` directly removes the dependency on
   an already-deprecated name.
3. **Real Kernel eval artifact registered.** The manifest's `evals` field
   (`src/lead_scoring/kernel_registry.py`) now points to
   `tests/test_lead_scoring_offline_eval.py` — a real, passing, deterministic
   test (`python3 -m unittest tests.test_lead_scoring_offline_eval -v` → OK,
   2 tests) covering `business_rules_node`'s tier thresholds — not the
   placeholder string `"lead_scoring_offline_eval_v1"` that had nothing
   behind it. Scope note: this evals the deterministic business-rule layer
   only, not DeepSeek/Claude judgment quality — that's tracked as a pilot
   success metric (§5), not a pre-registration gate, since it needs live
   pilot data to measure meaningfully.
4. **Stray checkpoint rows — script written, not yet run.**
   `research/langgraph-poc/lead-scoring/cleanup_stray_public_checkpoints.py`
   identifies and (with double confirmation, staging-only via
   `env.require_destructive()`) deletes the `public`-schema checkpoint rows
   left over from the pre-fix ADR-0002/0003 runs. Not run yet — it's your
   call whether to run it before or after the pilot; it's cosmetic
   (`public` isn't queried by anything else) and does not block production
   readiness either way.

Authoritative pricing confirmed and wired in (`src/lead_scoring/staging_e2e_report.py`):
DeepSeek V4-Flash $0.14/MTok in (cache miss) / $0.28/MTok out
([api-docs.deepseek.com/quick_start/pricing](https://api-docs.deepseek.com/quick_start/pricing),
checked 2026-08-13); Claude Haiku 4.5 $1/MTok in / $5/MTok out
([platform.claude.com/docs/en/about-claude/pricing](https://platform.claude.com/docs/en/about-claude/pricing),
checked 2026-08-13). With pinned models, `cost_report.status` now resolves
`VERIFIED` (confirmed locally: €0.00061 for the same hot-lead usage profile
measured in ADR-0004 — actually *cheaper* than the old unverified estimate,
since DeepSeek's real V4-Flash rate is about half what the stale placeholder
assumed). DeepSeek's pricing page notes a "significant" increase is planned
with no fixed date — re-check this rate before trusting any multi-month
projection built on it.

## 1. Pilot scope

**Tenant(s): left for you to name explicitly.** I don't have visibility into
your real client roster, so I can't pick one — this is the one item in this
plan that is a business decision, not an engineering one. Suggested
selection criteria, if useful: a client who (a) already gets inbound leads
regularly enough to produce meaningful signal within the pilot window, (b)
you can personally reach if something looks wrong, and (c) is not
currently mid-complaint or high-friction — a pilot is not the moment to
introduce a new automated system to a strained relationship. Recommend
**exactly one** workspace to start, per ADR-0001's own migration-path
discipline ("do not batch-migrate").

**Time-boxed, not open-ended.** Recommend a defined window — e.g. 2 weeks or
50 leads, whichever comes first — with an explicit checkpoint before any
extension, not an implicit "keep running until someone objects."

**Numeric limits** (enforced at the `agent_installations.budget_limits`
level, same mechanism already proven in staging):

| Limit | Recommended pilot value | Where enforced |
|---|---|---|
| Max leads processed | 50 (or time-box, whichever first) | Applied externally — Kernel doesn't count "leads," see §6 monitoring query |
| Daily token budget | 20,000 tokens/day (≈ 130 hot leads/day headroom at measured ~150 tokens/lead combined) | Not yet a Kernel-native daily counter — see §6, requires a monitoring query, not a hard block, until a real daily-budget field exists |
| Per-call budget | `max_money_eur=0.50, max_tokens=5000, max_runtime_seconds=120` (unchanged from staging) | `agent_installations.budget_limits`, enforced by `evaluate_policy()` every call |
| Max retries | 3 attempts per node (unchanged — `RetryPolicy(max_attempts=3)` in `graph.py`) | Code-level, already in place |
| Human approval | Required before any `crm.write` — already enforced (`human_approval` node gates `crm_draft`, per `route_after_claude`/`route_after_approval`) | Graph-level, already in place |
| Kill switch | `kernel_registry.disable()`-equivalent for production — see §4 | New, see below |

**Note on the daily-budget gap:** the Kernel's `CostEnvelope` enforces a
budget *per call*, not a running daily/monthly total — there is currently no
code path that sums spend across calls and blocks once a daily cap is hit.
For a pilot capped at 50 leads total, this gap is low-risk (worst case is
bounded by 50 × €0.50 = €25, far above the realistic €0.03 actual cost at
measured rates). It should NOT be treated as solved for a larger rollout —
flagged here, not fixed, since building real spend-accumulation is
out of scope for "limited pilot" and would be premature engineering before
real usage data exists.

## 2. Exact config changes

All of the below are Railway (production server) environment variables, not
local `.env` — `src/env.py`'s `_ON_SERVER` gate means these are structurally
unreachable from a laptop even if set locally, by design.

| Variable | Value | Notes |
|---|---|---|
| `VITRINA_ENV` | `production` | Already presumably set on the Railway production service — confirm, don't assume. |
| `DATABASE_URL_PRODUCTION` | (existing production Supabase connection string) | Already must exist for the rest of the app to function — no new credential. |
| `DEEPSEEK_API_KEY` | production-tier DeepSeek key | **Verify this is NOT the same key used for `research_worker.py`'s discovery passes** — separate quota/budget tracking is cleaner, and the Kernel's DeepSeek data-class gate is a policy control, not a billing boundary. |
| `AI_API_KEY` (or `ANTHROPIC_API_KEY`) | production Anthropic key | Same key `src/ai.py` already uses for website/brand copy — no new credential, already governed by existing production access. |
| `DEEPSEEK_MODEL_CHEAP` | *(leave unset — default `deepseek-v4-flash` is already pinned in code)* | Only set this to override, and only after re-verifying against DeepSeek's changelog. |
| `LEAD_SCORING_CLAUDE_MODEL` | *(leave unset — default `claude-haiku-4-5-20251001` is already pinned)* | Same caveat. |

**No new config surface beyond the above.** No changes to `src/config.py` are
required — `src/lead_scoring/` intentionally reads `DEEPSEEK_API_KEY`
directly (module docstring, `providers.py`) precisely so this pilot's
credential is separable from the rest of the app's AI config.

## 3. Exact production records to create/update

**Prerequisite check (read-only, do first):** confirm migration
`db/migrations/0001_agency_kernel.sql` has actually been applied to
production — `SELECT to_regclass('public.agent_registry');` should return a
non-null value. I cannot verify this myself (no production credential
reaches this sandbox); do not assume it mirrors staging just because
staging has it.

**New code required before any of the below can run** —
`src/lead_scoring/kernel_registry.py`'s `register()`/`install()`/`disable()`/
`registry_state()` all currently call `env.require(env.DEV, env.STAGING)`
and hardcode `_staging_conn_string()` — they structurally cannot target
production as written (this is intentional per ADR-0004's own scope
discipline, not an oversight). A production-safe equivalent needs:
- Its own connection resolver reading `DATABASE_URL_PRODUCTION` via
  `env.supabase()`/`env._pick()`, gated by `env.require(env.PRODUCTION)`.
- A `workspace_id` parameter for `install()`/`disable()` (unlike the
  staging version, which is deliberately hardcoded to one synthetic
  workspace) — but validated against an explicit allow-list of the pilot
  tenant(s) named in §1, not an arbitrary caller-supplied UUID, to preserve
  the same "cannot accidentally enable for the wrong client" property the
  staging version has by construction.

This is a deliberate, reviewable, small diff — building it is part of what
"explicit production approval" should approve, not something to pre-build
speculatively. Once approved, the records it would create/update are:

1. **`agent_registry`** — one row, `agent_key='lead_scoring_pilot'`,
   `version='1'`, `lifecycle='available'`, manifest identical in shape to
   the staging one (`kernel_registry.manifest_dict()`) with the now-real
   `evals=["tests/test_lead_scoring_offline_eval.py"]`.
2. **`agent_capabilities`** — one row linking `lead_scoring_pilot@1` to
   `lead.capture@1` (capability must already exist in
   `capability_definitions` in production — confirm, don't assume; it's
   seeded by the same migration as the registry table).
3. **`workspace_entitlements`** — one row for the chosen pilot tenant,
   `capability_key='lead.capture'`, `capability_version='1'`,
   `status='granted'`, `source='trial'` (matches the CHECK constraint's
   allowed values — `'trial'` is the honest label for a time-boxed pilot).
   **This table is not touched anywhere in the current staging code** —
   `evaluate_policy()`'s entitlements check (per `src/agency_kernel.py`)
   requires it; the staging pilot's `install()` never needed it because
   its test harness passes entitlements directly in-process. Production
   must actually populate this table for the real policy check to pass.
4. **`agent_installations`** — one row, `workspace_id=<chosen tenant's
   clients.id>`, `agent_key='lead_scoring_pilot'`, `agent_version='1'`,
   `status='enabled'`, `granted_permissions=["crm.write"]`,
   `budget_limits` per §1's table, `installed_by='adr-0005-production-pilot'`.

**Nothing else is created or modified.** No other client's rows, no schema
changes (migration 0001 either already applied or is itself a separate,
reviewable prerequisite step), no CRM connection (still draft-only —
`crm_draft_node` has no code path to a real CRM write in the current graph;
wiring a real CRM is explicitly out of scope for this pilot, per the
original ADR-0002 instruction that has never been revisited).

## 4. Rollback / disable procedure

**Immediate kill switch:**
```sql
UPDATE agent_installations
SET status = 'disabled', revoked_at = now(), revocation_reason = 'pilot rollback'
WHERE workspace_id = '<pilot tenant clients.id>'
  AND agent_key = 'lead_scoring_pilot' AND agent_version = '1';
```
Takes effect on the very next call — `evaluate_policy()` checks
installation status live, no cache, no deploy needed (same mechanism
proven in staging negative test #3, `disabled_agent`). This is the same
one-line change `disable_staging.py` already performs for staging; the
production version is the same UPDATE against `DATABASE_URL_PRODUCTION`.

**Full rollback (if disabling isn't enough — e.g. a manifest defect):**
1. Run the kill switch above first (stops new executions immediately).
2. `UPDATE agent_registry SET lifecycle = 'draft' WHERE agent_key =
   'lead_scoring_pilot' AND version = '1';` — demotes below the
   `lifecycle='available'` threshold `evaluate_policy()` requires, a second
   independent block beyond the installation status.
3. In-flight interrupted runs (a lead paused at `human_approval` when the
   kill switch is hit) are safe by construction: they sit in the
   checkpointer with no CRM write, and simply never get resumed if nobody
   calls `Command(resume=...)` — no cleanup needed, no partial state, no
   orphaned write. Confirm none are stuck mid-flight via the audit query in
   §6 before considering rollback complete.
4. No code deploy is required for either step — both are data-only changes,
   same class of action already proven safe in staging.

## 5. Safety invariants (all already proven in staging, must hold identically in production)

- No autonomous irreversible CRM action — `crm_draft_node` has no CRM-write
  code path at all right now; this holds by construction, not by policy
  alone.
- Human approval before any `crm.write`-permissioned step, for hot-tier or
  risk-flagged leads — `route_after_claude`/`human_approval` node, unchanged.
- Full audit trail — `_audit()` helper writes one event per node transition;
  confirmed accurate for both halt paths after the `halted_reason` fix.
- Idempotent writes — proven under real concurrency in the ADR-0004 rerun
  (5 concurrent duplicate submits → exactly 1 effective run). Caveat
  already flagged there: the guard is application-level
  (`get_state`-then-`invoke`), not a DB-level unique constraint — acceptable
  for a limited pilot's traffic volume, worth hardening before a larger
  rollout.
- Tenant isolation — proven under concurrent cross-tenant load in the same
  rerun; production installs are additionally hard-scoped by the
  allow-list requirement in §3's code-change note.
- PII stripped before DeepSeek — `enrich_classify_node` only ever passes the
  derived `features` dict (category/length/keyword-count/budget-boolean) to
  DeepSeek, never `raw_lead`; enforced independently by the Kernel's
  `deepseek_data_policy` check (proven fail-closed in staging negative test
  #1).

## 6. Success metrics — define before enabling, measure from the audit trail

All of these are queryable directly from `agent_tasks`/`agent_runs`/
`agency_audit_log`/`agency_events` (per `db/migrations/0001_agency_kernel.sql`)
plus the Lead Scoring graph's own `audit_log`/`usage_log` state fields —
no new instrumentation needed, only queries against what already gets
written on every run.

| Metric | How measured | Target for this pilot (proposed, confirm before enabling) |
|---|---|---|
| Scoring accuracy / human acceptance rate | % of `human_approval` events with `action='approved'` vs `'rejected'`, for hot-tier leads | ≥ 80% approved — below this, DeepSeek/Claude's judgment isn't trustworthy enough yet |
| False-positive rate (wrongly flagged hot/risk) | % of `approved=True` reviews where the human note indicates the tier was overstated (requires reading `agent_approvals.reason`/note text — no numeric field exists yet, this is a manual read for a 50-lead pilot, not a query) | No fixed target — track and report, since this is the metric this pilot exists to establish |
| False-negative rate (missed a hot lead) | Cannot be measured from pipeline data alone — requires comparing against leads that arrived but never entered the pipeline. Needs a manual cross-check against the CRM's actual inbound lead list for the pilot tenant during the window. | Flag any known miss immediately, don't wait for the pilot to end |
| Escalation rate to Claude | `count(claude_review audit events) / count(total leads)` | Expected 30-60% given `escalate_to_claude = confidence < 0.75 or tier == "hot"` — track actual vs. this expectation |
| Average cost per lead | `sum(usage_log costs, VERIFIED status only) / count(leads)` | ~€0.0006/lead at measured rates (§0) — flag if actual diverges by >2x, since that would mean the pinned-model assumption stopped holding |
| Latency | `total_wall_seconds` per run, from `agency_events`/graph audit timestamps | ≤ 10s p95 (measured baseline: 4.4-4.8s for a hot lead requiring both models) |
| Retry rate | `count(RetryPolicy attempts > 1) / count(total node executions)` | No fixed target — track; a high rate would indicate a real DeepSeek/Claude reliability problem worth escalating to those providers |
| Policy denials | `count(agency_audit_log entries with decision='denied')` | Expect ~0 for the pilot tenant specifically (denials were staging negative-test behavior, not expected production behavior) — any denial for the pilot tenant is a stop-and-investigate signal, not routine noise |
| Audit anomalies | Any `halted_reason` value outside the known set (`human_rejected`, `validation_failed`) | 0 — an unknown halt reason means a code path wasn't accounted for |

**Suggested monitoring query** (read-only, safe to run anytime against
production once the pilot is live):
```sql
SELECT
  date_trunc('day', a.created_at) AS day,
  count(*) FILTER (WHERE a.action = 'approved') AS approved,
  count(*) FILTER (WHERE a.action = 'rejected') AS rejected,
  count(*) FILTER (WHERE a.node = 'claude_review') AS claude_escalations,
  count(*) FILTER (WHERE a.node = 'halt_invalid') AS halts
FROM agency_audit_log a
JOIN agent_tasks t ON t.id = a.task_id
WHERE t.agent_key = 'lead_scoring_pilot'
GROUP BY 1 ORDER BY 1;
```
(Exact column names should be double-checked against production's actual
`agency_audit_log`/`agent_tasks` shape before first use — this mirrors the
migration file's schema but hasn't been run against production data.)

## 7. Pilot success / failure thresholds

**Success — continue/expand:**
- Human acceptance rate ≥ 80% across the pilot window.
- Zero unauthorized CRM writes (should be structurally impossible — see §5
  — but explicitly checked as a hard gate, not assumed).
- Zero audit anomalies (unknown halt reasons, missing audit events for any
  completed run).
- Cost within 2x of the €0.0006/lead baseline.
- At least one real false-negative check performed against the tenant's
  actual CRM lead list (not skipped for convenience).

**Failure — disable and re-evaluate before any retry:**
- Human acceptance rate < 60%, OR
- Any unauthorized/unapproved CRM write occurs (should be impossible;
  treat as a stop-everything defect if it ever happens), OR
- Any policy denial for the pilot tenant that isn't immediately explained, OR
- Model mismatch detector fires unexpectedly after pinning (would mean
  DeepSeek or Anthropic changed a pinned model ID's behavior underneath a
  fixed identifier — re-verify before continuing).

**Ambiguous zone (60-80% acceptance, or any single metric borderline):**
extend the pilot window with the same tenant rather than expanding to a
second tenant — more data before a broader decision, not a coin flip.

## Explicit non-goals of this plan

- This plan does not enable production. No record in §3 has been created.
- No new production-targeting code (the `kernel_registry` production
  equivalent described in §3) has been written — it is scoped, not built.
- No tenant has been chosen — that decision is yours to make (§1).
- No second workflow is implied — this stays scoped to Lead Scoring only,
  per ADR-0001's explicit "do not batch-migrate" migration path.

**Stopping here, per standing instruction. Awaiting your explicit approval
before any step in §2, §3, or the production-targeting code change described
in §3 is executed.**
