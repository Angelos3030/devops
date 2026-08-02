#!/usr/bin/env python3
"""
Συνδέει domain πελάτη ΜΕΣΩ Cloudflare Worker — χωρίς custom domain στο Railway.

    python scripts/link_domain_cf.py taverna-o-mitsos.gr

Γιατί όχι το link_domain.py: εκείνο δηλώνει το domain στο Railway, που δέχεται
μόνο 2 ανά service (Hobby) — ο 2ος πελάτης κολλάει. Εδώ η κίνηση περνάει από τον
Worker, οπότε δεν υπάρχει όριο.

Προϋποθέσεις:
  • Το zone του πελάτη υπάρχει στο Cloudflare (nameservers → Cloudflare)
  • Ο Worker ανεβασμένος: python scripts/deploy_worker.py
  • CF_API_TOKEN με: Zone → DNS → Edit, Zone → Workers Routes → Edit
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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://api.cloudflare.com/client/v4"
WORKER = "vitrina-tenant-router"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
_ctx = ssl.create_default_context(); _ctx.check_hostname = False; _ctx.verify_mode = ssl.CERT_NONE

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def env(key: str) -> str:
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


TOKEN = env("CF_API_TOKEN")


def cf(method: str, path: str, body=None) -> dict:
    req = urllib.request.Request(
        API + path,
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        method=method,
    )
    try:
        return json.loads(urllib.request.urlopen(req, timeout=30).read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def http(url: str) -> int | str:
    try:
        return urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}), timeout=20, context=_ctx).status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:  # noqa: BLE001
        return str(e)[:24]


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    domain = re.sub(r"^www\.", "", args[0].lower().strip())
    if not TOKEN:
        print("❌ Λείπει CF_API_TOKEN")
        return 2

    z = cf("GET", f"/zones?name={domain}")
    if not z.get("result"):
        print(f"❌ Το zone {domain} δεν υπάρχει στο Cloudflare.")
        print("   Πρόσθεσέ το πρώτα (Add site) και άλλαξε nameservers στον registrar.")
        return 1
    zid = z["result"][0]["id"]
    status = z["result"][0].get("status")
    print(f"zone {domain}  ({status})")

    # 1) DNS: apex + www proxied (ΠΡΕΠΕΙ να είναι orange για να τρέξει ο Worker)
    recs = cf("GET", f"/zones/{zid}/dns_records?per_page=100").get("result", [])
    for name in (domain, f"www.{domain}"):
        cur = next((r for r in recs if r["name"] == name and r["type"] in ("A", "CNAME")), None)
        body = {"type": "A", "name": name, "content": "192.0.2.1", "ttl": 1, "proxied": True}
        # 192.0.2.1 = τεκμηριωμένη «κενή» IP· η κίνηση δεν φτάνει ποτέ εκεί, την
        # πιάνει ο Worker στο edge. Έτσι δεν χρειάζεται δικός μας origin server.
        if cur:
            r = cf("PATCH", f"/zones/{zid}/dns_records/{cur['id']}", body)
        else:
            r = cf("POST", f"/zones/{zid}/dns_records", body)
        print(f"  DNS {name:34} proxied  {'OK' if r.get('success') else r.get('errors')}")

    # 2) Worker routes
    for pattern in (f"{domain}/*", f"www.{domain}/*"):
        r = cf("POST", f"/zones/{zid}/workers/routes", {"pattern": pattern, "script": WORKER})
        ok = r.get("success") or any(e.get("code") == 10020 for e in r.get("errors", []))  # ήδη υπάρχει
        print(f"  route {pattern:32} {'OK' if ok else r.get('errors')}")

    # 3) Επαλήθευση
    print("\n  ...αναμονή 20s για διάδοση")
    time.sleep(20)
    for host in (domain, f"www.{domain}"):
        print(f"  https://{host} -> {http(f'https://{host}')}")

    print("\n✅ Έτοιμο. Το SSL το εκδίδει αυτόματα το Cloudflare (Universal SSL).")
    print("   Αν δεις 5xx στην αρχή, δώσε λίγα λεπτά για το πιστοποιητικό.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
