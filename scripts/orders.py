#!/usr/bin/env python3
"""
Οι παραγγελίες domain που περιμένουν εσένα.

    python scripts/orders.py            # τι εκκρεμεί + τι να κάνεις
    python scripts/orders.py --all      # όλο το ιστορικό

Το μοντέλο είναι: ο πελάτης διαλέγει domain και πληρώνει (Stripe €24) → η
παραγγελία μένει `pending_fulfillment` → το αγοράζεις στον registrar (~3 λεπτά)
→ τρέχεις τη μία εντολή που σου τυπώνει εδώ και βγαίνει live.

**Τρέξε το κάθε μέρα.** Αν δεν το δεις, ο πελάτης έχει πληρώσει και περιμένει.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone

sys.path.insert(0, ".")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src import db  # noqa: E402

WAITING = ("paid", "pending_fulfillment")


def _age(iso: str) -> str:
    try:
        t = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        h = (datetime.now(timezone.utc) - t).total_seconds() / 3600
        if h < 1:
            return f"{int(h * 60)}′"
        if h < 48:
            return f"{int(h)}ω"
        return f"{int(h / 24)} μέρες"
    except Exception:  # noqa: BLE001
        return "?"


def main() -> int:
    show_all = "--all" in sys.argv
    try:
        orders = db.list_domain_orders()
    except Exception as e:  # noqa: BLE001
        print(f"❌ Δεν διάβασα τις παραγγελίες: {e}")
        return 2

    waiting = [o for o in orders if o.get("status") in WAITING]
    failed = [o for o in orders if o.get("status") == "failed"]

    print("=" * 62)
    print("ΠΑΡΑΓΓΕΛΙΕΣ DOMAIN")
    print("=" * 62)

    if waiting:
        print(f"\n🔴 {len(waiting)} ΠΛΗΡΩΜΕΝΕΣ — περιμένουν εσένα:\n")
        for o in waiting:
            client = db.get_client(o["client_id"]) or {}
            print(f"  ▸ {o['domain']}")
            print(f"      πελάτης : {client.get('name', '—')} ({client.get('phone') or client.get('email') or '—'})")
            print(f"      πληρωμή : {o.get('amount_cents', 0) / 100:.2f}€  ·  πριν {_age(o.get('created_at', ''))}")
            print(f"      1) αγόρασέ το στο Papaki με registrant τα στοιχεία ΤΟΥ πελάτη")
            print(f"      2) python scripts/link_domain.py {o['domain']}")
            print()
    else:
        print("\n✅ Καμία εκκρεμότητα — κανείς δεν περιμένει.")

    if failed:
        print(f"\n⚠ {len(failed)} απέτυχαν:")
        for o in failed:
            print(f"  • {o['domain']} — {(o.get('error') or '')[:70]}")

    if show_all:
        print(f"\n— Ιστορικό ({len(orders)}) —")
        for o in orders:
            print(f"  {o.get('status', '?'):20} {o['domain']:34} {_age(o.get('created_at', ''))}")

    print("\n" + "=" * 62)
    if waiting:
        print("⚠ ΠΡΟΣΟΧΗ: το Railway Hobby δέχεται 2 custom domains ανά service και")
        print("  είναι ήδη γεμάτο. Μέχρι να μπει το Cloudflare for SaaS (ή Railway Pro),")
        print("  το link_domain.py θα σου βγάλει «όριο custom domains».")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
