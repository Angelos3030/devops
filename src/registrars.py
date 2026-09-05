"""
Registrar adapters for domain registration.

For .gr domains, keep purchase with a Greek registrar (Papaki/Pointer/etc.) and
use Cloudflare only for DNS/Pages. Papaki's public GoldResellers API link has
been referenced by third parties, but the GitHub URL currently returns 404, so
the Papaki adapter is intentionally configuration-driven and fails closed until
we have official reseller credentials and endpoint docs.
"""

from __future__ import annotations

import os
from typing import Any, Protocol

import requests

from . import config as cfg


class Registrar(Protocol):
    def check_availability(self, domains: list[str]) -> list[dict[str, Any]]:
        ...

    def register_domain(self, domain: str, years: int = 1) -> dict[str, Any]:
        ...


class ManualRegistrar:
    """Safe fallback: collect paid orders, then fulfill from registrar dashboard."""

    def check_availability(self, domains: list[str]) -> list[dict[str, Any]]:
        return [
            {
                "domain": domain,
                "available": None,
                "price": cfg.DOMAIN_PRICE_EUR,
                "note": "Manual registrar check required.",
            }
            for domain in domains
        ]

    def register_domain(self, domain: str, years: int = 1) -> dict[str, Any]:
        raise RuntimeError(
            f"Domain {domain} is paid but DOMAIN_REGISTRAR=manual. "
            "Register it manually or configure a registrar adapter."
        )


class DnsRegistrar:
    """ΔΕΝ αποφαίνεται για διαθεσιμότητα. Επίτηδες.

    ΤΙ ΕΚΑΝΕ ΠΡΙΝ ΚΑΙ ΓΙΑΤΙ ΚΑΤΑΡΓΗΘΗΚΕ. Ρωτούσε το DNS για SOA και θεωρούσε
    το NXDOMAIN «μάλλον ελεύθερο». Το DNS δεν ξέρει τι είναι κατοχυρωμένο —
    ξέρει τι είναι ΡΥΘΜΙΣΜΕΝΟ. Ένα παρκαρισμένο domain δεν έχει DNS, οπότε
    φαινόταν ελεύθερο· ο πελάτης πλήρωνε €24 για κάτι που δεν μπορούσε να
    πάρει. Και κάθε αποτυχία εκτός δικτύου κατέληγε σε αισιόδοξη απάντηση.

    Η διαθεσιμότητα ζητιέται πλέον από `src/domain_availability.py`, που
    ρωτά RDAP (το πρωτόκολλο του ίδιου του μητρώου) ή registrar API. Εδώ
    επιστρέφεται `None` = άγνωστο, ποτέ εικασία.
    """

    def check_availability(self, domains: list[str]) -> list[dict[str, Any]]:
        return [
            {
                "domain": domain,
                "available": None,
                "price": cfg.DOMAIN_PRICE_EUR,
                "note": "Ο DNS έλεγχος δεν είναι αυθεντική πηγή διαθεσιμότητας.",
            }
            for domain in domains
        ]

    def register_domain(self, domain: str, years: int = 1) -> dict[str, Any]:
        raise RuntimeError(
            f"Domain {domain}: η αγορά χρειάζεται Papaki reseller (DOMAIN_REGISTRAR=papaki) "
            "ή χειροκίνητη καταχώρηση.")


