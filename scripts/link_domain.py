#!/usr/bin/env python3
"""
Κάνει live ένα client domain στο Railway + Cloudflare με ΜΙΑ εντολή.

    python scripts/link_domain.py koutrakiskouzines.gr
    python scripts/link_domain.py koutrakiskouzines.gr --www-only
    python scripts/link_domain.py koutrakiskouzines.gr --apex-only

Codifies the hard-won recipe (βλ. memory `railway-custom-domain-recipe.md`). Χωρίς αυτό,
το να συνδέσεις domain στο Railway χρειάζεται 5 μη-προφανή βήματα που όλα, αν λείψουν,
δίνουν 404 "Application not found" ή "train has not arrived":

  1. Railway GraphQL θέλει browser User-Agent (αλλιώς Cloudflare 403 code 1010).
  2. customDomainCreate ΑΛΛΑΖΕΙ το CNAME edge target σε κάθε κλήση → διάβασε το requiredValue.
  3. Τα custom domains ΑΠΑΙΤΟΥΝ ρητό targetPort (8080 για Next/uvicorn στο Railway).
  4. ΑΠΑΙΤΕΙΤΑΙ TXT verification στο ΑΚΡΙΒΕΣ verificationDnsHost (π.χ. `_railway-verify.www`).
  5. Μετά DNS+TXT+port σωστά → customDomainIssueCertificate → verified=true → live.

Απαιτεί στο .env: RAILWAY_TOKEN, CF_API_TOKEN. Railway ids: env vars ή τα defaults κάτω.
"""
from __future__ import annotations

import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request

# --- config (env-overridable· defaults = το τρέχον project/service) ---
def _env(k: str, default: str = "") -> str:
    v = os.environ.get(k)
    if v:
        return v
    try:
        for line in open(os.path.join(os.path.dirname(__file__), "..", ".env"), encoding="utf-8"):
            m = re.match(rf"^{k}=(.+)$", line.strip())
            if m:
                return m.group(1).strip().strip('"').strip("'")
    except OSError:
        pass
    return default

RAILWAY_TOKEN = _env("RAILWAY_TOKEN")
CF_TOKEN = _env("CF_API_TOKEN")
PROJECT_ID = _env("RAILWAY_PROJECT_ID", "2c75c49e-f00f-4455-b86d-5780360f209e")
ENVIRONMENT_ID = _env("RAILWAY_ENVIRONMENT_ID", "cd172187-5420-41b3-8b92-c523c0262789")
SITES_SERVICE_ID = _env("RAILWAY_SITES_SERVICE_ID", "80f0b283-2f6d-4fd6-be04-065af6d83590")
TARGET_PORT = int(_env("RAILWAY_SITES_PORT", "8080"))  # Next.js `next start` στο Railway ακούει 8080

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
RAILWAY_GQL = "https://backboard.railway.com/graphql/v2"
CF_API = "https://api.cloudflare.com/client/v4"
_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE

try:  # Greek output στα Windows terminals
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def gql(query: str) -> dict:
    req = urllib.request.Request(
        RAILWAY_GQL, data=json.dumps({"query": query}).encode(),
        headers={"Authorization": "Bearer " + RAILWAY_TOKEN,
                 "Content-Type": "application/json", "User-Agent": UA}, method="POST")
    try:
        return json.loads(urllib.request.urlopen(req, timeout=30).read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def cf(method: str, path: str, body: dict | None = None) -> dict:
    req = urllib.request.Request(
        CF_API + path, data=json.dumps(body).encode() if body else None,
        headers={"Authorization": "Bearer " + CF_TOKEN, "Content-Type": "application/json"},
        method=method)
    try:
        return json.loads(urllib.request.urlopen(req, timeout=25).read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def http_code(url: str) -> object:
    try:
        return urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}), timeout=15, context=_ctx).status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:  # noqa: BLE001
        return str(e)[:20]


def cf_zone_id(zone: str) -> str | None:
    r = cf("GET", f"/zones?name={zone}")
    return r["result"][0]["id"] if r.get("result") else None


