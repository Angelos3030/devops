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

Claude uses `src/config.py`'s `AI_API_KEY` (credential only, not model
selection — see pinning note below) and a plain `requests.post()` to the
Messages API — mirroring `src/ai.py`'s `_anthropic()` function EXACTLY (same
credential pairing, same base-URL resolution including its `deepseek.com`
guard), not the `anthropic` SDK. Three live staging attempts (see
`_anthropic_base_url()`'s docstring below) showed the SDK's own
base_url-resolution fallback and a naive "is this a valid absolute URL"
check both fail in this environment's actual `.env` shape — reusing
`src/ai.py`'s already-proven-working logic fixed it for real. This is the
same already-approved GDPR channel `src/ai.py` uses for customer-facing
text, not the Agent/session runtime in `src/agent_runtime.py` — provisioning
a new persistent cloud Agent (as `src/setup_agents.py` would) is a separate,
explicit decision outside this pilot's scope; a stateless call needs no new
cloud resource.

Model pinning (2026-08-13, ADR-0004 production-pilot pass): both model
identifiers below are deliberately PINNED, not read from `cfg.MODEL_CHEAP`/
a floating provider alias, and deliberately NOT shared with the rest of the
codebase's model selection. Two real findings drove this:

  1. Live staging traffic on 2026-08-13 showed the request for `deepseek-chat`
     resolved server-side to `deepseek-v4-flash`, and confirmed against
     DeepSeek's own official changelog (api-docs.deepseek.com/updates,
     2026-04-24 entry): this is INTENTIONAL — `deepseek-chat` is a legacy
     alias for DeepSeek-V4-Flash's non-thinking mode, and that legacy alias
     was scheduled for discontinuation on 2026-07-24 (already past, as of
     this pinning). Pointing at `deepseek-v4-flash` explicitly, rather than
     the (already-deprecated) alias, avoids depending on a name that could
     stop working at any time.
  2. The request for `claude-haiku-4-5` resolved to the dated snapshot
     `claude-haiku-4-5-20251001`. This is Anthropic's normal, documented
     alias-to-snapshot behavior, not a substitution risk — but pinning the
     dated snapshot explicitly (rather than the floating alias) guarantees
     this pilot's behavior and cost don't silently change if Anthropic ever
     repoints the `claude-haiku-4-5` alias to a different snapshot.

