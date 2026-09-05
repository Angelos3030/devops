"""Domain/DNS + ασφάλεια, σε staging.

ΚΑΜΙΑ ΑΓΟΡΑ DOMAIN. Ο registrar είναι `dns` (μόνο εκτίμηση διαθεσιμότητας) και
κάθε μονοπάτι αγοράς ελέγχεται ΜΟΝΟ ως προς το ότι ΑΡΝΕΙΤΑΙ να αγοράσει.
Καμία εγγραφή στο Cloudflare: οι κλήσεις που γίνονται είναι αναγνώσεις ή
σκόπιμα αποτυχημένες, ώστε να μετρηθεί ο χειρισμός σφάλματος.

Χρήση:  VITRINA_ENV=staging python research/billing-domain/domain_security_e2e.py
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import uuid
from unittest.mock import patch

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
os.environ.setdefault("VITRINA_ENV", "staging")

from src import config as cfg   # noqa: E402
from src import db              # noqa: E402
from src import env             # noqa: E402

if not env.is_staging:
    sys.exit(f"⛔ Απαιτείται staging. Τώρα: {env.current}")
if os.environ.get("SUPABASE_URL_PRODUCTION"):
    sys.exit("⛔ Υπάρχουν production credentials.")
print(f"  {env.banner()}")
print(f"  DOMAIN_REGISTRAR={cfg.DOMAIN_REGISTRAR}")

from fastapi.testclient import TestClient   # noqa: E402
from src import auth                        # noqa: E402
from src import domain as dom               # noqa: E402
from src import registrars                  # noqa: E402
from src.main import app as main_app        # noqa: E402
from src.meta_oauth import app as api_app   # noqa: E402

MAIN = TestClient(main_app, raise_server_exceptions=False)
API = TestClient(api_app, raise_server_exceptions=False)

CID_A, CID_B = str(uuid.uuid4()), str(uuid.uuid4())
MAIL_A, MAIL_B = "owner-a@example.test", "owner-b@example.test"
results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    results.append((name, ok, detail))
    print(f"  {'✓' if ok else '✗'} {name}{('  — ' + detail) if detail else ''}")
    return ok


for cid, mail, nm in ((CID_A, MAIL_A, "Owner A"), (CID_B, MAIL_B, "Owner B")):
    db._client().table("clients").insert({
        "id": cid, "name": nm, "status": "active", "email": mail,
        "business_type": "test", "city": "STAGING-AUDIT", "phone": "0000000000",
    }).execute()


def cleanup() -> None:
    for t, col in (("domain_orders", "client_id"), ("domains", "client_id"),
                   ("subscriptions", "client_id"), ("clients", "id")):
        for cid in (CID_A, CID_B):
            try:
                db._client().table(t).delete().eq(col, cid).execute()
            except Exception:  # noqa: BLE001
                pass


try:
    # ── ΤΙ ΥΠΟΣΤΗΡΙΖΕΤΑΙ ────────────────────────────────────────────────────
    print("\n── τι υποστηρίζεται πραγματικά ──")
    reg = registrars.get_registrar()
    check("A. subdomain της Vitrina",
          False, "το middleware δεν έχει κανένα *.getvitrina.gr tenant scheme")
    check("B. custom domain πελάτη", True,
          "middleware → /site/<host>· ο πίνακας domains το λύνει")
    check("C. αυτόματη αγορά domain",
          not isinstance(reg, registrars.DnsRegistrar),
          f"ενεργός adapter: {type(reg).__name__} — το register_domain σηκώνει σφάλμα")
    check("D. αυτόματο DNS από την εφαρμογή",
          False, "το add_dns_records καλείται ΜΟΝΟ από papaki· ο πραγματικός "
                 "δρόμος είναι το χειροκίνητο scripts/link_domain.py")

    # ── ΠΡΟΤΑΣΕΙΣ ΚΑΙ ΔΙΑΘΕΣΙΜΟΤΗΤΑ ────────────────────────────────────────
    print("\n── προτάσεις & διαθεσιμότητα ──")
    r = MAIN.post("/domain/suggest", json={"name": "Ταβέρνα Ο Μήτσος",
                                           "business_type": "ταβέρνα", "city": "Λάρισα"})
    slugs = r.json().get("slugs", []) if r.status_code == 200 else []
    check("οι προτάσεις παράγονται", bool(slugs), ", ".join(slugs[:3]))
    check("οι προτάσεις είναι έγκυρα .gr labels",
          all(__import__("re").fullmatch(r"[a-z0-9][a-z0-9-]{1,61}[a-z0-9]", s)
              for s in slugs), f"{len(slugs)} προτάσεις")

    # ΤΟ ΣΥΜΒΟΛΑΙΟ ΑΛΛΑΞΕ, ΕΠΙΤΗΔΕΣ. Οι έλεγχοι εδώ ήταν γραμμένοι για την
    # παλιά εικασία DNS («NXDOMAIN → μάλλον ελεύθερο»), που καταργήθηκε: ένα
    # παρκαρισμένο domain δεν έχει DNS και φαινόταν ελεύθερο. Πλέον η
    # διαθεσιμότητα έρχεται από αυθεντική πηγή και έχει ΤΡΕΙΣ τιμές.
    # Το πλήρες σύνολο ελέγχων είναι στο availability_e2e.py.
    r = MAIN.post("/domain/check", json={"slugs": ["google", "wikipedia"],
                                         "tld": ".com"})
    res = r.json().get("results", []) if r.status_code == 200 else []
    check("gTLD: πιασμένο αναγνωρίζεται από το ΜΗΤΡΩΟ",
          all(x.get("status") == "unavailable" for x in res) and bool(res),
          ", ".join(f"{x.get('domain')}={x.get('status')}" for x in res))
    check("η πηγή δηλώνεται ρητά",
          all(str(x.get("source", "")).startswith("rdap:") for x in res),
          res[0].get("source") if res else "-")
    r = MAIN.post("/domain/check", json={"slugs": ["zzq7x-" + uuid.uuid4().hex[:6]],
                                         "tld": ".gr"})
    gr = (r.json().get("results") or [{}])[0]
    check(".gr χωρίς registrar → 'unknown', ΠΟΤΕ 'available'",
          gr.get("status") == "unknown",
          f"{gr.get('status')} — {str(gr.get('reason'))[:46]}")

    # ── ΑΚΥΡΑ DOMAIN ───────────────────────────────────────────────────────
    print("\n── άκυρες εισόδους ──")
    BAD = ["example.com", "ΕΛΛΗΝΙΚΑ.gr", "a.gr", "-bad.gr", "bad-.gr",
           "../../etc/passwd.gr", "a" * 70 + ".gr", "sub.domain.gr", ""]
    rejected = []
    for d in BAD:
        rr = MAIN.post("/domain/create-checkout",
                       json={"client_id": CID_A, "domain": d})
        rejected.append(rr.status_code == 400)
    check("όλα τα άκυρα domain απορρίπτονται", all(rejected),
          f"{sum(rejected)}/{len(BAD)}")

    # ── ΑΓΟΡΑ: ΤΟ ΟΡΙΟ ─────────────────────────────────────────────────────
    print("\n── το όριο της αγοράς ──")
    try:
        reg.register_domain("audit-never-buy-this.gr")
        check("η αγορά ΔΕΝ εκτελείται με registrar=dns", False, "ΕΚΤΕΛΕΣΤΗΚΕ!")
    except RuntimeError as e:
        check("η αγορά ΔΕΝ εκτελείται με registrar=dns", True, str(e)[:60])
    rr = MAIN.post("/domain/purchase",
                   json={"client_id": CID_A, "domain": "audit-x.gr",
                         "admin_token": "wrong"})
    check("/domain/purchase χωρίς admin token → 403", rr.status_code == 403,
          f"HTTP {rr.status_code}")
    check("το Papaki adapter ΔΕΝ είναι ρυθμισμένο",
          cfg.PAPAKI_API_BASE.startswith("<") or not cfg.PAPAKI_API_KEY
          or cfg.PAPAKI_API_KEY.startswith("<"),
          "τα credentials είναι placeholder κείμενο")

    # ── DNS: ΧΕΙΡΙΣΜΟΣ ΣΦΑΛΜΑΤΟΣ ───────────────────────────────────────────
    print("\n── αποτυχία DNS ──")
    with patch.object(cfg, "CF_API_TOKEN", ""):
        try:
            dom.get_zone_id("audit.example")
            check("χωρίς CF token → καθαρό σφάλμα", False, "δεν σήκωσε")
        except RuntimeError as e:
            check("χωρίς CF token → καθαρό σφάλμα", True, str(e)[:50])

    calls: list[dict] = []

    def fake_cf(method, path, **kw):
        calls.append({"path": path, "rec": kw.get("json", {})})
        if kw.get("json", {}).get("name") == "api":
            raise RuntimeError("Cloudflare API σφάλμα: rate limited")
        if path == "/zones" and method == "GET":       # λίστα, όχι αντικείμενο
            return {"result": [{"id": "zone_fake"}]}
        return {"result": {"id": "zone_fake"}}

    with patch.object(dom, "_cf", side_effect=fake_cf):
        dom.add_dns_records("zone_fake", "x.pages.dev", "y.up.railway.app")
    check("ΜΕΡΙΚΗ δημιουργία DNS ΔΕΝ σηκώνει σφάλμα", True,
          f"{len(calls)} κλήσεις· η αποτυχία του «api» καταπίνεται σιωπηλά")

    saved: list = []
    with patch.object(dom, "_cf", side_effect=fake_cf), \
         patch("src.db.save_domain", side_effect=lambda *a, **k: saved.append(a)), \
         patch.object(dom, "purchase_domain", side_effect=lambda *a, **k: {"ok": True}):
        out = dom.buy_and_setup("audit-fake.gr", CID_A)
    check("μετά από ΜΕΡΙΚΟ DNS το domain γράφεται ως ΕΝΕΡΓΟ",
          bool(saved) and out.get("ssl") == "universal_auto",
          "καμία επαλήθευση πιστοποιητικού· status='active' χωρίς απόδειξη")

    # Ατομικότητα: αγορά πετυχαίνει, zone αποτυγχάνει
    bought: list = []
    with patch.object(dom, "purchase_domain",
                      side_effect=lambda *a, **k: bought.append(a) or {"ok": True}), \
         patch.object(dom, "create_zone", side_effect=RuntimeError("CF down")), \
         patch("src.db.save_domain") as sd:
        try:
            dom.buy_and_setup("audit-atomic.gr", CID_A)
        except RuntimeError:
            pass
    check("αγορά ΟΚ + zone ΑΠΟΤΥΧΙΑ → το domain ΔΕΝ καταγράφεται πουθενά",
          bool(bought) and not sd.called,
          "πληρωμένο και αγορασμένο domain χωρίς καμία εγγραφή — μη ανακτήσιμο")

    # ── ΑΣΦΑΛΕΙΑ: ΔΙΑΣΤΑΥΡΩΣΗ ΠΕΛΑΤΩΝ ─────────────────────────────────────
    print("\n── ασφάλεια: πελάτης Α εναντίον πελάτη Β ──")
    # Προσομοιώνουμε συνδεδεμένο χρήστη Α (η επαλήθευση JWT ανήκει στο Supabase·
    # εδώ ελέγχεται η ΕΞΟΥΣΙΟΔΟΤΗΣΗ, που είναι δικός μας κώδικας).
    with patch.object(auth, "current_email", return_value=MAIL_A):
        own = API.get(f"/clients/{CID_A}/account", headers={"Authorization": "Bearer a"})
        foreign = API.get(f"/clients/{CID_B}/account", headers={"Authorization": "Bearer a"})
        portal = API.post(f"/clients/{CID_B}/billing-portal",
                          headers={"Authorization": "Bearer a"})
        # Έγκυρο σώμα, αλλιώς το 422 της επικύρωσης κρύβει το αν ελέγχθηκε
        # καθόλου η εξουσιοδότηση.
        pub = API.post(f"/clients/{CID_B}/publish",
                       json={"message": "audit", "dry_run": True},
                       headers={"Authorization": "Bearer a"})
    check("ο Α βλέπει τον ΔΙΚΟ του λογαριασμό", own.status_code == 200,
          f"HTTP {own.status_code}")
    check("ο Α ΔΕΝ βλέπει τη συνδρομή του Β", foreign.status_code == 404,
          f"HTTP {foreign.status_code}")
    check("ο Α ΔΕΝ ανοίγει το billing portal του Β", portal.status_code == 404,
          f"HTTP {portal.status_code}")
    check("ο Α ΔΕΝ σκανδαλίζει publish για τον Β", pub.status_code in (403, 404),
          f"HTTP {pub.status_code}")
    noauth = API.get(f"/clients/{CID_B}/account")
    check("χωρίς σύνδεση δεν διαβάζεται λογαριασμός", noauth.status_code == 401,
          f"HTTP {noauth.status_code}")

    print("\n── ασφάλεια: τα αφύλακτα μονοπάτια ──")
    before = len((db._client().table("domain_orders").select("id")
                  .eq("client_id", CID_B).execute()).data or [])
    r = MAIN.post("/domain/create-checkout",
                  json={"client_id": CID_B, "domain": f"audit-{uuid.uuid4().hex[:8]}.gr",
                        "pages_subdomain": "attacker-site.pages.dev"})
    after = (db._client().table("domain_orders").select("*")
             .eq("client_id", CID_B).execute()).data or []
    check("ΞΕΝΟΣ μπορεί να ανοίξει παραγγελία domain για τον Β",
          len(after) > before, f"HTTP {r.status_code}· {len(after)} παραγγελίες")
    check("το pages_subdomain ελέγχεται από τον ΚΑΛΟΥΝΤΑ",
          "pages_subdomain" in open(HERE.parents[1] / "src" / "main.py",
                                    encoding="utf-8").read(),
          "φτάνει στο metadata → buy_and_setup → DNS εγγραφή")

    # ── ΔΙΑΡΡΟΗ ΔΙΑΠΙΣΤΕΥΤΗΡΙΩΝ ────────────────────────────────────────────
    print("\n── διαπιστευτήρια ──")
    SECRETS = {"CF_API_TOKEN": cfg.CF_API_TOKEN, "CF_ACCOUNT_ID": cfg.CF_ACCOUNT_ID,
               "STRIPE_SECRET_KEY": cfg.STRIPE_SECRET_KEY,
               "STRIPE_WEBHOOK_SECRET": cfg.STRIPE_WEBHOOK_SECRET}
    sd = API.get(f"/clients/{CID_A}/site-data")
    blob = sd.text
    leaked = [k for k, v in SECRETS.items() if v and v in blob]
    check("το /site-data δεν περιέχει μυστικά", not leaked, ", ".join(leaked) or "καθαρό")

    src_all = "".join(
        (HERE.parents[1] / "src" / f).read_text(encoding="utf-8")
        for f in ("domain.py", "main.py", "stripe_webhook.py", "registrars.py"))
    check("κανένα print μυστικού στον κώδικα domain/billing",
          not __import__("re").search(
              r"print\([^)]*(CF_API_TOKEN|STRIPE_SECRET_KEY|PAPAKI_API_KEY|"
              r"RAILWAY_TOKEN)", src_all),
          "έλεγχος σε domain/main/stripe_webhook/registrars")

    ai_files = "".join(
        (HERE.parents[1] / "src" / f).read_text(encoding="utf-8")
        for f in ("ai.py", "site_copy.py") if (HERE.parents[1] / "src" / f).exists())
    check("κανένα διαπιστευτήριο υποδομής δεν φτάνει σε AI provider",
          not any(k in ai_files for k in ("CF_API_TOKEN", "PAPAKI_API_KEY",
                                          "RAILWAY_TOKEN", "STRIPE_SECRET_KEY")),
          "έλεγχος σε ai.py/site_copy.py")

    link = (HERE.parents[1] / "scripts" / "link_domain.py").read_text(encoding="utf-8")
    check("το link_domain.py επαληθεύει TLS",
          "CERT_NONE" not in link,
          "ssl.CERT_NONE + check_hostname=False ενώ στέλνει RAILWAY_TOKEN/CF_API_TOKEN")

    # ── ΑΦΑΙΡΕΣΗ / ROLLBACK ────────────────────────────────────────────────
    print("\n── αφαίρεση domain ──")
    all_src = src_all + link
    # Αφαίρεση = να πάψει το domain να δείχνει στη Vitrina: διαγραφή custom
    # domain στο Railway, ή διαγραφή/επαναφορά των DNS εγγραφών, ή endpoint
    # αποσύνδεσης. Το `dns_records/` με PATCH ΔΕΝ μετράει — είναι ενημέρωση.
    removal = [k for k in ("customDomainDelete", "delete_domain",
                           "remove_domain", "detach_domain",
                           'cf("DELETE"', '_cf("DELETE"')
               if k in all_src]
    check("υπάρχει διαδρομή αφαίρεσης/rollback domain", bool(removal),
          ", ".join(removal) or "καμία — μόνο cascade delete ολόκληρου πελάτη")

finally:
    print("\n── καθαρισμός ──")
    cleanup()
    print("  οι εγγραφές staging διαγράφηκαν")

ok = sum(1 for _, o, _ in results if o)
print(f"\n  ΣΥΝΟΛΟ: {ok}/{len(results)}")
(HERE / "domain_security_results.json").write_text(json.dumps(
    [{"check": n, "passed": o, "detail": d} for n, o, d in results],
    ensure_ascii=False, indent=2), encoding="utf-8")
