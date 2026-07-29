#!/usr/bin/env python3
"""
End-to-end έλεγχος του ζωντανού συστήματος. Τρέξε ΠΡΙΝ και ΜΕΤΑ από κάθε deploy:

    python scripts/e2e.py              # όλα
    python scripts/e2e.py --quick      # χωρίς δημιουργία δοκιμαστικού πελάτη

Ελέγχει ό,τι θα δει πραγματικός πελάτης: εγγραφή → σχέδια → site, ασφάλεια
(κανείς δεν βλέπει ξένα δεδομένα), το ζωντανό site του πελάτη με χάρτη/schema,
τις διαφημιστικές σελίδες, και ότι κάθε domain σερβίρει ΤΟ ΔΙΚΟ ΤΟΥ robots/sitemap.

Ο δοκιμαστικός πελάτης διαγράφεται στο τέλος — δεν αφήνει σκουπίδια στη βάση.
Έξοδος: 0 όλα πέρασαν, 1 κάτι έσπασε (χρήσιμο για CI).
"""
from __future__ import annotations

import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.request

API = "https://devops-production-d563.up.railway.app"
SITES = "https://sites-production-da56.up.railway.app"
CLIENT_SITE = "https://www.koutrakiskouzines.gr"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"

_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

PASS, FAIL = [], []


def check(name: str, ok: bool, detail: str = "") -> bool:
    (PASS if ok else FAIL).append(name)
    print(f"  {'✓' if ok else '✗'} {name}{('  — ' + detail) if detail else ''}", flush=True)
    return ok


def req(url: str, data=None, headers=None, method=None):
    h = {"User-Agent": UA, **(headers or {})}
    body = None
    if data is not None:
        h["Content-Type"] = "application/json"
        body = json.dumps(data).encode()
    r = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        resp = urllib.request.urlopen(r, timeout=40, context=_ctx)
        return resp.status, resp.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")
    except Exception as e:  # noqa: BLE001
        return 0, str(e)


# --------------------------------------------------------------------------
def test_security() -> None:
    print("\n[ΑΣΦΑΛΕΙΑ] Τα δεδομένα πελατών θέλουν σύνδεση")
    cid = "981a3a75-2d55-48fa-ba31-23422773f8fa"
    for path in ("/clients/lookup",
                 f"/clients/{cid}/content",
                 f"/clients/{cid}/account"):
        code, _ = req(API + path)
        check(f"χωρίς token {path[:38]:38} → 401/403", code in (401, 403), f"πήρα {code}")
    # το παλιό leak: ?email= δεν πρέπει να δουλεύει ποτέ ξανά
    code, _ = req(API + "/clients/lookup?email=angelospapadopoulos30@gmail.com")
    check("το παλιό leak (?email=) είναι κλειστό", code in (401, 403), f"πήρα {code}")


def test_client_site() -> None:
    print("\n[ΠΕΛΑΤΗΣ] Το ζωντανό site")
    code, html = req(CLIENT_SITE)
    if not check("το site φορτώνει (200)", code == 200, f"πήρα {code}"):
        return
    check("δείχνει το όνομα του πελάτη", "Κουτράκ" in html)
    check("ΔΕΝ λέει «δεν είναι διαθέσιμο»", "δεν είναι διαθέσιμο" not in html)
    check("έχει ενότητα χάρτη", "Πού θα μας βρεις" in html and "google.com/maps" in html)

    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    if check("υπάρχει JSON-LD", bool(m)):
        d = json.loads(m.group(1))
        check("schema: geo συντεταγμένες", bool(d.get("geo")))
        check("schema: ωράριο δομημένο", bool(d.get("openingHoursSpecification")),
              "η Google δεν διαβάζει το ελληνικό κείμενο")
        check("schema: hasMap", bool(d.get("hasMap")))
        check("schema: τηλέφωνο", bool(d.get("telephone")))

    check("canonical", 'rel="canonical"' in html)
    check("SSR — περιεχόμενο χωρίς JS", "ουζίν" in html or "Υπηρεσίες" in html)

    # ασφάλεια μεταφοράς
    code, hdrs = 0, {}
    try:
        r = urllib.request.urlopen(urllib.request.Request(CLIENT_SITE, headers={"User-Agent": UA}),
                                   timeout=30, context=_ctx)
        hdrs = {k.lower(): v for k, v in r.headers.items()}
    except Exception:
        pass
    for h in ("strict-transport-security", "x-content-type-options", "x-frame-options"):
        check(f"header {h}", h in hdrs)


