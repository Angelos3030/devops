"""Αναζήτηση διαθεσιμότητας + αίτημα domain, σε staging.

ΚΑΜΙΑ ΑΓΟΡΑ. Το `/domain/request` δημιουργεί μόνο εγγραφή σε
`pending_fulfillment` — επαληθεύεται ρητά ότι κανένας registrar δεν κλήθηκε
για κατοχύρωση.

Χρήση:  VITRINA_ENV=staging python research/billing-domain/availability_e2e.py
"""
from __future__ import annotations

import json
import os
import pathlib
import socket
import sys
import urllib.error
import uuid
from unittest.mock import patch

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
os.environ.setdefault("VITRINA_ENV", "staging")

from src import db      # noqa: E402
from src import env     # noqa: E402

if not env.is_staging:
    sys.exit(f"⛔ Απαιτείται staging. Τώρα: {env.current}")
if os.environ.get("SUPABASE_URL_PRODUCTION"):
    sys.exit("⛔ Υπάρχουν production credentials.")
print(f"  {env.banner()}")

from fastapi.testclient import TestClient          # noqa: E402
from src import auth                               # noqa: E402
from src import domain_availability as av          # noqa: E402
from src import registrars                         # noqa: E402
from src.main import app as main_app               # noqa: E402

C = TestClient(main_app, raise_server_exceptions=False)

CID_A, CID_B = str(uuid.uuid4()), str(uuid.uuid4())
MAIL_A, MAIL_B = "avail-a@example.test", "avail-b@example.test"
FREE = f"vitrina-audit-{uuid.uuid4().hex[:10]}.com"     # σχεδόν βέβαια ελεύθερο
TAKEN = "google.com"
results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    results.append((name, ok, detail))
    print(f"  {'✓' if ok else '✗'} {name}{('  — ' + detail) if detail else ''}")
    return ok


for cid, mail, nm in ((CID_A, MAIL_A, "Avail A"), (CID_B, MAIL_B, "Avail B")):
    db._client().table("clients").insert({
        "id": cid, "name": nm, "status": "active", "email": mail,
        "business_type": "test", "city": "STAGING-AUDIT", "phone": "0000000000",
    }).execute()


def cleanup() -> None:
    for t, col in (("domain_orders", "client_id"), ("domains", "client_id"),
                   ("clients", "id")):
        for cid in (CID_A, CID_B):
            try:
                db._client().table(t).delete().eq(col, cid).execute()
            except Exception:  # noqa: BLE001
                pass


def orders(cid: str) -> list[dict]:
    return (db._client().table("domain_orders").select("*")
            .eq("client_id", cid).execute()).data or []


