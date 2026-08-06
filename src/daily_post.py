"""
RUNTIME — Καθημερινό post. Τρέχει από cron για κάθε ενεργό πελάτη.
Token-efficient: καλεί ΑΠΕΥΘΕΙΑΣ τον Social Agent (όχι coordinator).
Το generation δημιουργεί draft για έγκριση. Η δημοσίευση γίνεται χωριστά από
το `social_engine` worker μόνο όταν το post έχει εγκριθεί.

  python -m src.daily_post
"""

import json
import re

from . import config as cfg
from .agent_runtime import run_agent
from .db import get_active_clients, get_brand_profile, get_social_creds
from .social_engine import create_draft


def _parse_agent_json(raw: str) -> dict:
    """Εξάγει JSON από το output του agent (μπορεί να έχει markdown code block)."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    # Αν ο agent τύλιξε σε ```json ... ```
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    # Fallback: βρες το πρώτο { ... }
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        return json.loads(match.group())
    return {"caption": raw, "hashtags": []}


def post_for_client(client_row: dict) -> None:
    cid = client_row["id"]
    brand = get_brand_profile(cid)
    creds = get_social_creds(cid)
    if not brand:
        print(f"  ⏭️  {client_row['name']}: λείπει brand profile")
        return
    if not creds:
        print(f"  ⏭️  {client_row['name']}: δεν έχει συνδεθεί Facebook")
        return

    instruction = (
        "Φτιάξε το σημερινό post για Facebook & Instagram.\n"
        f"Brand profile:\n{json.dumps(brand, ensure_ascii=False)}\n"
        'Επίστρεψε ΜΟΝΟ JSON: {"caption": "...", "hashtags": ["#tag1", "#tag2"]}'
    )
    raw = run_agent(
        cfg.SOCIAL_AGENT_ID, instruction,
        title=f"Daily post — {client_row['name']}",
    )

    payload = _parse_agent_json(raw)
    caption = payload.get("caption", raw)
    hashtags = payload.get("hashtags", [])
    if hashtags:
        caption = f"{caption.rstrip()}\n\n{' '.join(hashtags)}"
    post_id = create_draft(cid, caption)
    print(f"  ✅ {client_row['name']}: draft {post_id} περιμένει έγκριση")


def main() -> None:
    clients = get_active_clients(plans=("social", "premium"))   # μόνο όσοι πληρώνουν social
    print(f"Ποστάρω για {len(clients)} πελάτες...")
    for c in clients:
        try:
            post_for_client(c)
        except Exception as e:
            print(f"  ❌ {c['name']}: {e}")


if __name__ == "__main__":
    main()
