# ADR-0004: Lead Scoring — controlled staging enablement

**Status:** Complete. Two staging runs (2026-08-13): first run confirmed
positive E2E + 5/6 negative tests and surfaced a `halted_reason` audit-trail
bug; second run (after fix + concurrency/cost-telemetry additions)
reconfirmed the fix and passed all 10 steps including concurrency-under-load
testing, with zero assertion failures. **Verdict: READY FOR LIMITED
PRODUCTION PILOT** (see bottom). Production has NOT been enabled — awaiting
separate explicit approval.
**Date:** 2026-08-13
**Builds on:** [0003-lead-scoring-staging-implementation.md](0003-lead-scoring-staging-implementation.md)
**Scope:** Staging only. This ADR does not enable, promote, or touch
production in any way — see "Explicit non-goals" below.

## What this authorizes (and what it doesn't)

The user explicitly approved, staging-only: promoting the manifest from
`draft` to `available`, installing (enabling) the agent for exactly one
dedicated synthetic workspace, minimum permissions, tight budget limits, and
running one real E2E scenario plus six negative tests. Production remains
completely untouched — no `PRODUCTION_*` credential is read anywhere in
`src/lead_scoring/`, and every enablement function additionally requires
`VITRINA_ENV` in `{dev, staging}` via `src/env.py`'s existing guard before
opening a connection.

## Two real bugs found and fixed during offline review, before any handoff

Reviewing the enablement code before asking the user to run it (rather than
finding out from a failed live run) surfaced two genuine defects:

1. **`register()`'s INSERT hardcoded `'draft'`** regardless of
   `manifest_dict()`'s actual `lifecycle` value. Promoting the manifest to
   `available` in `manifest_dict()` would have silently done nothing in the
   database — the registry row would stay `draft` forever. Fixed: the INSERT
   now uses `manifest["lifecycle"]` and the `ON CONFLICT` clause updates
   `lifecycle` too.
2. **`kernel_gate()` never set an explicit per-call budget.** `TaskRequest`'s
   default `CostEnvelope` has `max_runtime_seconds=300`, but
   `enable_staging.py`'s installation deliberately caps
   `budget_limits.max_runtime_seconds=120` (a tight, pilot-appropriate
   ceiling). Without a fix, `evaluate_policy()` would have returned
   `runtime_budget_exceeded` on every single call — the agent would still be
   permanently blocked even after correct enablement, for an unrelated
   reason nobody asked for. Fixed: `kernel_gate()` now passes an explicit,
   tight `CostEnvelope(max_runtime_seconds=60)` per call.

Verified offline (no network needed — pure `evaluate_policy()` call against
an in-memory reconstruction of the exact manifest/installation shapes the
real enablement scripts produce):

```
allowed= True reasons= ('autonomy_a1',)
CONFIRMED: enabled installation + fixed budget -> Kernel ALLOWS execution
```

`autonomy_a1` remains present as an **approval reason**, not a blocker — the
manifest's `A1` autonomy means execute-mode calls still carry an approval
annotation even when otherwise allowed, which is correct and matches the
`human_approval` node already in the graph for the cases that need it.

## Correction to ADR-0002/0003's isolation claim

`PostgresSaver` has no schema parameter — it writes checkpoint tables
(`checkpoints`, `checkpoint_blobs`, `checkpoint_writes`) to whichever schema
is first in the connection's `search_path`. Neither `pg_spike.py` (ADR-0002)
nor `run_staging_pilot.py` (ADR-0003) ever set `search_path`, so despite
creating an isolated schema, LangGraph's own tables actually landed in
`public` both times — only the separate RLS proof table
(`vitrina_poc_lead_scoring.lead_scoring_runs`) was genuinely isolated.
`staging_e2e_report.py` (this ADR) fixes this by setting
`options=-csearch_path=vitrina_lead_scoring_runtime,public` on its connection
string, so this run's checkpoint tables are truly isolated. The earlier runs'
`public`-schema checkpoint rows are harmless (small, clearly-named
`thread_id`s like `tenant-A::lead-42`) but worth a manual cleanup pass later
if `public` needs to stay clean — not done automatically here, since deleting
rows from a shared schema without being asked crosses into destructive
territory this ADR doesn't need to touch.

