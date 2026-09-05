"""Prove the editing migration against disposable PostgreSQL only."""
from __future__ import annotations

import json
import secrets
import socket
import subprocess
import time
import uuid
from pathlib import Path

import psycopg2

ROOT = Path(__file__).resolve().parents[1]


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def main() -> None:
    name = f"vitrina-editor-{secrets.token_hex(4)}"
    password, port = secrets.token_urlsafe(18), free_port()
    started = subprocess.run(["docker", "run", "-d", "--rm", "--name", name,
                              "-e", f"POSTGRES_PASSWORD={password}", "-p", f"{port}:5432",
                              "postgres:16-alpine"], capture_output=True, text=True)
    if started.returncode:
        raise SystemExit("EDITING SQL E2E: BLOCKED - Docker daemon unavailable: " +
                         (started.stderr or started.stdout).strip())
    dsn = f"postgresql://postgres:{password}@127.0.0.1:{port}/postgres"
    try:
        for _ in range(60):
            try:
                conn = psycopg2.connect(dsn, connect_timeout=2)
                break
            except psycopg2.OperationalError:
                time.sleep(.25)
        else:
            raise RuntimeError("Postgres did not start")
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute((ROOT / "db/migrations/0000_production_baseline.sql").read_text(encoding="utf-8"))
            cur.execute((ROOT / "db/migrations/0003_ai_editor_revisions.sql").read_text(encoding="utf-8"))
            cid = str(uuid.uuid4())
            state_a = {"name": "Test", "phone": "2100000000", "hours": "09:00-17:00"}
            state_b = {**state_a, "phone": "2101234567"}
            cur.execute("INSERT INTO clients(id,name,business_type,city) VALUES(%s,'Test','doctor','Athens')", (cid,))
            cur.execute("INSERT INTO site_content(client_id,content) VALUES(%s,%s)", (cid, json.dumps(state_a)))
            cur.execute("INSERT INTO sites(client_id,url,preset,html) VALUES(%s,'https://published.test','marble','PUBLISHED')", (cid,))
            args = (cid, 0, "edit-1", "phone", json.dumps([{"op":"update_phone","params":{"phone":"2101234567"}}]), json.dumps(state_a), json.dumps(state_b))
            cur.execute("SELECT editor_commit(%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb)", args)
            first = cur.fetchone()[0]
            assert first["version"] == 1 and first["content"]["phone"] == "2101234567"
            cur.execute("SELECT editor_commit(%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb)", args)
            assert cur.fetchone()[0]["duplicate"] is True
            cur.execute("SELECT count(*) FROM site_revisions WHERE client_id=%s", (cid,))
            assert cur.fetchone()[0] == 1
            try:
                cur.execute("SELECT editor_commit(%s,0,'stale','x','[]','{}','{}')", (cid,))
                raise AssertionError("stale write accepted")
            except psycopg2.errors.SerializationFailure:
                pass
            cur.execute("SELECT editor_undo(%s,1,'undo-1')", (cid,))
            undone = cur.fetchone()[0]
            assert undone["content"]["phone"] == "2100000000" and undone["version"] == 2
            cur.execute("SELECT content,editor_version FROM site_content WHERE client_id=%s", (cid,))
            persisted, version = cur.fetchone()
            assert persisted == state_a and version == 2
            cur.execute("SELECT html FROM sites WHERE client_id=%s AND url LIKE 'http%%'", (cid,))
            assert cur.fetchone()[0] == "PUBLISHED"
            cur.execute("SELECT count(*) FROM site_revisions WHERE client_id=%s", (cid,))
            assert cur.fetchone()[0] == 2
        conn.close()
        print("EDITING SQL E2E: PASS (commit, persistence, idempotency, stale conflict, undo, published isolation)")
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True)


if __name__ == "__main__":
    main()
