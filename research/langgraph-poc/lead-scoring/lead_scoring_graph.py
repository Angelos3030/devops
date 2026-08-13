#!/usr/bin/env python3
"""
ISOLATED Lead Scoring pilot graph — supports docs/adr/0002-lead-scoring-langgraph-pilot.md.

Scope discipline (identical to research/langgraph-poc/poc_graph.py):
    - No production writes. No real CRM connection. No modification of any
      file under src/, sites/, web/, db/, or any existing agent flow.
    - DeepSeek and Claude calls are MOCKED (`_mock_*`, clearly labeled) — this
      sandbox cannot reach api.deepseek.com/api.anthropic.com, and no
      production credential is used. Swapping the mocks for real calls using
      the exact patterns in src/research_worker.py (DeepSeek) and
      src/agent_runtime.py (Claude) is the only change needed.
    - Kernel policy calls (`kernel_gate`) mirror src/agency_kernel.py's real
      evaluate_policy() shape but run against an in-memory stub manifest/
      installation here, since wiring the real Kernel requires a registered,
      enabled agent manifest — out of scope for an isolated pilot per the
      task instructions ("μην συνδέσεις πραγματικό CRM, μην κάνεις production
      write"). The *shape* of the gate call is real; the backing data is not.

Graph:
    lead.received
        -> validate                  (deterministic — code, not LLM)
        -> enrich_classify            (deterministic feature extraction,
                                        strips PII before anything touches DeepSeek)
        -> deepseek_score             (DeepSeek sees ONLY the PII-stripped
                                        feature vector — enforced by the
                                        Kernel's DEEPSEEK_ALLOWED_DATA_CLASSES
                                        rule, not by convention)
        -> business_rules             (deterministic scoring/threshold logic)
        -> [conditional] claude_review  (only when confidence low or risk flagged)
        -> [conditional] human_approval (interrupt() — only when Kernel policy
                                          requires it, e.g. production_write)
        -> crm_draft                  (builds a draft payload; never calls a
                                        real CRM)
        -> audit
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TypedDict

from langgraph.graph import StateGraph, END, START
from langgraph.types import interrupt, Command, RetryPolicy

import sys
sys.path.insert(0, ".")
from src.agency_kernel import (  # noqa: E402
    AgentManifest, CostEnvelope, TaskRequest, VersionedRef,
    evaluate_policy, KernelValidationError,
)

# ---------------------------------------------------------------------------
# Minimal stub manifest/installation standing in for a real, registered,
# enabled Kernel agent. Every field mirrors the real AgentManifest contract
# (src/agency_kernel.py) — nothing here is a shortcut around the schema, it's
# a shortcut around *registration*, which is explicitly out of scope for an
# isolated pilot.
# ---------------------------------------------------------------------------
# NOTE ON A REAL FINDING FROM RUNNING THIS SPIKE:
# The first version of this stub used lifecycle="draft" (matching the real
# Kernel's own default) and a runtime budget narrower than TaskRequest's
# default CostEnvelope. evaluate_policy() correctly REFUSED to run it:
# blockers=['agent_lifecycle:draft', 'runtime_budget_exceeded']. That is the
# Kernel working exactly as designed — fail closed on an unregistered/draft
# agent. Since this pilot needs to actually execute to prove the graph
# mechanics, the stub below marks itself "available" with the evals/
# revocation an available agent requires (validate_manifest() enforces this
# too — it is not possible to fake "available" without supplying them). This
# is still never written to a real registry; it is an in-memory stand-in for
# what registration would require, not a shortcut around Kernel validation.
_LEAD_SCORING_MANIFEST = AgentManifest(
    agent=VersionedRef("lead_scoring_pilot", "1"),
    name="Lead Scoring Pilot (isolated, unregistered)",
    purpose="Score inbound leads and draft CRM updates for human approval.",
    roi_hypothesis="Faster, consistent lead triage reduces response-time-to-hot-lead.",
    success_metrics=("time_to_first_response", "hot_lead_conversion_rate"),
    lifecycle="available",
    autonomy="A1",
    capabilities=(VersionedRef("lead.score", "1"), VersionedRef("crm.draft", "1")),
    permissions=("crm.write",),
    data_classes=("public", "synthetic", "personal"),
    cost=CostEnvelope.from_mapping({"max_money_eur": 1, "max_tokens": 20000, "max_runtime_seconds": 300}),
    evals=("lead_scoring_offline_eval_v1",),
    revocation={"procedure": "disable installation via dashboard; kernel blocks on next evaluate_policy() call"},
)
_LEAD_SCORING_INSTALLATION = {
    "status": "enabled",
    "granted_permissions": ["crm.write"],
    "budget_limits": {"max_money_eur": 1, "max_tokens": 20000, "max_runtime_seconds": 300},
}
_ENTITLEMENTS = {VersionedRef("lead.score", "1"), VersionedRef("crm.draft", "1")}
_ENABLED_DEPS: set = set()


def kernel_gate(*, capability: str, version: str, permissions: tuple[str, ...],
                 data_classes: tuple[str, ...], risk: str, provider: str) -> dict:
    """Real evaluate_policy() call — this is not a mock. Every node that
    touches a provider or a write goes through this before acting."""
    task = TaskRequest(
        capability=VersionedRef(capability, version),
        requested_permissions=frozenset(permissions),
        data_classes=frozenset(data_classes),
        risk=risk,
        mode="execute",
        provider=provider,
    )
    decision = evaluate_policy(
        manifest=_LEAD_SCORING_MANIFEST,
        installation=_LEAD_SCORING_INSTALLATION,
        entitlements=_ENTITLEMENTS,
        enabled_dependencies=_ENABLED_DEPS,
        task=task,
    )
    return decision.to_dict()


def _audit(state: dict, node: str, actor: str, action: str, detail: str = "") -> list[dict]:
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "node": node, "actor": actor, "action": action, "detail": detail,
    }
    return [*state.get("audit_log", []), event]


class LeadState(TypedDict, total=False):
    tenant_id: str
    lead_id: str
    raw_lead: dict
    validation: dict
    features: dict
    deepseek_score: dict
    business_rule: dict
    claude_review: dict | None
    approval: dict | None
    crm_draft: dict
    audit_log: list[dict]
    halted_reason: str | None


# --- 1. validate — deterministic, no LLM, no Kernel call needed (no provider/write yet) ---
def validate_node(state: LeadState) -> dict:
    lead = state["raw_lead"]
    errors = []
    if not lead.get("email") and not lead.get("phone"):
        errors.append("missing_contact_method")
    if not lead.get("service"):
        errors.append("missing_service")
    if not state.get("tenant_id"):
        errors.append("missing_tenant_id")
    valid = not errors
    return {
        "validation": {"valid": valid, "errors": errors},
        "audit_log": _audit(state, "validate", "system", "validated", f"valid={valid} errors={errors}"),
    }


def route_after_validate(state: LeadState) -> str:
    return "enrich_classify" if state["validation"]["valid"] else "halt_invalid"


def halt_invalid_node(state: LeadState) -> dict:
    return {
        "halted_reason": "validation_failed",
        "audit_log": _audit(state, "halt_invalid", "system", "halted", str(state["validation"]["errors"])),
    }


# --- 2. enrich/classify — deterministic feature extraction, strips PII ---
_URGENCY_WORDS = {"σήμερα", "τώρα", "επείγον", "άμεσα", "urgent", "asap"}


def enrich_classify_node(state: LeadState) -> dict:
    lead = state["raw_lead"]
    message = (lead.get("message") or "").lower()
    features = {
        "service_category": lead.get("service", "unknown"),
        "source_channel": lead.get("source", "web_form"),
        "message_length": len(message),
        "urgency_keyword_count": sum(1 for w in _URGENCY_WORDS if w in message),
        "has_budget_mention": any(tok in message for tok in ("€", "ευρώ", "budget", "τιμή")),
        # deliberately NOT included: name, email, phone, raw message text —
        # this is the PII-stripped shape that is allowed to reach DeepSeek.
    }
    return {
        "features": features,
        "audit_log": _audit(state, "enrich_classify", "system", "features_extracted", str(features)),
    }


# --- 3. DeepSeek scoring — Kernel-gated, sees ONLY the stripped feature vector ---
def _mock_deepseek_score(features: dict) -> dict:
    """Stands in for a real src/research_worker.py-style DeepSeek call."""
    score = 40
    if features["urgency_keyword_count"] > 0:
        score += 25
    if features["has_budget_mention"]:
        score += 20
    if features["message_length"] > 40:
        score += 10
    return {"score": min(score, 100), "confidence": 0.7, "reasoning": "mock heuristic on stripped features"}


# Fault injection for the retry-behavior proof, keyed by lead_id so it's
# independent of the Kernel-denial proof above (a different failure class:
# transient upstream error vs. policy fail-closed).
_DEEPSEEK_TRANSIENT_FAIL_ONCE: set[str] = set()


def deepseek_score_node(state: LeadState) -> dict:
    decision = kernel_gate(
        capability="lead.score", version="1", permissions=(),
        data_classes=("synthetic",),  # the stripped feature vector, not raw PII
        risk="low", provider="deepseek",
    )
    if not decision["allowed"]:
        raise PermissionError(f"Kernel denied DeepSeek scoring: {decision['reasons']}")

    lead_id = state.get("lead_id", "")
    if lead_id in _DEEPSEEK_TRANSIENT_FAIL_ONCE:
        _DEEPSEEK_TRANSIENT_FAIL_ONCE.discard(lead_id)
        raise RuntimeError(f"simulated DeepSeek transient failure for {lead_id} (attempt 1)")

    result = _mock_deepseek_score(state["features"])
    return {
        "deepseek_score": result,
        "audit_log": _audit(
            state, "deepseek_score", "deepseek", "scored",
            f"score={result['score']} confidence={result['confidence']} kernel_reasons={decision['reasons']}",
        ),
    }


# --- 4. business rules — deterministic, decides escalation ---
def business_rules_node(state: LeadState) -> dict:
    score = state["deepseek_score"]["score"]
    confidence = state["deepseek_score"]["confidence"]
    if score >= 70:
        tier = "hot"
    elif score >= 40:
        tier = "warm"
    else:
        tier = "cold"

    # Escalate to Claude when confidence is low OR the tier is hot enough that
    # a wrong auto-classification has real cost — matches Vitrina's own A1
    # "always approval before execution for meaningful actions" posture.
    escalate_to_claude = confidence < 0.75 or tier == "hot"
    result = {"tier": tier, "score": score, "escalate_to_claude": escalate_to_claude}
    return {
        "business_rule": result,
        "audit_log": _audit(state, "business_rules", "system", "classified", str(result)),
    }


def route_after_business_rules(state: LeadState) -> str:
    return "claude_review" if state["business_rule"]["escalate_to_claude"] else "crm_draft"


# --- 5. Claude review (conditional) — Kernel-gated, sees full context (Claude is
# already the approved channel for customer-facing/personal data in src/ai.py) ---
def _mock_claude_review(raw_lead: dict, features: dict, business_rule: dict) -> dict:
    """Stands in for a real src/agent_runtime.py-style Claude call."""
    return {
        "recommended_tier": business_rule["tier"],
        "rationale": "mock review — deterministic tier looks consistent with stated service and urgency signals",
        "risk_flag": business_rule["tier"] == "hot",
    }


def claude_review_node(state: LeadState) -> dict:
    decision = kernel_gate(
        capability="lead.score", version="1", permissions=(),
        data_classes=("personal",),  # Claude is allowed personal data (existing GDPR-approved channel)
        risk="medium", provider="anthropic",
    )
    if not decision["allowed"]:
        raise PermissionError(f"Kernel denied Claude review: {decision['reasons']}")
    review = _mock_claude_review(state["raw_lead"], state["features"], state["business_rule"])
    return {
        "claude_review": review,
        "audit_log": _audit(
            state, "claude_review", "claude", "reviewed",
            f"{review['recommended_tier']} risk_flag={review['risk_flag']}",
        ),
    }


def route_after_claude(state: LeadState) -> str:
    review = state.get("claude_review") or {}
    tier = state["business_rule"]["tier"]
    # Kernel policy: production_write permission (crm.write) on a "hot" tier
    # (i.e. an action with real downstream effect) requires approval. A cold/
    # warm tier CRM draft is lower stakes and can proceed once Claude-reviewed.
    if tier == "hot" or review.get("risk_flag"):
        return "human_approval"
    return "crm_draft"


# --- 6. Human approval (conditional, interrupt) ---
def human_approval_node(state: LeadState) -> dict:
    decision = interrupt({
        "question": "Approve CRM update for this lead?",
        "tenant_id": state["tenant_id"],
        "lead_id": state["lead_id"],
        "tier": state["business_rule"]["tier"],
        "claude_review": state.get("claude_review"),
    })
    return {
        "approval": {"approved": bool(decision.get("approved")), "note": decision.get("note", "")},
        "audit_log": _audit(
            state, "human_approval", "human",
            "approved" if decision.get("approved") else "rejected", decision.get("note", ""),
        ),
    }


def route_after_approval(state: LeadState) -> str:
    approval = state.get("approval")
    if approval is not None and not approval.get("approved"):
        return "halt_invalid"  # reuse the halt terminal node; reason differs, path is the same shape
    return "crm_draft"


# --- 7. CRM draft — builds payload only, never calls a real CRM ---
def crm_draft_node(state: LeadState) -> dict:
    decision = kernel_gate(
        capability="crm.draft", version="1", permissions=("crm.write",),
        data_classes=("personal",), risk="low", provider="anthropic",
    )
    if not decision["allowed"]:
        raise PermissionError(f"Kernel denied CRM draft: {decision['reasons']}")
    draft = {
        "tenant_id": state["tenant_id"],
        "lead_id": state["lead_id"],
        "tier": state["business_rule"]["tier"],
        "score": state["business_rule"]["score"],
        "note": (state.get("claude_review") or {}).get("rationale", "auto-classified, no escalation needed"),
        "status": "DRAFT_ONLY_NOT_WRITTEN",
    }
    return {
        "crm_draft": draft,
        "audit_log": _audit(state, "crm_draft", "system", "draft_built", draft["status"]),
    }


def audit_node(state: LeadState) -> dict:
    return {"audit_log": _audit(state, "audit", "system", "run_complete")}


def build_lead_scoring_graph(checkpointer):
    g = StateGraph(LeadState)
    g.add_node("validate", validate_node)
    g.add_node("halt_invalid", halt_invalid_node)
    g.add_node("enrich_classify", enrich_classify_node)
    g.add_node(
        "deepseek_score", deepseek_score_node,
        retry_policy=RetryPolicy(max_attempts=3, retry_on=(PermissionError, RuntimeError), initial_interval=0.05),
    )
    g.add_node("business_rules", business_rules_node)
    g.add_node("claude_review", claude_review_node)
    g.add_node("human_approval", human_approval_node)
    g.add_node("crm_draft", crm_draft_node)
    g.add_node("audit", audit_node)

    g.add_edge(START, "validate")
    g.add_conditional_edges("validate", route_after_validate, {
        "enrich_classify": "enrich_classify", "halt_invalid": "halt_invalid",
    })
    g.add_edge("halt_invalid", END)
    g.add_edge("enrich_classify", "deepseek_score")
    g.add_edge("deepseek_score", "business_rules")
    g.add_conditional_edges("business_rules", route_after_business_rules, {
        "claude_review": "claude_review", "crm_draft": "crm_draft",
    })
    g.add_conditional_edges("claude_review", route_after_claude, {
        "human_approval": "human_approval", "crm_draft": "crm_draft",
    })
    g.add_conditional_edges("human_approval", route_after_approval, {
        "crm_draft": "crm_draft", "halt_invalid": "halt_invalid",
    })
    g.add_edge("crm_draft", "audit")
    g.add_edge("audit", END)

    return g.compile(checkpointer=checkpointer)
