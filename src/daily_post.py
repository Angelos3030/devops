"""
RUNTIME — Καθημερινό post. Τρέχει από cron για κάθε ενεργό πελάτη.
Token-efficient: καλεί ΑΠΕΥΘΕΙΑΣ τον Social Agent (όχι coordinator).
Posting path: direct Graph API (publish.py) — όχι Meta MCP.

  python -m src.daily_post
"""

import importlib.util
import json
import os
import re

from . import config as cfg
from .agent_runtime import run_agent
from .db import get_active_clients, get_brand_profile, get_social_creds, save_post

# Φόρτωση publish_all από skills/meta-publisher/publish.py (δεν είναι Python package)
_pub_path = os.path.join(os.path.dirname(__file__), "..", "skills", "meta-publisher", "publish.py")
_pub_spec = importlib.util.spec_from_file_location("meta_publisher", _pub_path)
_pub_mod = importlib.util.module_from_spec(_pub_spec)
_pub_spec.loader.exec_module(_pub_mod)
publish_all = _pub_mod.publish_all
Post = _pub_mod.Post


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
    post = Post(
        caption=payload.get("caption", raw),
        hashtags=payload.get("hashtags", []),
    )

    pub_result = publish_all(creds, post)
    print(f"  📤 {pub_result}")

    # Διάκριση αν πήγε καλά ή όχι
    errors = [k for k, v in pub_result.items() if str(v).startswith("error:")]
    status = "failed" if errors else "published"
    save_post(
        cid,
        caption=post.caption,
        status=status,
        fb_post_id=pub_result.get("facebook") if "error:" not in str(pub_result.get("facebook")) else None,
        ig_post_id=pub_result.get("instagram") if "error:" not in str(pub_result.get("instagram", "")) else None,
    )
    if errors:
        print(f"  ⚠️  {client_row['name']}: σφάλμα σε {errors}")
    else:
        print(f"  ✅ {client_row['name']}")


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
