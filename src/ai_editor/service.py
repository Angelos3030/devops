"""Provider-independent orchestration for one conversational editing request."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict

from src.ai_editor.engine import EditingEngine
from src.ai_editor.model import SiteEditingModel
from src.ai_editor.store import EditorStore, StaleRevisionError


@dataclass(frozen=True)
class ServiceResult:
    success: bool
    message: str
    content: Dict[str, Any]
    version: int
    revision_id: str | None = None
    duplicate: bool = False
    rejected: bool = False


class EditingService:
    def __init__(
        self,
        model: SiteEditingModel,
        store: EditorStore,
        authorize: Callable[[str], bool],
    ) -> None:
        self.model = model
        self.store = store
        self.authorize = authorize

    def edit(
        self,
        client_id: str,
        message: str,
        *,
        idempotency_key: str,
        expected_version: int,
        capabilities: Dict[str, Any] | None = None,
    ) -> ServiceResult:
        if not self.authorize(client_id):
            return ServiceResult(False, "Δεν έχεις πρόσβαση σε αυτό το site.", {}, expected_version, rejected=True)
        if not idempotency_key or len(idempotency_key) > 200:
            return ServiceResult(False, "Μη έγκυρο αναγνωριστικό αιτήματος.", {}, expected_version, rejected=True)
        if not isinstance(message, str) or not message.strip() or len(message) > 4000:
            return ServiceResult(False, "Το μήνυμα είναι κενό ή υπερβολικά μεγάλο.", {}, expected_version, rejected=True)

        duplicate = self.store.get_idempotent_result(client_id, idempotency_key)
        if duplicate:
            return ServiceResult(
                bool(duplicate["success"]),
                "Το αίτημα είχε ήδη εφαρμοστεί.",
                duplicate.get("content", {}),
                int(duplicate.get("version", expected_version)),
                duplicate.get("revision_id"),
                duplicate=True,
            )

        current = self.store.get_content(client_id)
        context = {
            key: current.get(key)
            for key in ("name", "trade", "city", "phone", "hours", "services", "palette")
        }
        context["media_count"] = len(self.store.get_assets(client_id))
        context["capabilities"] = capabilities or {}
        plan = self.model.plan_edit(context, message)
        if plan is None:
            return ServiceResult(False, "Ο βοηθός δεν απάντησε. Δεν άλλαξα τίποτα.", current, expected_version)
        if plan.confidence < 0.75:
            return ServiceResult(False, "Δεν είμαι αρκετά βέβαιος για την αλλαγή. Πες το λίγο πιο συγκεκριμένα.", current, expected_version, rejected=True)
        if plan.intent == "undo":
            try:
                result = self.store.undo(
                    client_id,
                    expected_version=expected_version,
                    idempotency_key=idempotency_key,
                )
            except StaleRevisionError:
                return ServiceResult(False, "Το site άλλαξε σε άλλη καρτέλα. Ανανέωσε και δοκίμασε ξανά.", current, self.store.get_version(client_id), rejected=True)
            return ServiceResult(
                bool(result["success"]),
                "Η τελευταία αλλαγή αναιρέθηκε." if result["success"] else "Δεν υπάρχει αλλαγή για αναίρεση.",
                result.get("content", current),
                int(result.get("version", expected_version)),
                duplicate=bool(result.get("duplicate", False)),
            )
        if not plan.operations:
            return ServiceResult(False, plan.explanation, current, expected_version, rejected=True)

        prepared = EditingEngine.execute_plan(
            client_id,
            plan,
            store=self.store,
            capabilities=capabilities,
            persist=False,
        )
        if not prepared.success:
            return ServiceResult(False, prepared.message, current, expected_version, rejected=True)

        try:
            committed = self.store.commit_edit(
                client_id,
                expected_version=expected_version,
                idempotency_key=idempotency_key,
                message=message,
                operations=[op.model_dump() for op in plan.operations],
                before_state=prepared.before_state,
                after_state=prepared.after_state,
            )
        except StaleRevisionError:
            return ServiceResult(False, "Το site άλλαξε σε άλλη καρτέλα. Ανανέωσε και δοκίμασε ξανά.", current, self.store.get_version(client_id), rejected=True)

        return ServiceResult(
            True,
            plan.explanation,
            committed["content"],
            int(committed["version"]),
            committed.get("revision_id"),
            duplicate=bool(committed.get("duplicate", False)),
        )
