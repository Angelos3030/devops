# ADR-0001: LangGraph as the Vitrina agent runtime/orchestration layer

**Status:** Proposed (research complete, POC complete, no production change made)
**Date:** 2026-08-12
**Deciders:** Vitrina project owner (angelos)
**Scope boundary:** This ADR and its POC are research artifacts only. Nothing in
`src/`, `sites/`, `web/`, `db/`, or any existing agent flow was modified to
produce it. The POC lives entirely under `research/langgraph-poc/`.

## Context

Vitrina's roadmap (`docs/22-AGENT-ECOSYSTEM.md`) plans ~42 named agents across
three phases (MVP, recurring growth engine, AI digital agency), each with an
autonomy level (A0 advisory → A3 autonomous), a required audit trail, and a
closed loop: `observe → diagnose → propose → approve → execute → verify →
measure → learn`. Phase 4A (`docs/25-AGENCY-KERNEL.md`) has already built a
deterministic policy kernel for this — manifest admission, capability
entitlements, approval-policy resolution, cost ceilings, and a DeepSeek
data-class restriction (DeepSeek may only see `public`/`repository`/`synthetic`
data, never customer data) — but it is explicitly staging-only and **owns
policy, not execution**.

Reading the actual code confirms there is currently no unified execution
runtime:

- `src/agent_runtime.py` is an 64-line adapter that opens one Anthropic agent
  session, streams a single message exchange, and returns text. Its own
  docstring states the design intent directly: *"Το backend καλεί ΑΠΕΥΘΕΙΑΣ τον
  σωστό agent — όχι μέσω runtime coordinator"* (the backend calls the right
  agent directly, not through a runtime coordinator). No persistence, no
  checkpointing, no retry, no multi-step state.
- `src/agency_kernel.py` is a pure policy/validation module — it explicitly
  does not call a provider or execute anything.
- `src/social_engine.py` is the one place a durable, resumable, approval-gated
  workflow already exists in production shape: draft → `pending_approval` row
  in Postgres → `process_post()` checks `approval_required`/`approved_at` →
  retry with an `attempts` counter and a `scheduled_for` backoff column. This
  works, but it is hand-rolled per workflow: durability = a status column,
  resumability = a cron polling `run_due()`, and every new long-running
  workflow (Lead Scoring, Ads, Review Response, ...) would reinvent the same
  pattern from scratch in its own tables.

The question this ADR answers: should the ~42-agent roadmap be built on this
same hand-rolled pattern repeated 42 times, or on a shared graph/state/
checkpoint runtime (LangGraph), with the Agency Kernel kept as-is for policy?

The earlier DeepSeek-assisted research pass (`research/agent-discovery/`)
surfaced LangGraph as a `REUSE`/`ADAPT`-rated candidate across nine separate
findings (supervisor pattern, hierarchical teams, reflection, plan-and-execute,
retries — see `research/agent-discovery/runs/2026-08-12-deepseek/findings.json`),
all pointing at the same MIT-licensed repo, evidence-verified independently.
That result is the trigger for this ADR, not its conclusion — the analysis
below evaluates LangGraph specifically against Vitrina's own architecture, not
generic LangGraph marketing claims.

## Decision

