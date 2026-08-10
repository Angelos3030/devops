"""Read/approval API for the Stage 4A Agency Kernel.

There is intentionally no execute/run endpoint in Phase 4A.
"""
from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from . import db
from .agency_kernel import build_action_queue_item, capability_matrix
from .auth import current_email, require_client_access


router = APIRouter(prefix="/clients/{client_id}/agency", tags=["agency-kernel"])


class ApprovalDecision(BaseModel):
    decision: str = Field(pattern="^(approved|rejected)$")
    reason: str | None = Field(default=None, max_length=1000)


def _plan_key(client: dict) -> str:
    aliases = {
        "site": "presence",
        "starter": "presence",
        "social": "growth",
        "premium": "revenue",
        "multi-location": "multi_location",
    }
    return aliases.get(str(client.get("plan") or "").lower(),
                       str(client.get("plan") or "presence").lower())


@router.get("/capabilities")
def capabilities(client_id: str, authorization: str | None = Header(default=None)):
    client = require_client_access(client_id, authorization)
    plan_key = _plan_key(client)
    resolved = capability_matrix(
        db.list_plan_capabilities(plan_key),
        db.list_workspace_entitlements(client_id),
    )
    rows = [
        {"key": ref.key, "version": ref.version, **details}
        for ref, details in sorted(resolved.items())
    ]
    return {
        "schema_version": "1.0",
        "workspace_id": client_id,
        "plan_key": plan_key,
        "capabilities": rows,
        "installations": db.list_agent_installations(client_id),
    }


@router.get("/actions")
def actions(client_id: str, limit: int = 50,
            authorization: str | None = Header(default=None)):
    require_client_access(client_id, authorization)
    safe_limit = max(1, min(limit, 100))
    return {
        "schema_version": "1.0",
        "workspace_id": client_id,
        "items": [build_action_queue_item(row)
                  for row in db.list_agency_actions(client_id, safe_limit)],
    }


@router.post("/approvals/{approval_id}")
def decide_approval(client_id: str, approval_id: str, body: ApprovalDecision,
                    authorization: str | None = Header(default=None)):
    require_client_access(client_id, authorization)
    actor = current_email(authorization)
    before = db.get_agent_approval(client_id, approval_id)
    if not before:
        raise HTTPException(404, "Δεν βρέθηκε το αίτημα έγκρισης.")
    if before.get("status") != "pending":
        raise HTTPException(409, "Το αίτημα έχει ήδη αποφασιστεί.")

    after = db.decide_agent_approval(
        client_id, approval_id, status=body.decision,
        decided_by=actor, reason=body.reason,
    )
    if not after:
        raise HTTPException(409, "Το αίτημα άλλαξε. Ανανέωσε τη σελίδα.")

    trace_id = f"approval:{approval_id}:{uuid4()}"
    db.append_agency_audit({
        "workspace_id": client_id,
        "task_id": before.get("task_id"),
        "actor_type": "user",
        "actor_id": actor,
        "action": f"approval.{body.decision}",
        "entity_type": "agent_approval",
        "entity_id": approval_id,
        "before_state": before,
        "after_state": after,
        "reason": body.reason,
        "trace_id": trace_id,
    })
    return {"approval": after, "trace_id": trace_id}
