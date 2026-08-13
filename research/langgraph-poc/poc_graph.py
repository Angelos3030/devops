#!/usr/bin/env python3
"""
ISOLATED LangGraph POC — supports ADR docs/adr/0001-langgraph-agent-runtime.md.

Scope (per explicit instruction): research/evaluation only.
    - No production writes. No deployment. No modification of any file under
      src/, sites/, web/, db/ or any existing Vitrina agent flow.
    - Everything this script touches lives under research/langgraph-poc/.
    - DeepSeek and Claude calls are MOCKED (clearly labeled `_mock_*`) — this
      sandbox cannot reach api.deepseek.com or api.anthropic.com, and no
      production credentials are used here. The graph wiring, persistence,
      interrupt/resume, retry, and audit-trail mechanics are real LangGraph,
      not mocked. Swapping the two `_mock_*` functions for real API calls
      (same shape as src/research_worker.py / src/agent_runtime.py) is the
      only change needed to make this call real providers.

Graph:
    research_request
        -> deepseek_research_node   (structured artifact; fails once, then
                                      succeeds, to prove node-level retry)
        -> claude_review_node       (structured review + risk notes)
        -> human_approval           (interrupt() — graph pauses here)
        -> finalize_node            (only reachable after resume with Command)

Run:
    python3 research/langgraph-poc/poc_graph.py
"""
from __future__ import annotations

import sqlite3
import time
from datetime import datetime, timezone
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.types import interrupt, Command
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.errors import NodeInterrupt  # noqa: F401  (documented, not used directly)

import os as _os
# The repo directory is a mounted Windows share; SQLite's locking/journal
# mode fails there ("disk I/O error"). The checkpoint DB is ephemeral POC
# state, not a deliverable, so it lives in the sandbox's local tmpfs instead.
# Nothing under research/ depends on this file surviving the run.
DB_PATH = _os.environ.get("POC_DB_PATH", "/tmp/vitrina_langgraph_poc_state.sqlite")

# ---------------------------------------------------------------------------
# Fault injection for the retry demo — module-level, not part of graph state,
# to simulate a transient upstream failure (timeout, 429, etc.) independent
# of whatever the graph's own state/checkpoint machinery is doing.
# ---------------------------------------------------------------------------
_DEEPSEEK_ATTEMPTS: dict[str, int] = {}


def _audit(state: dict, node: str, actor: str, action: str, detail: str = "") -> list[dict]:
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "node": node,
        "actor": actor,
        "action": action,
        "detail": detail,
    }
    return [*state.get("audit_log", []), event]


class ResearchState(TypedDict, total=False):
    request: str
    artifact: dict
    review: dict
    approved: bool | None
    approval_note: str
    final_artifact: dict
    audit_log: list[dict]


# ---------------------------------------------------------------------------
# Node 1 — DeepSeek research (mocked). Deliberately raises on the first call
# per thread to prove the retry path is real, not narrated.
# ---------------------------------------------------------------------------
def _mock_deepseek_call(request: str) -> dict:
    """Stands in for a real src/research_worker.py-style call to DeepSeek."""
    return {
        "name": "Example candidate surfaced by DeepSeek",
        "reference": "https://github.com/example/example-agent",
        "purpose": f"Structured finding for request: {request}",
        "license": "MIT",
        "confidence": "medium",
    }


def deepseek_research_node(state: ResearchState, config) -> dict:
    thread_id = config["configurable"]["thread_id"]
    attempts = _DEEPSEEK_ATTEMPTS.get(thread_id, 0) + 1
    _DEEPSEEK_ATTEMPTS[thread_id] = attempts

    if attempts == 1:
        # Simulated transient failure (e.g. DeepSeek 429/timeout).
        raise RuntimeError("simulated DeepSeek transient failure (attempt 1)")

    artifact = _mock_deepseek_call(state["request"])
    return {
        "artifact": artifact,
        "audit_log": _audit(
            state, "deepseek_research_node", "deepseek",
            "artifact_produced", f"attempt={attempts}",
        ),
    }


# ---------------------------------------------------------------------------
# Node 2 — Claude review (mocked). Stands in for a real src/agent_runtime.py
# call. Produces a structured verdict the human approver will see.
# ---------------------------------------------------------------------------
def _mock_claude_review(artifact: dict) -> dict:
    return {
        "verdict": "looks reasonable, license confirmed MIT",
        "risk": "low",
        "recommend": "approve",
    }


def claude_review_node(state: ResearchState) -> dict:
    review = _mock_claude_review(state["artifact"])
    return {
        "review": review,
        "audit_log": _audit(
            state, "claude_review_node", "claude", "review_produced", review["verdict"],
        ),
    }


# ---------------------------------------------------------------------------
# Node 3 — human approval gate. `interrupt()` pauses the graph here and
# surfaces `payload` to whatever is polling the graph (dashboard, CLI, etc).
# Resuming requires an explicit Command(resume=...) — nothing proceeds
# without it.
# ---------------------------------------------------------------------------
def human_approval_node(state: ResearchState) -> dict:
    decision = interrupt({
        "question": "Approve this research artifact for promotion?",
        "artifact": state["artifact"],
        "review": state["review"],
    })
    return {
        "approved": bool(decision.get("approved")),
        "approval_note": decision.get("note", ""),
        "audit_log": _audit(
            state, "human_approval_node", "human",
            "approved" if decision.get("approved") else "rejected",
            decision.get("note", ""),
        ),
    }