**ADAPT.** Adopt LangGraph as the shared execution/state/checkpoint layer for
future multi-step, long-running, human-gated agent workflows, keeping the
Agency Kernel exactly as designed (policy, entitlements, approval-policy
resolution stay Vitrina's own code — LangGraph has no equivalent and
shouldn't). Do not adopt it wholesale for the whole roadmap on day one; migrate
one real workflow first (candidate: Lead Scoring or the Social Media approval
queue, since both already have a manual state machine to replace and compare
against directly). No production wiring happens as part of this ADR.

## Options Considered

### Option A: Continue custom orchestration (per-workflow hand-rolled state machines)

| Dimension | Assessment |
|---|---|
| Complexity | Low per workflow, but multiplies — each of ~15-20 stateful workflows in the roadmap (Lead Scoring, Ads, Review Response, Booking, Follow-up, Reactivation, ...) re-implements durability, retry, and resume from scratch |
| Cost | No new dependency, no new failure surface, but growing maintenance surface (N bespoke state machines instead of 1 shared one) |
| Scalability | Fine at current single-tenant-per-workspace scale; degrades as workflow count grows — no shared observability/audit primitive across workflows |
| Team familiarity | Highest — it's exactly what exists today (`social_engine.py` pattern) |

**Pros:** Zero new dependency. Total control. No framework version risk. Matches the project's stated production-code discipline (deterministic code where possible, LLM only for judgment).
**Cons:** No shared checkpointing, no shared interrupt/resume primitive, no shared audit-trail shape — `social_engine.py`'s pattern (DB status column + cron poll) has to be manually re-derived for every new stateful agent. Retry logic, resume-after-approval, and parallel fan-out all get reinvented per workflow, with per-workflow bugs (exactly the class of bug already fixed twice in `src/research_worker.py` this session: lost progress on interrupt, silently dropped over-budget items).

### Option B: LangGraph as shared agent runtime, Agency Kernel unchanged as policy layer

| Dimension | Assessment |
|---|---|
| Complexity | Medium — one new dependency family (`langgraph`, `langgraph-checkpoint*`) and one new mental model (graph/node/state/checkpoint) to learn once, reused ~15-20 times instead of reinvented |
| Cost | New dependency surface (see Dependencies below); checkpoint storage cost (Postgres-backed checkpointer recommended for production — see Risks); no LLM cost change, since it orchestrates existing Claude/DeepSeek calls rather than replacing them |
| Scalability | Better — checkpointing, interrupt/resume, and retry are solved once at the framework level; parallel agent fan-out (Send API) is native instead of hand-rolled |
| Team familiarity | Low today, proven in this session's POC to be learnable and to work correctly against real requirements (persistence across process restart, retry-on-failure, human-gated interrupt) |

**Pros:** Solves exactly the three failure modes already hit in production-adjacent code this session (lost interrupt state, silent partial-result loss, no resumability) as first-class framework features instead of bespoke fixes. Native `interrupt()`/`Command(resume=...)` matches Vitrina's own `A1 — Draft: πάντα approval πριν την εκτέλεση` autonomy contract almost exactly. Model-provider agnostic — nodes are plain Python functions, so Claude and DeepSeek calls sit in the same graph with no framework lock to either vendor's SDK.
**Cons:** New dependency to vet, patch, and pin. Team must learn a new abstraction. LangGraph does not replace the Agency Kernel's policy/entitlement/manifest system — that stays fully custom regardless of this decision, so this is additive complexity, not complexity swapped out.

## Evaluation against the 15 criteria (grounded in the POC, not vendor docs)

1. **Durable execution / persistence** — Real. `SqliteSaver` (dev) / `PostgresSaver` (prod path) checkpoints full graph state after every node. POC step 3 proves it survives a simulated process restart (new DB connection, new graph object, same `thread_id`) — this is not in-memory state.
2. **Checkpointing and resume** — Native. `graph.get_state(config)` returns the exact paused point (`next=('human_approval',)`); resume requires an explicit `Command(resume=...)` — nothing proceeds implicitly, which matches Vitrina's "draft-first, explicit approval" contract in `src/social_engine.py` and the chat-to-edit rule in `CLAUDE.md`.
3. **Human-in-the-loop** — Native via `interrupt()`. This is a closer match to Vitrina's A1/A2 autonomy model than anything custom would casually build — the graph genuinely cannot proceed past `human_approval_node` without an external decision.
4. **Retries and failure recovery** — Native via `RetryPolicy(retry_on=..., max_attempts=...)` attached per node. POC step 1 vs step 2 demonstrates the difference directly: without a policy the node's exception propagates raw; with one, the same flaky node self-heals on attempt 2, visible in the audit log (`attempt=2`), not just claimed.
5. **Conditional routing** — Native (`add_conditional_edges`), not exercised in this POC but well-documented and low-risk; directly replaces what would otherwise be manual `if/elif` dispatch across agent modules.
6. **Parallel agents** — Native (`Send` API for fan-out/fan-in). Not exercised here since the requested POC was linear; relevant to Vitrina's future needs (e.g. QA Agent + SEO Agent running against the same deploy concurrently) but unverified by this POC specifically — flag for the first real migration to test under load.
7. **Agent handoffs** — Native — a node's return value can route to a different subgraph/node based on structured output, which maps cleanly onto Vitrina's `observe → diagnose → propose → approve → execute → verify` loop.
8. **State model** — Typed (`TypedDict`/Pydantic) shared state object threaded through every node, closer to Vitrina's existing preference for structured, non-free-text contracts (e.g. `AgentManifest`, `TaskRequest` dataclasses in `agency_kernel.py`) than to prompt-chaining frameworks.
9. **Observability / audit trail** — LangGraph gives checkpoint history and interrupt state for free; it does **not** give Vitrina's specific audit semantics (`build_action_queue_item`, `PolicyDecision.reasons`, append-only evidence tables). The POC's `audit_log` field is custom application code layered on top of LangGraph state, not a LangGraph feature — this is real work Vitrina still owns regardless of the decision.
10. **Tool permissions** — LangGraph has no concept of Vitrina's `PRODUCTION_WRITE_PERMISSIONS`, `data_classes`, or the `DEEPSEEK_ALLOWED_DATA_CLASSES` gate. The Agency Kernel's `evaluate_policy()` must remain the gate a node calls *before* acting — LangGraph orchestrates the call, the Kernel still decides if the call is allowed. This is the clearest boundary in the whole ADR: **LangGraph replaces execution plumbing, never policy.**
11. **Model-provider independence** — Confirmed by the POC itself: `deepseek_research_node` and `claude_review_node` are plain Python functions with no shared base class or vendor SDK dependency between them, sitting in one graph. Swapping either mock for a real call (DeepSeek via `src/research_worker.py`'s pattern, Claude via `src/agent_runtime.py`'s pattern) requires no graph-level change.
12. **Background / long-running workflows** — This is LangGraph's strongest fit for Vitrina: workflows like No-show Prevention, Follow-up, or Reactivation are exactly "pause for days, resume on an event" shapes that `interrupt()`/checkpoint solves natively instead of via cron-polling a status column (`social_engine.run_due()`'s current pattern).
13. **Deployment complexity** — Understated risk. Dev POC used SQLite; production needs `PostgresSaver` (already have Postgres/Supabase, so no new database, but a new schema/migration and connection-pool consideration), and a decision on where the graph *runs* (same FastAPI process vs. a worker). Not evaluated by this POC — first real migration should measure this explicitly before touching a second workflow.
14. **Testing** — Nodes are plain functions with typed input/output, which is easier to unit-test in isolation than the current pattern of testing `social_engine.process_post()` end-to-end against a mocked DB. Graph-level tests (interrupt/resume/retry) are what this POC essentially is.
15. **Vendor / framework lock-in** — Real but bounded. LangGraph's core primitives (`StateGraph`, `interrupt`, checkpointer) are a thin enough layer that the actual business logic (what a node does) stays plain Python/Vitrina code — only the orchestration shell would need rewriting if LangGraph were ever dropped. Contrast with AutoGen, which this session's DeepSeek research explicitly flagged as "in maintenance mode, not recommended for new development" — a real example of framework risk materializing, and a reason to re-verify LangGraph's maintenance status at time of first real migration, not just today.

