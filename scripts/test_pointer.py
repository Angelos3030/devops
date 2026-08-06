#!/usr/bin/env python3
"""
Δοκιμάζει τον adapter της Pointer ΧΩΡΙΣ το API τους.

    python scripts/test_pointer.py

Σηκώνει έναν ψεύτικο server που μιμείται τις απαντήσεις τους, και ελέγχει ότι
στέλνουμε ακριβώς το XML που περιμένουν και ότι διαβάζουμε σωστά ό,τι γυρίζουν.

Γιατί υπάρχει: το sandbox τους θέλει στατική IP που δεν έχουμε ακόμα. Χωρίς
αυτό το αρχείο, την ημέρα που θα πάρουμε πρόσβαση θα ανακαλύπταμε ένα-ένα τα
λάθη μορφής με δοκιμή και σφάλμα — και κάθε αποτυχημένη κλήση σε ΑΛΗΘΙΝΟ
registry είναι είτε χαμένος χρόνος είτε χαμένα λεφτά.
"""
from __future__ import annotations

import hashlib
import http.server
import os
import sys
import threading
import xml.etree.ElementTree as ET

sys.path.insert(0, ".")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

USER, PWD = "vitrina", "s3cret"
KEY = "SESSIONKEY123"

# Ό,τι στέλνει ο adapter, το κρατάμε εδώ για να το ελέγξουμε.
seen: list[tuple[str, dict[str, str]]] = []

REPLIES = {
    "login": f"<pointer><login><key>{KEY}</key></login><code>200</code></pointer>",
    "domain-check": """<pointer><domain-check><result>
        <item><domain>taverna-o-mitsos.gr</domain><available>1</available></item>
        <item><domain>taverna-o-mitsos.com</domain><available>0</available></item>
        </result></domain-check><code>200</code></pointer>""",
    "contact-domain": "<pointer><contact-domain><result><code>CT-9911</code></result>"
                      "</contact-domain><code>200</code></pointer>",
    "domain": "<pointer><code>200</code><message>Domain created</message></pointer>",
    "logout": "<pointer><code>200</code></pointer>",
    "_broke": "<pointer><code>303</code><message>Not enough credit</message></pointer>",
}

_fail_next = {"on": False}


class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        body = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode()
        root = ET.fromstring(body)
        kind = next((c.tag for c in root if c.tag not in ("username", "chksum", "key")), "?")
        seen.append((kind, {
            "chksum": root.findtext("chksum") or "",
            "username": root.findtext("username") or "",
            "key": root.findtext("key") or "",
            "testserver": self.headers.get("testserver", ""),
            "content_type": self.headers.get("Content-Type", ""),
            "body": body,
        }))
        xml = REPLIES["_broke"] if _fail_next["on"] else REPLIES.get(kind, REPLIES["logout"])
        data = xml.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/xml")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a: object) -> None:
        pass


PASS, FAIL = [], []


def check(name: str, ok: bool, detail: str = "") -> None:
    (PASS if ok else FAIL).append(name)
    print(f"  {'✓' if ok else '✗'} {name}{('  — ' + detail) if detail else ''}")


