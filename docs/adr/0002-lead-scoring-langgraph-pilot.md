# ADR-0002: Lead Scoring pilot — LangGraph implementation plan and proof

**Status:** Accepted (staging-verified 2026-08-13 — all 10 required properties
proven against real staging Supabase, not just the local fallback; see
`research/langgraph-poc/lead-scoring/pg_spike_output.txt`. Accepted as
baseline for the real Lead Scoring staging implementation; still no
production change made.)
**Date:** 2026-08-13
**Deciders:** Vitrina project owner (angelos)
**Builds on:** [0001-langgraph-agent-runtime.md](0001-langgraph-agent-runtime.md) (ADAPT decision, approved)
**Scope boundary:** No real CRM connected. No production write. No change to
`src/`, `sites/`, `web/`, `db/`, or any existing agent flow. Everything lives
under `research/langgraph-poc/lead-scoring/`.

## Context

ADR-0001 was approved: LangGraph owns execution/state/checkpoint/retry/
interrupt; the Agency Kernel (`src/agency_kernel.py`) keeps owning
permissions/entitlements/budgets/data-classification/approval policy
unchanged; the ~42-agent catalog becomes ~6 domain graphs (Website & QA, SEO &
Content, Social & Reputation, Leads & CRM, Ads & Growth, Security &
Compliance) instead of independent agents. This ADR picks the first concrete
migration target — **Lead Scoring**, inside the Leads & CRM domain — and
proves it end-to-end in isolation before touching anything real.

There is no existing Lead Scoring implementation in the codebase to migrate
*from*. The closest real precedent is `src/social_engine.py`'s draft/approval/
retry pattern (DB status column + `attempts` counter + cron `run_due()` poll),
which is the pattern a hand-rolled Lead Scoring workflow would most likely
have copied. The comparison section below is explicit about what's measured
directly versus estimated by extrapolation from that precedent.

## Architecture

```
lead.received (tenant_id, lead_id, raw_lead)
        |
        v
  [validate]  -- deterministic, no LLM, no Kernel call (nothing sent to a
        |         provider yet, nothing written yet)
        | invalid -> [halt_invalid] -> END (audited)
        v valid
  [enrich_classify]  -- deterministic feature extraction. Strips PII here:
        |               output is {service_category, source_channel,
        |               message_length, urgency_keyword_count,
        |               has_budget_mention} — no name/email/phone/raw message.
        v
  [deepseek_score]  -- Kernel-gated (evaluate_policy(), provider="deepseek",
        |               data_classes=("synthetic",)). Sees ONLY the stripped
        |               feature vector. RetryPolicy(RuntimeError) attached.
        v
  [business_rules]  -- deterministic thresholds -> tier: hot/warm/cold +
        |               escalate_to_claude (confidence<0.75 OR tier=="hot")
        |
        +-- no escalation --------------------------------+
        | escalate                                        |
        v                                                  |
  [claude_review]  -- Kernel-gated (provider="anthropic",  |
        |              data_classes=("personal",) — Claude |
        |              is the existing GDPR-approved        |
        |              channel for customer data, per       |
        |              src/ai.py's pre-existing design)      |
        |                                                    |
        +-- tier=="hot" or risk_flag -> [human_approval]     |
        |         (interrupt() — genuinely halts)             |
        |                    | rejected -> [halt_invalid]      |
        |                    | approved                         v
        +-- else --------------------------------------> [crm_draft]
                                                            (Kernel-gated,
                                                             permissions=
                                                             ("crm.write",);
                                                             builds a payload,
                                                             status=
                                                             "DRAFT_ONLY_NOT_
                                                             WRITTEN" — never
                                                             calls a real CRM)
                                                                |
                                                                v
                                                            [audit] -> END
```

Every node that touches a provider or a permission calls the **real**
`evaluate_policy()` from `src/agency_kernel.py` — not a re-implementation.
`kernel_gate()` in `lead_scoring_graph.py` builds a real `TaskRequest` and
checks it against a real `AgentManifest`/installation, both in-memory stand-
ins for a registered pilot (registration itself is out of scope for an
isolated pilot; the validation and policy logic run for real). This is the
concrete mechanism behind ADR-0001's stated boundary: *"LangGraph replaces
execution plumbing, never policy."*

## What the Kernel gate actually caught (not hypothetical)

Running this spike surfaced two real Kernel refusals, not staged ones:

1. **First manifest draft used `lifecycle="draft"`** (the Kernel's own
   default) with a runtime budget narrower than the default `TaskRequest`
   envelope. `evaluate_policy()` correctly returned
   `blockers=['agent_lifecycle:draft', 'runtime_budget_exceeded']` and refused
   to run — exactly the fail-closed behavior an unregistered/draft agent
   should get. Fixed by making the pilot stub genuinely satisfy the
   `lifecycle="available"` contract (evals + revocation procedure — required
   fields, not skippable), documented in `lead_scoring_graph.py`.