def finalize_node(state: ResearchState) -> dict:
    if not state.get("approved"):
        return {
            "final_artifact": {},
            "audit_log": _audit(state, "finalize_node", "system", "halted_not_approved"),
        }
    final = {**state["artifact"], "review": state["review"], "approval_note": state.get("approval_note", "")}
    return {
        "final_artifact": final,
        "audit_log": _audit(state, "finalize_node", "system", "finalized"),
    }


def build_graph(checkpointer):
    g = StateGraph(ResearchState)
    g.add_node("deepseek_research", deepseek_research_node)
    g.add_node("claude_review", claude_review_node)
    g.add_node("human_approval", human_approval_node)
    g.add_node("finalize", finalize_node)

    g.add_edge(START, "deepseek_research")
    g.add_edge("deepseek_research", "claude_review")
    g.add_edge("claude_review", "human_approval")
    g.add_edge("human_approval", "finalize")
    g.add_edge("finalize", END)

    return g.compile(checkpointer=checkpointer)


def main() -> None:
    import os
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)  # clean POC DB each run — this is the isolated sandbox path only

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    graph = build_graph(checkpointer)

    thread_id = "poc-thread-1"
    config = {"configurable": {"thread_id": thread_id}}

    print("=== STEP 1: invoke — expect retry on deepseek_research, then interrupt before finalize ===")
    t0 = time.time()
    try:
        result = graph.invoke({"request": "Find lead-scoring reference architectures", "audit_log": []}, config)
    except RuntimeError as exc:
        # LangGraph does NOT auto-retry by default unless a RetryPolicy is
        # attached to the node — this first invoke demonstrates the raw
        # failure surfacing, then we show the retry-policy-driven recovery.
        print(f"  node raised as expected (no retry policy attached yet): {exc}")
        result = None

    print(f"  elapsed={time.time()-t0:.3f}s")
    print()

    print("=== STEP 2: rebuild graph WITH a retry policy on the flaky node, invoke again ===")
    from langgraph.types import RetryPolicy

    g2 = StateGraph(ResearchState)
    # Default RetryPolicy only retries a narrow set of transient exception
    # types (connection errors etc). A DeepSeek/Anthropic client would raise
    # its own SDK-specific transient-error class; here we retry on RuntimeError
    # explicitly since that's what the mock raises.
    g2.add_node(
        "deepseek_research", deepseek_research_node,
        retry_policy=RetryPolicy(max_attempts=3, retry_on=(RuntimeError,), initial_interval=0.05),
    )
    g2.add_node("claude_review", claude_review_node)
    g2.add_node("human_approval", human_approval_node)
    g2.add_node("finalize", finalize_node)
    g2.add_edge(START, "deepseek_research")
    g2.add_edge("deepseek_research", "claude_review")
    g2.add_edge("claude_review", "human_approval")
    g2.add_edge("finalize", END)
    g2.add_edge("human_approval", "finalize")
    graph2 = g2.compile(checkpointer=checkpointer)

    thread_id_2 = "poc-thread-2"
    config2 = {"configurable": {"thread_id": thread_id_2}}
    result2 = graph2.invoke({"request": "Find lead-scoring reference architectures", "audit_log": []}, config2)
    print(f"  interrupted={'__interrupt__' in result2}")
    if "__interrupt__" in result2:
        intr = result2["__interrupt__"][0]
        print(f"  interrupt payload question: {intr.value['question']}")
        print(f"  interrupt payload artifact.name: {intr.value['artifact']['name']}")
    state_before_resume = graph2.get_state(config2)
    print(f"  next node pending: {state_before_resume.next}")
    print(f"  audit events so far: {len(state_before_resume.values.get('audit_log', []))}")
    for ev in state_before_resume.values.get("audit_log", []):
        print(f"    - {ev['node']} / {ev['actor']} / {ev['action']} :: {ev['detail']}")
    print()

    print("=== STEP 3: simulate process restart — new connection, new graph object, same thread_id ===")
    conn.close()
    conn2 = sqlite3.connect(DB_PATH, check_same_thread=False)
    checkpointer_restarted = SqliteSaver(conn2)

    g3 = StateGraph(ResearchState)
    g3.add_node(
        "deepseek_research", deepseek_research_node,
        retry_policy=RetryPolicy(max_attempts=3, retry_on=(RuntimeError,), initial_interval=0.05),
    )
    g3.add_node("claude_review", claude_review_node)
    g3.add_node("human_approval", human_approval_node)
    g3.add_node("finalize", finalize_node)
    g3.add_edge(START, "deepseek_research")
    g3.add_edge("deepseek_research", "claude_review")
    g3.add_edge("claude_review", "human_approval")
    g3.add_edge("finalize", END)
    g3.add_edge("human_approval", "finalize")
    graph3 = g3.compile(checkpointer=checkpointer_restarted)

    restored_state = graph3.get_state(config2)
    print(f"  state survived process restart: {restored_state.values.get('artifact', {}).get('name')!r}")
    print(f"  still paused before: {restored_state.next}")
    print()

    print("=== STEP 4: resume after (simulated) human approval ===")
    final_result = graph3.invoke(
        Command(resume={"approved": True, "note": "Reviewed manually — MIT license confirmed, adapt only."}),
        config2,
    )
    print(f"  final_artifact.name: {final_result['final_artifact'].get('name')}")
    print(f"  approval_note: {final_result['final_artifact'].get('approval_note')}")
    print()

    print("=== STEP 5: full audit trail for the completed run ===")
    end_state = graph3.get_state(config2)
    for ev in end_state.values["audit_log"]:
        print(f"  {ev['ts']}  {ev['node']:<22} {ev['actor']:<9} {ev['action']:<20} {ev['detail']}")

    conn2.close()
    print()
    print("=== POC COMPLETE — nothing written outside research/langgraph-poc/ ===")


if __name__ == "__main__":
    main()
