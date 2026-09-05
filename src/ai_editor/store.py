"""Persistence contracts for deterministic conversational editing.

The model never receives a store.  The editing service uses this narrow
interface after the model output has passed schema and capability validation.
The in-memory implementation is deliberately production-shaped so tests cover
versions, idempotency, revisions and undo without opening a Supabase socket.
"""
from __future__ import annotations

import copy
import threading
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol


class StaleRevisionError(RuntimeError):
    pass


class EditorStore(Protocol):
    def get_content(self, client_id: str) -> Dict[str, Any]: ...
    def get_assets(self, client_id: str) -> List[Dict[str, Any]]: ...
    def get_version(self, client_id: str) -> int: ...
    def get_idempotent_result(self, client_id: str, key: str) -> Optional[Dict[str, Any]]: ...
    def commit_edit(
        self,
        client_id: str,
        *,
        expected_version: int,
        idempotency_key: str,
        message: str,
        operations: List[Dict[str, Any]],
        before_state: Dict[str, Any],
        after_state: Dict[str, Any],
    ) -> Dict[str, Any]: ...
    def undo(self, client_id: str, *, expected_version: int, idempotency_key: str) -> Dict[str, Any]: ...


@dataclass
class _ClientState:
    content: Dict[str, Any]
    assets: List[Dict[str, Any]]
    version: int = 0


class InMemoryEditorStore:
    """Thread-safe transactional store used by offline integration tests."""

    def __init__(self) -> None:
        self._clients: Dict[str, _ClientState] = {}
        self._revisions: Dict[str, List[Dict[str, Any]]] = {}
        self._idempotency: Dict[tuple[str, str], Dict[str, Any]] = {}
        self._lock = threading.RLock()

    def add_client(
        self,
        client_id: str,
        content: Dict[str, Any],
        assets: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        with self._lock:
            self._clients[client_id] = _ClientState(copy.deepcopy(content), copy.deepcopy(assets or []))
            self._revisions[client_id] = []

    def get_content(self, client_id: str) -> Dict[str, Any]:
        with self._lock:
            return copy.deepcopy(self._clients[client_id].content)

    def get_assets(self, client_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            return copy.deepcopy(self._clients[client_id].assets)

    def get_version(self, client_id: str) -> int:
        with self._lock:
            return self._clients[client_id].version

    def revision_count(self, client_id: str) -> int:
        with self._lock:
            return len(self._revisions.get(client_id, []))

    def get_idempotent_result(self, client_id: str, key: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            result = self._idempotency.get((client_id, key))
            return copy.deepcopy(result) if result else None

    def commit_edit(
        self,
        client_id: str,
        *,
        expected_version: int,
        idempotency_key: str,
        message: str,
        operations: List[Dict[str, Any]],
        before_state: Dict[str, Any],
        after_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        with self._lock:
            duplicate = self._idempotency.get((client_id, idempotency_key))
            if duplicate:
                return copy.deepcopy(duplicate)
            state = self._clients[client_id]
            if state.version != expected_version:
                raise StaleRevisionError(
                    f"stale revision: expected {expected_version}, current {state.version}"
                )
            if state.content != before_state:
                raise StaleRevisionError("content changed after planning")

            revision = {
                "id": str(uuid.uuid4()),
                "client_id": client_id,
                "message": message,
                "operations": copy.deepcopy(operations),
                "before_state": copy.deepcopy(before_state),
                "after_state": copy.deepcopy(after_state),
                "version_before": state.version,
                "version_after": state.version + 1,
                "undone": False,
            }
            state.content = copy.deepcopy(after_state)
            state.version += 1
            self._revisions[client_id].append(revision)
            result = {
                "success": True,
                "duplicate": False,
                "revision_id": revision["id"],
                "version": state.version,
                "content": copy.deepcopy(state.content),
            }
            self._idempotency[(client_id, idempotency_key)] = copy.deepcopy(result)
            return result

    def undo(self, client_id: str, *, expected_version: int, idempotency_key: str) -> Dict[str, Any]:
        with self._lock:
            duplicate = self._idempotency.get((client_id, idempotency_key))
            if duplicate:
                return copy.deepcopy(duplicate)
            state = self._clients[client_id]
            if state.version != expected_version:
                raise StaleRevisionError(
                    f"stale revision: expected {expected_version}, current {state.version}"
                )
            revision = next(
                (item for item in reversed(self._revisions[client_id]) if not item["undone"]),
                None,
            )
            if revision is None:
                return {"success": False, "duplicate": False, "message": "no revision"}

            state.content = copy.deepcopy(revision["before_state"])
            state.version += 1
            revision["undone"] = True
            result = {
                "success": True,
                "duplicate": False,
                "undone_revision_id": revision["id"],
                "version": state.version,
                "content": copy.deepcopy(state.content),
            }
            self._idempotency[(client_id, idempotency_key)] = copy.deepcopy(result)
            return result


class DatabaseEditorStore:
    """Supabase adapter backed by one atomic RPC per mutation."""

    def get_content(self, client_id: str) -> Dict[str, Any]:
        from src import db
        return db.get_site_content(client_id) or {}

    def get_assets(self, client_id: str) -> List[Dict[str, Any]]:
        from src import db
        return db.get_client_assets(client_id, usage="site")

    def get_version(self, client_id: str) -> int:
        from src import db
        return db.editor_version(client_id)

    def get_idempotent_result(self, client_id: str, key: str) -> Optional[Dict[str, Any]]:
        from src import db
        return db.editor_idempotent_result(client_id, key)

    def commit_edit(self, client_id: str, **kwargs: Any) -> Dict[str, Any]:
        from src import db
        try:
            return db.editor_commit(client_id, kwargs)
        except Exception as exc:
            if "stale_editor_version" in str(exc) or "40001" in str(exc):
                raise StaleRevisionError("stale revision") from exc
            raise

    def undo(self, client_id: str, *, expected_version: int, idempotency_key: str) -> Dict[str, Any]:
        from src import db
        try:
            return db.editor_undo(client_id, expected_version, idempotency_key)
        except Exception as exc:
            if "stale_editor_version" in str(exc) or "40001" in str(exc):
                raise StaleRevisionError("stale revision") from exc
            raise
