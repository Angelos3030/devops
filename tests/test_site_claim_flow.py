"""Ownership hand-off contracts for site-first onboarding."""

import hashlib

from fastapi import HTTPException

from src import meta_oauth


def test_claim_uses_authenticated_email_and_hashes_token(monkeypatch):
    raw = "a" * 43
    seen = {}
    monkeypatch.setattr(meta_oauth.auth, "current_email", lambda _header: "Owner@Example.GR")

    def fake_claim(client_id, token_hash, email):
        seen.update(client_id=client_id, token_hash=token_hash, email=email)
        return True

    monkeypatch.setattr(meta_oauth.db, "claim_client_site", fake_claim)
    result = meta_oauth.claim_site(
        "11111111-1111-1111-1111-111111111111",
        meta_oauth.ClaimSite(token=raw),
        "Bearer verified-token",
    )

    assert result["ok"] is True
    assert seen["email"] == "Owner@Example.GR"
    assert seen["token_hash"] == hashlib.sha256(raw.encode()).hexdigest()
    assert raw not in seen.values()


def test_claim_rejects_short_or_consumed_tokens(monkeypatch):
    monkeypatch.setattr(meta_oauth.auth, "current_email", lambda _header: "owner@example.gr")
    try:
        meta_oauth.claim_site("client", meta_oauth.ClaimSite(token="short"), "Bearer token")
        assert False, "short token should fail"
    except HTTPException as exc:
        assert exc.status_code == 400

    monkeypatch.setattr(meta_oauth.db, "claim_client_site", lambda *_args: False)
    try:
        meta_oauth.claim_site("client", meta_oauth.ClaimSite(token="x" * 43), "Bearer token")
        assert False, "unknown/expired token should fail"
    except HTTPException as exc:
        assert exc.status_code == 404


def test_frontend_claim_contract_is_private_and_persistent():
    start = open("web/start.html", encoding="utf-8").read()
    choose = open("sites/app/choose/[client]/page.jsx", encoding="utf-8").read()
    dashboard = open("sites/app/dashboard/page.jsx", encoding="utf-8").read()

    assert "#claim=" in start
    assert "sessionStorage.setItem(`vitrina-claim:${client}`" in choose
    assert "history.replaceState" in choose
    assert "sessionStorage.getItem(claimKey)" in dashboard
    assert "`/clients/${fromUrl}/claim`" in dashboard
    assert "sessionStorage.removeItem(claimKey)" in dashboard
    assert "/clients/lookup" in dashboard
    assert "clients?.length > 1" in dashboard