2. **Asking DeepSeek to score `data_classes=("personal",)`** (i.e. simulating
   a careless node that forgot to strip PII first) was refused:
   `allowed=False, reasons=['deepseek_data_policy', ...]`. The correctly-
   scoped call (`data_classes=("synthetic",)`, the actual stripped feature
   vector) was allowed. This is `DEEPSEEK_ALLOWED_DATA_CLASSES` doing its job
   against a real call shape, proving the GDPR boundary holds inside a
   LangGraph node exactly as it would outside one — see full trace in
   `research/langgraph-poc/lead-scoring/pg_spike_output.txt`, "PROPERTY:
   policy-level failure recovery."

## Proof of the ten required properties

Full run transcript: `research/langgraph-poc/lead-scoring/pg_spike_output.txt`
(script: `pg_spike.py`, also copied there). Every property below is quoted
from that actual output, not asserted separately.

| # | Property | Proof |
|---|---|---|
| 1 | Persisted graph state | `PostgresSaver` checkpoints every node transition; state inspected via `graph.get_state()` mid-run shows 5 audit events before the interrupt |
| 2 | Resume after restart | Checkpointer connection fully closed (`with` block exit) and reopened as a new object; `state survived restart: tier='hot'`, `still paused before: ('human_approval',)` |
| 3 | Tenant isolation | Real RLS policy (`current_setting('app.tenant_id')`) on a dedicated table, tested through a **non-superuser** restricted role (`vitrina_poc_tenant_role`) — tenant-A session sees only its own row, tenant-B only its own; cross-tenant leak would have failed the assertion |
| 4 | Idempotency | Resubmitting `tenant-A::lead-42` after completion returns `cached=True` with zero node re-execution — an explicit application-level guard (`submit_lead()`), not a LangGraph built-in; documented as such |
| 5 | Retry behavior | `deepseek_score` injected with a first-attempt `RuntimeError`; `RetryPolicy(max_attempts=3, retry_on=(RuntimeError,))` absorbed it — `deepseek_score succeeded despite injected first-attempt failure: True` |
| 6 | Human approval | `interrupt()` genuinely halted before `human_approval`; graph result contained `__interrupt__`; nothing past that node ran until `Command(resume=...)` |
| 7 | Audit trail | 8 events (`validate` → `audit`) with timestamps, actor, action, detail — printed in full post-resume |
| 8 | Failure recovery | Two distinct classes proven separately: transient (#5 above) and policy fail-closed (Kernel gate denial for personal data reaching DeepSeek) |
| 9 | DeepSeek → Claude escalation | Low-confidence lead (`confidence=0.7 < 0.75`) routed through `claude_review` (`claude_reviewed: True`) without requiring human approval, since tier wasn't "hot" and no risk flag was raised — the escalation *threshold logic* actually executed, not just described |
| 10 | No production credentials/data used | Script attempts `DATABASE_URL_STAGING` first and logs the exact failure (DNS resolution failure — confirmed, not assumed); falls back to a throwaway local Postgres 16 instance (`pgserver`), never touching any real Supabase project. All test leads are synthetic |

**Caveat on property 10 / the "staging" label — RESOLVED 2026-08-13.** The
sandbox that built this pilot has no network route to Supabase (confirmed by
direct DNS failure). The user re-ran `pg_spike.py` from their own machine
against real `DATABASE_URL_STAGING` — no code change was needed, the script
picked up the real staging database automatically. First attempt surfaced a
genuine, staging-specific bug: Supabase's pooler (Supavisor) requires
connecting usernames to carry a `<role>.<project_ref>` suffix so the
multi-tenant pooler knows which project to route to; the restricted
(non-superuser) role's connection didn't have it and failed with
`ENOIDENTIFIER: no tenant identifier provided`. Fixed in
`tenant_role_connection()` by reusing the project_ref suffix already present
in the admin connection's username — this affects any new role connecting
through Supabase's pooler, not just this POC, and is worth remembering for
the real staging implementation below. After the fix, all 10 properties
passed cleanly against real staging Supabase. Full transcript:
`research/langgraph-poc/lead-scoring/pg_spike_output.txt`.

## Comparison: custom state machine vs. LangGraph implementation

No Lead Scoring code exists today to diff literally, so the "custom" column
extrapolates from the one real precedent in the codebase for this exact
shape — `src/social_engine.py`'s draft/approval/retry pattern — scaled up to
Lead Scoring's extra steps (enrichment, two-provider escalation, conditional
approval). The LangGraph column is measured directly from what was just
built and run.

