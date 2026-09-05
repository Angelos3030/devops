# Editing Engine Vertical Slice Report

Date: 2026-08-26

## Canonical state

- Business identity: `clients` (`name`, `business_type`, `city`, `phone`, etc.).
- Editable draft: `site_content.content`; the editor now adds monotonic `editor_version`.
- Theme selection: `sites` row with `url='selected'`.
- Palette: `site_content.content.palette`, constrained by `theme_capabilities` for the selected theme.
- Media: customer-owned `client_assets`; draft ordering is `site_content.content.photo_order` containing owned asset IDs.
- Published state: `sites` rows with an HTTP URL/static output. Editor RPCs never update `sites`.
- Preview state: normalized business data plus persisted `site_content` overrides. A proposed, unapproved edit remains frontend draft only.

## Supported schemas

Only these operations pass deterministic validation:

1. `update_phone {phone}`
2. `update_hours {hours}`
3. `update_business_field {field,value}` for an explicit field allowlist
4. `update_service {name,description?,price?,duration?}`
5. `reorder_media {order}`
6. `set_palette {palette}`

Unknown operations/parameters are rejected. Phone digit count and character set, time tokens, text lengths, active markup, URLs, media permutations, service limits and theme palette capability are checked independently of the model. Confidence below 0.75 is rejected.

## Flow and transaction mechanism

`POST /clients/{id}/chat-edit` is proposal-only:

`message -> model EditPlan -> schema/allowlist/capability/media validation -> projected draft`

It performs no database write. Explicit approval calls `POST /clients/{id}/editor/apply`, which reconstructs and revalidates the operations against fresh customer state. `editor_commit(...)` then locks the client's `site_content` row and writes content plus revision in one PostgreSQL transaction. A failure before or during the RPC leaves both unchanged.

The RPC is `SECURITY INVOKER`, callable only by `service_role`; execution is revoked from `PUBLIC`, `anon`, and `authenticated`. `site_revisions` has RLS enabled and no browser-facing policy.

## Revision, undo, idempotency and concurrency

Each successful approval records revision ID, client ID, previous revision, timestamp, source, message, operations, before/after snapshots, status, versions and idempotency key.

`editor_undo(...)` restores the latest non-undone transaction from `before_state`; no model is involved. Undo itself is append-only evidence and marks the restored revision undone.

- Duplicate `(client_id, idempotency_key)` returns the original result and creates no second revision.
- Row locking plus `editor_version` rejects stale tabs with a deterministic 409 path.
- Duplicate keys are rechecked after acquiring the row lock, covering concurrent retries.

## Tenant and model-failure safety

Every API entry first calls `require_client_access`. Media is loaded through a client-scoped query. Cross-client edit/undo/palette requests therefore fail before mutation. Invalid JSON, missing/no tool call, provider error, unsupported operation, bad values, forbidden palettes, low confidence and active HTML all produce no mutation and no revision.

## Evidence

- Frozen regression v1: 100/100 deterministic cases.
- Holdout/adversarial corpus: 366 requests retained; no fixture-specific tuning was added.
- Controlled real Kimi battery (25 Greek/Greeklish commands): schema 100%, intent 100%, operations 100%, argument values 84%, unsupported/authorization/capability rejection 100%, multi-operation 100%. Four hours cases failed strict argument accuracy; two lost meaningful temporal wording such as `tomorrow`.
- Python integration/security/transaction suite: **29/29 PASS**.
- Covered scenarios: three-operation rollback, phone persistence in store, deterministic undo, multi-submit idempotency, concurrent duplicate submission, stale revision, authorization boundary, capability rejection, unknown params, XSS, invalid time, duplicate media order, low confidence, malformed provider output and provider failure.
- Next production build: **PASS**, 22 pages generated.
- Real isolated staging transaction verifier: **8/8 PASS**.
- Real browser journey: **4/4 PASS**.
- Next production build: **PASS**, 22 pages generated.
- Resource leaks: focused suite runs with `ResourceWarning` promoted to error and exits cleanly. Browser harness kills its complete API/Next process trees.
- Whole repository: **151/168**, with 17 failures in theme-ranking expectations changed by the separate launch-theme work. Frontend `qa:editor` also has a stale marketing-copy assertion for `Logo Designer περιλαμβάνεται`; registry, trust, capabilities, profiles and vertical media gates pass.

## SQL/browser E2E status

The additive editor upgrades in `0004_ai_editor_atomic_upgrade.sql` and
`0005_editor_stale_error_code.sql` were applied only to the isolated
`vitrina-staging` project. Production was not queried with write credentials and
was not changed.

`scripts/verify_editor_staging.py` proves on real PostgreSQL/PostgREST:

- SECURITY INVOKER RPCs executable only by `service_role`;
- revision plus draft atomic commit;
- deliberate mid-transaction failure leaves neither revision nor draft change;
- idempotent duplicate submission;
- deterministic stale-version conflict;
- exact undo restoration and refresh query;
- draft/undo never change the published `sites` row.

`scripts/verify_editor_browser_staging.py` plus Playwright proves:

- proposal causes no database mutation;
- reject plus refresh causes no mutation;
- approve persists draft and refresh reads the same state;
- chat undo plus refresh restores the prior state;
- two real browser tabs starting from one version yield one commit and one 409,
  with no lost update.

## Bugs found and fixed

- Direct model-to-database mutation before customer approval.
- Content write and revision insert were separate, non-atomic operations.
- Old undo performed update then revision delete separately.
- The legacy `RevisionManager` entry point was removed so no caller can fall
  back to the old split write/delete path.
- Database editor store advertised no version/idempotency/commit implementation.
- Duplicate retries racing before a lock could hit the unique constraint; duplicate is now rechecked after lock acquisition.
- Phone accepted implausibly short values.
- Hours accepted impossible time tokens and markup.
- Media order accepted duplicate indices.
- Active HTML was escaped and stored instead of rejected.
- Frontend approval posted an arbitrary full content document; it now posts only the validated operation plan.

## Remaining blockers

1. The real-provider command gate is not green. `avrio kleinoume 3` and the
   correction `telika oxi 3, 4` became general hours and lost the temporal
   qualifier. This can publish a factually wrong schedule even though the
   operation schema is valid.
2. The complete repository suite is red because launch-theme ranking changed
   while its assertions still expect the previous themes (17 failures).
3. `sites/tests/editorFlow.mjs` expects old Logo Designer landing copy.

Do not deploy the editing engine or apply its migrations to production until the
hours semantics and complete-suite ownership are resolved.

## Decision

**EDITING ENGINE: BLOCKED BEFORE CONTROLLED STAGING ROLLOUT**

The database and browser vertical slice is proven. The blocker is now model
semantic accuracy for time-qualified hours, not persistence or transaction
safety. No production deployment or push was performed.