class PointerRegistrar:
    """Pointer.gr — ο ΜΟΝΟΣ έλεγχος που ρωτάει το ίδιο το registry.

    Ο DnsRegistrar μαντεύει από το DNS: ένα domain αγορασμένο αλλά παρκαρισμένο
    δεν έχει DNS, οπότε φαίνεται «ελεύθερο». Ο πελάτης το διαλέγει, πληρώνει,
    και στο ταμείο ανακαλύπτουμε ότι είναι πιασμένο. Εδώ δεν γίνεται αυτό.

    Θέλει POINTER_USERNAME/PASSWORD και πρόσβαση από δηλωμένη στατική IP
    (βλ. docs/16-STATIC-IP.md). Το `sandbox` ελέγχεται με POINTER_SANDBOX=0
    για πραγματικές αγορές — προεπιλογή είναι το test registry, ώστε να μη
    χρεωθεί ποτέ κάτι κατά λάθος.
    """

    def __init__(self) -> None:
        from . import registrar_pointer as rp
        self._rp = rp
        self.sandbox = os.environ.get("POINTER_SANDBOX", "1") != "0"

    def check_availability(self, domains: list[str]) -> list[dict[str, Any]]:
        from . import registrar_pointer as rp
        # Ομαδοποίηση ανά κατάληξη: το API τους παίρνει ονόματα και tld χωριστά.
        by_tld: dict[str, list[str]] = {}
        for d in domains:
            name, _, tld = d.partition(".")
            by_tld.setdefault("." + tld, []).append(name)

        found: dict[str, bool] = {}
        try:
            with rp.Pointer(sandbox=self.sandbox) as p:
                for tld, names in by_tld.items():
                    found.update(p.check(names, [tld]))
        except rp.PointerError as e:
            # Ποτέ δεν ρίχνουμε το signup επειδή έπεσε ο registrar — γυρνάμε στο
            # DNS, που είναι εκτίμηση αλλά καλύτερο από άδεια οθόνη.
            print(f"[pointer] έλεγχος απέτυχε ({e}) → πέφτω σε DNS")
            return DnsRegistrar().check_availability(domains)

        return [{"domain": d, "available": found.get(d), "price": cfg.DOMAIN_PRICE_EUR}
                for d in domains]

    def register_domain(self, domain: str, years: int | None = None) -> dict[str, Any]:
        from . import registrar_pointer as rp
        contact = os.environ.get("POINTER_CONTACT_CODE", "")
        if not contact:
            raise RuntimeError(
                "Λείπει POINTER_CONTACT_CODE (η επαφή ιδιοκτήτη). "
                "Φτιάξ' την μία φορά με registrar_pointer.create_contact().")
        with rp.Pointer(sandbox=self.sandbox) as p:
            # years=None → ο adapter βάζει το ελάχιστο της κατάληξης (2 για .gr)
            return p.register(domain, registrant=contact, years=years)


class PapakiRegistrar:
    """
    Papaki reseller adapter.

    Required envs:
      PAPAKI_API_BASE     Official reseller API base URL from Papaki.
      PAPAKI_API_KEY      Secret/token from Papaki reseller dashboard.
      PAPAKI_CONTACT_ID   Default registrant contact profile/id.

    Endpoint names are configurable only after official Papaki docs are supplied.
    This class uses conservative conventional paths behind `_request`; if Papaki
    provides different paths/payloads, update only this adapter.
    """

    def __init__(self) -> None:
        if not cfg.PAPAKI_API_BASE or not cfg.PAPAKI_API_KEY:
            raise RuntimeError("Λείπει PAPAKI_API_BASE ή PAPAKI_API_KEY.")
        self.base = cfg.PAPAKI_API_BASE.rstrip("/")

    def check_availability(self, domains: list[str]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for domain in domains:
            data = self._request("GET", "/domains/check", params={"domain": domain})
            available = bool(
                data.get("available")
                or data.get("is_available")
                or data.get("status") in {"available", "free"}
            )
            price = data.get("price") or data.get("registration_price") or cfg.DOMAIN_PRICE_EUR
            results.append({"domain": domain, "available": available, "price": price})
        return results

    def register_domain(self, domain: str, years: int = 1) -> dict[str, Any]:
        if not cfg.PAPAKI_CONTACT_ID:
            raise RuntimeError("Λείπει PAPAKI_CONTACT_ID για registrant contact.")
        return self._request(
            "POST",
            "/domains/register",
            json={
                "domain": domain,
                "years": years,
                "contact_id": cfg.PAPAKI_CONTACT_ID,
                "nameservers": [],
            },
        )

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {cfg.PAPAKI_API_KEY}",
        }
        if cfg.PAPAKI_RESELLER_ID:
            headers["X-Reseller-ID"] = cfg.PAPAKI_RESELLER_ID
        response = requests.request(
            method,
            f"{self.base}{path}",
            headers=headers,
            timeout=25,
            **kwargs,
        )
        try:
            data = response.json()
        except ValueError:
            data = {"raw": response.text}
        if not response.ok:
            raise RuntimeError(f"Papaki API error {response.status_code}: {data}")
        if data.get("success") is False or data.get("error"):
            raise RuntimeError(f"Papaki API error: {data}")
        return data


def get_registrar() -> Registrar:
    if cfg.DOMAIN_REGISTRAR == "pointer":
        return PointerRegistrar()
    if cfg.DOMAIN_REGISTRAR == "papaki":
        return PapakiRegistrar()
    if cfg.DOMAIN_REGISTRAR == "manual":
        return ManualRegistrar()
    # default: δωρεάν DNS availability check (λειτουργικό signup χωρίς creds)
    return DnsRegistrar()
