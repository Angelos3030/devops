#!/usr/bin/env python3
"""Real staging proof for the atomic conversational editor. Never targets production."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import uuid
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

STAGING_REF = "epsueuxccykyecgzgbbe"
PRODUCTION_REF = "rmhgkwscchyjzjkxezuf"
API = f"https://{STAGING_REF}.supabase.co"
MGMT = f"https://api.supabase.com/v1/projects/{STAGING_REF}/database/query"


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    if STAGING_REF == PRODUCTION_REF:
        fail("staging ref equals production ref")
    token = os.environ.get("SUPABASE_ACCESS_TOKEN", "").strip()
    if not token:
        fail("SUPABASE_ACCESS_TOKEN is missing")
    mh = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def sql(query: str):
        response = requests.post(MGMT, headers=mh, json={"query": query}, timeout=60)
        if not response.ok:
            raise RuntimeError(f"SQL {response.status_code}: {response.text[:500]}")
        return response.json()

    keys = requests.get(
        f"https://api.supabase.com/v1/projects/{STAGING_REF}/api-keys?reveal=true",
        headers={"Authorization": f"Bearer {token}"}, timeout=30,
    )
    keys.raise_for_status()
    service_key = next(k["api_key"] for k in keys.json() if k.get("name") == "service_role")
    rest_headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
    }

    def rpc(name: str, payload: dict) -> requests.Response:
        return requests.post(f"{API}/rest/v1/rpc/{name}", headers=rest_headers,
                             json=payload, timeout=15)

    client_id = str(uuid.uuid4())
    marker = uuid.uuid4().hex[:10]
    trigger_name = f"editor_qa_fail_{marker}"
    function_name = f"editor_qa_fail_{marker}"
    initial = {"name": "QA Studio", "phone": "2100000000", "hours": "09:00-17:00"}
    published_html = f"<html><body>published-{marker}</body></html>"
    passed: list[str] = []

    def ok(label: str) -> None:
        passed.append(label)
        print(f"  PASS  {label}")

    try:
        sql(f"""
          insert into public.clients(id,name,business_type,city,email,status)
          values ('{client_id}','Editor QA','qa','Athens','editor-{marker}@example.invalid','trial');
          insert into public.site_content(client_id,content,editor_version)
          values ('{client_id}','{json.dumps(initial)}'::jsonb,0);
          insert into public.sites(client_id,preset,html,url)
          values ('{client_id}','qa-theme','{published_html}','published-{marker}');
          notify pgrst, 'reload schema';
        """)
        ok("isolated synthetic staging client seeded")

        permissions = sql("""
          select p.proname, p.prosecdef as security_definer,
            has_function_privilege('anon',p.oid,'execute') as anon_execute,
            has_function_privilege('authenticated',p.oid,'execute') as auth_execute,
            has_function_privilege('service_role',p.oid,'execute') as service_execute
          from pg_proc p join pg_namespace n on n.oid=p.pronamespace
          where n.nspname='public' and p.proname in ('editor_commit','editor_undo')
          order by p.proname
        """)
        if len(permissions) != 2 or any(
            row["security_definer"] or row["anon_execute"] or row["auth_execute"]
            or not row["service_execute"] for row in permissions
        ):
            fail(f"unsafe RPC permissions: {permissions}")
        ok("RPCs are SECURITY INVOKER and service_role-only")

        before = dict(initial)
        after = {**initial, "phone": "2101111111"}
        payload = {
            "p_client_id": client_id, "p_expected_version": 0,
            "p_idempotency_key": f"commit-{marker}", "p_message": "change phone",
            "p_operations": [{"op": "update_phone", "params": {"phone": "2101111111"}}],
            "p_before_state": before, "p_after_state": after,
        }
        response = rpc("editor_commit", payload)
        if not response.ok:
            fail(f"commit failed: {response.status_code} {response.text[:300]}")
        result = response.json()
        state = sql(f"select content,editor_version from public.site_content where client_id='{client_id}'")[0]
        revisions = sql(f"select count(*)::int n from public.site_revisions where client_id='{client_id}'")[0]["n"]
        if state["content"] != after or state["editor_version"] != 1 or revisions != 1:
            fail("commit did not atomically persist content and revision")
        ok("commit persists draft + revision atomically")

        duplicate = rpc("editor_commit", payload)
        duplicate.raise_for_status()
        revisions2 = sql(f"select count(*)::int n from public.site_revisions where client_id='{client_id}'")[0]["n"]
        if not duplicate.json().get("duplicate") or revisions2 != 1:
            fail("idempotency created a duplicate revision")
        ok("duplicate idempotency key creates no mutation/revision")

        sql(f"""
          create function public.{function_name}() returns trigger language plpgsql as $$
          begin
            if new.client_id = '{client_id}'::uuid then raise exception 'intentional_editor_qa_failure'; end if;
            return new;
          end $$;
          create trigger {trigger_name} before update on public.site_content
          for each row execute function public.{function_name}();
        """)
        rollback_payload = {**payload, "p_expected_version": 1,
                            "p_idempotency_key": f"rollback-{marker}",
                            "p_after_state": {**after, "phone": "2102222222"}}
        failed_response = rpc("editor_commit", rollback_payload)
        if failed_response.ok:
            fail("intentional mid-transaction failure unexpectedly succeeded")
        rollback_state = sql(f"select content,editor_version from public.site_content where client_id='{client_id}'")[0]
        rollback_revision = sql(
            f"select count(*)::int n from public.site_revisions where client_id='{client_id}' "
            f"and idempotency_key='rollback-{marker}'"
        )[0]["n"]
        if rollback_state["content"] != after or rollback_state["editor_version"] != 1 or rollback_revision:
            fail("transaction left a partial revision or content update")
        ok("mid-transaction failure rolls back revision and draft")
        sql(f"drop trigger if exists {trigger_name} on public.site_content; "
            f"drop function if exists public.{function_name}();")

        def tab_call(suffix: str):
            candidate = {**after, "hours": f"{suffix}:00-18:00"}
            return rpc("editor_commit", {
                **payload, "p_expected_version": 1,
                "p_idempotency_key": f"race-{marker}-{suffix}",
                "p_before_state": after,
                "p_after_state": candidate,
            })

        # Both tabs loaded version 1. Tab A commits first; Tab B then submits
        # the stale version it still has in memory.
        tab_a = tab_call("08")
        tab_b = tab_call("10")
        if not tab_a.ok or tab_b.ok or "stale_editor_version" not in tab_b.text:
            fail(f"two-tab result was not success then stale conflict: {tab_a.status_code}/{tab_b.status_code}")
        race_state = sql(f"select content,editor_version from public.site_content where client_id='{client_id}'")[0]
        if race_state["editor_version"] != 2:
            fail("concurrent stale write caused a lost update")
        ok("two-tab stale version yields one commit and one deterministic conflict")

        undo = rpc("editor_undo", {
            "p_client_id": client_id, "p_expected_version": 2,
            "p_idempotency_key": f"undo-{marker}",
        })
        undo.raise_for_status()
        restored = sql(f"select content,editor_version from public.site_content where client_id='{client_id}'")[0]
        if restored["content"] != after or restored["editor_version"] != 3:
            fail("undo did not restore the exact previous snapshot")
        ok("undo restores exact prior state and survives refresh query")

        published = sql(
            f"select html,url,preset from public.sites where client_id='{client_id}' "
            f"and url='published-{marker}'"
        )[0]
        if published["html"] != published_html or published["preset"] != "qa-theme":
            fail("draft editing mutated the published site")
        ok("draft edits and undo leave published site untouched")

        print(f"\nEDITOR STAGING: PASS ({len(passed)}/{len(passed)})")
        return 0
    finally:
        try:
            sql(f"drop trigger if exists {trigger_name} on public.site_content; "
                f"drop function if exists public.{function_name}(); "
                f"delete from public.clients where id='{client_id}';")
        except Exception as exc:
            print(f"CLEANUP WARNING: {exc}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