| Dimension | Custom (social_engine.py pattern, extrapolated) | LangGraph (measured) |
|---|---|---|
| Lines/complexity | `social_engine.py` itself is 114 lines for a *single*-step draft→approve→publish flow with one retry counter. A Lead Scoring version needs: enrichment step, two-provider escalation logic, conditional approval, idempotency guard, and its own DB schema for status/attempts — estimated 250-350 lines of bespoke state-machine code, excluding the actual scoring logic. | `lead_scoring_graph.py` is 384 lines **including** all business logic (validation, feature extraction, two mock provider calls, Kernel gate wiring, routing) — the orchestration shell itself (node wiring, conditional edges, retry policy) is under 60 of those lines. Business logic is comparable either way; the state-machine plumbing is what shrinks. |
| Testability | Testing `social_engine.process_post()` requires standing up/mocking the DB and driving it through status transitions end-to-end — there's no way to unit-test "just the approval-routing decision" in isolation from persistence. | Nodes are plain functions with typed input/output (`route_after_business_rules`, `route_after_claude` etc.) — directly unit-testable with a dict in, string out, no DB required. Persistence/interrupt/retry are tested separately (this spike) from business logic. |
| Failure recovery | Manual: `attempts` counter + `scheduled_for` timestamp, checked by a cron polling `run_due()`. Silent-loss bugs are easy to introduce here — this exact class of bug was found and fixed twice this session in `src/research_worker.py` (lost progress on interrupt, dropped over-budget items) before this ADR was even started. | `RetryPolicy` per node, checkpointed automatically; proven in property #5 above to recover from a real injected failure without any bespoke counter/column. |
| Observability | Whatever the workflow's author remembered to log to the DB status column — no shared shape across workflows. | `graph.get_state()` gives the exact paused node, full state, and (with the added `audit_log` field, which is Vitrina's own code, not a LangGraph feature) a structured event trail — same shape reusable across every future domain graph. |
| Token cost | No orchestration-related token cost difference — LangGraph doesn't call an LLM itself, it only sequences the same Claude/DeepSeek calls the custom version would make. The real cost lever is the *escalation threshold* (confidence<0.75 OR tier=="hot"), which both approaches need to tune identically. No cost advantage either way. | Same. |
| Maintenance burden | Grows linearly with each new stateful workflow — every one of the ~6 domain graphs' worth of future capabilities would re-derive its own status/attempts/polling pattern from scratch, each with its own bug surface. | One runtime to patch/upgrade/understand, reused across all 6 domain graphs. Cost is front-loaded (team learning curve, already partly paid by this pilot) rather than repeated per workflow. |

## GO / NO-GO

**GO** — proceed to a real (non-mocked, staging-connected) Lead Scoring
migration, with these explicit conditions carried over from ADR-0001's
migration path and this pilot's findings:

1. ~~Re-run `pg_spike.py` from a network-connected machine against real
   `DATABASE_URL_STAGING`~~ — **DONE 2026-08-13.** All 10 properties passed
   against real staging Supabase after fixing the Supavisor pooler
   username-suffix issue (see caveat above). RLS holds under Supabase's real
   role/pooler model, not just plain local Postgres.
2. Register the Lead Scoring pilot as a real Kernel manifest
   (`lifecycle="available"`, real evals, real revocation procedure) instead
   of the in-memory stand-in used here — the stand-in exists only to make an
   isolated pilot runnable, not as a template to copy into production config.
3. Replace the two `_mock_*` functions with real calls using the exact
   patterns already in `src/research_worker.py` (DeepSeek) and
   `src/agent_runtime.py` (Claude) — no other graph change required, per the
   provider-independence property already demonstrated in ADR-0001's POC.
4. Keep `crm_draft` a draft-only node until a specific, separate approval
   to wire a real CRM connector — not part of this ADR.
5. Do not batch-migrate other domain graphs off this result; validate Lead
   Scoring in shadow/parallel mode first, per ADR-0001's migration path
   step 4.

## Action Items

1. [ ] Re-run `pg_spike.py` against real staging Supabase from a reachable machine; attach the output to this ADR before final sign-off.
2. [ ] Draft the real Kernel manifest for Lead Scoring (separate task, not part of this pilot).
3. [ ] Decide where the graph executes in production (in-process FastAPI vs. worker) — flagged as unresolved in ADR-0001, still unresolved here.
4. [ ] Swap mock provider calls for real ones once the above are settled.
5. [ ] No CRM connector work starts until this ADR's Action Items 1-4 are closed and separately approved.