## Do we need 44 agents, or fewer agents with LangGraph nodes underneath?

**Fewer agents, per your stated preference — and this is not just a preference call, the roadmap doc already half-implies it.** `docs/22-AGENT-ECOSYSTEM.md` states the design philosophy directly: *"Αν ένα βήμα είναι deterministic..., γίνεται με κανονικό κώδικα. LLM χρησιμοποιείται μόνο για κρίση, σύνθεση, ταξινόμηση ή δημιουργία"* — steps that are deterministic were never meant to be separate autonomous agents in the first place.

Concretely: many of the ~27 "differentiating" agents in section 3 of that doc
are variations on a small number of *domain* concerns wired to different
triggers — e.g. Follow-up Agent, No-show Prevention Agent, and Reactivation
Agent are the same shape (customer lifecycle event → policy-gated message →
approval → send → audit) with a different trigger and message template. Under
LangGraph these become **one Customer Lifecycle graph with three entry
nodes/triggers**, not three agents with three separate manifests, three
separate approval flows, and three separate retry implementations. Similarly
Review Growth, Review Response, and Review Intelligence are one Reputation
domain graph with different nodes, not three agents.

Recommended shape: **a handful of domain-level LangGraph graphs** (Website &
QA, SEO & Content, Social & Reputation, Leads & CRM, Ads & Growth, Security &
Compliance — roughly six, mapping to the existing Presence/Growth/Revenue/
Agency capability packages already defined in the Agency Kernel), each
containing the finer-grained steps as **nodes, not top-level agents**. The
Agency Kernel's manifest/capability/entitlement model does not need to change
shape for this — a "graph" can register as one kernel-admitted agent with
multiple versioned capabilities, which the kernel already supports
(`AgentManifest.capabilities: tuple[VersionedRef, ...]`).