try:
    # ── 1. Διαθέσιμο / μη διαθέσιμο, από αυθεντική πηγή ────────────────────
    print("\n── 1. αυθεντικό αποτέλεσμα ──")
    a = av.check(TAKEN)
    check("πιασμένο domain → unavailable", a.status == av.UNAVAILABLE,
          f"{a.status} από {a.source}")
    check("η πηγή είναι το ΜΗΤΡΩΟ, όχι το DNS", a.source.startswith("rdap:"),
          a.source)
    b = av.check(FREE)
    check("ελεύθερο domain → available", b.status == av.AVAILABLE,
          f"{b.status} από {b.source}")
    check("το αποτέλεσμα έχει χρονοσήμανση", bool(b.checked_at), b.checked_at[:19])

    # ── 2. .gr — η κατάληξη χωρίς RDAP ─────────────────────────────────────
    print("\n── 2. .gr (καμία αυθεντική δωρεάν πηγή) ──")
    g = av.check("google.gr")
    check(".gr ΔΕΝ επιστρέφει ποτέ ψεύτικο 'available'", g.status != av.AVAILABLE,
          f"{g.status} — {g.reason[:50]}")
    check(".gr δηλώνει ρητά γιατί δεν ξέρει", bool(g.reason), g.source)

    # ── 3. Άκυρη είσοδος ───────────────────────────────────────────────────
    print("\n── 3. άκυρη είσοδος ──")
    BAD = ["", ".gr", "a..gr", "-x.gr", "x-.gr", "mitsos", "../../etc/passwd.gr",
           "a" * 70 + ".gr", "ελ", "http://", "@@@.gr"]
    bad_ok = []
    for raw in BAD:
        try:
            av.check(raw)
            bad_ok.append(False)
        except av.InvalidDomain:
            bad_ok.append(True)
    check("κάθε άκυρη είσοδος απορρίπτεται καθαρά", all(bad_ok),
          f"{sum(bad_ok)}/{len(BAD)}")

    # ── 4. Ελληνικά / IDN ──────────────────────────────────────────────────
    print("\n── 4. ελληνική είσοδος (IDN) ──")
    puny, disp = av.normalize_domain("Καφέ-Μήτσος.GR")
    check("ελληνικό domain → punycode", puny.startswith("xn--"), puny)
    check("ο πελάτης βλέπει το δικό του κείμενο", disp == "καφέ-μήτσος.gr", disp)
    p1, _ = av.normalize_domain("καφέ.gr")
    p2, _ = av.normalize_domain(
        "καφέ.gr")                        # ίδιο οπτικά, αποσυντεθειμένο
    check("NFC: δύο γραφές του ίδιου → ΙΔΙΟ punycode", p1 == p2, f"{p1} / {p2}")
    n1, _ = av.normalize_domain("  https://WWW.Mitsos.GR/menu?x=1 ")
    check("θόρυβος (scheme/www/path/κεφαλαία) καθαρίζεται", n1 == "mitsos.gr", n1)

    # ── 5. Αποτυχίες παρόχου — ΠΟΤΕ 'available' ────────────────────────────
    print("\n── 5. αποτυχίες παρόχου ──")

    def boom(exc):
        def _f(*a, **k):
            raise exc
        return _f

    scenarios = [
        ("timeout", boom(socket.timeout("timed out"))),
        ("5xx", boom(urllib.error.HTTPError("u", 503, "down", {}, None))),
        ("429 rate limit", boom(urllib.error.HTTPError("u", 429, "slow", {}, None))),
        ("δίκτυο κάτω", boom(urllib.error.URLError("no route"))),
        ("απρόσμενο", boom(ValueError("κάτι άλλο"))),
    ]
    for label, side in scenarios:
        with patch("urllib.request.urlopen", side_effect=side):
            r = av.check(FREE)
        check(f"{label} → unknown, όχι available",
              r.status == av.UNKNOWN, f"{r.status} — {r.reason[:44]}")

    with patch("src.domain_availability._bootstrap", return_value={}):
        r = av.check(TAKEN)
    check("αποτυχία IANA bootstrap → unknown", r.status == av.UNKNOWN,
          f"{r.status} — {r.reason[:44]}")

    # ── 6. Ο DNS δεν αποφαίνεται πια ───────────────────────────────────────
    print("\n── 6. η παλιά εικασία DNS ──")
    rows = registrars.DnsRegistrar().check_availability(["oti-na-nai.gr"])
    check("ο DnsRegistrar ΔΕΝ επιστρέφει πια boolean",
          rows[0]["available"] is None, str(rows[0]["available"]))
    src = (HERE.parents[1] / "src" / "registrars.py").read_text(encoding="utf-8")
    check("δεν έμεινε κώδικας που μαντεύει από NXDOMAIN",
          "Status" not in src and "dns-query" not in src,
          "ο DoH έλεγχος αφαιρέθηκε")

    # ── 7. /domain/check — το endpoint ─────────────────────────────────────
    print("\n── 7. endpoint /domain/check ──")
    r = C.post("/domain/check", json={"slugs": [TAKEN.split(".")[0],
                                                FREE.split(".")[0]], "tld": ".com"})
    got = {x.get("domain"): x.get("status") for x in r.json().get("results", [])}
    check("το endpoint επιστρέφει τρεις σαφείς καταστάσεις",
          got.get(TAKEN) == "unavailable" and got.get(FREE) == "available",
          json.dumps(got, ensure_ascii=False)[:70])
    r = C.post("/domain/check", json={"slugs": ["-bad-", "καλό"], "tld": ".gr"})
    kinds = [x.get("status") for x in r.json().get("results", [])]
    check("άκυρο σε λίστα δεν ρίχνει τα υπόλοιπα", "invalid" in kinds,
          str(kinds))

    # ── 8. Αίτημα domain — ΧΩΡΙΣ αγορά ─────────────────────────────────────
    print("\n── 8. αίτημα domain ──")
    bought: list = []
    with patch.object(auth, "current_email", return_value=MAIL_A), \
         patch.object(registrars.DnsRegistrar, "register_domain",
                      side_effect=lambda *a, **k: bought.append(a)):
        r = C.post("/domain/request",
                   json={"client_id": CID_A, "domain": FREE},
                   headers={"Authorization": "Bearer a"})
    body = r.json() if r.status_code == 200 else {}
    check("το αίτημα δημιουργείται", r.status_code == 200, f"HTTP {r.status_code}")
    check("κατάσταση = pending_fulfillment",
          body.get("status") == "pending_fulfillment", str(body.get("status")))
    check("ΔΕΝ αγοράστηκε τίποτα", not bought, f"{len(bought)} κλήσεις αγοράς")
    row = orders(CID_A)[0] if orders(CID_A) else {}
    for field in ("client_id", "domain", "availability", "availability_source",
                  "availability_checked_at", "requested_at", "status"):
        check(f"αποθηκεύτηκε: {field}", bool(row.get(field)),
              str(row.get(field))[:44])
    check("δεν χρεώθηκε ποσό", row.get("amount_cents") == 0,
          str(row.get("amount_cents")))

    # ── 9. Διπλό αίτημα ────────────────────────────────────────────────────
    print("\n── 9. διπλό αίτημα ──")
    with patch.object(auth, "current_email", return_value=MAIL_A):
        r2 = C.post("/domain/request", json={"client_id": CID_A, "domain": FREE},
                    headers={"Authorization": "Bearer a"})
    check("δεύτερο αίτημα δεν δημιουργεί δεύτερη γραμμή",
          len(orders(CID_A)) == 1, f"{len(orders(CID_A))} γραμμές")
    check("επιστρέφει την ΙΔΙΑ παραγγελία",
          r2.json().get("order_id") == body.get("order_id"))

    # ── 10. Πιασμένο domain δεν γίνεται αίτημα ─────────────────────────────
    print("\n── 10. πιασμένο domain ──")
    with patch.object(auth, "current_email", return_value=MAIL_A):
        r3 = C.post("/domain/request", json={"client_id": CID_A, "domain": TAKEN},
                    headers={"Authorization": "Bearer a"})
    check("πιασμένο → 409, καμία παραγγελία", r3.status_code == 409,
          f"HTTP {r3.status_code}")
    check("δεν προστέθηκε γραμμή", len(orders(CID_A)) == 1,
          f"{len(orders(CID_A))} γραμμές")

    # ── 11. Δύο πελάτες ────────────────────────────────────────────────────
    print("\n── 11. δύο πελάτες ──")
    FREE_B = f"vitrina-audit-{uuid.uuid4().hex[:10]}.com"
    with patch.object(auth, "current_email", return_value=MAIL_B):
        C.post("/domain/request", json={"client_id": CID_B, "domain": FREE_B},
               headers={"Authorization": "Bearer b"})
    check("κάθε πελάτης έχει τη δική του παραγγελία",
          len(orders(CID_A)) == 1 and len(orders(CID_B)) == 1,
          f"A={len(orders(CID_A))} B={len(orders(CID_B))}")
    with patch.object(auth, "current_email", return_value=MAIL_A):
        rx = C.post("/domain/request",
                    json={"client_id": CID_B, "domain": "vitrina-audit-x.com"},
                    headers={"Authorization": "Bearer a"})
    check("ο Α ΔΕΝ ζητά domain για τον Β", rx.status_code in (401, 403, 404),
          f"HTTP {rx.status_code}")
    check("καμία γραμμή δεν προστέθηκε στον Β", len(orders(CID_B)) == 1,
          f"{len(orders(CID_B))} γραμμές")
    r = C.post("/domain/request", json={"client_id": CID_A, "domain": "x.com"})
    check("χωρίς ταυτοποίηση → απόρριψη", r.status_code in (401, 403, 404),
          f"HTTP {r.status_code}")

    # ── 12. Η διαθεσιμότητα αλλάζει πριν την εκτέλεση ──────────────────────
    print("\n── 12. πιάστηκε πριν προλάβουμε ──")
    oid = orders(CID_A)[0]["id"]
    later = av.Availability(FREE, FREE, av.UNAVAILABLE, "rdap:test",
                            av.datetime.now(av.timezone.utc).isoformat())
    updated = db.record_fulfillment_check(oid, later.as_dict())
    check("η κατάσταση γίνεται unavailable_at_fulfillment",
          updated.get("status") == "unavailable_at_fulfillment",
          str(updated.get("status")))
    check("ο ΠΡΩΤΟΣ έλεγχος (τι είδε ο πελάτης) ΔΕΝ ξαναγράφτηκε",
          updated.get("availability") == "available",
          f"πελάτης={updated.get('availability')} · "
          f"operator={updated.get('fulfillment_availability')}")
    check("καταγράφηκε η αιτία", bool(updated.get("error")),
          str(updated.get("error"))[:52])

    # Και η καθαρή περίπτωση: ακόμα ελεύθερο
    FREE_C = f"vitrina-audit-{uuid.uuid4().hex[:10]}.com"
    with patch.object(auth, "current_email", return_value=MAIL_A):
        rc = C.post("/domain/request", json={"client_id": CID_A, "domain": FREE_C},
                    headers={"Authorization": "Bearer a"})
    oid2 = rc.json()["order_id"]
    still = db.record_fulfillment_check(oid2, av.check(FREE_C).as_dict())
    check("αν είναι ακόμα ελεύθερο, μένει pending_fulfillment",
          still.get("status") == "pending_fulfillment",
          f"{still.get('status')} · operator={still.get('fulfillment_availability')}")

    # ── 13. Η ουρά του operator ────────────────────────────────────────────
    print("\n── 13. ουρά operator ──")
    q = db.list_domain_orders(status="pending_fulfillment", limit=50)
    mine = [o for o in q if o["client_id"] in (CID_A, CID_B)]
    check("η ουρά δείχνει τα εκκρεμή με ό,τι χρειάζεται ο operator",
          bool(mine) and all(o.get("availability_checked_at") for o in mine),
          f"{len(mine)} εκκρεμή")

finally:
    print("\n── καθαρισμός ──")
    cleanup()
    print("  οι εγγραφές staging διαγράφηκαν")

ok = sum(1 for _, o, _ in results if o)
print(f"\n  ΣΥΝΟΛΟ: {ok}/{len(results)}")
(HERE / "availability_results.json").write_text(json.dumps(
    [{"check": n, "passed": o, "detail": d} for n, o, d in results],
    ensure_ascii=False, indent=2), encoding="utf-8")
sys.exit(0 if ok == len(results) else 1)
