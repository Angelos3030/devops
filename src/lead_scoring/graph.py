"""Real (non-mocked) Lead Scoring graph — staging track.

Same shape as the isolated pilot (research/langgraph-poc/lead-scoring/
lead_scoring_graph.py), with two real changes:
  1. `providers.py`'s real DeepSeek/Claude calls replace the `_mock_*` functions.
  2. `kernel_gate()` reads the REAL registered manifest from staging's
     `agent_registry` (via kernel_registry.fetch_registered_manifest()) and
     the REAL `agent_installations` row (via fetch_installation()) instead of
     an in-memory stand-in. Since this pilot deliberately never creates an
     installation row (see kernel_registry.py docstring), evaluate_policy()
     will correctly return `blockers=['installation:missing']` until someone
     explicitly enables it — that is the intended current behavior.

CRM step remains draft-only: it builds a payload and returns
status="DRAFT_ONLY_NOT_WRITTEN". No code path in this file calls a real CRM.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TypedDict

from langgraph.graph import StateGraph, END, START
from langgraph.types import interrupt, RetryPolicy

from ..agency_kernel import CostEnvelope, TaskRequest, VersionedRef, evaluate_policy
from . import kernel_registry, providers

_URGENCY_WORDS = {"σήμερα", "τώρα", "επείγον", "άμεσα", "urgent", "asap"}


def _audit(state: dict, node: str, actor: str, action: str, detail: str = "") -> list[dict]:
    event = {"ts": datetime.now(timezone.utc).isoformat(), "node": node, "actor": actor,
              "action": action, "detail": detail}
    return [*state.get("audit_log", []), event]


class LeadState(TypedDict, total=False):
    tenant_id: str  # real workspace_id (clients.id) once a real caller supplies one
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
    usage_log: list[dict]  # real measured token usage per provider call
    halted_reason: str | None


def _usage(state: dict, entry: dict) -> list[dict]:
    return [*state.get("usage_log", []), entry]


def kernel_gate(*, capability: str, version: str, permissions: tuple[str, ...],
                 data_classes: tuple[str, ...], risk: str, provider: str,
                 tenant_id: str | None) -> dict:
    """Real evaluate_policy() call against the REAL registered manifest and
    the REAL (currently nonexistent, by design) installation row."""
    manifest = kernel_registry.fetch_registered_manifest()
    installation = kernel_registry.fetch_installation(tenant_id)
    task = TaskRequest(
        capability=VersionedRef(capability, version),
        requested_permissions=frozenset(permissions),
        data_classes=frozenset(data_classes),
        risk=risk, mode="execute", provider=provider,
        # Explicit, tight per-call budget — NOT the CostEnvelope default
        # (max_runtime_seconds=300), which would exceed enable_staging.py's
        # installation cap (120s) on every single call and permanently block
        # execution even once correctly enabled. Discovered by reviewing this
        # code before handoff, not by a failed live run.
        budget=CostEnvelope.from_mapping({"max_money_eur": 0, "max_tokens": 0, "max_runtime_seconds": 60}),
    )
    decision = evaluate_policy(
        manifest=manifest, installation=installation,
        entitlements={VersionedRef(capability, version)},
        enabled_dependencies=set(), task=task,
    )
    return decision.to_dict()


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
    reason = state.get("halted_reason") or "validation_failed"
    return {"halted_reason": reason,
            "audit_log": _audit(state, "halt_invalid", "system", "halted", reason)}


def enrich_classify_node(state: LeadState) -> dict:
    lead = state["raw_lead"]
    message = (lead.get("message") or "").lower()
    features = {
        "service_category": lead.get("service", "unknown"),
        "source_channel": lead.get("source", "web_form"),
        "message_length": len(message),
        "urgency_keyword_count": sum(1 for w in _URGENCY_WORDS if w in message),
        "has_budget_mention": any(tok in message for tok in ("€", "ευρώ", "budget", "τιμή")),
    }
    return {"features": features,
            "audit_log": _audit(state, "enrich_classify", "system", "features_extracted", str(features))}


def deepseek_score_node(state: LeadState) -> dict:
    decision = kernel_gate(
        capability="lead.capture", version="1", permissions=(),
        data_classes=("synthetic",), risk="low", provider="deepseek",
        tenant_id=state.get("tenant_id"),
    )
    if not decision["allowed"]:
        raise PermissionError(f"Kernel denied DeepSeek scoring: {decision['reasons']}")
    result = providers.deepseek_score(state["features"])
    usage = result.pop("_usage", {})
    return {
        "deepseek_score": result,
        "usage_log": _usage(state, {**usage, "node": "deepseek_score"}) if usage else state.get("usage_log", []),
        "audit_log": _audit(state, "deepseek_score", "deepseek", "scored",
                             f"score={result['score']} confidence={result['confidence']} "
                             f"kernel_reasons={decision['reasons']}"),
    }


def business_rules_node(state: LeadState) -> dict:
    score = state["deepseek_score"]["score"]
    confidence = state["deepseek_score"]["confidence"]
    tier = "hot" if score >= 70 else "warm" if score >= 40 else "cold"
    escalate_to_claude = confidence < 0.75 or tier == "hot"
    result = {"tier": tier, "score": score, "escalate_to_claude": escalate_to_claude}
    return {"business_rule": result,
            "audit_log": _audit(state, "business_rules", "system", "classified", str(result))}


def route_after_business_rules(state: LeadState) -> str:
    return "claude_review" if state["business_rule"]["escalate_to_claude"] else "crm_draft"


def claude_review_node(state: LeadState) -> dict:
    decision = kernel_gate(
        capability="lead.capture", version="1", permissions=(),
        data_classes=("personal",), risk="medium", provider="anthropic",
        tenant_id=state.get("tenant_id"),
    )
    if not decision["allowed"]:
        raise PermissionError(f"Kernel denied Claude review: {decision['reasons']}")
    review = providers.claude_review(state["raw_lead"], state["features"], state["business_rule"])
    usage = review.pop("_usage", {})
    return {
        "claude_review": review,
        "usage_log": _usage(state, {**usage, "node": "claude_review"}) if usage else state.get("usage_log", []),
        "audit_log": _audit(state, "claude_review", "claude", "reviewed",
                             f"{review['recommended_tier']} risk_flag={review['risk_flag']}"),
    }


def route_after_claude(state: LeadState) -> str:
    review = state.get("claude_review") or {}
    tier = state["business_rule"]["tier"]
    if tier == "hot" or review.get("risk_flag"):
        return "human_approval"
    return "crm_draft"


def human_approval_node(state: LeadState) -> dict:
    decision = interrupt({
        "question": "Approve CRM update for this lead?",
        "tenant_id": state["tenant_id"], "lead_id": state["lead_id"],
        "tier": state["business_rule"]["tier"], "claude_review": state.get("claude_review"),
    })
    approved = bool(decision.get("approved"))
    update: dict = {
        "approval": {"approved": approved, "note": decision.get("note", "")},
        "audit_log": _audit(state, "human_approval", "human",
                             "approved" if approved else "rejected", decision.get("note", "")),
    }
    if not approved:
        # halt_invalid_node's own default ("validation_failed") is reused by
        # BOTH the real-validation-failure path (route_after_validate) and
        # this approval-rejection path, since neither previously set
        # halted_reason before reaching halt_invalid_node. That made the
        # audit trail wrongly claim a rejected-by-human lead had failed
        # input validation. Set the real reason here so halt_invalid_node's
        # `state.get("halted_reason") or "validation_failed"` picks THIS
        # value up instead of falling through to the generic default.
        update["halted_reason"] = "human_rejected"
    return update


def route_after_approval(state: LeadState) -> str:
    approval = state.get("approval")
    if approval is not None and not approval.get("approved"):
        return "halt_invalid"
    return "crm_draft"


def crm_draft_node(state: LeadState) -> dict:
    decision = kernel_gate(
        capability="lead.capture", version="1", permissions=("crm.write",),
        data_classes=("personal",), risk="low", provider="anthropic",
        tenant_id=state.get("tenant_id"),
    )
    if not decision["allowed"]:
        raise PermissionError(f"Kernel denied CRM draft: {decision['reasons']}")
    draft = {
        "tenant_id": state["tenant_id"], "lead_id": state["lead_id"],
        "tier": state["business_rule"]["tier"], "score": state["business_rule"]["score"],
        "note": (state.get("claude_review") or {}).get("rationale", "auto-classified, no escalation needed"),
        "status": "DRAFT_ONLY_NOT_WRITTEN",  # no code path here calls a real CRM
    }
    return {"crm_draft": draft,
            "audit_log": _audit(state, "crm_draft", "system", "draft_built", draft["status"])}


def audit_node(state: LeadState) -> dict:
    return {"audit_log": _audit(state, "audit", "system", "run_complete")}


def build_graph(checkpointer):
    g = StateGraph(LeadState)
    g.add_node("validate", validate_node)
    g.add_node("halt_invalid", halt_invalid_node)
    g.add_node("enrich_classify", enrich_classify_node)
    g.add_node("deepseek_score", deepseek_score_node,
               retry_policy=RetryPolicy(max_attempts=3,
                                         retry_on=(providers.LeadScoringProviderError,), initial_interval=1.0))
    g.add_node("business_rules", business_rules_node)
    g.add_node("claude_review", claude_review_node,
               retry_policy=RetryPolicy(max_attempts=3,
                                         retry_on=(providers.LeadScoringProviderError,), initial_interval=1.0))
    g.add_node("human_approval", human_approval_node)
    g.add_node("crm_draft", crm_draft_node)
    g.add_node("audit", audit_node)

    g.add_edge(START, "validate")
    g.add_conditional_edges("validate", route_after_validate,
                             {"enrich_classify": "enrich_classify", "halt_invalid": "halt_invalid"})
    g.add_edge("halt_invalid", END)
    g.add_edge("enrich_classify", "deepseek_score")
    g.add_edge("deepseek_score", "business_rules")
    g.add_conditional_edges("business_rules", route_after_business_rules,
                             {"claude_review": "claude_review", "crm_draft": "crm_draft"})
    g.add_conditional_edges("claude_review", route_after_claude,
                             {"human_approval": "human_approval", "crm_draft": "crm_draft"})
    g.add_conditional_edges("human_approval", route_after_approval,
                             {"crm_draft": "crm_draft", "halt_invalid": "halt_invalid"})
    g.add_edge("crm_draft", "audit")
    g.add_edge("audit", END)
    return g.compile(checkpointer=checkpointer)