def main() -> int:
    srv = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_address[1]

    os.environ.update(POINTER_USERNAME=USER, POINTER_PASSWORD=PWD,
                      POINTER_NS1="ada.ns.cloudflare.com", POINTER_NS2="bob.ns.cloudflare.com")
    from src import registrar_pointer as rp
    rp.API_URL = f"http://127.0.0.1:{port}/api"

    print("=" * 62)
    print("POINTER — έλεγχος adapter χωρίς το API τους")
    print("=" * 62)

    # ---------------------------------------------------------------- login
    print("\n[ΣΥΝΔΕΣΗ]")
    p = rp.Pointer(sandbox=True)
    p.login()
    kind, req = seen[-1]
    check("στέλνει <login>", kind == "login")
    check("ο κωδικός πάει md5-αρισμένος, ΠΟΤΕ ωμός",
          hashlib.md5(PWD.encode()).hexdigest() in req["body"] and f">{PWD}<" not in req["body"])
    check("checksum = md5(user+pass+'login')",
          req["chksum"] == hashlib.md5(f"{USER}{PWD}login".encode()).hexdigest())
    check("δεν στέλνει <key> στο login", req["key"] == "")
    check("header testserver: 1 στο sandbox", req["testserver"] == "1")
    check("Content-Type: text/xml", "xml" in req["content_type"])
    check("κράτησε το κλειδί συνεδρίας", p.key == KEY, p.key)

    # ------------------------------------------------------------ αναζήτηση
    print("\n[ΔΙΑΘΕΣΙΜΟΤΗΤΑ]")
    res = p.check(["taverna-o-mitsos"], [".gr", ".com"])
    kind, req = seen[-1]
    check("στέλνει <domain-check>", kind == "domain-check")
    check("checksum με το όνομα ΜΕΘΟΔΟΥ 'domainCheck' (όχι το tag)",
          req["chksum"] == hashlib.md5(f"{USER}{PWD}domainCheck{KEY}".encode()).hexdigest())
    check("περιλαμβάνει και τα δύο tld", "<tld>.gr</tld>" in req["body"] and "<tld>.com</tld>" in req["body"])
    check("διάβασε σωστά διαθέσιμο/πιασμένο",
          res == {"taverna-o-mitsos.gr": True, "taverna-o-mitsos.com": False}, str(res))

    # --------------------------------------------------------------- επαφή
    print("\n[ΕΠΑΦΗ ΙΔΙΟΚΤΗΤΗ]")
    code = p.create_contact("taverna-o-mitsos.gr", ".gr", name="Δημήτρης Μήτσος",
                            street="Λ. Μαραθώνος 12", city="Καλαμαριά",
                            postal_code="55132", phone="+30.2310000000",
                            email="info@taverna-o-mitsos.gr")
    kind, req = seen[-1]
    check("στέλνει <contact-domain>", kind == "contact-domain")
    check("τα ελληνικά περνάνε σωστά (UTF-8)", "Δημήτρης" in req["body"])
    check("επέστρεψε κωδικό επαφής", code == "CT-9911", code)

    # -------------------------------------------------------------- αγορά
    print("\n[ΑΓΟΡΑ]")
    out = p.register("taverna-o-mitsos.gr", registrant="CT-9911", years=1)
    kind, req = seen[-1]
    check("στέλνει <domain><create>", kind == "domain" and "<create>" in req["body"])
    check("βάζει τα nameservers μας", "ada.ns.cloudflare.com" in req["body"])
    check("κλειδώνει το domain (lock=1)", "<lock>1</lock>" in req["body"])
    check("επιτυχία", out.get("ok") is True)

    # ------------------------------------------------------------- σφάλμα
    print("\n[ΣΦΑΛΜΑΤΑ] Το μήνυμα πρέπει να λέει ΤΙ φταίει")
    _fail_next["on"] = True
    try:
        p.register("allo.gr", registrant="CT-9911")
        check("το 303 πετάει σφάλμα", False, "δεν πέταξε")
    except rp.PointerError as e:
        msg = str(e)
        check("το 303 πετάει σφάλμα", True)
        check("λέει ελληνικά ότι δεν φτάνει το υπόλοιπο", "ΥΠΟΛΟΙΠΟ" in msg, msg[:70])
    _fail_next["on"] = False

    # ---------------------------------------------------- ασφάλεια & έξοδος
    print("\n[ΑΣΦΑΛΕΙΑ]")
    check("ο ωμός κωδικός δεν εμφανίζεται ΠΟΥΘΕΝΑ στα αιτήματα",
          not any(f">{PWD}<" in r["body"] for _, r in seen))

    p.logout()
    check("το logout καθάρισε το κλειδί", p.key == "")

    # -------------------------------------------------- παραγωγή = ΟΧΙ test
    print("\n[ΠΑΡΑΓΩΓΗ] sandbox=False πρέπει να αλλάζει το header")
    seen.clear()
    p2 = rp.Pointer(sandbox=False)
    p2.login()
    check("header testserver: 0 (πραγματικές αγορές)", seen[-1][1]["testserver"] == "0")

    srv.shutdown()
    print("\n" + "=" * 62)
    print(f"ΠΕΡΑΣΑΝ: {len(PASS)}   ΕΣΠΑΣΑΝ: {len(FAIL)}")
    if FAIL:
        print("\n❌ " + "\n   ".join(FAIL))
        return 1
    print("\n✅ Ο adapter στέλνει ό,τι περιμένει η Pointer. Μένει μόνο το sandbox.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
