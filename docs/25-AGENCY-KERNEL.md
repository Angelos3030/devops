# Phase 4A - Agency Kernel

Status: implemented locally, migration **not applied**, no specialist enabled.

## Binding decisions

### Workspace

`clients.id` is the Stage-4 `workspace_id`. We do not introduce another tenant
model. The kernel extends the existing FastAPI, Supabase and `agent_runtime.py`.

### Agent Registration / Marketplace

An agent is a versioned plugin (`agent_key@version`), not a prompt. Registration
does not install it and installation does not enable it.

Every manifest declares one unique purpose, ROI hypothesis, measurable success
metrics, lifecycle, autonomy, versioned capabilities/dependencies, verticals,
APIs, permissions, data classes, cost ceilings, deterministic evals, revocation
procedure and entrypoint.

Admission rule: create a new agent only when it has clear ROI, a unique purpose
and measurable benefit. If a feature fits an existing agent, extend that agent
unless separation materially reduces complexity, risk, permissions, context or
evaluation burden. `src/agency_kernel.py` enforces this rule.

### Capability matrix

Policy code consumes versioned capability keys, never marketing plan labels.
The existing packages remain:

| Package | Capability intent |
|---|---|
| Presence | website, QA, SEO, accessibility, performance, security, maintenance |
| Growth | Presence + content, social drafts, reviews, listings, demand, reporting |
| Revenue | Growth + leads, booking checks, no-show, reactivation, attribution |
| Agency | Revenue + ads drafts, experiments, offers, competitors, customer voice |
| Multi-location | Agency + location control, governance, enterprise integrations |

`plan_capabilities` materializes the mapping. `workspace_entitlements` can grant
or deny individual versioned capabilities. Marketing names may change without
changing kernel contracts.

## Policy gate

Before any future run, `evaluate_policy()` checks, fail closed: lifecycle and
installation state; capability entitlement; permissions; dependencies; data
classes; cost/runtime ceilings; risk, autonomy and approvals; provider policy.

Production writes always require approval. DeepSeek is allowed only for
`public`, `repository` or `synthetic` data. It is forbidden for conversations,
personal, sensitive or customer data.

## Persistence and state

Migration `0008_agency_kernel.sql` adds registry, capabilities, installations,
entitlements, tasks, runs, approvals, artifacts, events, KPIs and append-only
audit evidence. RLS is enabled on every new table. It seeds only capabilities
and plan mappings: **zero agents are registered, installed or enabled**.

## Dashboard contract

Authenticated, workspace-scoped endpoints:

- `GET /clients/{id}/agency/capabilities`
- `GET /clients/{id}/agency/actions`
- `POST /clients/{id}/agency/approvals/{approval_id}`

Action items use `schema_version: "1.0"`. There is deliberately no run/execute
endpoint in Phase 4A.

## Runtime boundary

`agent_runtime.py` remains a provider adapter. The kernel owns admission,
entitlements, policy, budgets, approvals, persistence and audit around any
future provider call. Specialist agents require a later explicit activation.

## Rollout checklist

1. Review and apply migration in local/dev only.
2. Run kernel tests and inspect RLS with service/anon roles.
3. Wire dashboard action queue without execution controls.
4. Register one draft deterministic manifest and run admission evals.
5. Enable only after explicit approval; staging before production.
