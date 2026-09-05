"""Διαθεσιμότητα domain από ΑΥΘΕΝΤΙΚΗ πηγή — ποτέ από εικασία.

ΤΟ ΠΡΟΒΛΗΜΑ ΠΟΥ ΛΥΝΕΙ. Ο προηγούμενος έλεγχος ρωτούσε το DNS: αν το SOA
γυρνούσε NXDOMAIN, το domain θεωρούνταν ελεύθερο. Αυτό είναι λάθος με δύο
τρόπους, και οι δύο κοστίζουν χρήματα σε πελάτη:

  · Παρκαρισμένο domain δεν έχει DNS. Φαίνεται ελεύθερο, είναι πιασμένο.
    Ο πελάτης πληρώνει €24 για κάτι που δεν μπορεί να πάρει.
  · Πτώση δικτύου έδινε «άγνωστο», αλλά κάθε άλλη αποτυχία κατέληγε σε
    αισιόδοξη απάντηση. Η αποτυχία παρόχου ΔΕΝ σημαίνει ποτέ «ελεύθερο».

ΤΡΙΑ ΑΠΟΤΕΛΕΣΜΑΤΑ, ΠΟΤΕ ΔΥΟ: `available`, `unavailable`, `unknown`.
Το `unknown` είναι πλήρης, αποδεκτή απάντηση — όχι σφάλμα προς απόκρυψη.

ΠΟΙΑ ΠΗΓΗ ΓΙΑ ΠΟΙΑ ΚΑΤΑΛΗΞΗ (μετρημένο, όχι υποτιθέμενο):

  gTLD (.com/.net/.org/.shop…)  → RDAP, το πρωτόκολλο του ΙΔΙΟΥ του μητρώου
                                   (RFC 9082). Δωρεάν, χωρίς λογαριασμό.
                                   Μετρήθηκε: google.com → 200, τυχαίο → 404,
                                   ~60ms.

  .gr                            → ΔΕΝ ΥΠΑΡΧΕΙ ούτε RDAP ούτε WHOIS.
                                   Επαληθεύτηκε στο IANA: το bootstrap
                                   (data.iana.org/rdap/dns.json) δεν περιέχει
                                   `gr`, και η εγγραφή TLD του IANA έχει ΚΕΝΟ
                                   πεδίο `whois:`. Οι υποψήφιοι hosts
                                   (whois.nic.gr, whois.ics.forth.gr) δεν
                                   λύνονται· ο whois.grnet.gr δεν απαντά στο 43.
                                   Άρα η μόνη αυθεντική πηγή είναι registrar
                                   API με λογαριασμό.

Χωρίς ρυθμισμένο registrar, το `.gr` επιστρέφει `unknown` — ΠΟΤΕ `available`.
"""
from __future__ import annotations

import json
import re
import socket
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

AVAILABLE = "available"
UNAVAILABLE = "unavailable"
UNKNOWN = "unknown"

_TIMEOUT = 8          # δευτ. ανά κλήση παρόχου
_UA = "vitrina-domain-availability/1.0"


class InvalidDomain(ValueError):
    """Το κείμενο δεν είναι έγκυρο όνομα domain."""


@dataclass(frozen=True)
class Availability:
    domain: str            # κανονικοποιημένο, punycode
    display: str           # όπως το γράφει ο άνθρωπος (unicode)
    status: str            # available | unavailable | unknown
    source: str            # ποια πηγή απάντησε
    checked_at: str        # ISO 8601 UTC
    reason: str = ""       # γιατί, όταν είναι unknown

    def as_dict(self) -> dict:
        return asdict(self)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Κανονικοποίηση ─────────────────────────────────────────────────────────
#
# Ο πελάτης γράφει «www.Καφέ-Μήτσος.gr », «https://mitsos.gr/menu», «MITSOS.GR».
# Όλα είναι το ίδιο domain. Η κανονικοποίηση πρέπει να είναι ΝΤΕΤΕΡΜΙΝΙΣΤΙΚΗ,
# γιατί από αυτήν εξαρτάται το unique index «ένα ανοιχτό αίτημα ανά domain».

_LABEL = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")
_STRIP_SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*://", re.I)


