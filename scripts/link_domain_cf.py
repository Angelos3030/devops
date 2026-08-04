#!/usr/bin/env python3
"""
Συνδέει domain πελάτη ΜΕΣΩ Cloudflare Worker — χωρίς custom domain στο Railway.

    python scripts/link_domain_cf.py taverna-o-mitsos.gr
    python scripts/link_domain_cf.py taverna-o-mitsos.gr --dry-run

Γιατί όχι το link_domain.py: εκείνο δηλώνει το domain στο Railway, που δέχεται
μόνο 2 ανά service (Hobby) — ο 2ος πελάτης κολλάει. Εδώ η κίνηση περνάει από τον
Worker, οπότε δεν υπάρχει όριο.

ΣΕΙΡΑ (μη την αλλάξεις): route ΠΡΩΤΑ → αναμονή → DNS μετά. Αν γίνουν μαζί, το
DNS στέλνει κίνηση σε proxy που δεν σερβίρει ακόμα και το site βγάζει 522.
Αν η επαλήθευση αποτύχει, το DNS επαναφέρεται αυτόματα.

Προϋποθέσεις: zone στο Cloudflare, Worker ανεβασμένος (deploy_worker.py),
CF_API_TOKEN με Zone→DNS→Edit και Zone→Workers Routes→Edit.
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
PLACEHOLDER = "192.0.2.1"      # τεκμηριωμένη «κενή» IP· την κίνηση την πιάνει ο Worker
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
    dry = "--dry-run" in sys.argv
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
        print("   Πρόσθεσέ το (Add site) και άλλαξε nameservers στον registrar.")
        return 1
    zid = z["result"][0]["id"]
    print(f"zone {domain}  ({z['result'][0].get('status')})")

    hosts = [domain, f"www.{domain}"]
    recs = cf("GET", f"/zones/{zid}/dns_records?per_page=100").get("result", [])
    before = {h: next((r for r in recs if r["name"] == h and r["type"] in ("A", "AAAA", "CNAME")), None)
              for h in hosts}

    if dry:
        print("\n--dry-run· θα γινόταν:")
        for h in hosts:
            cur = before[h]
            print(f"  route  {h}/*  -> {WORKER}")
            print(f"  DNS    {h}: {cur['type'] + ' ' + cur['content'] if cur else '(νέο)'}"
                  f" -> A {PLACEHOLDER} proxied")
        return 0

    # --- 1) ROUTES ΠΡΩΤΑ (ακίνδυνο: το DNS δεν περνάει ακόμα από proxy) ---
    print("\n1) Worker routes")
    for h in hosts:
        r = cf("POST", f"/zones/{zid}/workers/routes", {"pattern": f"{h}/*", "script": WORKER})
        ok = r.get("success") or any(e.get("code") == 10020 for e in r.get("errors", []))
        print(f"   {h}/*  {'OK' if ok else r.get('errors')}")
        if not ok:
            print("   ❌ Δεν μπήκε το route — σταματάω ΠΡΙΝ αγγίξω το DNS (το site μένει ζωντανό).")
            return 1

    print("   ...αναμονή 25s να ενεργοποιηθούν")
    time.sleep(25)

    # --- 2) DNS μετά ---
    print("\n2) DNS -> proxied")
    for h in hosts:
        cur = before[h]
        body = {"type": "A", "name": "@" if h == domain else h,
                "content": PLACEHOLDER, "ttl": 1, "proxied": True}
        r = (cf("PATCH", f"/zones/{zid}/dns_records/{cur['id']}", body) if cur
             else cf("POST", f"/zones/{zid}/dns_records", body))
        print(f"   {h}  {'OK' if r.get('success') else r.get('errors')}")

    # --- 3) Επαλήθευση, με rollback αν αποτύχει ---
    print("\n3) Επαλήθευση")
    ok = False
    for attempt in range(6):
        time.sleep(10)
        codes = {h: http(f"https://{h}") for h in hosts}
        print(f"   t+{25 + (attempt + 1) * 10}s  " + "  ".join(f"{h}={c}" for h, c in codes.items()))
        if all(c == 200 for c in codes.values()):
            ok = True
            break

    if not ok:
        print("\n⚠ Δεν απάντησε σωστά — ΕΠΑΝΑΦΟΡΑ DNS στην προηγούμενη κατάσταση")
        for h in hosts:
            cur = before[h]
            if not cur:
                continue
            cf("PATCH", f"/zones/{zid}/dns_records/{cur['id']}",
               {"type": cur["type"], "name": cur["name"], "content": cur["content"],
                "ttl": cur.get("ttl", 1), "proxied": cur.get("proxied", False)})
            print(f"   {h} -> {cur['type']} {cur['content']} (proxied={cur.get('proxied')})")
        print("\n   Το site επανήλθε. Έλεγξε ότι ο Worker είναι ανεβασμένος:")
        print("   python scripts/deploy_worker.py")
        return 1

    print("\n✅ Έτοιμο — το domain σερβίρεται μέσω Worker (χωρίς Railway custom domain).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