## Enablement mechanics (`src/lead_scoring/enable_staging.py`)

1. `kernel_registry.register()` — promotes `agent_registry` row to
   `lifecycle='available'` (now with real `evals`/`revocation.procedure`, as
   `validate_manifest()` requires for that lifecycle — not skippable).
2. `kernel_registry.create_staging_workspace()` — idempotent insert of ONE
   synthetic `clients` row, following `scripts/seed_staging.py`'s own
   existing QA-data convention exactly (fixed uuid `aaaa0007-...`, next free
   id after that script's `aaaa0001`-`aaaa0006`; `qa-leadscoring@vitrina.test`
   email; Greek "Δοκιμή" name) — so existing staging tooling recognizes it as
   synthetic automatically, and it's never confused with a real customer.
3. `kernel_registry.install()` — the actual enablement, hard-scoped to
   `STAGING_WORKSPACE_ID` only (the function does not accept an arbitrary
   workspace_id parameter — it cannot be called against a real client no
   matter how it's invoked). Grants exactly `["crm.write"]` (nothing broader
   than the manifest declares) with tight budget limits:
   `max_money_eur=0.50, max_tokens=5000, max_runtime_seconds=120`.
4. Revocation (requirement #9): `kernel_registry.disable()` /
   `src/lead_scoring/disable_staging.py` — immediate, idempotent, sets
   `agent_installations.status='disabled'`. `evaluate_policy()` blocks on the
   very next call, no code change needed. Exercised for real as negative
   test #2 below, not just described.

## E2E + negative-test measurement (`src/lead_scoring/staging_e2e_report.py`)

Requires `enable_staging.py` to have already run (checks and fails loudly if
not). Runs, against real staging, real DeepSeek, real Claude:

**Positive E2E**: one hot synthetic lead through
`validate → enrich_classify (PII stripped) → deepseek_score → business_rules
→ claude_review → human_approval (interrupt) → resume → crm_draft (draft
only) → audit`. Measures, from real data (not estimated): node timings
(computed from consecutive real audit-event timestamps), DeepSeek and Claude
token usage (read directly from each API response's own `usage` field, now
that `providers.py` surfaces it), approximate EUR cost (DeepSeek rate from
`src/research_worker.py`'s own documented pricing; Claude Haiku rate flagged
explicitly as an approximation, not verified against a real invoice),
approval wait/resume elapsed time, checkpoint row count for the run's
`thread_id`, and the full audit trail.

**Six negative tests**, each asserted, not just observed:

1. `pii_to_deepseek` — direct `kernel_gate()` call with
   `data_classes=("personal",)`, `provider="deepseek"` → must be denied.
2. `disabled_agent` — calls `kernel_registry.disable()` for real, attempts a
   lead, confirms `PermissionError`, then re-enables afterward so the
   workspace isn't left broken for future runs.
3. `duplicate_lead` — submits the identical `lead_id` twice through the same
   idempotency-aware `submit()` wrapper used in ADR-0002's pilot; confirms
   the second call is served from cache with zero node re-execution.
4. `transient_failure` — monkeypatches `providers.deepseek_score` to fail
   exactly once then delegate to the real function, confirms `RetryPolicy`
   recovers within the real (not mocked) graph, restores the real function
   afterward regardless of outcome.
5. `tenant_mismatch` — a fresh random UUID that was never installed; confirms
   rejection (`installation:missing` for that tenant specifically, proving
   per-tenant isolation of the policy check, not just DB-level RLS).
6. `human_rejection` — resumes an interrupted hot lead with
   `approved=False`; confirms no `crm_draft` is produced and the workflow
   halts.

Writes `research/langgraph-poc/lead-scoring/staging_e2e_report.json` with
every measured number for the final report.

## Run this (in order)

```powershell
cd greek-smb-agent
$env:VITRINA_ENV="staging"
python -m src.lead_scoring.enable_staging
python -m src.lead_scoring.staging_e2e_report
```

Paste back the full output of both. If `staging_e2e_report.py` raises an
`AssertionError` on any negative test, or the positive E2E doesn't reach
`crm_draft`, stop there and send the traceback — per the original
instruction, that's a STOP-and-diagnose condition, not something to retry
past silently.

To revoke the pilot at any point: `python -m src.lead_scoring.disable_staging`.

## Explicit non-goals (unchanged from ADR-0003)

- No production credential is read anywhere in this package.
- No real CRM is connected — `crm_draft_node` always returns
  `status="DRAFT_ONLY_NOT_WRITTEN"`.
- No production promotion happens as part of this ADR, regardless of how the
  staging run turns out — that is a separate, explicit decision the user
  reserved for themselves, per their own instructions.

## Final report

Source of truth: `research/langgraph-poc/lead-scoring/staging_e2e_report.json`,
written by a real run of `staging_e2e_report.py` against real staging
Supabase, real DeepSeek, real Claude, on 2026-08-13T05:58:56Z. Nothing below
is estimated; every number is read from that file or from
`enable_staging.py`'s own printed output.

### Enablement changes applied

1. `agent_registry` row for `lead.capture@1` promoted `draft` → `available`,
   with real `evals=("lead_scoring_offline_eval_v1",)` and
   `revocation.procedure` set (required by `validate_manifest()` for that
   lifecycle — not bypassed).
2. Synthetic staging workspace created in `clients`:
   `id=aaaa0007-0000-4000-8000-000000000007`,
   `email=qa-leadscoring@vitrina.test`, following the existing
   `scripts/seed_staging.py` QA-data convention exactly.
3. `agent_installations` row created for that workspace only:
   `status=enabled`, `granted_permissions=["crm.write"]`,
   `budget_limits={max_money_eur: 0.50, max_tokens: 5000,
   max_runtime_seconds: 120}`.
4. No other workspace, no production credential, and no real CRM connection
   was touched by enablement — `install()` is hard-scoped to
   `STAGING_WORKSPACE_ID` at the function level, not just by convention.

### Exact registry / installation state (confirmed via `registry_state()`)

- `registry.lifecycle = "available"`
- `installation.status = "enabled"` (dedicated synthetic workspace only)

### Positive E2E result

One hot synthetic lead (`ξυλουργός`, urgency keyword + budget mention) ran
the full path: `validate → enrich_classify → deepseek_score → business_rules
→ claude_review → human_approval (interrupt) → resume(approved) → crm_draft
→ audit`.

- **Interrupted before approval:** yes — the graph genuinely paused at
  `human_approval` and required an explicit resume, not a same-call
  auto-continue.
- **Total wall time:** 4.4294s. **Approval wait → resume:** 0.5642s (the
  resume leg only; the rest is real DeepSeek + Claude latency).
- **Per-node timings** (from consecutive real audit-event timestamps):
  validate→enrich_classify 0.001s, enrich_classify→deepseek_score 1.795s
  (DeepSeek call), deepseek_score→business_rules 0.001s,
  business_rules→claude_review 1.909s (Claude call),
  claude_review→human_approval 0.131s, human_approval→crm_draft 0.411s
  (resume + draft build), crm_draft→audit 0.001s. The two model calls
  account for ~3.7s of the 4.43s total — the graph/Kernel/DB overhead around
  them is small.
- **Checkpoints created for this thread:** 10 (confirmed genuinely isolated
  in `vitrina_lead_scoring_runtime`, not `public` — see schema-isolation
  correction below).
- **crm_draft.status:** `DRAFT_ONLY_NOT_WRITTEN` — no real CRM was called,
  confirmed by the field itself, not just by code inspection.
- **Final tier:** `hot`, matching both DeepSeek's score (78) and Claude's
  independent review (`recommended_tier=hot, risk_flag=false`).

### Measured token cost

| Call | Model | Input tokens | Output tokens |
|---|---|---|---|
| DeepSeek scoring | deepseek-chat | 137 | 39 |
| Claude review | claude-haiku-4-5 | 240 | 82 |

Total measured cost for this one lead: **≈€0.000671**, using DeepSeek's
already-documented rate (`src/research_worker.py`'s `_COST_PER_1M`) and an
**unverified approximate** Claude Haiku rate — `staging_e2e_report.py`
surfaces this as an explicit warning (`"claude-haiku-4-5 rate is an
approximation — verify current pricing"`), not silently. Extrapolated
naively to 1,000 leads/month at this tier mix that's roughly €0.67/month in
model cost, but that extrapolation assumes every lead reaches Claude review
and human approval, which will not hold once the `escalate_to_claude`/`tier
== "hot"` conditions filter most traffic — a real volume estimate needs
production-like tier distribution, not one hot-lead sample.

### Negative-test results (6 required)

| # | Test | Result | Detail |
|---|---|---|---|
| 1 | `pii_to_deepseek` | **blocked, as required** | `reasons=[deepseek_data_policy, autonomy_a1]` |
| 2 | `disabled_agent` | **blocked, as required** | `Kernel denied DeepSeek scoring: [installation:disabled, autonomy_a1]`; workspace re-enabled after the test, confirmed not left broken |
| 3 | `duplicate_lead` | **correct** | first submit not cached, second submit served from cache — zero node re-execution, no duplicate CRM draft |
| 4 | `transient_failure` | **recovered** | injected one DeepSeek failure; `RetryPolicy` recovered within the real graph on the real retry path |
| 5 | `tenant_mismatch` | **blocked, as required** | fresh never-installed workspace UUID rejected per-tenant, not just by a shared DB-level check |
| 6 | `human_rejection` | **behavior correct, audit label wrong (fixed)** | no `crm_draft` was created (the actual requirement) — correct. But `halted_reason` was recorded as `validation_failed`, which is misleading: the lead passed validation; it was halted because a human explicitly rejected it at the approval step. See "Issues discovered." |

5 of 6 negative tests are fully clean. #6's core safety property held (no
CRM write happened without approval) but its audit trail was wrong, which
matters given "keep all audit events enabled" was one of this ADR's own
minimum-enablement requirements — an audit event that misreports its own
cause is a real defect, not a cosmetic one.

### Audit evidence

Full 8-event trail captured for the positive E2E run (`validate` →
`features_extracted` → `scored` → `classified` → `reviewed` → `approved` →
`draft_built` → `run_complete`), each with a real UTC timestamp, actor
(`system`/`deepseek`/`claude`/`human`), and detail string — matches the
Kernel's `agency_audit_log` append-only design intent from
`db/migrations/0001_agency_kernel.sql`. The rejection-path audit event
itself (`action="rejected"`) was correctly recorded at the `human_approval`
node; only the *subsequent* `halt_invalid` node's derived `halted_reason`
field was wrong, not the human-approval event itself.

### Issues discovered

1. **`halted_reason` mislabeling (real bug, now fixed).**
   `halt_invalid_node` used `state.get("halted_reason") or
   "validation_failed"`, and nothing upstream of the approval-rejection path
   ever set `halted_reason` before reaching that node — so a human-rejected
   lead and a genuinely-invalid lead produced the identical audit label.
   **Fix applied:** `human_approval_node` now sets
   `halted_reason="human_rejected"` in its own state update when
   `approved=False`, so `halt_invalid_node` picks that value up instead of
   falling through to the generic default. **Regression coverage added:**
   `tests/test_lead_scoring_graph.py` — three tests, run locally against an
   in-memory checkpointer with stubbed providers/kernel_gate (no network,
   no staging credentials needed), confirming: a real validation failure
   still halts with `validation_failed`; a human rejection now halts with
   `human_rejected`; the two values are asserted distinct. All three pass:
   `python3 -m unittest tests.test_lead_scoring_graph -v` → `OK` (3 tests,
   0.06s). **Not yet reconfirmed against live staging** — the JSON report
   above predates this fix; rerunning `staging_e2e_report.py` is the one
   remaining action before this ADR closes (see "Run this" below).
2. **`PostgresSaver` schema-isolation gap in the two earlier ADRs**
   (ADR-0002/0003), already documented above — fixed in this ADR's own
   script via explicit `search_path`, confirmed by this run's
   `checkpoints_created=10` actually landing in
   `vitrina_lead_scoring_runtime`. Earlier runs' stray `public`-schema
   checkpoint rows are still unremediated (small, clearly-named, harmless,
   but not cleaned up — flagged, not silently fixed, per this ADR's own
   stated scope discipline).
3. **Claude Haiku pricing is an unverified approximation.** The cost figure
   above is internally consistent but has not been checked against a real
   invoice or current published rate card.
4. **Sample size is minimal.** One hot lead, one cold lead, no concurrent
   submissions, no load test, single-run timing. Node timings and cost are
   real measurements of one execution, not a statistically stable estimate.

### Changes required before production

1. Ship the `halted_reason` fix (done) and get one clean live-staging rerun
   confirming `human_rejection` now reports `halted_reason=human_rejected`
   (pending — see "Run this").
2. Decide and document graph execution location/deployment topology — still
   open from ADR-0001, not addressed by this staging-only ADR.
3. Register a real, non-placeholder Kernel eval identifier
   (`lead_scoring_offline_eval_v1` is currently a stub name, not a real
   evals artifact) before `lifecycle=available` is trusted as meaningful
   outside this pilot.
4. Get sign-off on (or replace) the approximate Claude Haiku pricing before
   treating any cost projection as reliable for budgeting.
5. Run a small load/concurrency pass (several leads in flight against the
   same workspace) before trusting the idempotency/dedup behavior at
   anything beyond single-request scale.
6. Manual cleanup pass on the stray `public`-schema checkpoint rows from
   ADR-0002/0003, if `public` needs to stay clean long-term (not urgent —
   harmless, but currently just documented rather than removed).

## Second pass (2026-08-13): reconfirmation + concurrency + cost-telemetry validation

Three things were added to `staging_e2e_report.py` and `providers.py` since
the first run, none of which change the positive-E2E or 5 clean
negative-test results already confirmed above:

1. **Steps [8]/[8b]/[8c] — concurrency/idempotency.** Fires 5 concurrent
   duplicate submits of one never-before-seen lead through independent DB
   connections (realistic pooled-connection simulation, not one shared
   connection) and asserts `deepseek_score`/`crm_draft` each executed **at
   most once** despite the race — this is a real test of whether the
   app-level `submit()` idempotency guard (`get_state()` check before
   `invoke()`) actually holds under concurrency, not just under the
   sequential double-submit already proven by negative test #4. If it does
   NOT hold, the script prints an explicit `⚠ RACE DETECTED` line rather
   than silently passing — this is a genuine open question the rerun will
   answer, not a foregone conclusion. Also tests: two tenants racing on the
   identical `lead_id` string (proves per-tenant thread-id isolation holds
   concurrently, not just sequentially) and three concurrently-retried leads
   with injected transient failures (proves `RetryPolicy` recovery doesn't
   leak state between concurrent invocations).
2. **Step [9] — cost-telemetry validation.** `providers.py` now reads the
   actual served model back from each API response body (`body["model"]`)
   instead of trusting the requested `cfg.MODEL_CHEAP`/`DEEPSEEK_MODEL`
   value, and flags a `model_mismatch` if they differ. `_cost_eur()` was
   rewritten: neither DeepSeek's nor Claude's pricing in this codebase comes
   from an authoritative source (DeepSeek's own rate table is commented
   `"Δεν είναι επίσημο API"` — not an official API, indicative only; Claude
   Haiku's rate was always just a number typed into a file) — so cost is now
   reported as a structured `cost_report` with `status: "UNVERIFIED"` and an
   `indicative_eur_approx` figure kept only for order-of-magnitude context,
   never presented as a trusted number. This is a stricter standard than the
   first pass applied — the first pass's `measured_cost_eur_approx: 0.000671`
   was internally consistent but should be read as indicative, not verified,
   for the same reason.
3. **ADR-0001 deployment-topology question — resolved for this workflow**,
   not deferred. See the new section added to `docs/adr/0001-langgraph-agent-runtime.md`:
   in-process, request/event-triggered invocation is sufficient for Lead
   Scoring specifically (measured 4.43s active compute, `interrupt()`
   releases the process during the human-wait, no multi-day pauses in this
   workflow). The topology question remains open and explicitly deferred —
   not resolved — for future multi-day-pause workflows (Follow-up, No-show
   Prevention, Reactivation).

All three are also covered by `tests/test_lead_scoring_graph.py`'s existing
regression tests where applicable, plus the new inline assertions in
`staging_e2e_report.py` itself (`assert rejected_state.get("halted_reason")
== "human_rejected"`, `assert all_recovered`, `assert
tenant_isolation_result["fake_tenant_blocked"]`).

### Run this (the one remaining hand-off item)

```powershell
cd greek-smb-agent
$env:VITRINA_ENV="staging"
python -m src.lead_scoring.staging_e2e_report
```

This single command now covers everything: the `[7/10]` reconfirmation, the
new `[8]/[8b]/[8c]` concurrency tests, and the `[9]` cost-telemetry summary.
Paste back the full output. Specifically check:

- `[7/10]` line ends with `(correct label)` — confirms `halted_reason=human_rejected`.
- `[8/10]` line — if it prints `⚠ RACE DETECTED`, stop and report it; that
  means the idempotency guard needs a real DB-level constraint (e.g. a
  unique index on `(tenant_id, lead_id)` backing the dedup, not just an
  application-level check-then-act) before this is production-safe under
  real concurrent webhook delivery.
- `[9/10]` line — confirms `cost_status=UNVERIFIED` is being reported
  honestly (expected, given no authoritative pricing source exists yet) and
  surfaces any `MODEL MISMATCH DETECTED` warning, which would itself be a
  stop-and-report condition.

If any `AssertionError` is raised anywhere in the script, stop and send the
full traceback — per the original instruction, that is a STOP-and-diagnose
condition.

## Rerun result (2026-08-13, confirmed against real staging)

All 10 steps passed, zero `AssertionError`s.

- **`[7/10]` reconfirmed:** `halted_reason=human_rejected (correct label)`.
  The fix holds against live staging, not just the local regression test.
- **`[8/10]` concurrency — no race detected.** 5 concurrent duplicate
  submits of one lead, across independent DB connections: `deepseek_score`
  ran exactly 1x, `crm_draft` ran exactly 1x. The app-level idempotency
  guard held under real concurrency against real Postgres, not just under
  the sequential double-submit already covered by negative test #4.
  (`checkpoints=41` for that thread — higher than the single-run baseline of
  10, expected: 5 racing workers each wrote checkpoints up to the point one
  of them won the race, not a defect.)
- **`[8b/10]` tenant isolation under concurrency — held.** Real tenant
  succeeded, a never-installed tenant racing it concurrently was still
  blocked.
- **`[8c/10]` concurrent retries — held.** 3 concurrently-retried leads all
  recovered independently via `RetryPolicy`, no cross-talk.
- **`[9/10]` cost telemetry — correctly reported `UNVERIFIED`,** and it
  surfaced something the first run's report couldn't see: **both** provider
  calls resolved to a different model than requested.
  - DeepSeek: requested `deepseek-chat`, response reported
    `deepseek-v4-flash`. This needs verification with DeepSeek's own
    documentation/account dashboard — it's plausible `deepseek-chat` is a
    floating alias DeepSeek has repointed to a newer model tier, but that is
    an assumption, not a confirmed fact, and a different tier can carry
    different pricing and different behavior.
  - Claude: requested `claude-haiku-4-5`, response reported
    `claude-haiku-4-5-20251001`. This is very likely benign — Anthropic
    commonly resolves a named alias to a dated snapshot, which is expected,
    documented behavior, not a silent substitution. Still worth pinning
    explicitly (see below) rather than relying on the floating alias, purely
    for reproducibility.
  - Practical effect: because neither resolved model string matched the
    indicative rate table, this run couldn't even produce an *indicative*
    cost figure — cost visibility for this run is fully `UNVERIFIED` with no
    fallback number at all, which is more honest than the first run's
    €0.000671 figure but also means cost is currently unmonitored.

### Updated "changes required before production" (supersedes the first-pass list)

1. ~~Fix + reconfirm `halted_reason`~~ — **done, confirmed live.**
2. ~~Deployment topology~~ — **done, resolved for this workflow (ADR-0001).**
3. ~~Load/concurrency test~~ — **done, passed cleanly, no race detected.**
4. ~~Pin exact model versions instead of floating aliases~~ — **done.**
   `src/lead_scoring/providers.py` now pins `deepseek-v4-flash` and
   `claude-haiku-4-5-20251001` explicitly. Pricing re-verified against each
   provider's own official pricing page on 2026-08-13 (DeepSeek: $0.14/MTok
   in, $0.28/MTok out; Claude Haiku 4.5: $1/MTok in, $5/MTok out) and wired
   into `staging_e2e_report.py`'s `_AUTHORITATIVE_RATES` — `cost_report`
   now resolves `VERIFIED` when pinned models are used (confirmed by
   `tests/test_lead_scoring_pinning_and_cost.py`, local, no network). See
   [0005-lead-scoring-production-pilot-plan.md](0005-lead-scoring-production-pilot-plan.md) §0.
5. ~~Register a real, non-placeholder Kernel eval identifier~~ — **done.**
   `evals` now points to `tests/test_lead_scoring_offline_eval.py`, a real
   passing test (deterministic coverage of `business_rules_node`'s tier
   thresholds), not the placeholder string `lead_scoring_offline_eval_v1`.
   `validate_manifest()` still accepts the manifest unchanged (regression
   tested).
6. Manual cleanup pass on stray `public`-schema checkpoint rows from
   ADR-0002/0003 — script written
   (`research/langgraph-poc/lead-scoring/cleanup_stray_public_checkpoints.py`,
   staging-only, double-confirmed, not yet run) — cosmetic, non-blocking.

## Final recommendation: **READY FOR LIMITED PRODUCTION PILOT**

Every safety-relevant property held, including under conditions this ADR
series had not yet tested: fail-closed PII gate, fail-closed disabled-agent
gate, per-tenant isolation (now proven under concurrent load, not just
sequential), idempotent dedup (now proven under real concurrency, not
assumed), retry recovery (now proven concurrently across independent leads),
and no CRM write without explicit human approval. Zero assertion failures
across 10 steps on live staging data.

This is "LIMITED," not unqualified GA-ready, because two real items remain
open and are governance/observability gaps, not correctness or safety gaps:
model versions are floating rather than pinned (discovered by this very
validation pass, which is the mechanism working as intended), and cost
telemetry is currently blind rather than merely approximate. Neither of
those risks customer data, spend beyond the tight installation budget cap
(`max_money_eur=0.50, max_runtime_seconds=120`), or an unapproved CRM write
— they affect observability and reproducibility, which matters for a
limited pilot's monitoring but does not itself compromise the pilot's
safety envelope.

**Per standing instruction: production is NOT being enabled by this report.
Stopping here — explicit, separate production approval is required before
any production-track work begins, regardless of this verdict.**
