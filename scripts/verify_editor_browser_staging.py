#!/usr/bin/env python3
"""Launch local API/UI against isolated staging and run the real browser journey."""
from __future__ import annotations

import base64
import json
import os
import socket
import subprocess
import sys
import time
import uuid
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
REF = "epsueuxccykyecgzgbbe"
PRODUCTION_REF = "rmhgkwscchyjzjkxezuf"
SUPABASE_URL = f"https://{REF}.supabase.co"
MGMT = f"https://api.supabase.com/v1/projects/{REF}/database/query"
API_URL = "http://127.0.0.1:8098"
APP_URL = "http://127.0.0.1:3701"


def assert_port_available(port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            probe.bind(("127.0.0.1", port))
        except OSError as exc:
            raise RuntimeError(f"QA port {port} is already in use") from exc


def terminate_tree(proc: subprocess.Popen | None) -> None:
    if not proc or proc.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
        )
        return
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


def wait_url(url: str, timeout: int = 90) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if requests.get(url, timeout=2).status_code < 500:
                return
        except requests.RequestException:
            pass
        time.sleep(1)
    raise RuntimeError(f"server did not start: {url}")


def main() -> int:
    if REF == PRODUCTION_REF:
        raise RuntimeError("production project is blocked")
    token = os.environ.get("SUPABASE_ACCESS_TOKEN", "").strip()
    if not token:
        raise RuntimeError("SUPABASE_ACCESS_TOKEN is missing")
    assert_port_available(8098)
    assert_port_available(3701)
    mh = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def sql(query: str):
        response = requests.post(MGMT, headers=mh, json={"query": query}, timeout=60)
        response.raise_for_status()
        return response.json()

    key_response = requests.get(
        f"https://api.supabase.com/v1/projects/{REF}/api-keys?reveal=true",
        headers={"Authorization": f"Bearer {token}"}, timeout=30,
    )
    key_response.raise_for_status()
    keys = key_response.json()
    anon = next(k["api_key"] for k in keys if k.get("name") == "anon")
    service = next(k["api_key"] for k in keys if k.get("name") == "service_role")
    kimi_key = os.environ.get("KIMI_API_KEY", "").strip()
    if not kimi_key:
        raise RuntimeError("KIMI_API_KEY is missing for the controlled staging run")

    marker = uuid.uuid4().hex[:10]
    client_id = str(uuid.uuid4())
    email = f"editor-browser-{marker}@example.invalid"
    password = f"Qa-{uuid.uuid4().hex}!"
    user_id = None
    api_proc = ui_proc = None
    try:
        admin = {"apikey": service, "Authorization": f"Bearer {service}",
                 "Content-Type": "application/json"}
        created = requests.post(f"{SUPABASE_URL}/auth/v1/admin/users", headers=admin,
                                json={"email": email, "password": password,
                                      "email_confirm": True}, timeout=30)
        created.raise_for_status()
        user_id = created.json()["id"]

        sql(f"""
          insert into public.clients(id,name,business_type,city,email,phone,status)
          values ('{client_id}','Browser QA Studio','salon','Athens','{email}','2100000000','trial');
          insert into public.site_content(client_id,content,editor_version)
          values ('{client_id}', '{{"name":"Browser QA Studio","trade":"salon","city":"Athens","phone":"2100000000","hours":"09:00-17:00","services":[{{"name":"Κούρεμα","description":"Υπηρεσία QA"}}],"template":"elegance-salon","palette":"original","font_pair":"editorial"}}'::jsonb, 0);
          insert into public.sites(client_id,preset,url) values ('{client_id}','elegance-salon','selected');
        """)

        login = requests.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={"apikey": anon, "Content-Type": "application/json"},
            json={"email": email, "password": password}, timeout=30,
        )
        login.raise_for_status()
        session = login.json()

        child_env = {**os.environ,
                     "VITRINA_ENV": "staging",
                     "SUPABASE_URL_STAGING": SUPABASE_URL,
                     "SUPABASE_KEY_STAGING": service,
                     "NEXT_PUBLIC_SUPABASE_URL": SUPABASE_URL,
                     "NEXT_PUBLIC_SUPABASE_ANON_KEY": anon,
                     "NEXT_PUBLIC_API_BASE": API_URL,
                     "NEXT_DIST_DIR": ".next-editor-staging",
                     "AI_API_KEY": kimi_key,
                     "AI_BASE_URL": "https://api.moonshot.ai/v1",
                     "AI_MODEL": "kimi-k2.6",
                     "AI_PROVIDER": "openai",
                     "PYTHONIOENCODING": "utf-8"}
        api_proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1",
             "--port", "8098", "--log-level", "warning"], cwd=ROOT, env=child_env)
        ui_proc = subprocess.Popen(
            ["cmd", "/c", "npx next dev -p 3701"], cwd=ROOT / "sites", env=child_env)
        wait_url(f"{API_URL}/healthz")
        wait_url(f"{APP_URL}/dashboard", timeout=120)

        qa_env = {**child_env,
                  "QA_APP_URL": APP_URL, "QA_API_URL": API_URL,
                  "QA_CLIENT_ID": client_id,
                  "QA_SESSION_B64": base64.b64encode(
                      json.dumps(session).encode("utf-8")).decode("ascii")}
        completed = subprocess.run(
            ["node", "tests/editorStagingBrowser.mjs"], cwd=ROOT / "sites",
            env=qa_env, check=False)
        return completed.returncode
    finally:
        for proc in (ui_proc, api_proc):
            terminate_tree(proc)
        try:
            sql(f"delete from public.clients where id='{client_id}';")
        except Exception as exc:
            print(f"client cleanup warning: {exc}", file=sys.stderr)
        if user_id:
            try:
                requests.delete(f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}",
                                headers=admin, timeout=30).raise_for_status()
            except Exception as exc:
                print(f"auth cleanup warning: {exc}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