def test_per_domain_seo() -> None:
    print("\n[SEO ανά domain] Κάθε domain το ΔΙΚΟ του robots/sitemap")
    code, robots = req(CLIENT_SITE + "/robots.txt")
    check("robots.txt πελάτη (200)", code == 200)
    check("ΔΕΝ δείχνει στο δικό μας sitemap", "railway.app/sitemap" not in robots,
          "θα έστελνε τη Google στις δικές μας σελίδες")
    check("δείχνει στο δικό του sitemap", "koutrakiskouzines.gr/sitemap.xml" in robots)

    code, sm = req(CLIENT_SITE + "/sitemap.xml")
    check("sitemap πελάτη (200)", code == 200)
    check("περιέχει ΜΟΝΟ το domain του", "koutrakiskouzines.gr" in sm and "/gia/" not in sm)

    code, ours = req(SITES + "/sitemap.xml")
    check("το δικό μας sitemap έμεινε ανέπαφο", code == 200 and ours.count("<loc>") == 10,
          f"{ours.count('<loc>')} σελίδες")


def test_marketing() -> None:
    print("\n[MARKETING] Σελίδες που φέρνουν πελάτες")
    trades = ["taverna", "kafe", "kommotirio", "iatreio", "dikigoros",
              "texnitis", "domatia", "gymnastirio", "synergeio", "paragogos"]
    bad = [t for t in trades if req(f"{SITES}/gia/{t}")[0] != 200]
    check(f"και οι {len(trades)} διαφημιστικές σελίδες", not bad, f"έσπασαν: {bad}")

    code, html = req(SITES + "/dashboard")
    check("dashboard φορτώνει", code == 200)
    code, _ = req(SITES + "/odigos/google")
    check("οδηγός Google για πελάτες", code == 200)


def test_signup() -> str | None:
    print("\n[ΕΓΓΡΑΦΗ] Η διαδρομή που περνάει ο πελάτης")
    code, body = req(API + "/onboard", {
        "name": "ΔΟΚΙΜΗ E2E", "type": "Ταβέρνα", "city": "Αθήνα",
        "email": "e2e@getvitrina.gr"})
    if not check("δημιουργία πελάτη", code == 200, body[:80]):
        return None
    cid = json.loads(body)["client_id"]

    tpls = []
    for _ in range(10):
        time.sleep(3)
        code, body = req(f"{API}/clients/{cid}/designs")
        if code == 200:
            tpls = json.loads(body).get("templates", [])
            if tpls:
                break
    check("προτείνονται σχέδια", bool(tpls), str(tpls))
    check("smart-match: ταβέρνα → ember", tpls[:1] == ["ember"] if tpls else False, str(tpls[:1]))

    code, html = req(f"{SITES}/site/{cid}")
    check("το site του render-άρει", code == 200 and "ΔΟΚΙΜΗ" in html)
    return cid


def cleanup(cid: str) -> None:
    print("\n[ΚΑΘΑΡΙΣΜΟΣ]")
    try:
        sys.path.insert(0, ".")
        from src import db
        db.delete_client(cid)
        check("ο δοκιμαστικός πελάτης διαγράφηκε", True)
    except Exception as e:  # noqa: BLE001
        check("ο δοκιμαστικός πελάτης διαγράφηκε", False, str(e)[:90])
        print(f"    ⚠ σβήσε χειροκίνητα: {cid}")


def main() -> int:
    quick = "--quick" in sys.argv
    print("=" * 64)
    print("VITRINA — έλεγχος ζωντανού συστήματος")
    print("=" * 64)

    test_security()
    test_client_site()
    test_per_domain_seo()
    test_marketing()

    cid = None
    if not quick:
        cid = test_signup()
        if cid:
            cleanup(cid)
    else:
        print("\n[ΕΓΓΡΑΦΗ] παραλείφθηκε (--quick)")

    print("\n" + "=" * 64)
    print(f"ΠΕΡΑΣΑΝ: {len(PASS)}   ΕΣΠΑΣΑΝ: {len(FAIL)}")
    if FAIL:
        print("\n❌ ΠΡΟΒΛΗΜΑΤΑ:")
        for f in FAIL:
            print(f"   • {f}")
        return 1
    print("\n✅ Όλα καλά — μπορείς να κάνεις deploy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