This does not mean discard the 42-agent table — it stays valuable as a
**capability catalog and ROI/priority backlog**. It stops being a literal count
of things to independently build, test, and grant permissions to.

## POC summary

Location: `research/langgraph-poc/poc_graph.py` (+ `poc_run_output.txt` for the
captured transcript). Graph: `Research request → DeepSeek research node
(mocked) → Claude review node (mocked) → human_approval (interrupt) → finalize
(only reachable via Command(resume=...))`.

Proven, not asserted (see transcript for exact output):
- DeepSeek and Claude in the same graph, same shared typed state, no shared SDK dependency between the two nodes.
- Checkpointed state survived a simulated process restart (new SQLite connection, new graph object, same `thread_id`).
- `interrupt()` genuinely halted execution before `human_approval` — `graph.invoke()` returned with `__interrupt__` populated and zero further nodes executed.
- Resume required an explicit `Command(resume={...})` — no implicit continuation path existed.
- A node configured with no `RetryPolicy` let its exception propagate raw (Step 1); the same node with `RetryPolicy(retry_on=(RuntimeError,))` recovered automatically on its second attempt (Step 2), visible in the audit log as `attempt=2`.
- Structured outputs throughout (`TypedDict` state, dict artifacts) — no free-text parsing between nodes.
- A custom `audit_log` list accumulated one event per node and survived the same checkpoint/resume/restart cycle — proving audit trails compose cleanly with LangGraph state, while confirming (per criterion 9 above) that Vitrina's specific audit *shape* is still Vitrina's own code to write.

DeepSeek/Claude calls are mocked and clearly labeled `_mock_*` in the POC — this
sandbox has no path to `api.deepseek.com`/`api.anthropic.com`, and no
production credential was used. Swapping the two mock functions for real calls
using the exact patterns already in `src/research_worker.py` (DeepSeek) and
`src/agent_runtime.py` (Claude) is the only change needed to make the graph
call real providers; the orchestration mechanics proven above do not change.

## Architecture diagram

Current (Option A shape, per-workflow):

```
Trigger --> Agent module (direct Claude call via agent_runtime.py)
              |
              v
        DB status column (e.g. posts.status = 'pending_approval')
              |
              v
        Cron poll (social_engine.run_due()) --checks approval/attempts--> execute or retry
```//
repeated once per stateful workflow, with no shared code between repetitions.

Proposed (Option B shape, one runtime for N domain graphs):

```
                    +-------------------------------+
                    |   Agency Kernel (unchanged)    |
                    |  evaluate_policy() gate:       |
                    |  entitlements / permissions /  |
                    |  data-class / cost / approval  |
                    +---------------+-----------------+
                                    | node calls this before acting
                                    v
Trigger --> LangGraph domain graph (e.g. "Leads & CRM")
              node: DeepSeek research/classify  (research_worker.py pattern)
              node: Claude judgment/draft        (agent_runtime.py pattern)
              node: interrupt() -- human approval gate
              node: execute (writes only after Kernel + human approval)
              node: audit event append
              |
              v
      PostgresSaver checkpoint (Supabase) -- durable, resumable, inspectable
```

## What this replaces vs. what stays

**Replaces (per migrated workflow, not repo-wide on day one):**
- The hand-rolled `pending_approval` / `attempts` / `scheduled_for` state
  machine pattern in `src/social_engine.py`, and any workflow that would
  otherwise reinvent it.
