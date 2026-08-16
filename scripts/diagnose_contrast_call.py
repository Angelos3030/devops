#!/usr/bin/env python3
"""Καταγράφει ΜΙΑ κλήση contrast-repair και τον έλεγχο, χωρίς να αλλάξει τίποτα.

Δεν πειράζει theme, tokens, worker. Στέλνει ακριβώς ό,τι στέλνει το
`_contrast_only_fix` και αποθηκεύει ολόκληρο τον φάκελο απάντησης, ώστε να
σταματήσουμε να μαντεύουμε γιατί το `content` βγαίνει κενό.

ΠΟΤΕ δεν γράφει API key, Authorization header ή άλλο μυστικό.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

from src import contrast_repair as cr  # noqa: E402

# Το κλειδί ζει στο .env, όπως και για τον worker. Δεν τυπώνεται ποτέ.
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except Exception:  # noqa: BLE001
    pass

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "port-worker" / "diagnostics"
SECRET_KEYS = ("authorization", "api-key", "x-api-key", "cookie")


def _sanitise(headers: dict) -> dict:
    return {k: ("<redacted>" if k.lower() in SECRET_KEYS else v) for k, v in headers.items()}


def send(label: str, model: str, system: str, user: str, max_tokens: int,
         response_format: dict | None) -> dict:
    base = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not key:
        raise SystemExit("DEEPSEEK_API_KEY δεν βρέθηκε — abort")
    endpoint = f"{base}/chat/completions"
    payload: dict = {
        "model": model, "temperature": 0.2, "max_tokens": max_tokens,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
    }
    if response_format:
        payload["response_format"] = response_format
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    r = requests.post(endpoint, headers=headers, json=payload, timeout=120)
    try:
        body = r.json()
    except Exception:  # noqa: BLE001
        body = {"_unparseable_text": r.text[:4000]}

    choice = (body.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    record = {
        "label": label,
        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "request": {
            "endpoint": endpoint,
            "headers": _sanitise(headers),
            "model": model,
            "max_tokens": max_tokens,
            "temperature": payload["temperature"],
            "response_format": payload.get("response_format"),
            "system_prompt": system,
            "user_prompt_final": user,          # ΜΕΤΑ από κάθε .format()
            "user_prompt_length": len(user),
        },
        "response": {
            "http_status": r.status_code,
            "model_returned": body.get("model"),
            "id": body.get("id"),
            "created": body.get("created"),
            "choices_count": len(body.get("choices") or []),
            "finish_reason": choice.get("finish_reason"),
            "message": msg,
            "content": msg.get("content"),
            "content_length": len(msg.get("content") or ""),
            "reasoning_content": msg.get("reasoning_content"),
            "reasoning_content_length": len(msg.get("reasoning_content") or ""),
            "refusal": msg.get("refusal"),
            "tool_calls": msg.get("tool_calls"),
            "usage": body.get("usage"),
            "error": body.get("error"),
            "raw_body": body,
        },
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{label}.json").write_text(
        json.dumps(record, indent=1, ensure_ascii=False), encoding="utf-8")
    return record


def brief(rec: dict) -> None:
    q, s = rec["request"], rec["response"]
    print(f"\n=== {rec['label']} ===")
    print(f"  model ζητήθηκε : {q['model']}")
    print(f"  model επέστρεψε: {s['model_returned']}")
    print(f"  HTTP           : {s['http_status']}")
    print(f"  choices        : {s['choices_count']}")
    print(f"  finish_reason  : {s['finish_reason']!r}")
    print(f"  content        : {(s['content'] or '')[:120]!r}  (len {s['content_length']})")
    print(f"  reasoning      : {(s['reasoning_content'] or '')[:100]!r}  (len {s['reasoning_content_length']})")
    print(f"  refusal        : {s['refusal']!r}")
    print(f"  usage          : {json.dumps(s['usage'], ensure_ascii=False)}")
    print(f"  error          : {s['error']!r}")
    print(f"  response_format στο αίτημα: {q['response_format']}")


def main() -> int:
    cheap = os.environ.get("DEEPSEEK_MODEL_CHEAP") or "deepseek-chat"

    # --- Το ΠΡΑΓΜΑΤΙΚΟ αίτημα, με το ίδιο prompt μετά από .format()
    fail = {"fg_token": "accent-ink", "bg_token": "surface-2",
            "fg_value": "#247cff", "bg_value": "#F9F9F9",
            "measured": 3.69, "required": 4.5}
    real_user = cr.PROMPT.format(**fail)
    failing = send("failing-contrast-call", cheap,
                   "Return JSON only. No prose, no markdown.",
                   real_user, 300, {"type": "json_object"})

    # --- Ελάχιστη κλήση ελέγχου: ίδιο transport, ίδιο μοντέλο, ίδιο format
    control = send("control-minimal-call", cheap,
                   "Return JSON only.",
                   'Return exactly this JSON object:\n'
                   '{"token":"--vt-accent-ink","value":"#000000"}',
                   300, {"type": "json_object"})

    brief(failing)
    brief(control)
    print(f"\nαποθηκεύτηκαν στο {OUT.relative_to(ROOT)}")
    print("\n--- ΤΕΛΙΚΟ prompt που στάλθηκε (πρώτοι 400 χαρακτήρες) ---")
    print(real_user[:400])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
