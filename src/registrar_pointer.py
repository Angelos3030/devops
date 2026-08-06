"""
Pointer.gr — αγορά και διαχείριση domain μέσω του API τους.

Μέχρι σήμερα αγοράζαμε τα domain των πελατών με το χέρι (~3 λεπτά ο καθένας).
Αυτό το αυτοματοποιεί.

Είναι παλιό XML API, όχι REST. Τρία πράγματα δεν είναι προφανή και κοστίζουν
ώρες αν δεν τα ξέρεις — τα βρήκα στο παράδειγμα PHP τους, ΟΧΙ στην τεκμηρίωση:

  1. **URL**: https://www.pointer.gr/api — δεν αναφέρεται πουθενά στο API.md.
  2. **Sandbox**: δεν είναι άλλο endpoint· είναι το header `testserver: 1`.
  3. **Checksum**: md5(username + password + ACTION + key), όπου ACTION είναι το
     όνομα της μεθόδου τους (`domainCheck`), ΟΧΙ το XML tag (`domain-check`).
     Ο κωδικός μπαίνει ΩΜΟΣ στο checksum αλλά md5-αρισμένος στο <password>.

Χρειάζεται προπληρωμένο υπόλοιπο στον λογαριασμό — κάθε ενέργεια το τραβάει
άμεσα (κωδικός σφάλματος 303 όταν δεν φτάνει).

⚠️ Δεν έχει δοκιμαστεί σε ζωντανό API: το sandbox θέλει στατική IP που δεν
έχουμε ακόμα (βλ. docs/emails-reseller.md). Ο κώδικας ακολουθεί κατά γράμμα
το επίσημο παράδειγμά τους.
"""
from __future__ import annotations

import hashlib
import os
import ssl
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any

API_URL = "https://www.pointer.gr/api"
TIMEOUT = 30

# Τα δικά μας nameservers — τα domain των πελατών δείχνουν στο Cloudflare.
DEFAULT_NS = (
    os.environ.get("POINTER_NS1", ""),
    os.environ.get("POINTER_NS2", ""),
)

# Τι σημαίνουν οι κωδικοί τους, στα ελληνικά. Χωρίς αυτό, ένα «303» δεν λέει
# τίποτα σε όποιον διαβάζει τα logs στις 2 τη νύχτα.
CODES = {
    "200": "Επιτυχία",
    "102": "Λάθος στοιχεία σύνδεσης",
    "103": "Το κλειδί συνεδρίας έληξε — ξανασυνδέσου",
    "104": "Υπέρβαση ορίου συνδέσεων",
    "301": "Λάθος παράμετροι",
    "302": "Δεν βρέθηκε το domain ή το προϊόν",
    "303": "ΔΕΝ ΦΤΑΝΕΙ ΤΟ ΥΠΟΛΟΙΠΟ στον λογαριασμό Pointer",
    "304": "Δεν υποστηρίζεται από αυτό το TLD",
    "305": "Δεν υποστηρίζεται από αυτό το TLD",
    "309": "Η επαφή είναι δεμένη με ενεργά domain και δεν αλλάζει",
    "501": "Σφάλμα στον server της Pointer",
}

_ctx = ssl.create_default_context()


class PointerError(RuntimeError):
    """Σφάλμα από το API τους — με το δικό τους μήνυμα, αυτούσιο."""


