"""Deterministic Agency Kernel contracts for Vitrina Stage 4A.

This module does not call an AI provider and does not execute production actions.
It validates installable agent manifests, resolves versioned capabilities and
decides whether a future execution may proceed or must be blocked/approved.

`clients.id` is the Stage-4 workspace identifier. This keeps the kernel on the
existing tenancy model instead of introducing a parallel framework.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
import re
from typing import Any, Iterable, Mapping


KERNEL_VERSION = "4A.1"
ACTION_QUEUE_SCHEMA_VERSION = "1.0"

_KEY_RE = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
_VERSION_RE = re.compile(r"^[1-9][0-9]*(?:\.[0-9]+){0,2}$")
_LIFECYCLES = {"draft", "available", "deprecated", "revoked"}
_INSTALLATION_STATES = {"installed", "enabled", "disabled", "revoked"}
_AUTONOMY = {"A0", "A1", "A2", "A3"}
_APPROVAL_POLICIES = {"none", "client", "operator", "dual"}
_DATA_CLASSES = {"public", "repository", "synthetic", "internal", "personal", "sensitive"}
_SEPARATION_DIMENSIONS = {"complexity", "risk", "permissions", "context", "evaluation"}

# A task requesting one of these permissions can never run without an approval.
PRODUCTION_WRITE_PERMISSIONS = frozenset({
    "ads.spend", "billing.charge", "content.publish", "customer.message",
    "data.delete", "domain.manage", "pricing.write", "refund.issue",
})

DEEPSEEK_ALLOWED_DATA_CLASSES = frozenset({"public", "repository", "synthetic"})


class KernelValidationError(ValueError):
    """A manifest or task violates a deterministic kernel contract."""


@dataclass(frozen=True, order=True)
class VersionedRef:
    key: str
    version: str

    def __post_init__(self) -> None:
        if not _KEY_RE.fullmatch(self.key):
            raise KernelValidationError(f"Invalid key: {self.key!r}")
        if not _VERSION_RE.fullmatch(self.version):
            raise KernelValidationError(f"Invalid version: {self.version!r}")

    @classmethod
    def parse(cls, value: str) -> "VersionedRef":
        key, separator, version = value.rpartition("@")
        if not separator:
            raise KernelValidationError(f"Versioned reference required: {value!r}")
        return cls(key=key, version=version)

    def __str__(self) -> str:
        return f"{self.key}@{self.version}"


@dataclass(frozen=True)
class CostEnvelope:
    max_money_eur: Decimal = Decimal("0")
    max_tokens: int = 0
    max_runtime_seconds: int = 300

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any] | None) -> "CostEnvelope":
        raw = raw or {}
        money = Decimal(str(raw.get("max_money_eur", raw.get("money_eur", 0))))
        tokens = int(raw.get("max_tokens", raw.get("tokens", 0)))
        runtime = int(raw.get("max_runtime_seconds", raw.get("deadline_s", 300)))
        if money < 0 or tokens < 0 or runtime <= 0:
            raise KernelValidationError("Cost limits must be non-negative and runtime positive")
        return cls(money, tokens, runtime)

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_money_eur": str(self.max_money_eur),
            "max_tokens": self.max_tokens,
            "max_runtime_seconds": self.max_runtime_seconds,
        }


@dataclass(frozen=True)
class AgentManifest:
    agent: VersionedRef
    name: str
    purpose: str
    roi_hypothesis: str
    success_metrics: tuple[str, ...]
    lifecycle: str
    autonomy: str
    capabilities: tuple[VersionedRef, ...]
    verticals: tuple[str, ...] = ("*",)
    dependencies: tuple[VersionedRef, ...] = ()
    apis: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    data_classes: tuple[str, ...] = ("public",)
    cost: CostEnvelope = field(default_factory=CostEnvelope)
    evals: tuple[str, ...] = ()
    revocation: Mapping[str, Any] = field(default_factory=dict)
    overlaps_with: tuple[VersionedRef, ...] = ()
    separation_reasons: tuple[str, ...] = ()
    entrypoint: str = ""

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "AgentManifest":
        manifest = cls(
            agent=VersionedRef(str(raw.get("agent_key", "")), str(raw.get("version", ""))),
            name=str(raw.get("name", "")).strip(),
            purpose=str(raw.get("purpose", "")).strip(),
            roi_hypothesis=str(raw.get("roi_hypothesis", "")).strip(),
            success_metrics=tuple(_clean_strings(raw.get("success_metrics"))),
            lifecycle=str(raw.get("lifecycle", "draft")),
            autonomy=str(raw.get("autonomy", "A0")),
            capabilities=tuple(VersionedRef.parse(v) for v in _clean_strings(raw.get("capabilities"))),
            verticals=tuple(_clean_strings(raw.get("verticals"))) or ("*",),
            dependencies=tuple(VersionedRef.parse(v) for v in _clean_strings(raw.get("dependencies"))),
            apis=tuple(_clean_strings(raw.get("apis"))),
            permissions=tuple(_clean_strings(raw.get("permissions"))),
            data_classes=tuple(_clean_strings(raw.get("data_classes"))) or ("public",),
            cost=CostEnvelope.from_mapping(raw.get("cost")),
            evals=tuple(_clean_strings(raw.get("evals"))),
            revocation=dict(raw.get("revocation") or {}),
            overlaps_with=tuple(VersionedRef.parse(v) for v in _clean_strings(raw.get("overlaps_with"))),
            separation_reasons=tuple(_clean_strings(raw.get("separation_reasons"))),
            entrypoint=str(raw.get("entrypoint", "")).strip(),
        )
        validate_manifest(manifest)
        return manifest

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_key": self.agent.key,
            "version": self.agent.version,
            "name": self.name,
            "purpose": self.purpose,
            "roi_hypothesis": self.roi_hypothesis,
            "success_metrics": list(self.success_metrics),
            "lifecycle": self.lifecycle,
            "autonomy": self.autonomy,
            "capabilities": [str(ref) for ref in self.capabilities],
            "verticals": list(self.verticals),
            "dependencies": [str(ref) for ref in self.dependencies],
            "apis": list(self.apis),
            "permissions": list(self.permissions),
            "data_classes": list(self.data_classes),
            "cost": self.cost.to_dict(),
            "evals": list(self.evals),
            "revocation": dict(self.revocation),
            "overlaps_with": [str(ref) for ref in self.overlaps_with],
            "separation_reasons": list(self.separation_reasons),
            "entrypoint": self.entrypoint,
        }


def _clean_strings(values: Any) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        values = [values]
    if not isinstance(values, (list, tuple, set, frozenset)):
        raise KernelValidationError("Expected a list of strings")
    return [str(value).strip() for value in values if str(value).strip()]


def validate_manifest(manifest: AgentManifest) -> None:
    """Enforce the marketplace admission rule before registration."""
    if not manifest.name or not manifest.purpose:
        raise KernelValidationError("Agent name and unique purpose are required")
    if not manifest.roi_hypothesis or not manifest.success_metrics:
        raise KernelValidationError("Agent admission requires explicit ROI and measurable benefit")
    if not manifest.capabilities:
        raise KernelValidationError("At least one versioned capability is required")
    if manifest.lifecycle not in _LIFECYCLES:
        raise KernelValidationError(f"Invalid lifecycle: {manifest.lifecycle}")
    if manifest.autonomy not in _AUTONOMY:
        raise KernelValidationError(f"Invalid autonomy: {manifest.autonomy}")
    if not set(manifest.data_classes).issubset(_DATA_CLASSES):
        raise KernelValidationError("Unknown data classification")
    if manifest.agent in manifest.dependencies:
        raise KernelValidationError("An agent cannot depend on itself")
    if manifest.lifecycle == "available" and not manifest.evals:
        raise KernelValidationError("Available agents require deterministic evals")
    if manifest.lifecycle == "available" and not manifest.revocation.get("procedure"):
        raise KernelValidationError("Available agents require a revocation procedure")
    if manifest.overlaps_with:
        dimensions = set(manifest.separation_reasons)
        if not dimensions.intersection(_SEPARATION_DIMENSIONS):
            raise KernelValidationError(
                "Overlapping functionality belongs in the existing agent unless separation "
                "is justified by complexity/risk/permissions/context/evaluation"
            )


def admit_manifest(manifest: AgentManifest, existing: Iterable[AgentManifest]) -> None:
    """Validate uniqueness and reject unjustified duplicate-purpose agents."""
    validate_manifest(manifest)
    purpose = " ".join(manifest.purpose.lower().split())
    for current in existing:
        if current.agent == manifest.agent:
            raise KernelValidationError(f"Agent already registered: {manifest.agent}")
        if " ".join(current.purpose.lower().split()) == purpose and not manifest.overlaps_with:
            raise KernelValidationError(
                f"Purpose already owned by {current.agent}; extend it or justify separation"
            )


@dataclass(frozen=True)
class TaskRequest:
    capability: VersionedRef
    requested_permissions: frozenset[str] = frozenset()
    data_classes: frozenset[str] = frozenset({"public"})
    budget: CostEnvelope = field(default_factory=CostEnvelope)
    risk: str = "low"
    approval_policy: str = "none"
    mode: str = "propose"  # propose | execute
    provider: str = "deterministic"

    def __post_init__(self) -> None:
        if self.risk not in {"low", "medium", "high"}:
            raise KernelValidationError(f"Invalid risk: {self.risk}")
        if self.approval_policy not in _APPROVAL_POLICIES:
            raise KernelValidationError(f"Invalid approval policy: {self.approval_policy}")
        if self.mode not in {"propose", "execute"}:
            raise KernelValidationError(f"Invalid mode: {self.mode}")
        if not self.data_classes.issubset(_DATA_CLASSES):
            raise KernelValidationError("Unknown task data classification")


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    requires_approval: bool
    reasons: tuple[str, ...]
    effective_approval_policy: str
    kernel_version: str = KERNEL_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "requires_approval": self.requires_approval,
            "reasons": list(self.reasons),
            "effective_approval_policy": self.effective_approval_policy,
            "kernel_version": self.kernel_version,
        }


def evaluate_policy(
    *,
    manifest: AgentManifest,
    installation: Mapping[str, Any],
    entitlements: Iterable[VersionedRef],
    enabled_dependencies: Iterable[VersionedRef],
    task: TaskRequest,
) -> PolicyDecision:
    """Fail closed. A future executor may run only when this returns allowed."""
    blockers: list[str] = []
    approval_reasons: list[str] = []
    entitlement_set = set(entitlements)
    dependency_set = set(enabled_dependencies)

    state = str(installation.get("status", ""))
    if manifest.lifecycle != "available":
        blockers.append(f"agent_lifecycle:{manifest.lifecycle}")
    if state not in _INSTALLATION_STATES or state != "enabled":
        blockers.append(f"installation:{state or 'missing'}")
    if task.capability not in manifest.capabilities:
        blockers.append("capability_not_declared")
    if task.capability not in entitlement_set:
        blockers.append("capability_not_entitled")

    granted = set(installation.get("granted_permissions") or [])
    requested = set(task.requested_permissions)
    if not requested.issubset(set(manifest.permissions)):
        blockers.append("permission_not_declared")
    if not requested.issubset(granted):
        blockers.append("permission_not_granted")
    if not set(manifest.dependencies).issubset(dependency_set):
        blockers.append("dependency_not_enabled")
    if not task.data_classes.issubset(set(manifest.data_classes)):
        blockers.append("data_class_not_declared")

    provider = task.provider.lower()
    if "deepseek" in provider and not task.data_classes.issubset(DEEPSEEK_ALLOWED_DATA_CLASSES):
        blockers.append("deepseek_data_policy")

    limits = CostEnvelope.from_mapping(installation.get("budget_limits"))
    if limits.max_money_eur and task.budget.max_money_eur > limits.max_money_eur:
        blockers.append("money_budget_exceeded")
    if limits.max_tokens and task.budget.max_tokens > limits.max_tokens:
        blockers.append("token_budget_exceeded")
    if task.budget.max_runtime_seconds > limits.max_runtime_seconds:
        blockers.append("runtime_budget_exceeded")
    if manifest.cost.max_money_eur and task.budget.max_money_eur > manifest.cost.max_money_eur:
        blockers.append("manifest_money_ceiling_exceeded")
    if manifest.cost.max_tokens and task.budget.max_tokens > manifest.cost.max_tokens:
        blockers.append("manifest_token_ceiling_exceeded")

    effective = task.approval_policy
    if task.risk == "high" and effective == "none":
        effective = "operator"
        approval_reasons.append("high_risk")
    if requested.intersection(PRODUCTION_WRITE_PERMISSIONS) and effective == "none":
        effective = "client"
        approval_reasons.append("production_write")
    if task.mode == "execute" and manifest.autonomy in {"A0", "A1"} and effective == "none":
        effective = "client"
        approval_reasons.append(f"autonomy_{manifest.autonomy.lower()}")

    requires_approval = effective != "none"
    return PolicyDecision(
        allowed=not blockers,
        requires_approval=requires_approval,
        reasons=tuple(blockers + approval_reasons),
        effective_approval_policy=effective,
    )


def build_action_queue_item(row: Mapping[str, Any]) -> dict[str, Any]:
    """Stable backend-to-dashboard contract; no UI implementation is implied."""
    status = str(row.get("status") or "queued")
    return {
        "schema_version": ACTION_QUEUE_SCHEMA_VERSION,
        "task_id": str(row.get("task_id") or row.get("id") or ""),
        "workspace_id": str(row.get("workspace_id") or ""),
        "agent": {
            "key": str(row.get("agent_key") or ""),
            "version": str(row.get("agent_version") or ""),
            "name": str(row.get("agent_name") or row.get("agent_key") or ""),
        },
        "capability": {
            "key": str(row.get("capability_key") or ""),
            "version": str(row.get("capability_version") or ""),
        },
        "goal": str(row.get("goal") or ""),
        "status": status,
        "risk": str(row.get("risk") or "low"),
        "needs_approval": bool(row.get("needs_approval")),
        "approval": {
            "id": str(row.get("approval_id") or ""),
            "status": str(row.get("approval_status") or ""),
            "policy": str(row.get("approval_policy") or "none"),
        },
        "value": {
            "metric": row.get("value_metric"),
            "before": row.get("kpi_before"),
            "after": row.get("kpi_after"),
            "unit": row.get("value_unit"),
        },
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }


def capability_matrix(
    plan_rows: Iterable[Mapping[str, Any]],
    entitlement_rows: Iterable[Mapping[str, Any]] = (),
) -> dict[VersionedRef, dict[str, Any]]:
    """Resolve plan grants plus workspace overrides without using marketing names in code."""
    resolved: dict[VersionedRef, dict[str, Any]] = {}
    for row in plan_rows:
        ref = VersionedRef(str(row["capability_key"]), str(row["capability_version"]))
        resolved[ref] = {"source": "plan", "limits": dict(row.get("limits") or {})}
    for row in entitlement_rows:
        ref = VersionedRef(str(row["capability_key"]), str(row["capability_version"]))
        if row.get("status") == "denied":
            resolved.pop(ref, None)
        elif row.get("status", "granted") == "granted":
            resolved[ref] = {
                "source": str(row.get("source") or "override"),
                "limits": dict(row.get("limits") or {}),
            }
    return resolved
