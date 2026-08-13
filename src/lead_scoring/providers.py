"""Real provider clients for the Lead Scoring pilot.

Replaces the `_mock_*` functions from the isolated pilot
(research/langgraph-poc/lead-scoring/lead_scoring_graph.py) with real calls.
Graph-level orchestration (retry, checkpoint, interrupt) is unchanged — these
functions raise on failure so the node's `RetryPolicy` can catch it, same
contract as `research/langgraph-poc/poc_graph.py`'s `_mock_deepseek_call`
that failed on first attempt.

DeepSeek reads `DEEPSEEK_API_KEY` directly from the environment, deliberately
NOT via `src/config.py` — this keeps the DeepSeek credential/quota fully
separate from the production `AI_API_KEY` channel, same boundary already
established in `src/research_worker.py` and documented in CLAUDE.md's
"Μαζική έρευνα → DeepSeek worker" section. DeepSeek is only ever called here
with the PII-stripped feature vector — see `graph.py`'s `enrich_classify_node`
and the Kernel's `DEEPSEEK_ALLOWED_DATA_CLASSES` gate, which this module does
not bypass (the gate runs in `graph.py` before this module is ever called).

Claude uses `src/config.py`'s `ANTHROPIC_API_KEY`/`MODEL_CHEAP` — the same
already-approved GDPR channel `src/ai.py` uses for customer-facing text. This
is a plain, stateless `messages.create()` call, not the Agent/session runtime
in `src/agent_runtime.py` — provisioning a new persistent cloud Agent (as
`src/setup_agents.py` would) is a separate, explicit decision outside this
pilot's scope; a stateless call needs no new cloud resource.
"""
from __future__ import annotations

import json
import os
import time

import requests
import anthropic

from .. import config as cfg


class LeadScoringProviderError(RuntimeError):
    """A provider call failed. Nodes attach a RetryPolicy for transient cases."""


DEEPSEEK_TIMEOUT = 30
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL_CHEAP", "deepseek-chat")

_DEEPSEEK_SYSTEM = (
    "You score inbound leads for a Greek SMB digital agency. You receive ONLY "
    "an anonymized feature vector — never raw customer text or contact info. "
    "Return strict JSON: {\"score\": int 0-100, \"confidence\": float 0-1, "
    "\"reasoning\": \"short string, no markdown\"}. No other text."
)


def deepseek_score(features: dict) -> dict:
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        raise LeadScoringProviderError("DEEPSEEK_API_KEY not set")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": _DEEPSEEK_SYSTEM},
            {"role": "user", "content": json.dumps(features, ensure_ascii=False)},
        ],
        "response_format": {"type": "json_object"},
        "max_tokens": 300,
        "temperature": 0.1,
    }
    try:
        resp = requests.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload, timeout=DEEPSEEK_TIMEOUT,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        result = json.loads(content)
    except Exception as exc:  # noqa: BLE001 — surfaced to caller as LeadScoringProviderError
        raise LeadScoringProviderError(f"DeepSeek scoring call failed: {exc}") from exc

    if not isinstance(result.get("score"), (int, float)):
        raise LeadScoringProviderError(f"DeepSeek returned no numeric score: {result!r}")
    return {
        "score": max(0, min(100, int(result["score"]))),
        "confidence": float(result.get("confidence", 0.5)),
        "reasoning": str(result.get("reasoning", ""))[:300],
    }


_CLAUDE_SYSTEM = (
    "You review an already-computed lead classification for a Greek SMB "
    "digital agency's lead-scoring pipeline. You do NOT re-score from scratch "
    "— you sanity-check the deterministic tier assignment against the lead's "
    "actual service request and message, and flag risk (e.g. complaint tone, "
    "legal/medical sensitivity, clearly wrong tier). Reply with strict JSON: "
    "{\"recommended_tier\": \"hot\"|\"warm\"|\"cold\", \"rationale\": \"short "
    "string, no markdown\", \"risk_flag\": true|false}. No other text."
)


def claude_review(raw_lead: dict, features: dict, business_rule: dict) -> dict:
    if not cfg.ANTHROPIC_API_KEY:
        raise LeadScoringProviderError("ANTHROPIC_API_KEY not set")
    client = anthropic.Anthropic(api_key=cfg.ANTHROPIC_API_KEY, base_url=cfg.ANTHROPIC_BASE_URL or None)
    user_content = json.dumps({
        "service": raw_lead.get("service"),
        "message": raw_lead.get("message"),  # Claude is the approved channel for this — see module docstring
        "computed_tier": business_rule["tier"],
        "computed_score": business_rule["score"],
        "features": features,
    }, ensure_ascii=False)
    try:
        resp = client.messages.create(
            model=cfg.MODEL_CHEAP,
            max_tokens=300,
            system=_CLAUDE_SYSTEM,
            messages=[{"role": "user", "content": user_content}],
        )
        text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
        result = json.loads(text)
    except Exception as exc:  # noqa: BLE001
        raise LeadScoringProviderError(f"Claude review call failed: {exc}") from exc

    if result.get("recommended_tier") not in ("hot", "warm", "cold"):
        raise LeadScoringProviderError(f"Claude returned no valid tier: {result!r}")
    return {
        "recommended_tier": result["recommended_tier"],
        "rationale": str(result.get("rationale", ""))[:300],
        "risk_flag": bool(result.get("risk_flag", False)),
    }