def normalize_domain(raw: str) -> tuple[str, str]:
    """Επιστρέφει (punycode, εμφανίσιμο). Σηκώνει InvalidDomain.

    Υποστηρίζει ελληνικά (IDN): το μητρώο του .gr δέχεται ελληνικούς
    χαρακτήρες, οπότε το «καφέ.gr» είναι υπαρκτό domain — γίνεται
    «xn--mxaeeo.gr» για τον πάροχο, αλλά ο πελάτης βλέπει το δικό του.
    """
    if not isinstance(raw, str):
        raise InvalidDomain("Δώσε ένα όνομα domain.")
    s = raw.strip()
    if not s:
        raise InvalidDomain("Δώσε ένα όνομα domain.")
    # NFC πριν από οτιδήποτε: το «καφέ» μπορεί να έρθει αποσυντεθειμένο και
    # δύο οπτικά ίδια κείμενα θα έδιναν ΔΙΑΦΟΡΕΤΙΚΟ punycode.
    s = unicodedata.normalize("NFC", s)
    s = _STRIP_SCHEME.sub("", s)
    s = s.split("/")[0].split("?")[0].split("#")[0]
    s = s.split("@")[-1]                    # ό,τι μοιάζει με email
    s = s.split(":")[0]                     # θύρα
    s = s.strip().strip(".").lower()
    if s.startswith("www."):
        s = s[4:]
    if not s:
        raise InvalidDomain("Δώσε ένα όνομα domain.")
    if len(s) > 253:
        raise InvalidDomain("Το domain είναι πολύ μεγάλο.")

    labels = s.split(".")
    if len(labels) < 2:
        raise InvalidDomain("Χρειάζεται και κατάληξη, π.χ. .gr")

    puny: list[str] = []
    for label in labels:
        if not label:
            raise InvalidDomain("Το domain έχει κενό τμήμα (διπλή τελεία).")
        try:
            # `idna` του Python επιβάλλει και τους κανόνες μήκους/χαρακτήρων.
            encoded = label.encode("idna").decode("ascii") if not label.isascii() \
                else label
        except UnicodeError as e:
            raise InvalidDomain(f"Μη έγκυροι χαρακτήρες: {label}") from e
        if not _LABEL.match(encoded):
            raise InvalidDomain(f"Μη έγκυρο τμήμα: {label}")
        puny.append(encoded)

    tld = puny[-1]
    if not (tld.isalpha() or tld.startswith("xn--")) or len(tld) < 2:
        raise InvalidDomain("Μη έγκυρη κατάληξη.")
    return ".".join(puny), s


# ── Πηγή 1: RDAP (το πρωτόκολλο του μητρώου) ───────────────────────────────

_BOOT_URL = "https://data.iana.org/rdap/dns.json"
_BOOT_TTL = 24 * 3600
_boot_lock = threading.Lock()
_boot: dict[str, str] = {}
_boot_at: float = 0.0


def _bootstrap() -> dict[str, str]:
    """TLD → RDAP base URL, από το IANA. Κενό dict αν δεν φορτώθηκε."""
    global _boot, _boot_at
    with _boot_lock:
        if _boot and (time.time() - _boot_at) < _BOOT_TTL:
            return _boot
        try:
            req = urllib.request.Request(_BOOT_URL, headers={"User-Agent": _UA})
            data = json.loads(urllib.request.urlopen(req, timeout=_TIMEOUT).read())
            table: dict[str, str] = {}
            for entry in data.get("services", []):
                tlds, urls = entry[0], entry[1]
                if not urls:
                    continue
                for t in tlds:
                    table[t.lower()] = urls[0].rstrip("/")
            if table:
                _boot, _boot_at = table, time.time()
        except Exception as e:  # noqa: BLE001 — αποτυχία bootstrap ≠ ελεύθερο
            print(f"[availability] RDAP bootstrap απέτυχε: {e}")
        return _boot


