# Vitrina — Reusable Architecture Patterns from Agent Discovery

**Generated:** 2026-08-12 12:00 UTC  
**Source Analysis:** Citadel, Agent Memory Guard, Lead Score Flow, GenAI_Agents, PII Sanitizer  

This document captures **framework-agnostic architectural patterns** worth adopting into Vitrina's future Agent OS.

---

## 1. Router-Based Orchestration (Citadel)

### Pattern Description
Instead of agents deciding what to do, a **router** classifies incoming requests into tiers and routes to the cheapest execution path.

```
User Request
    ↓
Tier 1: Pattern Match (zero tokens) → direct edit, log analysis, simple lookup
    ↓ if no match
Tier 2: Session State (zero tokens) → check if resuming active campaign
    ↓ if no match
Tier 3: Keyword Lookup (zero tokens) → match request against skill keywords
    ↓ if no match
Tier 4: LLM Classification (~500 tokens) → complex reasoning about intent
    ↓
Route to appropriate execution path (skill, marshal, archon, fleet)
```

### Why Adopt
- **Cost efficiency:** Most requests (70-90%) resolve without model inference
- **Latency:** Tier 1-3 are instant; only complex cases wait for LLM
- **Debuggability:** Exact routing decision is auditable and explainable

### Vitrina Application
- Route agent requests through 4-tier classifier before spawning reasoning agents
- Tier 1: Simple queries ("what's my lead count?") → database query
- Tier 2: Resume active campaign (marketing batch in progress) → restore state
- Tier 3: Keyword trigger ("score leads", "send email") → invoke skill
- Tier 4: Novel requests → agent reasoning

### Implementation Notes
- Router itself can be a small LLM call, or deterministic state machine
- Requires clear separation of concerns (pure routing vs. execution)
- Audit every routing decision for transparency

---

## 2. Campaign Persistence (Citadel)

### Pattern Description
**Multi-session workflows are tracked as campaigns with durable state.** When a workflow spans multiple sessions or hits context limits, the campaign state survives.

```
Session N: Start "Q3 Marketing Campaign"
  ├─ Phase: Content Strategy (completed, state saved)
  ├─ Phase: Asset Creation (in progress, partial results saved)
  └─ Phase: Distribution (pending)

Context Reset / Session Boundary
  ↓

Session N+1: Resume "Q3 Marketing Campaign"
  ├─ Load campaign state from persistent store
  ├─ Resume Phase: Asset Creation (from checkpoint)
  └─ Continue uninterrupted
```

### Why Adopt
- **Long-running workflows:** Don't restart from scratch on session boundaries
- **Agent memory:** Decisions and discoveries persist
- **Cost efficiency:** Avoid redundant work across sessions

### Vitrina Application
- Marketing campaigns (multi-week content + distribution)
- Lead nurture workflows (multi-month engagement)
- Customer onboarding sequences

### Implementation Notes
- Save decision history (why was choice X made)
- Checkpoint frequently (after each major step)
- Make resumption deterministic (same inputs → continue from saved state, not restart)
- Include rollback capability (revert to known-good state if agent goes off-course)

---

## 3. Fail-Closed Security (PII Sanitizer)

### Pattern Description
**When uncertain, deny rather than allow.** Default to block/redact/quarantine; only allow when confidence is high.

```
Before: Agent encounters "email: john@example.com"
  ├─ Rule-based detection: Is this PII? (sometimes wrong)
  └─ Decision: allow or redact?

Fail-Closed: Assume it's PII unless proven otherwise
  ├─ Redact by default
  ├─ Only allow if operator explicitly approves
  └─ Log decision for audit
```

### Why Adopt
- **Bias toward safety:** Conservative approach prevents accidental data leakage
- **Compliance:** Better to redact too much than leak customer data
- **Trust:** Users can trust autonomous actions have safety guardrails

### Vitrina Application
- PII detection (emails, phone, SSN, credit card)
- Data access approval (agent requests customer data)
- Secret isolation (API keys, credentials)

### Implementation Notes
- Make fail-closed explicit in config (not default `allow`)
- Provide "whitelist" mechanism for known-safe cases
- Log every redaction for forensics
- Review redaction accuracy regularly (may over-redact initially)

---

## 4. Memory Policy-as-Code (Agent Memory Guard)

### Pattern Description
**Security policies for agent memory are declared in YAML, not hardcoded.** A policy engine evaluates all memory operations against rules.

```yaml
version: 1
default_action: allow

protected_keys:
  - system.*
  - identity.role

immutable_keys:
  - identity.user_id
  - audit.timestamp

rules:
  - name: block_prompt_injection
    on: prompt_injection
    action: block
    
  - name: redact_emails
    on: sensitive_data
    action: redact
    regex: /[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/
    
  - name: block_protected_keys
    on: protected_key
    action: block
```

### Why Adopt
- **Declarative security:** Policies are auditable and updateable without code changes
- **Flexibility:** Different agents/environments can have different policies
- **Audit trail:** Every policy decision is logged with reason

