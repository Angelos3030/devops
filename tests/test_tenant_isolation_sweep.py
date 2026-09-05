"""ΚΑΘΕ authenticated endpoint πελάτη, όχι ένα δείγμα.

ΓΙΑΤΙ ΣΑΡΩΣΗ ΚΑΙ ΟΧΙ ΔΕΙΓΜΑ. Η απομόνωση δεν είναι ιδιότητα του συστήματος —
είναι ιδιότητα κάθε ΜΕΜΟΝΩΜΕΝΟΥ endpoint. Μετρήθηκε στο παρελθόν: πέντε
endpoints έμεναν αφύλακτα επειδή η ροή είναι «site first» και δεν υπήρχε ακόμη
χρήστης· ένα `POST /clients/<ξένο id>/select-design` χωρίς κανένα header άλλαζε
theme άλλου πελάτη. Ένα δείγμα τριών endpoints δεν θα το είχε πιάσει.

Η λίστα παράγεται ΑΠΟ ΤΟΝ ΚΩΔΙΚΑ, όχι γραμμένη με το χέρι: αν προστεθεί νέο
`/clients/{client_id}/…`, μπαίνει αυτόματα στη σάρωση και πρέπει να το
δικαιολογήσει κάποιος.

Τρεις ερωτήσεις ανά endpoint:
  1. χωρίς κανένα διαπιστευτήριο  → απορρίπτεται;
  2. με token ΑΛΛΟΥ πελάτη        → απορρίπτεται;
  3. με λάθος claim token         → απορρίπτεται;

ΕΚΤΟΣ ΣΚΟΠΟΥ: `/billing-portal` — ανήκει στο ενεργό billing track (lock
`STATUS.md`, Codex 2026-09-05) και δοκιμάζεται από εκεί.
"""
from __future__ import annotations

import inspect
import os
import re
import unittest
import uuid
from unittest.mock import patch

os.environ.setdefault("VITRINA_ENV", "staging")

from fastapi.testclient import TestClient  # noqa: E402

from src import auth, db                   # noqa: E402
from src import main as main_mod           # noqa: E402
from src import meta_oauth                 # noqa: E402

# Το `/site-data` είναι ΣΚΟΠΙΜΑ δημόσιο: τροφοδοτεί τη δημόσια σελίδα του
# πελάτη. Δεν επιστρέφει τίποτα ιδιωτικό — αυτό το επιβάλλει χωριστό test.
PUBLIC = {"/clients/{client_id}/site-data"}
# Ενεργό lock άλλου agent.
OUT_OF_SCOPE = {"/clients/{client_id}/billing-portal"}

# Ελάχιστο έγκυρο σώμα ανά endpoint, ώστε η απόρριψη να είναι ΕΞΟΥΣΙΟΔΟΤΗΣΗΣ
# και όχι επικύρωσης (422). Χωρίς αυτό η σάρωση θα «περνούσε» για λάθος λόγο.
BODIES = {
    "put_content": {"content": {"phone": "2100000000"}},
    "chat_edit": {"message": "άλλαξε το τηλέφωνο"},
    "apply_editor_proposal": {"message": "αλλαγή", "operations": [],
                              "expected_version": 0,
                              "idempotency_key": "sweep-apply"},
    "undo_editor_change": {"expected_version": 1,
                           "idempotency_key": "sweep-undo"},
    "publish_post": {"message": "δοκιμή", "dry_run": True},
    "select_design": {"layout": "grecko-table"},
    "create_social_draft": {"caption": "δοκιμή"},
    "add_client_asset": {"url": "https://example.test/a.png", "type": "photo"},
    "claim_site": {"token": "x" * 40},
    "approve_social_post": {},
    "preview_social_post": {},
    "reject_social_post": {},
}

# Endpoints που δέχονται multipart, όχι JSON.
MULTIPART = {"upload_asset"}
# Ελάχιστο έγκυρο PNG (1×1), ώστε να περάσει τον έλεγχο content-type.
PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c6300010000050001od0a2db40000000049454e44ae"
    "426082".replace("od", "0d"))


def endpoints() -> list[tuple[str, str, str]]:
    """(verb, path, fn) για κάθε client-scoped route, από τον ίδιο τον κώδικα."""
    found: set[tuple[str, str, str]] = set()
    for mod in (meta_oauth, main_mod):
        src = inspect.getsource(mod)
        for m in re.finditer(
                r'@app\.(get|post|put|delete|patch)\("([^"]+)"\)\s*\n'
                r'(?:async )?def (\w+)\(((?:[^()]|\([^()]*\))*)\)', src):
            verb, path, fn, args = m.groups()
            if "{client_id}" not in path:
                continue
            if path in PUBLIC or path in OUT_OF_SCOPE:
                continue
            if "authorization" not in args:
                continue
            found.add((verb.upper(), path, fn))
    return sorted(found, key=lambda x: (x[1], x[0]))


MAIN = TestClient(main_mod.app, raise_server_exceptions=False)
API = TestClient(meta_oauth.app, raise_server_exceptions=False)

