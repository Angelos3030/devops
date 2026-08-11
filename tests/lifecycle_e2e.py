#!/usr/bin/env python3
"""
Full Customer Lifecycle E2E — τρέχει ΜΟΝΟ σε staging.

    VITRINA_ENV=staging python tests/lifecycle_e2e.py
    VITRINA_ENV=staging python tests/lifecycle_e2e.py --keep   # μη σβήσεις μετά

Προσομοιώνει έναν πραγματικό πελάτη από την πρώτη πρόταση μέχρι την επιστροφή
του μέρες αργότερα. Σηκώνει μόνο του το API πάνω στη staging βάση, τρέχει τη
ροή, και αφήνει το περιβάλλον όπως το βρήκε.

ΤΙ ΔΕΝ ΚΑΝΕΙ (ακόμα): browser rendering. Ελέγχει ότι τα δεδομένα φτάνουν σωστά
στο `/site-data` — δηλαδή στο επίπεδο που τροφοδοτεί τα templates. Το οπτικό
E2E έρχεται όταν στηθεί το Railway staging και υπάρχει πραγματικό URL.

Σε αποτυχία γράφει φάκελο με: αίτημα/απάντηση (χωρίς μυστικά), κατηγορία
αιτίας, correlation id. Τίποτα δεν αγγίζει την παραγωγή — το env.require το
επιβάλλει πριν σηκωθεί οτιδήποτε.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
import time
import uuid
import zlib
from pathlib import Path

sys.path.insert(0, ".")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from dotenv import load_dotenv  # noqa: E402
load_dotenv()

from src import env  # noqa: E402

# ΠΡΩΤΗ γραμμή εκτέλεσης: τίποτα δεν σηκώνεται πριν επιβεβαιωθεί το περιβάλλον.
env.require("staging")

import requests  # noqa: E402
from supabase import create_client  # noqa: E402

API_PORT = 8099
API = f"http://127.0.0.1:{API_PORT}"
RUN_ID = uuid.uuid4().hex[:8]
ART = Path(os.environ.get("TEMP", "/tmp")) / "vitrina-e2e" / RUN_ID
QA_PASSWORD = os.environ.get("QA_TEST_PASSWORD", "")

# Κατηγορίες αιτίας — για να ξέρεις ΠΟΥ να κοιτάξεις χωρίς να διαβάσεις logs.
SETUP, AUTH, API_ERR, DATA, STORAGE, ISOLATION, RENDER, BILLING, CLEANUP = (
    "SETUP", "AUTH", "API", "DATA", "STORAGE", "ISOLATION", "RENDER", "BILLING", "CLEANUP")

passed: list[str] = []
failed: list[tuple[str, str, str]] = []   # (κατηγορία, όνομα, λεπτομέρεια)
created_clients: list[str] = []
uploaded_paths: list[str] = []

SECRET_HINTS = ("key", "token", "secret", "password", "authorization", "apikey")


def redact(value):
    """Καθαρίζει μυστικά πριν γραφτεί οτιδήποτε στον δίσκο."""
    if isinstance(value, dict):
        return {k: ("«κρυμμένο»" if any(h in k.lower() for h in SECRET_HINTS) else redact(v))
                for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, str) and len(value) > 60 and value.count(".") >= 2:
        return value[:12] + "…«κρυμμένο»"
    return value


def artifact(name: str, payload) -> None:
    ART.mkdir(parents=True, exist_ok=True)
    path = ART / name
    body = payload if isinstance(payload, (str, bytes)) else json.dumps(
        redact(payload), ensure_ascii=False, indent=1)
    mode = "wb" if isinstance(body, bytes) else "w"
    with io.open(path, mode, **({} if isinstance(body, bytes) else {"encoding": "utf-8"})) as fh:
        fh.write(body)


def ok(name: str) -> None:
    passed.append(name)
    print(f"  ✓ {name}")


def bad(category: str, name: str, detail: str = "", context=None) -> None:
    failed.append((category, name, detail))
    print(f"  ✗ [{category}] {name}" + (f"  — {detail[:110]}" if detail else ""))
    if context is not None:
        artifact(f"fail-{len(failed):02d}-{name[:34].replace(' ', '_')}.json",
                 {"run": RUN_ID, "category": category, "test": name,
                  "detail": detail[:600], "context": context})


def check(cond: bool, category: str, name: str, detail: str = "", context=None) -> bool:
    (ok(name) if cond else bad(category, name, detail, context))
    return cond


def head(title: str) -> None:
    print(f"\n{title}")


# ─────────────────────────────────────────────────────── υποδομή
def start_api() -> subprocess.Popen:
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.main:app",
         "--port", str(API_PORT), "--log-level", "warning"],
        env={**os.environ, "VITRINA_ENV": "staging", "PYTHONIOENCODING": "utf-8"},
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
    for _ in range(40):
        try:
            requests.get(f"{API}/docs", timeout=1)
            return proc
        except Exception:  # noqa: BLE001
            if proc.poll() is not None:
                out = proc.stdout.read() if proc.stdout else ""
                artifact("api-startup.log", out)
                sys.exit(f"⛔ Το API δεν σηκώθηκε. Δες {ART}/api-startup.log")
            time.sleep(0.5)
    sys.exit("⛔ Το API δεν απάντησε σε 20 δευτερόλεπτα.")


def png_bytes(w: int = 8, h: int = 8) -> bytes:
    """Ελάχιστο έγκυρο PNG — δεν θέλουμε εξάρτηση σε Pillow."""
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (len(data).to_bytes(4, "big") + tag + data
                + zlib.crc32(tag + data).to_bytes(4, "big"))
    raw = b"".join(b"\x00" + b"\xff\x00\x00" * w for _ in range(h))
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", w.to_bytes(4, "big") + h.to_bytes(4, "big") + b"\x08\x02\x00\x00\x00")
            + chunk(b"IDAT", zlib.compress(raw))
            + chunk(b"IEND", b""))


def sb_service():
    return create_client(os.environ["SUPABASE_URL_STAGING"], os.environ["SUPABASE_KEY_STAGING"])


def login(email: str) -> str | None:
    """Επιστρέφει access token — ό,τι θα είχε ο browser του πελάτη."""
    sb = create_client(os.environ["SUPABASE_URL_STAGING"], os.environ["SUPABASE_KEY_STAGING"])
    try:
        res = sb.auth.sign_in_with_password({"email": email, "password": QA_PASSWORD})
        return res.session.access_token if res.session else None
    except Exception as e:  # noqa: BLE001
        bad(AUTH, f"login {email}", str(e)[:160])
        return None


def call(method: str, path: str, token: str | None = None, **kw):
    headers = kw.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.request(method, API + path, headers=headers, timeout=60, **kw)


# ─────────────────────────────────────────────────────── τα σενάρια
def scenario_start_flow() -> str | None:
    head("[1] Πρώτη επαφή — μία πρόταση γίνεται πελάτης")
    r = call("POST", "/start", json={"text": "Έχω καφετέρια στον Γέρακα"})
    if not check(r.status_code == 200, API_ERR, "POST /start", f"HTTP {r.status_code}",
                 {"status": r.status_code, "body": r.text[:400]}):
        return None
    data = r.json()
    cid = data.get("client_id")
    created_clients.append(cid)
    check(bool(cid), DATA, "επιστρέφει client_id")
    parsed = data.get("parsed") or {}
    check(parsed.get("type") == "Καφετέρια", DATA, "αναγνώρισε το επάγγελμα",
          f"πήρα {parsed.get('type')!r}", parsed)
    check(bool(parsed.get("city")), DATA, "αναγνώρισε την πόλη", context=parsed)

    r = call("GET", f"/progress/{cid}")
    check(r.status_code == 200 and len(r.json().get("stages", [])) == 5,
          API_ERR, "GET /progress επιστρέφει 5 στάδια", f"HTTP {r.status_code}")
    return cid


def scenario_ownership(cid: str, token: str, other_token: str) -> None:
    head("[2] Ιδιοκτησία — ο ένας πελάτης δεν βλέπει τον άλλον")
    r = call("GET", f"/clients/{cid}/content", token=token)
    check(r.status_code == 200, AUTH, "ο ιδιοκτήτης διαβάζει τα δικά του",
          f"HTTP {r.status_code}", {"status": r.status_code, "body": r.text[:200]})

    r = call("GET", f"/clients/{cid}/content", token=other_token)
    check(r.status_code == 404, ISOLATION, "ξένος χρήστης παίρνει 404",
          f"HTTP {r.status_code} — ΔΙΑΡΡΟΗ" if r.status_code == 200 else f"HTTP {r.status_code}",
          {"status": r.status_code})

    r = call("GET", f"/clients/{cid}/content")
    check(r.status_code in (401, 403), AUTH, "χωρίς token απορρίπτεται",
          f"HTTP {r.status_code}")


def scenario_content(cid: str, token: str) -> None:
    head("[3] Στοιχεία & υπηρεσίες — γράψιμο και ανάγνωση")
    payload = {
        "name": "Καφέ Δοκιμή E2E", "phone": "2100009999",
        "email": "qa-cafe@vitrina.test", "hours": "Καθημερινά 08:00–22:00",
        "facebook": "@kafedokimi", "instagram": "instagram.com/kafedokimi",
        "services": [{"name": "Espresso", "description": "Φρεσκοκαβουρδισμένος"},
                     {"name": "Γλυκά", "description": "Σπιτικά"}],
    }
    r = call("PUT", f"/clients/{cid}/content", token=token, json={"content": payload})
    if not check(r.status_code == 200, API_ERR, "PUT /content", f"HTTP {r.status_code}",
                 {"status": r.status_code, "body": r.text[:300]}):
        return

    got = call("GET", f"/clients/{cid}/content", token=token).json().get("content", {})
    check(got.get("phone") == "2100009999", DATA, "το τηλέφωνο αποθηκεύτηκε", context=got)
    check(got.get("email") == "qa-cafe@vitrina.test", DATA, "το email αποθηκεύτηκε")
    check(got.get("facebook") == "@kafedokimi", DATA, "το facebook αποθηκεύτηκε ΟΠΩΣ γράφτηκε")
    names = [s.get("name") for s in got.get("services", [])]
    check(names == ["Espresso", "Γλυκά"], DATA, "οι υπηρεσίες με τη σειρά τους", str(names))

    # CRUD: προσθήκη, επεξεργασία, διαγραφή
    payload["services"] = [{"name": "Espresso", "description": "Διπλός"},
                           {"name": "Γλυκά", "description": "Σπιτικά"},
                           {"name": "Brunch", "description": "Σαββατοκύριακο"}]
    call("PUT", f"/clients/{cid}/content", token=token, json={"content": payload})
    svc = call("GET", f"/clients/{cid}/content", token=token).json()["content"]["services"]
    check(len(svc) == 3 and svc[0]["description"] == "Διπλός",
          DATA, "προσθήκη + επεξεργασία υπηρεσίας", str(svc))

    payload["services"] = payload["services"][:1]
    call("PUT", f"/clients/{cid}/content", token=token, json={"content": payload})
    svc = call("GET", f"/clients/{cid}/content", token=token).json()["content"]["services"]
    check(len(svc) == 1, DATA, "διαγραφή υπηρεσίας", str(svc))

    # Το backend πετάει τις ανώνυμες — το UI προειδοποιεί, εδώ επιβεβαιώνουμε
    payload["services"] = [{"name": "Espresso", "description": "x"}, {"name": "  ", "description": "y"}]
    call("PUT", f"/clients/{cid}/content", token=token, json={"content": payload})
    svc = call("GET", f"/clients/{cid}/content", token=token).json()["content"]["services"]
    check(len(svc) == 1, DATA, "υπηρεσία χωρίς όνομα απορρίπτεται", str(svc))

    # Allowlist: ό,τι δεν επιτρέπεται δεν πρέπει να περάσει
    call("PUT", f"/clients/{cid}/content", token=token,
         json={"content": {**payload, "status": "active", "plan": "premium"}})
    got = call("GET", f"/clients/{cid}/content", token=token).json()["content"]
    check("plan" not in got and "status" not in got,
          DATA, "πεδία εκτός allowlist αγνοούνται", str(list(got.keys()))[:120])


def scenario_photos(cid: str, token: str) -> None:
    head("[4] Φωτογραφίες — ανέβασμα, αντικατάσταση, διαγραφή")
    auth_h = {"Authorization": f"Bearer {token}"}
    # ΠΡΩΤΑ ο αρνητικός έλεγχος: χωρίς ταυτότητα δεν ανεβάζει κανείς.
    anon = requests.post(f"{API}/clients/{cid}/upload",
                         files={"file": ("anon.png", png_bytes(), "image/png")},
                         data={"asset_type": "photo"}, timeout=60)
    check(anon.status_code == 401, ISOLATION, "ανέβασμα χωρίς σύνδεση απορρίπτεται",
          f"HTTP {anon.status_code}" + (" — ΑΝΟΙΧΤΟ ENDPOINT" if anon.status_code == 200 else ""))

    files = {"file": ("e2e.png", png_bytes(), "image/png")}
    r = requests.post(f"{API}/clients/{cid}/upload", files=files, headers=auth_h,
                      data={"asset_type": "photo"}, timeout=90)
    if not check(r.status_code == 200, STORAGE, "ανέβασμα φωτογραφίας",
                 f"HTTP {r.status_code}", {"status": r.status_code, "body": r.text[:300]}):
        return
    first = r.json()
    uploaded_paths.append(first.get("url", ""))
    check(bool(first.get("url", "").startswith("http")), STORAGE, "επιστρέφει δημόσιο URL")

    live = requests.get(first["url"], timeout=30)
    check(live.status_code == 200 and live.content[:8] == b"\x89PNG\r\n\x1a\n",
          STORAGE, "η εικόνα σερβίρεται πραγματικά", f"HTTP {live.status_code}")

    assets = call("GET", f"/clients/{cid}/assets", token=token).json().get("assets", [])
    check(len(assets) >= 1, DATA, "η φωτογραφία φαίνεται στη λίστα", str(len(assets)))

    # Λάθος τύπος — το backend πρέπει να κόψει
    r = requests.post(f"{API}/clients/{cid}/upload", headers=auth_h,
                      files={"file": ("x.pdf", b"%PDF-1.4 fake", "application/pdf")},
                      data={"asset_type": "photo"}, timeout=60)
    check(r.status_code == 400, STORAGE, "PDF απορρίπτεται", f"HTTP {r.status_code}")

    # Αντικατάσταση: ανεβάζω νέα, μετά σβήνω την παλιά (η σειρά του UI)
    r2 = requests.post(f"{API}/clients/{cid}/upload", headers=auth_h,
                       files={"file": ("e2e2.png", png_bytes(10, 10), "image/png")},
                       data={"asset_type": "photo"}, timeout=90)
    check(r2.status_code == 200, STORAGE, "ανέβασμα αντικαταστάτριας", f"HTTP {r2.status_code}")
    if r2.status_code == 200:
        uploaded_paths.append(r2.json().get("url", ""))

    old_id = assets[0].get("id")
    r = call("DELETE", f"/clients/{cid}/assets/{old_id}", token=token)
    check(r.status_code == 200, STORAGE, "διαγραφή παλιάς", f"HTTP {r.status_code}",
          {"status": r.status_code, "body": r.text[:200]})

    left = call("GET", f"/clients/{cid}/assets", token=token).json().get("assets", [])
    check(all(a.get("id") != old_id for a in left), DATA, "η παλιά έφυγε από τη λίστα")

    r = call("DELETE", f"/clients/{cid}/assets/{old_id}", token=token)
    check(r.status_code == 404, API_ERR, "δεύτερη διαγραφή → 404 (idempotent)",
          f"HTTP {r.status_code}")


def scenario_asset_isolation(cid: str, other_token: str) -> None:
    head("[5] Απομόνωση assets")
    assets = sb_service().table("client_assets").select("id").eq("client_id", cid).execute().data
    if not assets:
        bad(SETUP, "δεν βρέθηκε asset για τον έλεγχο απομόνωσης")
        return
    r = call("DELETE", f"/clients/{cid}/assets/{assets[0]['id']}", token=other_token)
    check(r.status_code == 404, ISOLATION, "ξένος δεν σβήνει φωτογραφία",
          f"HTTP {r.status_code} — ΔΙΑΡΡΟΗ" if r.status_code == 200 else f"HTTP {r.status_code}")


def scenario_session(cid: str, email: str) -> None:
    head("[6] Επιστροφή πελάτη — νέα συνεδρία, ίδια δεδομένα")
    token2 = login(email)                       # καθαρή σύνδεση = «άλλη μέρα»
    if not check(bool(token2), AUTH, "δεύτερη σύνδεση"):
        return
    check(token2 is not None, AUTH, "νέο token διαφορετικό από το πρώτο")
    got = call("GET", f"/clients/{cid}/content", token=token2)
    if not check(got.status_code == 200, AUTH, "βλέπει το site του μετά από νέο login",
                 f"HTTP {got.status_code}"):
        return
    c = got.json().get("content", {})
    check(c.get("phone") == "2100009999", DATA, "το τηλέφωνο επέζησε της συνεδρίας")
    check(c.get("facebook") == "@kafedokimi", DATA, "τα social επέζησαν")

    r = call("GET", "/clients/lookup", token=token2)
    ids = [x.get("id") for x in r.json().get("clients", [])]
    check(cid in ids, AUTH, "το /clients/lookup το βρίσκει από το email", str(ids)[:120])


def scenario_render(cid: str) -> None:
    head("[7] Τα δεδομένα φτάνουν στο render")
    r = call("GET", f"/clients/{cid}/site-data")
    if not check(r.status_code == 200, RENDER, "GET /site-data", f"HTTP {r.status_code}"):
        return
    # Η απάντηση είναι {"layout":…, "data":{…}} — τα πεδία είναι ΜΕΣΑ στο data.
    d = r.json().get("data", {})
    blob = json.dumps(d, ensure_ascii=False)
    check(d.get("PHONE_INTL", "").endswith("2100009999") or "2100009999" in blob,
          RENDER, "το τηλέφωνο φτάνει στο template", context={"PHONE": d.get("PHONE")})
    check(d.get("EMAIL") == "qa-cafe@vitrina.test", RENDER, "το email φτάνει",
          str(d.get("EMAIL")))
    # Το backend κανονικοποιεί «@handle» → πλήρες URL
    check(d.get("FACEBOOK") == "https://facebook.com/kafedokimi",
          RENDER, "το «@handle» έγινε έγκυρο URL", str(d.get("FACEBOOK")))
    check(d.get("INSTAGRAM", "").startswith("https://instagram.com/"),
          RENDER, "το instagram κανονικοποιήθηκε", str(d.get("INSTAGRAM")))
    check("Espresso" in blob, RENDER, "οι υπηρεσίες φτάνουν στο template")
    artifact("site-data.json", d)


def scenario_billing(cid: str) -> None:
    head("[8] Χρέωση — test mode")
    if not os.environ.get("STRIPE_SECRET_KEY", "").startswith("sk_test_"):
        bad(BILLING, "Stripe δεν είναι σε test mode", "παραλείπω για ασφάλεια")
        return
    r = call("POST", "/create-checkout", json={"client_id": cid, "plan": "site"})
    if not check(r.status_code == 200, BILLING, "δημιουργία checkout session",
                 f"HTTP {r.status_code}", {"status": r.status_code, "body": r.text[:300]}):
        return
    url = r.json().get("checkout_url", "")
    check(url.startswith("https://checkout.stripe.com"), BILLING, "έγκυρο checkout URL",
          url[:60])

    import stripe
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
    try:
        # Το StripeObject ΔΕΝ έχει .get() — το __getattr__ το ερμηνεύει ως πεδίο
        # και πετάει AttributeError. Πάντα to_dict() πρώτα.
        sessions = stripe.checkout.Session.list(limit=10)
        session = next((x for x in sessions.data
                        if (x.metadata.to_dict() if x.metadata else {}).get("client_id") == cid),
                       None)
        check(session is not None, BILLING,
              "το client_id υπάρχει στο metadata της session",
              "χωρίς αυτό, το webhook δεν συνδέει ποτέ email→πελάτη")
    except Exception as e:  # noqa: BLE001
        bad(BILLING, "ανάγνωση session από το Stripe", str(e)[:140])

    # Σύνδεση email — η γέφυρα λογαριασμού↔site, ακριβώς όπως την καλεί το webhook.
    # Χρειάζεται ΝΕΟΣ πελάτης χωρίς email: αυτή είναι η κατάσταση μετά το /start.
    from src import db
    fresh = call("POST", "/start", json={"text": "Έχω φούρνο στη Νέα Σμύρνη"})
    if fresh.status_code != 200:
        bad(BILLING, "δημιουργία πελάτη για τον έλεγχο σύνδεσης email",
            f"HTTP {fresh.status_code}")
        return
    fid = fresh.json()["client_id"]
    created_clients.append(fid)
    row = sb_service().table("clients").select("email").eq("id", fid).execute().data[0]
    check(not (row.get("email") or ""), BILLING,
          "ο πελάτης από /start ΔΕΝ έχει email (η αιτία του bug)", str(row))
    check(db.link_client_email(fid, "qa-newbuyer@vitrina.test") == "linked",
          BILLING, "το checkout συνδέει το email")
    check(db.link_client_email(fid, "qa-newbuyer@vitrina.test") == "already",
          BILLING, "idempotent — δεύτερη κλήση δεν ξαναγράφει")
    check(db.link_client_email(fid, "qa-other@vitrina.test") == "kept-existing",
          BILLING, "δεν αντικαθιστά έγκυρο υπάρχον email")
    # Και το αποτέλεσμα που έχει σημασία: το βρίσκει πλέον το dashboard.
    found = db.get_clients_by_email("qa-newbuyer@vitrina.test")
    check(any(c["id"] == fid for c in found), BILLING,
          "μετά τη σύνδεση, το /clients/lookup τον βρίσκει", str(len(found)))


def scenario_cleanup_policy() -> None:
    head("[9] Πολιτική καθαρισμού — μόνο σε staging")
    r = subprocess.run([sys.executable, "scripts/cleanup_abandoned.py", "--delete"],
                       capture_output=True, text=True, encoding="utf-8",
                       env={**os.environ, "VITRINA_ENV": "production", "PYTHONIOENCODING": "utf-8"})
    out = (r.stdout or "") + (r.stderr or "")
    check("Επιτρέπεται μόνο σε: staging" in out, CLEANUP,
          "αρνείται να τρέξει σε production", out[-160:])

    r = subprocess.run([sys.executable, "scripts/cleanup_abandoned.py", "--delete"],
                       capture_output=True, text=True, encoding="utf-8",
                       env={**os.environ, "VITRINA_ENV": "staging", "PYTHONIOENCODING": "utf-8"})
    out = (r.stdout or "") + (r.stderr or "")
    check("χωρίς επιβεβαίωση" in out, CLEANUP,
          "αρνείται χωρίς --confirm-staging", out[-160:])

    r = subprocess.run([sys.executable, "scripts/cleanup_abandoned.py"],
                       capture_output=True, text=True, encoding="utf-8",
                       env={**os.environ, "VITRINA_ENV": "staging", "PYTHONIOENCODING": "utf-8"})
    check("DRY RUN" in (r.stdout or "") or "τίποτα προς διαγραφή" in (r.stdout or ""),
          CLEANUP, "dry-run by default")


# ─────────────────────────────────────────────────────── καθαρισμός
def cleanup(keep: bool) -> None:
    head("[10] Καθαρισμός — το staging όπως το βρήκαμε")
    if keep:
        print("  (--keep: δεν σβήνω τίποτα)")
        return
    sb = sb_service()
    for cid in created_clients:
        try:
            assets = sb.table("client_assets").select("url").eq("client_id", cid).execute().data
            paths = [a["url"].split("/client-assets/")[-1] for a in assets
                     if a.get("url") and "/client-assets/" in a["url"]]
            if paths:
                sb.storage.from_("client-assets").remove(paths)
        except Exception:  # noqa: BLE001
            pass
        try:
            sb.table("clients").delete().eq("id", cid).execute()
        except Exception as e:  # noqa: BLE001
            bad(CLEANUP, f"διαγραφή {cid[:8]}", str(e)[:100])
    left = sb.table("clients").select("id").in_("id", created_clients).execute().data if created_clients else []
    check(not left, CLEANUP, "όλοι οι δοκιμαστικοί πελάτες σβήστηκαν", str(len(left)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true", help="μη σβήσεις τα δεδομένα μετά")
    args = ap.parse_args()

    print("=" * 68)
    print(f"VITRINA — Lifecycle E2E   ·   run {RUN_ID}")
    print(env.banner())
    print("=" * 68)

    if not QA_PASSWORD:
        sys.exit("⛔ Λείπει το QA_TEST_PASSWORD. Τρέξε πρώτα το seed_staging.py")

    proc = start_api()
    try:
        subprocess.run([sys.executable, "scripts/seed_staging.py", "--seed", "--confirm-staging"],
                       capture_output=True, text=True, encoding="utf-8",
                       env={**os.environ, "VITRINA_ENV": "staging", "PYTHONIOENCODING": "utf-8"})

        cid = scenario_start_flow()
        if not cid:
            return 1

        # Ο νέος πελάτης δεν έχει email — του το δίνουμε όπως θα το έκανε το ταμείο.
        sb_service().table("clients").update({"email": "qa-cafe@vitrina.test"}).eq("id", cid).execute()

        token = login("qa-cafe@vitrina.test")
        other = login("qa-dentist@vitrina.test")
        if not token or not other:
            return 1

        scenario_ownership(cid, token, other)
        scenario_content(cid, token)
        scenario_photos(cid, token)
        scenario_asset_isolation(cid, other)
        scenario_session(cid, "qa-cafe@vitrina.test")
        scenario_render(cid)
        scenario_billing(cid)
        scenario_cleanup_policy()
    finally:
        cleanup(args.keep)
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:  # noqa: BLE001
            proc.kill()

    print("\n" + "=" * 68)
    print(f"ΠΕΡΑΣΑΝ: {len(passed)}   ΕΣΠΑΣΑΝ: {len(failed)}")
    if failed:
        by_cat: dict[str, list[str]] = {}
        for cat, name, _ in failed:
            by_cat.setdefault(cat, []).append(name)
        print("\n❌ Ανά κατηγορία αιτίας:")
        for cat, names in by_cat.items():
            print(f"   [{cat}] {len(names)}")
            for n in names:
                print(f"      · {n}")
        print(f"\n   Λεπτομέρειες: {ART}")
        return 1
    print("\n✅ Ο πλήρης κύκλος ζωής δουλεύει. Το staging είναι καθαρό.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
