"""
Domain search, availability check, and purchase via Cloudflare Registrar API.
Χρησιμοποιεί τα ίδια CF_API_TOKEN + CF_ACCOUNT_ID που έχουμε ήδη.

Cloudflare Registrar:
  - At-cost pricing (χωρίς markup, χωρίς certificate αγορά — SSL δωρεάν)
  - Domain + DNS + SSL όλα σε ένα
  - Docs: https://developers.cloudflare.com/registrar/
  - API:  https://developers.cloudflare.com/api/resources/registrar/

Endpoints που χρησιμοποιούμε:
  GET  /accounts/{id}/registrar/domains/search?query=foo.gr   → availability
  POST /accounts/{id}/registrar/domains                        → αγορά
  GET  /accounts/{id}/registrar/domains                        → λίστα domains
  POST /zones                                                   → zone (αν δεν δημιουργηθεί αυτόματα)
  POST /zones/{id}/dns_records                                  → DNS records
"""

import re
import unicodedata
import requests
from . import config as cfg

# ---------------------------------------------------------------------------
# Greek → ASCII transliteration για domain slug
# ---------------------------------------------------------------------------
_GR = str.maketrans({
    'α': 'a',  'β': 'b',  'γ': 'g',  'δ': 'd',  'ε': 'e',  'ζ': 'z',
    'η': 'i',  'θ': 'th', 'ι': 'i',  'κ': 'k',  'λ': 'l',  'μ': 'm',
    'ν': 'n',  'ξ': 'x',  'ο': 'o',  'π': 'p',  'ρ': 'r',  'σ': 's',
    'ς': 's',  'τ': 't',  'υ': 'y',  'φ': 'f',  'χ': 'ch', 'ψ': 'ps',
    'ω': 'o',  'ά': 'a',  'έ': 'e',  'ή': 'i',  'ί': 'i',  'ό': 'o',
    'ύ': 'y',  'ώ': 'o',  'ϊ': 'i',  'ϋ': 'y',  'ΐ': 'i',  'ΰ': 'y',
})

_TYPE_SLUG = {
    'ταβέρνα': 'taverna', 'εστιατόριο': 'restaurant', 'καφέ': 'cafe',
    'καφετέρια': 'cafe', 'κρεοπωλείο': 'kreas', 'αρτοποιείο': 'fournos',
    'φούρνος': 'fournos', 'ζαχαροπλαστείο': 'pastry', 'πιτσαρία': 'pizza',
    'υδραυλικός': 'hydravlikos', 'ηλεκτρολόγος': 'ilektrologos',
    'κομμωτήριο': 'hair', 'κουρείο': 'barber',
    'γυμναστήριο': 'gym', 'φυσικοθεραπευτής': 'physio',
    'δικηγόρος': 'law', 'λογιστής': 'logistis', 'γιατρός': 'doctor',
    'οδοντίατρος': 'dentist', 'κτηνίατρος': 'vet',
    'ανθοπωλείο': 'flowers', 'φαρμακείο': 'pharma',
}


def _slug(text: str) -> str:
    t = text.lower().translate(_GR)
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode()
    t = re.sub(r'[^a-z0-9]+', '-', t).strip('-')
    return t


def suggest_domains(name: str, business_type: str = '', city: str = '') -> list[str]:
    """Δημιουργεί έξυπνες προτάσεις domain slug."""
    n = _slug(name)
    c = _slug(city) if city else ''
    t = _TYPE_SLUG.get(business_type.lower(), _slug(business_type)) if business_type else ''

    candidates = []
    if n:                   candidates.append(n)
    if n and c:             candidates.append(f"{n}-{c}")
    if n and t:             candidates.append(f"{t}-{n}")
    if n and t and c:       candidates.append(f"{n}-{t}-{c}")
    if c and t:             candidates.append(f"{t}-{c}")
    if n and c:             candidates.append(f"{c}-{n}")

    seen: set[str] = set()
    result = []
    for d in candidates:
        if d and d not in seen and len(d) >= 3:
            seen.add(d)
            result.append(d)
    return result[:8]


# ---------------------------------------------------------------------------
# Cloudflare API helpers
# ---------------------------------------------------------------------------

_CF_BASE = "https://api.cloudflare.com/client/v4"


def _cf(method: str, path: str, **kwargs) -> dict:
    if not cfg.CF_API_TOKEN:
        raise RuntimeError("Λείπει το CF_API_TOKEN στο .env")
    headers = {
        "Authorization": f"Bearer {cfg.CF_API_TOKEN}",
        "Content-Type": "application/json",
    }
    r = requests.request(method, f"{_CF_BASE}{path}", headers=headers,
                         timeout=20, **kwargs)
    data = r.json()
    if not r.ok or not data.get("success"):
        raise RuntimeError(f"Cloudflare API σφάλμα: {data.get('errors', r.text)}")
    return data


