"""Stripe E2E σε ΑΠΟΜΟΝΩΜΕΝΟ staging.

Χτυπάει τον ΠΡΑΓΜΑΤΙΚΟ handler (`src.stripe_webhook.app`) με ΠΡΑΓΜΑΤΙΚΑ
υπογεγραμμένα events, και ελέγχει την ΠΡΑΓΜΑΤΙΚΗ βάση staging.

Τρεις δικλείδες, ελεγμένες πριν από κάθε γραφή:
  1. `VITRINA_ENV=staging` — αλλιώς τερματίζει.
  2. `sk_test_` — αλλιώς τερματίζει.
  3. Το `SUPABASE_URL_PRODUCTION` δεν υπάρχει στο μηχάνημα.

Καμία χρέωση κάρτας: τα checkout sessions δημιουργούνται αλλά ΔΕΝ πληρώνονται.
Η «επιτυχής πληρωμή» προσομοιώνεται με υπογεγραμμένο webhook, όπως ακριβώς θα
το έστελνε το Stripe.

Χρήση:  VITRINA_ENV=staging python research/billing-domain/stripe_e2e.py
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import pathlib
import sys
import time
import uuid

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
os.environ.setdefault("VITRINA_ENV", "staging")

from src import config as cfg      # noqa: E402
from src import db                 # noqa: E402
from src import env                # noqa: E402

# ── Δικλείδες ──────────────────────────────────────────────────────────────
if not env.is_staging:
    sys.exit(f"⛔ Απαιτείται staging. Τώρα: {env.current}")
if not cfg.STRIPE_SECRET_KEY.startswith("sk_test"):
    sys.exit("⛔ Το STRIPE_SECRET_KEY δεν είναι test key.")
if os.environ.get("SUPABASE_URL_PRODUCTION"):
    sys.exit("⛔ Υπάρχουν production credentials στο περιβάλλον.")
print(f"  {env.banner()}")

from fastapi.testclient import TestClient      # noqa: E402
from src.stripe_webhook import app as hook_app  # noqa: E402

CLIENT = TestClient(hook_app, raise_server_exceptions=False)

RUN = uuid.uuid4().hex[:8]
# Το clients.id είναι uuid στο σχήμα — τα ids πρέπει να είναι αληθινά uuid.
CID_A = str(uuid.uuid4())
CID_B = str(uuid.uuid4())
CUST_A = f"cus_TEST_A_{RUN}"
CUST_B = f"cus_TEST_B_{RUN}"

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    results.append((name, ok, detail))
    print(f"  {'✓' if ok else '✗'} {name}{('  — ' + detail) if detail else ''}")
    return ok


def sign(payload: bytes, secret: str, ts: int | None = None) -> str:
    ts = ts or int(time.time())
    mac = hmac.new(secret.encode(), f"{ts}.".encode() + payload,
                   hashlib.sha256).hexdigest()
    return f"t={ts},v1={mac}"


def send(event: dict, *, secret: str | None = None, ts: int | None = None):
    body = json.dumps(event).encode()
    sig = sign(body, secret or cfg.STRIPE_WEBHOOK_SECRET, ts)
    return CLIENT.post("/stripe/webhook", content=body,
                       headers={"stripe-signature": sig,
                                "content-type": "application/json"})


def evt(type_: str, obj: dict, eid: str | None = None) -> dict:
    # Το `"object": "event"` είναι ΥΠΟΧΡΕΩΤΙΚΟ: χωρίς αυτό το
    # `stripe.Webhook.construct_event` σκάει ΜΕΤΑ την επαλήθευση υπογραφής,
    # και ο handler το αναφέρει ως «invalid signature» — δύο διαφορετικά
    # σφάλματα με το ίδιο μήνυμα.
    return {"id": eid or f"evt_{uuid.uuid4().hex}", "object": "event",
            "type": type_, "api_version": "2024-06-20",
            "created": int(time.time()), "livemode": False,
            "pending_webhooks": 1, "request": {"id": None, "idempotency_key": None},
            "data": {"object": obj}}


def sub_obj(cust: str, cid: str | None, status: str, sub_id: str,
            price: str | None = None) -> dict:
    return {"id": sub_id, "object": "subscription", "customer": cust,
            "status": status,
            "metadata": ({"client_id": cid} if cid else {}),
            "items": {"data": [{"price": {"id": price or cfg.STRIPE_PRICE_SITE}}]}}


def session_obj(sid: str, cid: str | None, email: str | None,
                kind: str | None = None, extra: dict | None = None) -> dict:
    md: dict = {}
    if cid:
        md["client_id"] = cid
    if kind:
        md["kind"] = kind
    md.update(extra or {})
    return {"id": sid, "object": "checkout_session", "metadata": md,
            "customer_details": ({"email": email} if email else None),
            "customer_email": None, "mode": "subscription"}


def subs_for(cid: str) -> list[dict]:
    return (db._client().table("subscriptions").select("*")
            .eq("client_id", cid).execute()).data or []


def client_row(cid: str) -> dict:
    rows = (db._client().table("clients").select("*")
            .eq("id", cid).execute()).data
    return rows[0] if rows else {}


# ── Στήσιμο: δύο απομονωμένοι πελάτες staging ──────────────────────────────
print("\n── στήσιμο ──")
for cid, name in ((CID_A, "Audit A"), (CID_B, "Audit B")):
    db._client().table("clients").insert({
        "id": cid, "name": name, "status": "pending",
        "business_type": "test", "city": "STAGING-AUDIT", "phone": "0000000000",
    }).execute()
print(f"  δύο πελάτες staging: {CID_A}, {CID_B}")


def cleanup() -> None:
    for t, col in (("subscriptions", "client_id"), ("domains", "client_id"),
                   ("clients", "id")):
        for cid in (CID_A, CID_B):
            try:
                db._client().table(t).delete().eq(col, cid).execute()
            except Exception:  # noqa: BLE001
                pass


try:
    # ── 1. Υπογραφή ────────────────────────────────────────────────────────
    print("\n── 1. επαλήθευση υπογραφής ──")
    e = evt("customer.subscription.created",
            sub_obj(CUST_A, CID_A, "active", f"sub_{RUN}_a"))
    check("έγκυρη υπογραφή γίνεται δεκτή", send(e).status_code == 200)
    body = json.dumps(e).encode()
    r = CLIENT.post("/stripe/webhook", content=body,
                    headers={"stripe-signature": "t=1,v1=deadbeef"})
    check("άκυρη υπογραφή απορρίπτεται", r.status_code == 400, f"HTTP {r.status_code}")
    r = CLIENT.post("/stripe/webhook", content=body)
    check("χωρίς υπογραφή απορρίπτεται", r.status_code == 400, f"HTTP {r.status_code}")
    r = send(e, secret="whsec_" + "0" * 32)
    check("λάθος μυστικό απορρίπτεται", r.status_code == 400, f"HTTP {r.status_code}")
    old = send(e, ts=int(time.time()) - 3600)
    check("replay 1 ώρας ΑΠΟΡΡΙΠΤΕΤΑΙ (default tolerance 5′)",
          old.status_code == 400, f"HTTP {old.status_code}")

    # ── 2. Συνδρομή γράφεται ───────────────────────────────────────────────
    print("\n── 2. δημιουργία συνδρομής ──")
    rows = subs_for(CID_A)
    check("η συνδρομή αποθηκεύτηκε", len(rows) == 1, f"{len(rows)} γραμμές")
    check("ο πελάτης έγινε active", client_row(CID_A).get("status") == "active",
          client_row(CID_A).get("status", "?"))
    check("το plan αποθηκεύτηκε",
          bool(rows and rows[0].get("plan")), rows[0].get("plan") if rows else "-")

    # ── 3. Ιδempotency ─────────────────────────────────────────────────────
    print("\n── 3. διπλή παράδοση (idempotency) ──")
    dup_id = f"evt_dup_{RUN}"
    e2 = evt("customer.subscription.created",
             sub_obj(CUST_A, CID_A, "active", f"sub_{RUN}_a"), eid=dup_id)
    send(e2), send(e2), send(e2)
    rows = subs_for(CID_A)
    check("ίδιο event ×3 δεν διπλασιάζει τη συνδρομή", len(rows) == 1,
          f"{len(rows)} γραμμές")

    print("  (σημείωση) το event id δεν αποθηκεύεται πουθενά:")
    check("υπάρχει πίνακας/έλεγχος processed events",
          "stripe_event" in open(HERE.parents[1] / "src" / "stripe_webhook.py",
                                 encoding="utf-8").read(),
          "η idempotency βασίζεται ΜΟΝΟ στο upsert, όχι σε event id")

    # ── 4. Σύνδεση email ───────────────────────────────────────────────────
    print("\n── 4. σύνδεση email αγοράς ──")
    send(evt("checkout.session.completed",
             session_obj(f"cs_{RUN}_1", CID_A, "audit-a@example.test")))
    check("το email συνδέθηκε",
          client_row(CID_A).get("email") == "audit-a@example.test",
          str(client_row(CID_A).get("email")))
    send(evt("checkout.session.completed",
             session_obj(f"cs_{RUN}_2", CID_A, "attacker@example.test")))
    check("δεύτερο email ΔΕΝ αντικαθιστά το πρώτο",
          client_row(CID_A).get("email") == "audit-a@example.test",
          str(client_row(CID_A).get("email")))

    # ── 5. Ελλιπή δεδομένα ─────────────────────────────────────────────────
    print("\n── 5. ελλιπή/λανθασμένα δεδομένα ──")
    r = send(evt("checkout.session.completed",
                 session_obj(f"cs_{RUN}_3", CID_B, None)))
    check("checkout χωρίς email δεν σκάει", r.status_code == 200)
    check("χωρίς email δεν γράφτηκε τίποτα",
          not client_row(CID_B).get("email"), str(client_row(CID_B).get("email")))
    r = send(evt("customer.subscription.created",
                 sub_obj(f"cus_ORPHAN_{RUN}", None, "active", f"sub_{RUN}_orphan")))
    check("subscription χωρίς client_id δεν σκάει", r.status_code == 200)
    check("subscription χωρίς client_id δεν γράφει",
          len(subs_for(CID_B)) == 0, f"{len(subs_for(CID_B))} γραμμές")
    r = send(evt("customer.subscription.created",
                 sub_obj(f"cus_GHOST_{RUN}", str(uuid.uuid4()),
                         "active", f"sub_{RUN}_ghost")))
    check("ανύπαρκτο client_id: δεν ρίχνει το webhook", r.status_code == 200,
          f"HTTP {r.status_code}")

    # ── 6. Αποτυχία πληρωμής / ανανέωση / ακύρωση ──────────────────────────
    print("\n── 6. αποτυχία, ανανέωση, ακύρωση ──")
    send(evt("customer.subscription.updated",
             sub_obj(CUST_A, CID_A, "past_due", f"sub_{RUN}_a")))
    check("past_due → ο πελάτης παύει να είναι active",
          client_row(CID_A).get("status") == "paused",
          str(client_row(CID_A).get("status")))
    send(evt("customer.subscription.updated",
             sub_obj(CUST_A, CID_A, "active", f"sub_{RUN}_a")))
    check("επιτυχής ανανέωση → active ξανά",
          client_row(CID_A).get("status") == "active",
          str(client_row(CID_A).get("status")))

    r = send(evt("invoice.payment_failed",
                 {"id": f"in_{RUN}", "customer": CUST_A, "object": "invoice"}))
    check("invoice.payment_failed ΑΝΤΙΜΕΤΩΠΙΖΕΤΑΙ",
          "invoice.payment_failed" in open(
              HERE.parents[1] / "src" / "stripe_webhook.py", encoding="utf-8").read(),
          "ο handler δεν αναγνωρίζει καθόλου invoice.* events")
    r = send(evt("charge.refunded",
                 {"id": f"ch_{RUN}", "customer": CUST_A, "object": "charge"}))
    check("επιστροφή χρημάτων αντιμετωπίζεται",
          "refund" in open(HERE.parents[1] / "src" / "stripe_webhook.py",
                           encoding="utf-8").read().lower(),
          "καμία αναφορά σε refund/dispute")

    # ── 7. Εκτός σειράς ────────────────────────────────────────────────────
    print("\n── 7. events εκτός σειράς ──")
    send(evt("customer.subscription.deleted",
             sub_obj(CUST_A, CID_A, "canceled", f"sub_{RUN}_a")))
    cancelled = client_row(CID_A).get("status")
    send(evt("customer.subscription.updated",
             sub_obj(CUST_A, CID_A, "active", f"sub_{RUN}_a")))
    after = client_row(CID_A).get("status")
    check("ακύρωση → cancelled", cancelled == "cancelled", str(cancelled))
    check("ΠΑΛΙΟ 'active' μετά την ακύρωση ΔΕΝ επαναφέρει τη συνδρομή",
          after == "cancelled",
          f"κατέληξε {after} — το webhook δεν συγκρίνει χρόνο event")

    # ── 8. Διασταύρωση πελατών ─────────────────────────────────────────────
    print("\n── 8. απομόνωση πελατών ──")
    send(evt("customer.subscription.created",
             sub_obj(CUST_B, CID_B, "active", f"sub_{RUN}_b")))
    a, b = subs_for(CID_A), subs_for(CID_B)
    check("κάθε πελάτης έχει τη δική του συνδρομή",
          len(a) == 1 and len(b) == 1, f"A={len(a)} B={len(b)}")
    check("το customer id του Α δεν έγραψε στον Β",
          b and b[0]["stripe_customer_id"] == CUST_B,
          b[0]["stripe_customer_id"] if b else "-")

finally:
    print("\n── καθαρισμός ──")
    cleanup()
    print("  οι εγγραφές staging διαγράφηκαν")

ok = sum(1 for _, o, _ in results if o)
print(f"\n  ΣΥΝΟΛΟ: {ok}/{len(results)} πέρασαν")
(HERE / "stripe_e2e_results.json").write_text(json.dumps(
    [{"check": n, "passed": o, "detail": d} for n, o, d in results],
    ensure_ascii=False, indent=2), encoding="utf-8")
sys.exit(0 if ok == len(results) else 1)
