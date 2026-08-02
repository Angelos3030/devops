#!/usr/bin/env python3
"""
Ανεβάζει τον tenant-router Worker στο Cloudflare.

    python scripts/deploy_worker.py

Ο Worker είναι ο τρόπος να έχουμε απεριόριστα domain πελατών: το Railway
δρομολογεί με Host header και γυρνάει 404 σε ό,τι δεν είναι δηλωμένο (2 ανά
service στο Hobby). Ο Worker προωθεί στο Railway με Host που αναγνωρίζει, και
περνάει το πραγματικό domain σε `x-tenant-host`.

Χρειάζεται CF_API_TOKEN με: Account → Workers Scripts → Edit.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKER_FILE = os.path.join(ROOT, "infra", "tenant-router.worker.js")
WORKER_NAME = "vitrina-tenant-router"
API = "https://api.cloudflare.com/client/v4"

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
ACCOUNT = env("CF_ACCOUNT_ID")


def upload(script: str) -> dict:
    """PUT του script ως ES module (χωρίς εξαρτήσεις — multipart με το χέρι)."""
    boundary = "----vitrina" + os.urandom(8).hex()
    metadata = json.dumps({"main_module": "worker.js",
                           "compatibility_date": "2026-01-01"})
    parts = [
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="metadata"\r\n'
        f"Content-Type: application/json\r\n\r\n{metadata}\r\n",
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="worker.js"; filename="worker.js"\r\n'
        f"Content-Type: application/javascript+module\r\n\r\n{script}\r\n",
        f"--{boundary}--\r\n",
    ]
    body = "".join(parts).encode("utf-8")
    req = urllib.request.Request(
        f"{API}/accounts/{ACCOUNT}/workers/scripts/{WORKER_NAME}",
        data=body,
        headers={"Authorization": f"Bearer {TOKEN}",
                 "Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="PUT",
    )
    try:
        return json.loads(urllib.request.urlopen(req, timeout=45).read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def main() -> int:
    if not TOKEN or not ACCOUNT:
        print("❌ Λείπει CF_API_TOKEN ή CF_ACCOUNT_ID στο .env")
        return 2
    script = open(WORKER_FILE, encoding="utf-8").read()
    origin = re.search(r"const ORIGIN = '([^']+)'", script)
    print(f"Worker : {WORKER_NAME}")
    print(f"Origin : {origin.group(1) if origin else '?'}")

    res = upload(script)
    if not res.get("success"):
        print(f"❌ Απέτυχε: {res.get('errors')}")
        print("   Χρειάζεται permission: Account → Workers Scripts → Edit")
        return 1

    print("✅ Ο Worker ανέβηκε.")
    print("\nΓια κάθε νέο πελάτη τρέχεις:  python scripts/link_domain.py <domain>")
    print("(συνδέει DNS + route στον Worker — χωρίς custom domain στο Railway)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