# ---------------------------------------------------------------------------
# Domain availability check (Cloudflare Registrar)
# ---------------------------------------------------------------------------

def check_availability(slugs: list[str], tld: str = ".gr") -> list[dict]:
    """
    Ελέγχει διαθεσιμότητα via Cloudflare Registrar search.
    Επιστρέφει: [{"domain": "foo.gr", "available": True, "price": 9.0}, ...]
    """
    results = []
    for slug in slugs:
        domain = f"{slug}{tld}"
        try:
            data = _cf("GET", f"/accounts/{cfg.CF_ACCOUNT_ID}/registrar/domains/search",
                       params={"query": domain, "per_page": 1})
            items = data.get("result", [])
            if items:
                item = items[0]
                results.append({
                    "domain": domain,
                    "available": item.get("available", False),
                    "price": item.get("price"),
                })
            else:
                results.append({"domain": domain, "available": False, "price": None})
        except RuntimeError:
            results.append({"domain": domain, "available": False, "price": None})
    return results


# ---------------------------------------------------------------------------
# Domain purchase (Cloudflare Registrar)
# ---------------------------------------------------------------------------

def purchase_domain(domain: str, years: int = 1) -> dict:
    """
    Αγοράζει domain μέσω Cloudflare Registrar.
    SSL: δωρεάν Universal SSL — δεν χρειάζεται τίποτα άλλο.
    Το domain προστίθεται αυτόματα ως Cloudflare zone.

    Body: {name, years, type: "full"}
    """
    data = _cf("POST", f"/accounts/{cfg.CF_ACCOUNT_ID}/registrar/domains",
               json={"name": domain, "years": years, "type": "full"})
    return data.get("result", {})


# ---------------------------------------------------------------------------
# Zone management (DNS records)
# ---------------------------------------------------------------------------

def get_zone_id(domain: str) -> str | None:
    """Βρίσκει zone_id αν υπάρχει ήδη στο Cloudflare account."""
    data = _cf("GET", "/zones", params={"name": domain})
    zones = data.get("result", [])
    return zones[0]["id"] if zones else None


def create_zone(domain: str) -> str:
    """Δημιουργεί zone αν δεν υπάρχει (το Registrar συνήθως το κάνει αυτόματα)."""
    existing = get_zone_id(domain)
    if existing:
        return existing
    data = _cf("POST", "/zones",
               json={"name": domain,
                     "account": {"id": cfg.CF_ACCOUNT_ID},
                     "jump_start": True})
    return data["result"]["id"]


def add_dns_records(zone_id: str,
                    pages_subdomain: str,
                    railway_url: str) -> None:
    """
    Προσθέτει:
      CNAME www → <pages>.pages.dev   (proxied — site)
      CNAME api → <railway>.up.railway.app  (proxied — backend)
    """
    records = [
        {"type": "CNAME", "name": "www", "content": pages_subdomain,
         "proxied": True, "ttl": 1},
        {"type": "CNAME", "name": "api", "content": railway_url,
         "proxied": True, "ttl": 1},
    ]
    for rec in records:
        try:
            _cf("POST", f"/zones/{zone_id}/dns_records", json=rec)
            print(f"  ✅ DNS {rec['name']} → {rec['content']}")
        except RuntimeError as e:
            # Αγνόησε "already exists" errors
            if "already exists" not in str(e).lower():
                print(f"  ⚠️ DNS {rec['name']}: {e}")


# ---------------------------------------------------------------------------
# High-level: ολόκληρη η ροή
# ---------------------------------------------------------------------------

def buy_and_setup(domain: str, client_id: str,
                  pages_subdomain: str = "vitrina-7uq.pages.dev",
                  railway_url: str = "greek-smb-agent-production.up.railway.app") -> dict:
    """
    1) Αγοράζει domain μέσω Cloudflare Registrar (SSL αυτόματο + δωρεάν)
    2) Βρίσκει/δημιουργεί Cloudflare zone
    3) Προσθέτει DNS: www → Pages, api → Railway
    4) Αποθηκεύει στη DB
    Επιστρέφει {"domain", "zone_id", "ssl": "universal_auto"}
    """
    from .db import save_domain

    # 1) Αγορά
    purchase_domain(domain)
    print(f"✅ Αγοράστηκε: {domain} (SSL δωρεάν αυτόματα)")

    # 2) Zone (δημιουργείται αυτόματα από το Registrar, απλώς το βρίσκουμε)
    zone_id = create_zone(domain)
    print(f"✅ Zone: {zone_id}")

    # 3) DNS
    add_dns_records(zone_id, pages_subdomain, railway_url)

    # 4) DB
    save_domain(client_id, domain, zone_id)

    return {
        "domain": domain,
        "zone_id": zone_id,
        "ssl": "universal_auto",
        "site_url": f"https://www.{domain}",
        "api_url": f"https://api.{domain}",
    }