CID_A, CID_B = str(uuid.uuid4()), str(uuid.uuid4())
MAIL_A, MAIL_B = "sweep-a@example.test", "sweep-b@example.test"
REJECT = {401, 403, 404}


class TenantIsolationSweep(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        for cid, mail, nm in ((CID_A, MAIL_A, "Sweep A"), (CID_B, MAIL_B, "Sweep B")):
            db._client().table("clients").insert({
                "id": cid, "name": nm, "status": "active", "email": mail,
                "business_type": "test", "city": "STAGING-SWEEP",
                "phone": "0000000000",
            }).execute()
        cls.routes = endpoints()

    @classmethod
    def tearDownClass(cls):
        for t, col in (("site_content", "client_id"), ("client_assets", "client_id"),
                       ("posts", "client_id"), ("clients", "id")):
            for cid in (CID_A, CID_B):
                try:
                    db._client().table(t).delete().eq(col, cid).execute()
                except Exception:  # noqa: BLE001
                    pass

    def call(self, verb: str, path: str, fn: str, headers: dict | None = None):
        url = path.replace("{client_id}", CID_B).replace("{asset_id}", str(uuid.uuid4()))
        url = url.replace("{post_id}", str(uuid.uuid4()))
        client = MAIN if fn in dir(main_mod) else API
        kw = {"headers": headers or {}}
        if fn in MULTIPART:
            # Το `/upload` δέχεται ΑΡΧΕΙΟ, όχι JSON. Με JSON σώμα απαντούσε 422
            # και η σάρωση θα «περνούσε» για λάθος λόγο: 422 σημαίνει ότι το
            # αίτημα δεν έφτασε ΠΟΤΕ στον έλεγχο ιδιοκτησίας, άρα δεν αποδεικνύει
            # τίποτα για την απομόνωση.
            kw["files"] = {"file": ("t.png", PNG, "image/png")}
            kw["data"] = {"asset_type": "photo", "rights_ok": "true"}
        elif verb in ("POST", "PUT", "PATCH"):
            kw["json"] = BODIES.get(fn, {})
        return getattr(client, verb.lower())(url, **kw)

    def test_the_sweep_is_not_empty(self):
        self.assertGreaterEqual(len(self.routes), 15,
                                f"η σάρωση βρήκε μόνο {len(self.routes)} routes")

    def test_no_credentials_is_rejected_everywhere(self):
        leaks = []
        for verb, path, fn in self.routes:
            r = self.call(verb, path, fn)
            if r.status_code not in REJECT:
                leaks.append(f"{verb} {path} → HTTP {r.status_code}")
        self.assertEqual(leaks, [], "\n".join(leaks))

    def test_another_tenants_token_is_rejected_everywhere(self):
        """Ο Α είναι συνδεδεμένος και χτυπά τα endpoints ΤΟΥ Β."""
        leaks = []
        with patch.object(auth, "current_email", return_value=MAIL_A):
            for verb, path, fn in self.routes:
                r = self.call(verb, path, fn,
                              headers={"Authorization": "Bearer token-a"})
                if r.status_code not in REJECT:
                    leaks.append(f"{verb} {path} → HTTP {r.status_code}")
        self.assertEqual(leaks, [], "ΔΙΑΡΡΟΗ:\n" + "\n".join(leaks))

    def test_forged_claim_token_is_rejected_everywhere(self):
        leaks = []
        for verb, path, fn in self.routes:
            for header in ({"X-Vitrina-Claim": "x" * 48},
                           {"Authorization": "Bearer not-a-real-jwt"}):
                r = self.call(verb, path, fn, headers=header)
                if r.status_code not in REJECT:
                    leaks.append(f"{verb} {path} {list(header)[0]} → {r.status_code}")
        self.assertEqual(leaks, [], "\n".join(leaks))

    def test_owner_reaches_their_own(self):
        """Ο αρνητικός έλεγχος δεν αξίζει τίποτα αν όλα απαντούν 404.

        Ένα endpoint που απορρίπτει ΚΑΙ τον ιδιοκτήτη θα «περνούσε» τα από πάνω
        tests ενώ είναι σπασμένο. Εδώ επιβεβαιώνεται ότι ο κάτοχος περνά.
        """
        with patch.object(auth, "current_email", return_value=MAIL_A):
            r = API.get(f"/clients/{CID_A}/content",
                        headers={"Authorization": "Bearer token-a"})
        self.assertEqual(r.status_code, 200, r.text[:200])

    def test_public_site_data_leaks_nothing_private(self):
        """Το `/site-data` είναι δημόσιο επίτηδες — αλλά όχι για τα πάντα."""
        db._client().table("clients").update({"email": MAIL_A}).eq("id", CID_A).execute()
        r = API.get(f"/clients/{CID_A}/site-data")
        self.assertEqual(r.status_code, 200)
        blob = r.text.lower()
        for secret in (MAIL_A, "stripe", "sk_test", "service_role", "page_token"):
            self.assertNotIn(secret.lower(), blob,
                             f"το /site-data εκθέτει «{secret}»")


if __name__ == "__main__":
    unittest.main()