class Pointer:
    """Μία συνεδρία. Χρησιμοποίησέ το ως context manager ώστε να γίνεται logout.

        with Pointer(sandbox=True) as p:
            print(p.check(["taverna-o-mitsos"], [".gr"]))
    """

    def __init__(self, username: str | None = None, password: str | None = None,
                 sandbox: bool = True) -> None:
        self.username = username or os.environ.get("POINTER_USERNAME", "")
        self._password = password or os.environ.get("POINTER_PASSWORD", "")
        self.sandbox = sandbox
        self.key = ""
        if not self.username or not self._password:
            raise PointerError("Λείπουν POINTER_USERNAME / POINTER_PASSWORD.")

    # ------------------------------------------------------------------ core
    def _chksum(self, action: str) -> str:
        """ΠΡΟΣΟΧΗ: ωμός κωδικός εδώ, md5 στο <password>. Έτσι το κάνουν."""
        return hashlib.md5(
            f"{self.username}{self._password}{action}{self.key}".encode()).hexdigest()

    def _post(self, xml: str) -> ET.Element:
        req = urllib.request.Request(
            API_URL, data=xml.encode("utf-8"),
            headers={
                "Content-Type": "text/xml",
                # 1 = test registry (sandbox), 0 = πραγματικές αγορές με χρέωση
                "testserver": "1" if self.sandbox else "0",
            })
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=_ctx) as r:
            body = r.read().decode("utf-8", "ignore")
        try:
            root = ET.fromstring(body)
        except ET.ParseError:
            raise PointerError(f"Μη έγκυρη XML απάντηση: {body[:200]}") from None

        code = (root.findtext("code") or "200").strip()
        if code != "200":
            msg = (root.findtext("message") or "").strip()
            raise PointerError(f"[{code}] {CODES.get(code, 'Άγνωστο σφάλμα')}"
                               + (f" — {msg}" if msg else ""))
        return root

    def _envelope(self, action: str, inner: str, with_key: bool = True) -> str:
        key_el = f"<key>{self.key}</key>" if (with_key and self.key) else ""
        return (
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<pointer>"
            f"{inner}"
            f"{key_el}"
            f"<username>{self.username}</username>"
            f"<chksum>{self._chksum(action)}</chksum>"
            "</pointer>"
        )

    # --------------------------------------------------------------- session
    def login(self) -> str:
        pwd_md5 = hashlib.md5(self._password.encode()).hexdigest()
        # Στο login δεν υπάρχει ακόμα key — ούτε στο checksum ούτε στο XML.
        xml = self._envelope("login", f"<login><password>{pwd_md5}</password></login>",
                             with_key=False)
        root = self._post(xml)
        self.key = (root.findtext("login/key") or "").strip()
        if not self.key:
            raise PointerError("Το Pointer δεν επέστρεψε κλειδί συνεδρίας.")
        return self.key

    def logout(self) -> None:
        if not self.key:
            return
        try:
            self._post(self._envelope("logout", "<logout></logout>"))
        except PointerError:
            pass          # το logout δεν αξίζει να ρίξει τη ροή
        finally:
            self.key = ""

    def __enter__(self) -> "Pointer":
        self.login()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.logout()

    # --------------------------------------------------------------- domains
    def check(self, names: list[str], tlds: list[str] | None = None) -> dict[str, bool]:
        """{'taverna-o-mitsos.gr': True} — True σημαίνει ΔΙΑΘΕΣΙΜΟ."""
        tlds = tlds or [".gr"]
        inner = (
            "<domain-check>"
            "<tlds>" + "".join(f"<tld>{t}</tld>" for t in tlds) + "</tlds>"
            "<domains>" + "".join(f"<domain>{n}</domain>" for n in names) + "</domains>"
            "</domain-check>"
        )
        root = self._post(self._envelope("domainCheck", inner))
        out: dict[str, bool] = {}
        for item in root.findall("domain-check/result/item"):
            dom = (item.findtext("domain") or "").strip()
            avail = (item.findtext("available") or "").strip().lower()
            if dom:
                out[dom] = avail in ("1", "true", "yes")
        return out

    def create_contact(self, domain: str, tld: str, *, name: str, street: str,
                       city: str, postal_code: str, phone: str, email: str,
                       region: str = "", country: str = "GR") -> str:
        """Η επαφή ιδιοκτήτη. ΠΡΕΠΕΙ να υπάρχει πριν αγοραστεί το domain.

        `phone` σε μορφή ITU: +30.2101234567
        """
        inner = (
            "<contact-domain><create>"
            f"<domain>{domain}</domain><tld>{tld}</tld>"
            f"<name>{name}</name><street>{street}</street><city>{city}</city>"
            f"<sp>{region or city}</sp><pc>{postal_code}</pc><country>{country}</country>"
            f"<phone>{phone}</phone><email>{email}</email>"
            "</create></contact-domain>"
        )
        root = self._post(self._envelope("contactDomainCreate", inner))
        return (root.findtext("contact-domain/result/code")
                or root.findtext("code") or "").strip()

    def register(self, domain: str, *, registrant: str, years: int = 1,
                 ns1: str = "", ns2: str = "", lock: bool = True) -> dict[str, Any]:
        """Αγοράζει το domain. ΤΡΑΒΑΕΙ ΧΡΗΜΑΤΑ όταν sandbox=False."""
        ns1 = ns1 or DEFAULT_NS[0]
        ns2 = ns2 or DEFAULT_NS[1]
        if not ns1 or not ns2:
            raise PointerError("Λείπουν nameservers (POINTER_NS1 / POINTER_NS2).")
        inner = (
            "<domain><create>"
            f"<domain>{domain}</domain><duration>{years}</duration>"
            f"<ns1>{ns1}</ns1><ns2>{ns2}</ns2>"
            f"<registrant>{registrant}</registrant>"
            f"<lock>{1 if lock else 0}</lock>"
            "</create></domain>"
        )
        root = self._post(self._envelope("domainCreate", inner))
        return {"ok": True, "domain": domain,
                "message": (root.findtext("message") or "").strip()}

    def update_nameservers(self, domain: str, ns1: str, ns2: str) -> None:
        """⚠️ Κλειδωμένο domain ΔΕΝ αλλάζει nameservers — ξεκλείδωσε πρώτα."""
        inner = ("<domain><updatens>"
                 f"<domain>{domain}</domain><ns1>{ns1}</ns1><ns2>{ns2}</ns2>"
                 "</updatens></domain>")
        self._post(self._envelope("domainUpdatens", inner))