### Vitrina Application
- Define immutable fields (user_id, timestamps, audit markers)
- Define protected keys (system config, model instructions)
- Define detection rules (prompt injection, PII, size anomalies)
- Define actions (allow, redact, block, quarantine)

### Implementation Notes
- Version your policies (git track YAML)
- Test policy changes before rolling out (test suite for detection rules)
- Provide admin interface to enable/disable rules without redeploying

---

## 5. Human Approval Gates (Lead Score Flow)

### Pattern Description
**Mark tasks/decisions as requiring human review.** Agent pauses execution until human approves.

```
Agent: "I've scored these 5 leads. Shall I email them?"
  ├─ Pause execution
  ├─ Present decision to human: [Approve] [Reject] [Modify]
  ├─ Wait for response
  └─ Resume with human decision

Outcomes:
  ├─ Approve → send emails as planned
  ├─ Reject → skip emails, move to next task
  └─ Modify → adjust decision, then send
```

### Why Adopt
- **Compliance & accountability:** Autonomous action is still human-responsible
- **User control:** Users stay in the loop on important decisions
- **Learning:** System learns from human corrections

### Vitrina Application
- Before sending emails (brand voice, customer relationship)
- Before posting to social media (brand reputation risk)
- Before updating customer CRM (data integrity)
- Before charging customer (financial impact)

### Implementation Notes
- Make approval decision fast (<30 sec interface)
- Provide context (what decision is being made, why)
- Log decision + human metadata (who approved, when, notes)
- Set approval timeout (if no response in 24h, default action)

---

## 6. Source-Class Provenance Tracking (Agent Memory Guard)

### Pattern Description
**Every memory write carries metadata about where the data originated.** Four classes: USER_INPUT, EXTERNAL_TOOL, AGENT_AUTHORED, SYSTEM.

```
Agent writes to memory:
  guard.write(
    "lead.qualification",
    "High-intent, ready to pitch",
    source_class=SourceClass.AGENT_AUTHORED,
    receipt_uri="satp://receipts/01HE4G9Y5R7Q8K2A3B0CWX6F8M"
  )
  
Later, during threat detection:
  Detector checks: "Is this memory from external source (higher risk)?"
  → source_class = AGENT_AUTHORED (internal, lower risk)
  → Detection rule: less aggressive threshold
```

### Why Adopt
- **Threat modeling:** External data is higher risk than agent-authored data
- **Forensics:** Trace where decision came from if something goes wrong
- **SIEM correlation:** Feed metadata to security information & event management system

### Vitrina Application
- Flag data from customer inputs (higher risk of manipulation)
- Track data from tool API responses (verify against expectations)
- Distinguish agent conclusions (lower risk, but verify reasoning)
- Mark system-generated data (configurations, defaults)

### Implementation Notes
- Define four source classes clearly (avoid ambiguity)
- Emit SecurityEvent for every write (structured logging)
- Adjust threat detection rules based on source_class
- Export metadata to SIEM (Splunk, Datadog, etc.)

---

## 7. Lifecycle Hooks (Citadel)

### Pattern Description
**Agents emit 29 lifecycle events** (pre/post/error handlers) at key decision points. Hooks let you insert safety checks without modifying core agent logic.

```
Agent Lifecycle Events:
  pre_decision
    ├─ Hook: Validate decision against policy
    └─ Hook: Check approval status
  ↓
  execute_decision
  ↓
  post_decision
    ├─ Hook: Log decision with audit metadata
    ├─ Hook: Emit metrics
    └─ Hook: Trigger downstream actions
  ↓
  error
    ├─ Hook: Log failure
    ├─ Hook: Attempt recovery
    └─ Hook: Alert operator if unrecoverable
```

### Why Adopt
- **Non-invasive safety:** Add guardrails without touching agent code
- **Observability:** Comprehensive event stream for monitoring
- **Extensibility:** Hooks are injection points for custom behavior

### Vitrina Application
- `pre_destructive_action` hook: Require approval before delete/publish/charge
- `pre_memory_write` hook: Sanitize PII before persisting
- `post_decision` hook: Log to audit trail
- `on_error` hook: Backoff and retry with exponential delay
- `on_token_budget_exceeded` hook: Stop work, alert operator

