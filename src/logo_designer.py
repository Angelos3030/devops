"""Deterministic Logo Designer MVP.

Creates three lightweight SVG drafts from workspace data. Draft generation is
read-only; only the explicit approve endpoint persists a logo asset.
"""
from __future__ import annotations

import html
import re
from typing import Any

from fastapi import APIRouter, Header, HTTPException

from . import auth, db

router = APIRouter(tags=["logo-designer"])


def _clean(value: Any, fallback: str = "Vitrina") -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text[:64] or fallback


def _initials(name: str) -> str:
    words = [w for w in re.split(r"[^0-9A-Za-zΑ-ΩΆΈΉΊΌΎΏα-ωάέήίόύώϊϋΐΰ]+", name) if w]
    return "".join(word[0].upper() for word in words[:2]) or "V"


def _palette(trade: str) -> tuple[str, str, str]:
    flat = trade.lower()
    if any(x in flat for x in ("οδοντ", "ιατρ", "κλιν")):
        return "#0B4F6C", "#E8F6F8", "#22A7A0"
    if any(x in flat for x in ("νυχ", "κομμ", "αισθητ", "beauty")):
        return "#3B2536", "#FFF5F7", "#E65C7B"
    if any(x in flat for x in ("καφε", "ταβερ", "εστια", "φουρν")):
        return "#33251D", "#FFF8ED", "#D96432"
    if any(x in flat for x in ("ξυλ", "επιπλ", "κουζιν")):
        return "#20251F", "#F5F0E6", "#B86B3C"
    return "#172033", "#F5F7FA", "#FF7A1A"


def generate_logo_drafts(name: str, trade: str = "") -> list[dict[str, str]]:
    """Return three distinct, accessible SVG directions without provider calls."""
    name = _clean(name)
    trade = _clean(trade, "Τοπική επιχείρηση")
    safe_name, safe_trade = html.escape(name), html.escape(trade)
    initials = html.escape(_initials(name))
    ink, paper, accent = _palette(trade)

    drafts = [
        {
            "id": "monogram",
            "label": "Μονόγραμμα",
            "description": "Καθαρό γεωμετρικό σήμα που διαβάζεται και σε μικρό μέγεθος.",
            "svg": f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 240" role="img" aria-label="{safe_name}"><rect width="640" height="240" rx="28" fill="{paper}"/><rect x="36" y="36" width="168" height="168" rx="36" fill="{ink}"/><path d="M62 176 178 64" stroke="{accent}" stroke-width="12" stroke-linecap="round"/><text x="120" y="143" fill="#fff" text-anchor="middle" font-family="Arial,sans-serif" font-size="62" font-weight="800">{initials}</text><text x="236" y="112" fill="{ink}" font-family="Arial,sans-serif" font-size="42" font-weight="800">{safe_name}</text><text x="238" y="153" fill="{accent}" font-family="Arial,sans-serif" font-size="19">{safe_trade}</text></svg>''',
        },
        {
            "id": "emblem",
            "label": "Σήμα",
            "description": "Αναγνωρίσιμο έμβλημα με ήρεμη premium παρουσία.",
            "svg": f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 240" role="img" aria-label="{safe_name}"><rect width="640" height="240" rx="28" fill="{ink}"/><circle cx="120" cy="120" r="78" fill="none" stroke="{accent}" stroke-width="8"/><circle cx="120" cy="120" r="58" fill="{paper}"/><text x="120" y="141" fill="{ink}" text-anchor="middle" font-family="Georgia,serif" font-size="58" font-weight="700">{initials}</text><text x="230" y="111" fill="{paper}" font-family="Georgia,serif" font-size="43" font-weight="700">{safe_name}</text><path d="M232 132h300" stroke="{accent}" stroke-width="4"/><text x="232" y="165" fill="{paper}" opacity=".78" font-family="Arial,sans-serif" font-size="18">{safe_trade}</text></svg>''',
        },
        {
            "id": "wordmark",
            "label": "Wordmark",
            "description": "Τυπογραφική ταυτότητα χωρίς περιττό σύμβολο.",
            "svg": f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 240" role="img" aria-label="{safe_name}"><rect width="640" height="240" rx="28" fill="{paper}"/><path d="M48 64h12v112H48zM74 64h72v12H74zM74 164h72v12H74z" fill="{accent}"/><text x="174" y="122" fill="{ink}" font-family="Georgia,serif" font-size="50" font-weight="700">{safe_name}</text><text x="177" y="158" fill="{ink}" opacity=".66" font-family="Arial,sans-serif" font-size="17" letter-spacing="2">{safe_trade.upper()}</text></svg>''',
        },
    ]
    return drafts


def _workspace_identity(client: dict[str, Any], client_id: str) -> tuple[str, str]:
    content = db.get_site_content(client_id)
    return (
        _clean(content.get("name") or client.get("name")),
        _clean(
            content.get("trade") or client.get("business_type") or client.get("type"),
            "Τοπική επιχείρηση",
        ),
    )


@router.get("/clients/{client_id}/logo-drafts")
def logo_drafts(client_id: str, authorization: str | None = Header(default=None)):
    client = auth.require_client_access(client_id, authorization)
    name, trade = _workspace_identity(client, client_id)
    return {"drafts": generate_logo_drafts(name, trade), "requires_approval": True}


@router.post("/clients/{client_id}/logo-drafts/{draft_id}/approve")
def approve_logo_draft(client_id: str, draft_id: str,
                       authorization: str | None = Header(default=None)):
    client = auth.require_client_access(client_id, authorization)
    name, trade = _workspace_identity(client, client_id)
    draft = next((item for item in generate_logo_drafts(name, trade)
                  if item["id"] == draft_id), None)
    if not draft:
        raise HTTPException(404, "Δεν βρέθηκε αυτή η πρόταση λογοτύπου.")

    url = db.upload_to_storage(
        client_id, f"logo-generated-{draft_id}.svg",
        draft["svg"].encode("utf-8"), "image/svg+xml",
    )
    asset_id = db.save_client_asset(client_id, {
        "type": "logo", "title": f"{draft['label']} — {name}", "url": url,
        "usage": "site", "rights_ok": True,
    })
    for asset in db.get_client_assets(client_id, usage="site"):
        if asset.get("type") == "logo" and asset.get("id") != asset_id:
            db.delete_client_asset(client_id, asset["id"])
    return {"approved": True, "asset_id": asset_id, "url": url}
