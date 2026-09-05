# Conversational Editor QA Evidence

Date: 2026-08-25  
Scope: offline/test only. No staging or production writes. No deploy.

## Regression V1

- Corpus: 100 queries.
- Frozen SHA-256: `ae5437aea0a4f1d14578e23c8e7d5507d6c4c50e7f26c58b5bf3dba6939f6c50`.
- Schema validity: 100%.
- Intent accuracy: 100% against the deterministic v1 mock.
- Operation accuracy: 100% against the deterministic v1 mock.
- Important interpretation: this is a regression contract, not evidence of
  model generalization. The corpus includes 66 synthetic `dummy request`
  placeholders and must not be used for further planner tuning.

## Holdout / Adversarial

- Corpus: 366 inputs, separate from regression v1.
- Exact overlap with regression v1: 0.
- Categories: phone 40, hours 40, business fields 64, services 35,
  palettes 24, media 20, multi-operation 35, undo 24, follow-up 15,
  capability 5, unsupported 16, malformed 8, XSS 8, prompt injection 8,
  arbitrary code 8, authorization boundary 8, ambiguous 8.
- Corpus integrity and expected-plan validation: PASS.
- Real provider evaluation with Kimi (`kimi-k3`): **COMPLETE, 366/366 issued**.
- Structured output remained mandatory. Kimi uses `tool_choice=auto` because
  its reasoning mode rejects a forced function choice; responses without an
  `edit_site` tool call were rejected rather than parsed as free-form JSON.

| Metric | Kimi holdout |
|---|---:|
| Schema validity | 88.25% |
| Intent accuracy | 28.96% |
| Operation accuracy | 84.97% |
| Argument/value accuracy | 64.48% |
| Unsupported-operation rejection | 95.36% |
| Authorization-boundary rejection | 99.73% |
| Capability-rule enforcement | 100.00% |
| Multi-operation accuracy | 95.36% |

Provider reliability affected schema validity: the run observed HTTP 429
engine-overloaded responses, 60-second read timeouts, and responses without a
tool call. These remain counted as failures; no retries or holdout-specific
tuning were used. DeepSeek remains unevaluated because its configured key
failed preflight with HTTP 401.

Kimi rerun command:

```powershell
$env:PYTHONUTF8='1'
$env:AI_EDITOR_EVAL_PROVIDER='kimi'
python scripts\eval_ai_editor_holdout.py
```

## Integration

13 scenarios: PASS.

- message -> model -> strict `EditPlan` -> operation/capability validation ->
  mutation -> persisted in-memory revision -> preview content: PASS.
- provider unavailable: PASS, no mutation.
- malformed tool arguments: PASS, rejected.
- plain JSON without required tool call: PASS, rejected.
- unexpected top-level fields: PASS, rejected by Pydantic.
- unexpected operation parameters: PASS, rejected before mutation.

The integration store has the same version/idempotency/revision semantics
required of production, but is isolated in memory. It does not prove Supabase
transaction behavior.

## Transaction / Undo

- operation 2 of 3 invalid -> operation 1 not committed: PASS.
- revision persisted with before/after state: PASS.
- undo restores stored before-state without asking the model: PASS.
- duplicate idempotency key -> one mutation and one revision: PASS.
- five concurrent duplicate submissions -> one mutation/revision: PASS.
- stale expected version -> rejected with no second mutation: PASS.

## Security

- operation allowlist: PASS.
- unexpected parameters: PASS.
- strict top-level schema / unsupported schema version / confidence bounds:
  PASS.
- authorization rejection before model/mutation: PASS.
- theme palette capability enforcement: PASS.
- arbitrary JSON fallback disabled; structured tool call is mandatory: PASS.
- HTML is escaped by the deterministic engine: PASS.

The 366-case Kimi authorization-boundary score is 99.73%; capability
enforcement is 100%. This does not override the deterministic server-side
authorization and capability checks.

## Resource Leaks

PASS for the offline suites.

Command:

```powershell
python -W error::ResourceWarning -m unittest \
  tests.test_ai_editor \
  tests.test_ai_editor_holdout \
  tests.test_ai_editor_integration -v
```

Result: 26 tests passed in 0.026s; no Supabase deprecation warning, no SSL
socket warning, no leaked resource. The harness no longer imports or writes to
Supabase. Persistence is supplied explicitly through `InMemoryEditorStore`.

## Known Limitations / Production Blockers

1. **Kimi is not ready as the sole production editor model.** The honest
   holdout result is 28.96% intent accuracy and 64.48% argument accuracy, with
   provider overload/timeouts. The frozen corpus must not be used for tuning;
   improvements require general parser/planner design and a new holdout.
2. **Production atomic persistence is not implemented.** The existing endpoint
   still saves site content and creates a revision in separate Supabase calls.
   `DatabaseEditorStore.commit_edit()` deliberately raises `NotImplementedError`
   rather than pretending this is safe. Production needs one version-checked,
   idempotent database transaction/RPC covering content + revision.
3. The production HTTP endpoint has not yet been migrated to `EditingService`.
   Doing so before the atomic Supabase transaction exists would provide false
   safety.
4. Preview evidence in this pass is the deterministic updated content payload,
   not a Playwright browser screenshot.
5. Follow-up interpretation is represented in the holdout context contract,
   but cannot be measured against the real provider until authentication works.

## Commands Executed

```powershell
python -W error::ResourceWarning -m unittest tests.test_ai_editor tests.test_ai_editor_holdout tests.test_ai_editor_integration -v
python -m py_compile src\ai_editor\model.py src\ai_editor\engine.py src\ai_editor\service.py src\ai_editor\store.py scripts\eval_ai_editor_holdout.py
python scripts\eval_ai_editor_holdout.py
$env:AI_EDITOR_EVAL_PROVIDER='kimi'; python scripts\eval_ai_editor_holdout.py
```