Both are overridable via env var for the rare case a controlled upgrade is
needed, but the default is the pinned, currently-verified identifier — never
a floating alias.
"""
from __future__ import annotations

import json
import os

import requests

from .. import config as cfg


class LeadScoringProviderError(RuntimeError):
    """A provider call failed. Nodes attach a RetryPolicy for transient cases."""


DEEPSEEK_TIMEOUT = 30
# Pinned, not the legacy floating alias "deepseek-chat" — see module docstring.
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL_CHEAP", "deepseek-v4-flash")
# Pinned dated Claude snapshot, not the floating alias "claude-haiku-4-5" —
# deliberately independent of cfg.MODEL_CHEAP (see module docstring).
CLAUDE_MODEL = os.environ.get("LEAD_SCORING_CLAUDE_MODEL", "claude-haiku-4-5-20251001")

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
        body = resp.json()
        content = body["choices"][0]["message"]["content"]
        result = json.loads(content)
    except Exception as exc:  # noqa: BLE001 — surfaced to caller as LeadScoringProviderError
        raise LeadScoringProviderError(f"DeepSeek scoring call failed: {exc}") from exc

    if not isinstance(result.get("score"), (int, float)):
        raise LeadScoringProviderError(f"DeepSeek returned no numeric score: {result!r}")
    usage = body.get("usage", {})
    # Same authoritative-model-vs-requested-model check as claude_review().
    resolved_model = body.get("model", "")
    return {
        "score": max(0, min(100, int(result["score"]))),
        "confidence": float(result.get("confidence", 0.5)),
        "reasoning": str(result.get("reasoning", ""))[:300],
        # real measured usage, not estimated — read from the API response itself
        "_usage": {
            "provider": "deepseek",
            "model": resolved_model or DEEPSEEK_MODEL,
            "requested_model": DEEPSEEK_MODEL,
            "model_mismatch": bool(resolved_model and resolved_model != DEEPSEEK_MODEL),
            "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
        },
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


def _anthropic_base_url() -> str:
    """Mirrors src/ai.py's `_anthropic()` base-URL resolution EXACTLY — that
    function is this codebase's own already-working, already-tested Claude
    channel, and this pilot's job is to reuse its logic, not reinvent it a
    third time.

    Real bug trail, three live staging attempts before landing here:
      1st attempt (raw anthropic.Anthropic(base_url=cfg.ANTHROPIC_BASE_URL or
      None)) crashed: httpx.UnsupportedProtocol — cfg.ANTHROPIC_BASE_URL
      wasn't a full absolute URL.
      2nd attempt (base_url=None when invalid) still crashed the same way:
      confirmed by reading the anthropic SDK's own source that passing
      base_url=None makes it re-read the SAME raw ANTHROPIC_BASE_URL env var
      itself — passing None doesn't skip a bad value, it re-fetches it.
      3rd attempt (always pass an explicit valid URL, defaulting to
      api.anthropic.com when the configured one isn't absolute) got past the
      protocol error but then got a real 401 "invalid x-api-key" — because
      cfg.ANTHROPIC_API_KEY/cfg.ANTHROPIC_BASE_URL in this environment are
      paired for a DIFFERENT endpoint (their value contains "deepseek.com",
      the exact case src/ai.py's own `_anthropic()` already guards against),
      so silently falling back to api.anthropic.com sent the wrong key to
      the wrong place. This function fixes it for real, by using the same
      credential pairing and the same guard as the proven-working code.
    """
    configured_base = cfg.AI_BASE_URL or ""
    return ("https://api.anthropic.com" if "deepseek.com" in configured_base.lower()
            else configured_base or "https://api.anthropic.com")


def claude_review(raw_lead: dict, features: dict, business_rule: dict) -> dict:
    if not cfg.AI_API_KEY:
        raise LeadScoringProviderError("AI_API_KEY/ANTHROPIC_API_KEY not set")
    base_url = _anthropic_base_url()
    user_content = json.dumps({
        "service": raw_lead.get("service"),
        "message": raw_lead.get("message"),  # Claude is the approved channel for this — see module docstring
        "computed_tier": business_rule["tier"],
        "computed_score": business_rule["score"],
        "features": features,
    }, ensure_ascii=False)
    try:
        resp = requests.post(
            f"{base_url}/v1/messages",
            headers={"x-api-key": cfg.AI_API_KEY, "anthropic-version": "2023-06-01",
                     "Content-Type": "application/json"},
            json={"model": CLAUDE_MODEL, "max_tokens": 300, "system": _CLAUDE_SYSTEM,
                  "messages": [{"role": "user", "content": user_content}]},
            timeout=30,
        )
        resp.raise_for_status()
        body = resp.json()
    except Exception as exc:  # noqa: BLE001
        raise LeadScoringProviderError(f"Claude review HTTP call failed: {exc}") from exc

    text = "".join(b.get("text", "") for b in body.get("content", []) if b.get("type") == "text")
    # Lenient extraction — matches src/ai.py's complete_json(), which exists
    # precisely because models sometimes wrap JSON in markdown fences or a
    # sentence despite instructions not to. A strict json.loads(text) failed
    # on a real staging run with "Expecting value: line 1 column 1" against
    # non-empty `text`, consistent with exactly this wrapping.
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise LeadScoringProviderError(
            f"Claude response had no JSON object. stop_reason={body.get('stop_reason')!r} "
            f"content_block_types={[b.get('type') for b in body.get('content', [])]} "
            f"raw_text={text[:300]!r}"
        )
    try:
        result = json.loads(text[start:end + 1])
    except json.JSONDecodeError as exc:
        raise LeadScoringProviderError(f"Claude returned malformed JSON: {exc}. raw_text={text[:300]!r}") from exc

    if result.get("recommended_tier") not in ("hot", "warm", "cold"):
        raise LeadScoringProviderError(f"Claude returned no valid tier: {result!r}")
    usage = body.get("usage", {})
    # Cost-telemetry validation (2026-08-13 pass): the response body itself
    # confirms which model actually served the request (`body["model"]`) —
    # this is authoritative; `CLAUDE_MODEL` (now pinned, see module docstring)
    # is only what we REQUESTED, and a provider-side alias/redirect could
    # still silently serve a different model than the one we pinned. Surface
    # both so the report can flag a mismatch instead of trusting the
    # request-side config blindly.
    resolved_model = body.get("model", "")
    requested_model = CLAUDE_MODEL
    return {
        "recommended_tier": result["recommended_tier"],
        "rationale": str(result.get("rationale", ""))[:300],
        "risk_flag": bool(result.get("risk_flag", False)),
        # real measured usage, not estimated — read from the API response itself
        "_usage": {
            "provider": "anthropic",
            "model": resolved_model or requested_model,
            "requested_model": requested_model,
            "model_mismatch": bool(resolved_model and resolved_model != requested_model),
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
        },
    }