def cf_upsert(zid: str, rtype: str, name: str, content: str, proxied: bool = False) -> bool:
    q = cf("GET", f"/zones/{zid}/dns_records?type={rtype}&name={name}")
    body = {"type": rtype, "name": name, "content": content, "ttl": 1}
    if rtype in ("A", "AAAA", "CNAME"):
        body["proxied"] = proxied
    if q.get("result"):
        res = cf("PATCH", f"/zones/{zid}/dns_records/{q['result'][0]['id']}", body)
    else:
        res = cf("POST", f"/zones/{zid}/dns_records", body)
    if not res.get("success"):
        print(f"    ! Cloudflare {rtype} {name}: {res.get('errors')}")
    return bool(res.get("success"))


def link_host(host: str, zone: str, zid: str) -> bool:
    """Ένα host (apex ή www): register στο Railway, στήσε DNS+TXT, verify, live."""
    print(f"\n== {host} ==")
    q = ('mutation { customDomainCreate(input: { domain: "%s", projectId: "%s", '
         'environmentId: "%s", serviceId: "%s", targetPort: %d }) { id '
         'status { verificationDnsHost verificationToken dnsRecords { requiredValue } } } }'
         % (host, PROJECT_ID, ENVIRONMENT_ID, SITES_SERVICE_ID, TARGET_PORT))
    d = gql(q)
    cd = d.get("data", {}).get("customDomainCreate") if d.get("data") else None
    if not cd:
        errs = d.get("errors", [{}])
        msg = errs[0].get("message", str(errs))
        if "limit for custom domains" in msg:
            print(f"    ! Hobby όριο (2 domains/service). Σβήσε ένα αχρησιμοποίητο ή upgrade. ({msg})")
        else:
            print(f"    ! customDomainCreate: {msg}")
        return False
    cid = cd["id"]
    st = cd["status"]
    target = st["dnsRecords"][0]["requiredValue"]
    vhost = st["verificationDnsHost"]         # π.χ. "_railway-verify.www" ή "_railway-verify"
    vtok = st["verificationToken"]
    print(f"    Railway: id={cid[:8]}… target={target} verify@={vhost}")

    name = "@" if host == zone else host.split("." + zone)[0]
    cf_upsert(zid, "CNAME", name, target, proxied=False)               # DNS-only (apex flattened)
    cf_upsert(zid, "TXT", vhost, vtok)                                 # ownership proof (ΚΡΙΣΙΜΟ)

    print("    ...propagation 35s")
    time.sleep(35)
    gql('mutation { customDomainIssueCertificate(id: "%s") }' % cid)   # trigger verify+cert

    for i in range(12):
        time.sleep(20)
        code = http_code(f"https://{host}")
        if code == 200:
            print(f"    ✓ LIVE — https://{host}")
            return True
        print(f"    t+{35 + i * 20}s http={code}")
    print(f"    ! Δεν έγινε live σε ~4′. Τσέκαρε Railway dashboard για το {host}.")
    return False


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if not args:
        print(__doc__)
        return 2
    domain = re.sub(r"^www\.", "", args[0].lower().strip())
    if not RAILWAY_TOKEN or not CF_TOKEN:
        print("! Λείπει RAILWAY_TOKEN ή CF_API_TOKEN στο .env")
        return 2
    zid = cf_zone_id(domain)
    if not zid:
        print(f"! Το zone {domain} δεν υπάρχει στο Cloudflare. Πρόσθεσέ το πρώτα (add site + NS).")
        return 2

    hosts = []
    if "--apex-only" in flags:
        hosts = [domain]
    elif "--www-only" in flags:
        hosts = ["www." + domain]
    else:
        hosts = ["www." + domain, domain]   # www primary + apex

    print(f"Linking {domain} (zone {zid[:8]}…) → hosts: {hosts}")
    ok = all(link_host(h, domain, zid) for h in hosts)
    print("\n" + ("✅ ΟΛΑ LIVE" if ok else "⚠️ Κάτι δεν ολοκληρώθηκε — δες πιο πάνω"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
