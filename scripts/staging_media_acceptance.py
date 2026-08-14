#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Visual acceptance για το media authenticity — ΕΝΑΣ πελάτης, πέντε καταστάσεις.

Στήνει τα δεδομένα στην ΠΡΑΓΜΑΤΙΚΗ staging βάση και τυπώνει τι επιστρέφει το
`/clients/{id}/site-data` σε κάθε κατάσταση. Τα screenshots τα τραβάει ξεχωριστά
ο browser runner πάνω στο ίδιο URL.

    VITRINA_ENV=staging python scripts/staging_media_acceptance.py --confirm-staging setup
    VITRINA_ENV=staging python scripts/staging_media_acceptance.py --confirm-staging state 2
    VITRINA_ENV=staging python scripts/staging_media_acceptance.py --confirm-staging cleanup

Καμία production ενέργεια: `env.require("staging")` + ξεχωριστά credentials.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src import env  # noqa: E402

env.require("staging")

from src import db  # noqa: E402
from src import media_semantics as ms  # noqa: E402
from src import meta_oauth as mo  # noqa: E402

MARK = Path("sites/artifacts/acceptance-client.json")
U = "https://images.unsplash.com/photo-{}?auto=format&fit=crop&w=1400&q=80"

# Ένας συνθετικός πελάτης, αναγνωρίσιμος ώστε ο καθαρισμός να μην αγγίξει άλλον.
CLIENT = {"name": "ACCEPTANCE Υδραυλικά Δοκιμής", "business_type": "Υδραυλικός", "city": "Λάρισα"}

REAL = [
    ("1607472586893-edb57bdc0e39", ms.REAL_WORK, "Αλλαγή σωληνώσεων"),
    ("1585704032915-c3400ca199e7", ms.REAL_WORK, "Τοποθέτηση θερμοσίφωνα"),
    ("1621905252507-b35492cc74b4", ms.REAL_WORK, "Επισκευή μπάνιου"),
    ("1504148455328-c376907d081c", ms.REAL_SPACE, "Το συνεργείο μας"),
]
ILLUSTRATIVE = [
    ("1581578731548-c64695cc6952", ms.ILLUSTRATIVE, "Τεχνική υποστήριξη"),
    ("1621905251189-08b45d6a269e", ms.ILLUSTRATIVE, "Εργασία"),
]
REPLACEMENT = ("1620626011761-996317b8d101", ms.REAL_WORK, "Νέα εγκατάσταση")


def sb():
    return db._client()


def cid() -> str:
    return json.loads(MARK.read_text(encoding="utf-8"))["client_id"]


def _wipe_assets(client_id: str) -> None:
    sb().table("client_assets").delete().eq("client_id", client_id).execute()


def _add(client_id: str, items) -> None:
    for pid, cls, title in items:
        db.save_client_asset(client_id, {
            "type": "photo", "title": title, "usage": "site",
            "url": U.format(pid), "rights_ok": True, "media_class": cls,
        })


def _policy(client_id: str, value) -> None:
    sb().table("clients").update({"media_policy": value}).eq("id", client_id).execute()


def report(client_id: str, label: str) -> dict:
    d = mo.site_data(client_id)["data"]
    gal = d.get("gallery") or []
    classes = [g.get("media_class") for g in gal]
    out = {
        "state": label,
        "policy": d.get("MEDIA_POLICY"),
        "gallery": len(gal),
        "classes": classes,
        "illustrative_leak": [c for c in classes if c not in ms.REAL_CLASSES],
        "hero_is_real": d.get("HERO_IS_REAL"),
        "media_illustrative": d.get("MEDIA_ILLUSTRATIVE"),
        "gallery_title": d.get("GALLERY_TITLE"),
        "hero": (d.get("HERO_IMAGE") or "")[:58],
    }
    print(json.dumps(out, ensure_ascii=False))
    return out


STATES = {
    "1": ("χωρίς πολιτική (default)", None, REAL),
    "2": ("real-only + 4 πραγματικά", "real-only", REAL),
    "3": ("real-only + μεικτά", "real-only", REAL[:2] + ILLUSTRATIVE),
    "4": ("real-only + μόνο ενδεικτικά", "real-only", ILLUSTRATIVE),
    "5": ("real-only + αντικατάσταση εικόνας", "real-only", REAL[:3] + [REPLACEMENT]),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["setup", "state", "cleanup", "id"])
    ap.add_argument("which", nargs="?", default="")
    ap.add_argument("--confirm-staging", action="store_true")
    args = ap.parse_args()
    env.require_destructive(args.confirm_staging)

    if args.command == "setup":
        client_id = db.create_client(CLIENT)
        db.save_site_content(client_id, {
            "description": "Μικρό συνεργείο υδραυλικών για βλάβες, αποφράξεις και εγκαταστάσεις.",
            "services": [
                {"title": "Αποκατάσταση διαρροών", "desc": "Εντοπισμός και επισκευή σε σωληνώσεις."},
                {"title": "Αποφράξεις", "desc": "Καθαρισμός αποχέτευσης και σιφωνιών."},
                {"title": "Θερμοσίφωνες", "desc": "Τοποθέτηση και συντήρηση."},
                {"title": "Είδη υγιεινής", "desc": "Τοποθέτηση λεκάνης, νιπτήρα και μπαταριών."},
            ],
        })
        sb().table("clients").update({
            "phone": "2410 330440", "email": "acceptance@example.gr",
        }).eq("id", client_id).execute()
        MARK.parent.mkdir(parents=True, exist_ok=True)
        MARK.write_text(json.dumps({"client_id": client_id}), encoding="utf-8")
        print(f"client_id={client_id}")
        return 0

    if args.command == "id":
        print(cid())
        return 0

    if args.command == "cleanup":
        removed = 0
        rows = sb().table("clients").select("id,name").ilike("name", "ACCEPTANCE%").execute()
        for r in rows.data or []:
            sb().table("client_assets").delete().eq("client_id", r["id"]).execute()
            try:
                sb().table("site_content").delete().eq("client_id", r["id"]).execute()
            except Exception:
                pass
            sb().table("clients").delete().eq("id", r["id"]).execute()
            removed += 1
        MARK.unlink(missing_ok=True)
        print(f"καθαρίστηκαν {removed} πελάτες acceptance")
        return 0

    label, policy, assets = STATES[args.which]
    client_id = cid()
    _wipe_assets(client_id)
    _add(client_id, assets)
    _policy(client_id, policy)
    report(client_id, f"{args.which} · {label}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