- Cron-based polling for "is this ready to resume" (`run_due()`), in favor of
  event-driven resume via `Command(resume=...)`.
- Ad hoc retry loops (the exact class of bug fixed twice this session in
  `src/research_worker.py` — lost progress on interrupt, silently dropped
  over-budget candidates) — LangGraph's checkpoint+retry primitives make both
  bugs structurally harder to reintroduce.

**Stays exactly as-is, unconditionally:**
- `src/agency_kernel.py` — policy, entitlements, manifest admission, approval-policy resolution, cost ceilings, DeepSeek data-class gate. LangGraph has no equivalent and none should be built; a graph node calls `evaluate_policy()` before acting, same as any other caller would.
- The Supabase/Postgres tenancy model (`clients.id` as workspace id) — no parallel data model introduced.
- `src/agent_runtime.py` and `src/research_worker.py` call patterns — these become the bodies of LangGraph nodes, not replaced code.
- All draft-first / explicit-approval contracts already documented in `CLAUDE.md` (chat-to-edit, social publishing) — LangGraph's `interrupt()` implements this contract, it doesn't change it.

## Migration path

1. Pick one real, already-partially-built stateful workflow to migrate first — Lead Scoring or the Social Media approval queue (both already have a manual state machine to migrate *from* and measure against directly). Do not start with a brand-new capability.
2. Stand up `PostgresSaver` against a **new, isolated schema** (not the existing `clients`/`sites` tables) — first spike should just prove checkpoint read/write against real Supabase Postgres, mirroring what the POC proved against SQLite.
3. Rewrite that one workflow's steps as graph nodes, each node calling existing Vitrina code (Kernel `evaluate_policy()`, `agent_runtime.run_agent()`, DB writes) — no new business logic, only new plumbing.
4. Run the migrated workflow in parallel/shadow mode against the existing one for a defined period; compare outcomes, not just code.
5. Cut over one workflow behind an explicit approval (per `CLAUDE.md`'s own "no reverting to auto-save/auto-publish without explicit approval" discipline).
6. Only after one workflow is stable in production, evaluate migrating a second. Do not batch-migrate the roadmap.

## Estimated complexity

Medium. The mechanics (this POC) are proven working in under a day. The real
cost is: (a) standing up `PostgresSaver` against Supabase correctly under RLS
(Row-Level Security is already a hard requirement per `docs/25-AGENCY-KERNEL.md`
— every new table gets RLS; the checkpoint schema needs the same review), and
(b) deciding where graphs execute (in-process with FastAPI vs. a separate
worker) for genuinely long-running workflows (days-long No-show/Follow-up
cases) without blocking request threads.

## Dependencies introduced

`langgraph`, `langgraph-checkpoint` (base), and one checkpointer backend
(`langgraph-checkpoint-sqlite` for dev, `langgraph-checkpoint-postgres` for
prod). All pure-Python, MIT-licensed (verified: `langchain-ai/langgraph`
LICENSE file, same verification method used in the DeepSeek research pass).
No new external service — checkpoints live in Supabase Postgres, already in
the stack.

## Risks

- **RLS correctness on a new checkpoint schema** — get this wrong and either leak cross-workspace state or block legitimate reads; needs the same review rigor as any other new table per the Agency Kernel's own stated discipline.
- **Framework maintenance risk** — mitigated but not eliminated; re-check LangGraph's release cadence/maintenance status at first real migration, not just at ADR time (AutoGen's "maintenance mode" status, surfaced in this session's own research, is the concrete cautionary example).
- **Team learning curve** — one new abstraction, but it replaces N bespoke ones; net complexity should go down after the first migration, not before.
- **Scope creep temptation** — the roadmap's 42-agent table makes it easy to over-scope this into "rebuild everything on LangGraph now." The migration path above deliberately forces one workflow first.
- **DeepSeek/Claude boundary must be enforced by the Kernel, not by convention** — a LangGraph node calling DeepSeek must still go through `evaluate_policy()`'s `deepseek_data_policy` check; LangGraph will not stop a careless node from passing customer data to DeepSeek. This is a code-review discipline risk, not a LangGraph risk, but worth stating because the whole point of the existing Kernel gate is to prevent exactly that GDPR exposure.

## What happens to the planned 42-agent architecture

It survives as the **capability catalog and roadmap**, unchanged in content —
every agent in `docs/22-AGENT-ECOSYSTEM.md` still represents real, distinct
business value and ROI hypothesis. What changes is the *implementation unit*:
most rows become nodes/subgraphs inside a small number (roughly six) of
domain-level LangGraph graphs aligned to the Kernel's existing
Presence/Growth/Revenue/Agency capability packages, rather than 42
independently-built, independently-approved, independently-tested agents. This
is a recommendation to revisit at the start of Phase 2 planning
(`docs/22-AGENT-ECOSYSTEM.md` §4), not a change to make now.

## Deployment-topology resolution for Lead Scoring (2026-08-13, ADR-0004 follow-up)

Criterion 13 flagged this as unresolved: "a decision on where the graph
*runs* (same FastAPI process vs. a worker)... not evaluated by this POC —
first real migration should measure this explicitly." The first real
migration (Lead Scoring, ADR-0002/0003/0004) has now run against real
staging, so this can be answered for that workflow specifically — it is
**not** a blanket answer for every future domain graph.

**Decision for Lead Scoring: in-process, request/event-triggered invocation.
No dedicated worker process is required for this workflow.**

Reasoning, grounded in what was actually measured:

1. `interrupt()` does not hold a process open while waiting for a human.
   `graph.invoke()` returns control to the caller the moment it hits
   `human_approval`, with `__interrupt__` populated — confirmed by both the
   POC and every staging run since. The wait for approval happens with
   **zero process holding it open**; state sits in Postgres via the
   checkpointer. Resuming is a separate, later `graph.invoke(Command(resume=...))`
   call, naturally triggered by whatever UI action records the approval
   (dashboard button, API call) — not a polling loop.
2. Active compute time per lead is short and now measured, not estimated:
   4.43s wall time end-to-end for a hot lead requiring both DeepSeek and
   Claude, of which ~3.7s is the two model calls themselves. This is well
   within a normal HTTP request timeout or a lightweight background task —
   it does not need a separate long-running worker to avoid blocking
   anything.
3. This reasoning does **not** generalize to every future domain graph.
   Workflows with genuinely multi-day pauses (Follow-up, No-show Prevention,
   Reactivation — named explicitly in criterion 12 as LangGraph's strongest
   fit) still need an explicit decision about what triggers the resume call
   after days of real-world waiting: an inbound webhook/event is the natural
   fit (same pattern as Lead Scoring's approval trigger), but a cron-style
   sweep may still be needed as a fallback for missed events. **That decision
   is deferred to whichever of those workflows is migrated next** — it is
   not required to unblock a Lead Scoring pilot and forcing it now would be
   solving a problem the current workflow doesn't have.

**What this means for production readiness:** the deployment-topology
question is resolved for Lead Scoring specifically and is not a blocker for
a limited pilot. It remains open, and should stay explicitly tracked, for
any future migration of a multi-day-pause workflow.

## Action Items

1. [ ] Review this ADR and the POC transcript; decide go/no-go on the first real migration (recommend Lead Scoring or Social Media approval queue).
2. [ ] If go: spike `PostgresSaver` against an isolated Supabase schema with RLS, separate from this ADR.
3. [ ] If go: draft the domain-graph grouping (six graphs proposed above) as a follow-up doc before writing any migration code.
4. [ ] Re-verify LangGraph's license and maintenance status at time of first real migration (not just today).
5. [ ] Do not integrate any of the parked research findings (below) as part of this decision — they remain separately gated.

## Parked findings (explicitly not integrated by this ADR/POC)

- **OWASP Agent Memory Guard** (Apache-2.0) — security-layer candidate for agent memory poisoning defense. Parked.
- **TrustBoost PII Sanitizer** — PII-protection candidate, license still unverified by direct manual check (automated check returned `LICENSE_UNVERIFIED`). Parked pending that check.
- **CrewAI examples repo** — pattern/reference only; repo-level licensing still unverified. Parked.
- **Citadel** — study-only, relevant to coordinating multiple Claude Code agents on this repo (a development-process concern), not the Vitrina product runtime. Parked.

None of these were touched, installed, or referenced by the POC.