def _rdap(domain: str, display: str) -> Availability:
    tld = domain.rsplit(".", 1)[1]
    base = _bootstrap().get(tld)
    if not base:
        return Availability(domain, display, UNKNOWN, "rdap", _now(),
                            f"Η κατάληξη .{tld} δεν έχει RDAP.")
    url = f"{base}/domain/{domain}"
    req = urllib.request.Request(
        url, headers={"Accept": "application/rdap+json", "User-Agent": _UA})
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
            # 200 = το μητρώο έχει εγγραφή γι' αυτό το domain.
            src = f"rdap:{urllib.parse.urlsplit(base).hostname}"
            return Availability(domain, display, UNAVAILABLE, src, _now())
    except urllib.error.HTTPError as e:
        host = urllib.parse.urlsplit(base).hostname
        if e.code == 404:
            # 404 = δεν υπάρχει εγγραφή στο μητρώο = ελεύθερο.
            return Availability(domain, display, AVAILABLE, f"rdap:{host}", _now())
        # 429/403/5xx: ο πάροχος δεν απάντησε. ΔΕΝ σημαίνει ελεύθερο.
        return Availability(domain, display, UNKNOWN, f"rdap:{host}", _now(),
                            f"HTTP {e.code} από το μητρώο.")
    except (urllib.error.URLError, socket.timeout, TimeoutError) as e:
        return Availability(domain, display, UNKNOWN, "rdap", _now(),
                            f"Δεν απάντησε το μητρώο: {type(e).__name__}")
    except Exception as e:  # noqa: BLE001
        return Availability(domain, display, UNKNOWN, "rdap", _now(),
                            f"Απρόσμενο σφάλμα: {type(e).__name__}")


# ── Πηγή 2: registrar (για καταλήξεις χωρίς RDAP, δηλαδή .gr) ─────────────

def _registrar(domain: str, display: str) -> Availability:
    from . import config as cfg
    from . import registrars

    name = (cfg.DOMAIN_REGISTRAR or "").lower()
    # Ο «dns» ΔΕΝ είναι αυθεντική πηγή — είναι η εικασία που καταργήθηκε.
    if name not in ("pointer", "papaki", "openprovider"):
        return Availability(
            domain, display, UNKNOWN, "registrar:none", _now(),
            "Δεν έχει ρυθμιστεί registrar με αυθεντικό έλεγχο διαθεσιμότητας.")
    try:
        rows = registrars.get_registrar().check_availability([domain])
    except Exception as e:  # noqa: BLE001
        return Availability(domain, display, UNKNOWN, f"registrar:{name}", _now(),
                            f"Ο registrar δεν απάντησε: {type(e).__name__}")
    row = rows[0] if rows else {}
    val = row.get("available")
    if val is True:
        status = AVAILABLE
    elif val is False:
        status = UNAVAILABLE
    else:
        status = UNKNOWN
    return Availability(domain, display, status, f"registrar:{name}", _now(),
                        "" if status != UNKNOWN else "Ο registrar δεν αποφάνθηκε.")


# ── Δημόσια είσοδος ────────────────────────────────────────────────────────

def check(raw: str) -> Availability:
    """Ένα domain, μία αυθεντική απάντηση. Σηκώνει InvalidDomain σε άκυρο."""
    domain, display = normalize_domain(raw)
    tld = domain.rsplit(".", 1)[1]
    table = _bootstrap()
    if tld in table:
        return _rdap(domain, display)
    if not table:
        # Χωρίς τον πίνακα του IANA δεν ξέρουμε ΚΑΝ αν η κατάληξη έχει RDAP.
        # Το να πέσουμε σιωπηλά στον registrar θα έδινε παραπλανητική αιτία.
        return Availability(domain, display, UNKNOWN, "rdap", _now(),
                            "Δεν φορτώθηκε ο πίνακας RDAP του IANA.")
    return _registrar(domain, display)


def check_many(raws: list[str]) -> list[Availability | dict]:
    """Πολλά ονόματα. Τα άκυρα επιστρέφονται ως σφάλμα, δεν ρίχνουν τη λίστα."""
    out: list[Availability | dict] = []
    for raw in raws:
        try:
            out.append(check(raw))
        except InvalidDomain as e:
            out.append({"domain": str(raw)[:120], "status": "invalid",
                        "reason": str(e), "checked_at": _now()})
    return out