### Implementation Notes
- Keep hooks fast (they're in the critical path)
- Make hooks idempotent (safe to call multiple times)
- Provide hook ordering (some must run before others)
- Document every hook (what it's called for, side effects)

---

## 8. Worktree Isolation (Citadel)

### Pattern Description
**Parallel agents execute in isolated git worktrees.** Each agent gets a clean copy of the codebase, avoiding conflicts and enabling safe rollback.

```
Main Worktree (HEAD)
  │
  ├─ Agent 1 Worktree (isolated git checkout)
  │   ├─ API implementation attempt
  │   └─ Can fail independently
  │
  ├─ Agent 2 Worktree (isolated git checkout)
  │   ├─ Tests attempt
  │   └─ Can fail independently
  │
  └─ Agent 3 Worktree (isolated git checkout)
      ├─ Docs attempt
      └─ Can fail independently

After: Merge successful changes from Agent 1 & 3, skip Agent 2
```

### Why Adopt
- **Parallelism:** Multiple agents work simultaneously on same codebase
- **Safety:** Agent failures don't corrupt main branch
- **Rollback:** If merge fails, discard worktree

### Vitrina Application
- Parallel website generation (design agent + content agent + SEO agent all working)
- Parallel marketing campaign prep (strategy + asset creation + scheduling)
- Multi-agent code generation (backend + frontend + tests)

### Implementation Notes
- Use git worktree (built into git, no external dependency)
- Each agent gets unique worktree path
- Merge strategy: cherrypick successful changes
- Clean up worktrees after completion

---

## 9. Circuit Breaker for Failure Spirals

### Pattern Description
**Stop agent work if repeated failures exceed threshold.** Prevents infinite retries wasting tokens/time.

```
Agent attempts task:
  Attempt 1: Fails (backoff 1s)
  Attempt 2: Fails (backoff 2s)
  Attempt 3: Fails (backoff 4s)
  Attempt 4: Fails
  
Circuit Breaker: Threshold exceeded
  → STOP work
  → Alert operator: "Agent stuck, manual intervention needed"
  → Discard partial results
```

### Why Adopt
- **Cost control:** Prevent runaway token spend
- **Reliability:** Fail fast rather than hang indefinitely
- **Observability:** Alert operator to actual problems (not infinite retries)

### Vitrina Application
- If social media API is down, don't retry forever
- If lead qualification repeatedly fails, stop and alert
- If email sending has 5% failure rate, pause and investigate

### Implementation Notes
- Make threshold tunable (different agents may have different tolerances)
- Log circuit breaker events with context (what task, why failed)
- Provide manual override (allow operator to retry after investigation)
- Reset circuit after time period (T=1h) in case transient failure

---

## 10. Structured Event Logging

### Pattern Description
**All agent decisions emit structured events, not free-text logs.** Events include: timestamp, agent, action, input, output, approval, source_class, decision_id.

```json
{
  "event_type": "agent_decision",
  "timestamp": "2026-08-12T12:34:56Z",
  "agent_id": "lead-scorer-v1",
  "decision": "score_lead",
  "input": {"lead_id": "L-12345", "source": "web_form"},
  "output": {"score": 87, "tier": "high-intent"},
  "approved": true,
  "approval_metadata": {"approver": "user@vitrina.com", "time_to_approve": "2.3s"},
  "source_class": "user_input",
  "event_id": "evt-2026-08-12-98765",
  "trace_id": "tr-campaign-q3-marketing-001"
}
```

### Why Adopt
- **Searchability:** Query events by agent, action, time, approval status
- **Compliance:** Full audit trail of autonomous actions
- **Debugging:** Trace decision lineage (why did agent choose X)
- **Analytics:** Aggregate metrics (approval rate, latency, error rate)

### Vitrina Application
- Feed to SIEM (Splunk, Datadog) for security & compliance
- Dashboard for operator visibility (what agents did today)
- Postmortem investigation (what led to customer issue)

### Implementation Notes
- Use standard logging format (JSON, not free text)
- Include trace ID for request tracing (link all events in a campaign)
- Emit events BEFORE action (approval) and AFTER (success/failure)
- Index events for fast querying (Elasticsearch, Splunk, S3 with Athena)

---

## Adoption Checklist

Before finalizing Vitrina's architecture, ensure you've adopted:

- [ ] Router-based orchestration (4-tier classification)
- [ ] Campaign persistence (durable multi-session state)
- [ ] Fail-closed security (default deny, explicit allow)
- [ ] Memory policy-as-code (YAML policies)
- [ ] Human approval gates (pause for important decisions)
- [ ] Source-class provenance (track data origin)
- [ ] Lifecycle hooks (29 event points for extensibility)
- [ ] Worktree isolation (parallel agent safety)
- [ ] Circuit breaker (stop on failure spiral)
- [ ] Structured event logging (JSON events for audit/analytics)

**Quick Win:** Start with #3 (fail-closed security) and #10 (structured logging). Both are low-risk, high-value.

---

## Framework Recommendations

Based on patterns, here's our ranking of available frameworks for Vitrina's core orchestration:

| Rank | Framework | Router | Campaigns | Hooks | Parallel | Why |
|------|-----------|--------|-----------|-------|----------|-----|
| 1 | **Citadel** | ✓ (4-tier) | ✓ | ✓ (29 hooks) | ✓ (worktrees) | All patterns native |
| 2 | **LangGraph** | ✗ | ✗ | ✓ (events) | ✓ | Good orchestration, missing router/campaigns |
| 3 | **CrewAI** | ✗ | ✗ | ✗ | ✓ (parallel crews) | Simple, lacks infrastructure |
| 4 | **Custom** | ✓ (build) | ✓ (build) | ✓ (build) | ✓ (build) | Full control, 3-4 months engineering |

**Recommendation:** Citadel is the clear winner — it natively implements 7/10 patterns. Build only what's missing (Vitrina-specific agents, memory backends).

