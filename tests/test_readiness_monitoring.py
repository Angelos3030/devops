"""Το monitoring πρέπει να ΒΛΕΠΕΙ την αποτυχία, όχι απλώς να υπάρχει.

Κάθε έλεγχος εδώ προκαλεί την αποτυχία και απαιτεί να φανεί — στο status code
ή στα logs. Ένα readiness endpoint που επιστρέφει πάντα 200 είναι χειρότερο από
κανένα: δίνει ψεύτικη σιγουριά.

Ιστορικό που το επιβάλλει: το `/healthz` επέστρεφε `ok: true` επί εβδομάδες ενώ
ο chat editor γύριζε 502 σε κάθε μήνυμα πελάτη, γιατί κοίταζε μόνο το
`src/ai.py` και ποτέ τον πάροχο του editor.
"""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("VITRINA_ENV", "staging")

from fastapi.testclient import TestClient  # noqa: E402

from src import config as cfg, db  # noqa: E402
from src.main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)


# --------------------------------------------------------------- liveness
def test_healthz_stays_dependency_free():
    """Το /healthz είναι η πύλη deploy του Railway — δεν αγγίζει τη βάση.

    Αν αποκτήσει εξάρτηση, μια αργή βάση αρχίζει να ρίχνει deploys για λόγο
    άσχετο με τον κώδικα που ανεβαίνει.
    """
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["ok"] is True


# -------------------------------------------------------------- readiness
def test_readyz_reports_every_subsystem():
    r = client.get("/readyz")
    assert r.status_code in (200, 503)
    checks = r.json()["checks"]
    for key in ("db", "stripe", "ai", "registrar"):
        assert key in checks, f"λείπει ο έλεγχος {key}"
    assert "editor" in checks["ai"] and "site_copy" in checks["ai"]


def test_readyz_turns_503_when_database_is_down(monkeypatch):
    """Ελεγχόμενη αποτυχία: πέφτει η βάση — το endpoint ΠΡΕΠΕΙ να το δείξει."""
    def boom():
        raise RuntimeError("connection refused")

    monkeypatch.setattr(db, "_client", boom)
    r = client.get("/readyz")
    assert r.status_code == 503, "η πεσμένη βάση πέρασε ως έτοιμη"
    body = r.json()
    assert body["ready"] is False
    assert body["checks"]["db"]["ok"] is False
    assert body["checks"]["db"]["error"] == "RuntimeError"


def test_readyz_never_leaks_secrets(monkeypatch):
    """Το σώμα δεν πρέπει να περιέχει καμία τιμή κλειδιού."""
    monkeypatch.setattr(cfg, "STRIPE_SECRET_KEY", "sk_test_SUPERSECRETVALUE")
    monkeypatch.setattr(cfg, "DEEPSEEK_API_KEY", "sk-deepseekSECRET")
    monkeypatch.setattr(cfg, "AI_API_KEY", "sk-ant-ANTHROPICSECRET")
    text = client.get("/readyz").text
    for secret in ("SUPERSECRETVALUE", "sk-deepseekSECRET", "ANTHROPICSECRET"):
        assert secret not in text, f"διέρρευσε μυστικό: {secret}"


def test_readyz_flags_accidental_stripe_live(monkeypatch):
    """Η μοναδική εξωτερική ένδειξη ότι η παραγωγή μπήκε κατά λάθος σε LIVE."""
    monkeypatch.setattr(cfg, "STRIPE_SECRET_KEY", "sk_test_x")
    assert client.get("/readyz").json()["checks"]["stripe"]["mode"] == "test"
    monkeypatch.setattr(cfg, "STRIPE_SECRET_KEY", "sk_live_x")
    assert client.get("/readyz").json()["checks"]["stripe"]["mode"] == "live"
    monkeypatch.setattr(cfg, "STRIPE_SECRET_KEY", "")
    assert client.get("/readyz").json()["checks"]["stripe"]["mode"] == "missing"


def test_readyz_catches_the_provider_mixup_that_killed_the_editor(monkeypatch):
    """Ακριβώς το σφάλμα παραγωγής: κλειδί Anthropic ως κλειδί του editor.

    Χωρίς DEEPSEEK_API_KEY, το ai_editor/model.py κρατά το `sk-ant-` κλειδί και
    το στέλνει στο api.deepseek.com → 401 → 502 σε κάθε μήνυμα πελάτη.
    """
    monkeypatch.setattr(cfg, "DEEPSEEK_API_KEY", "")
    monkeypatch.setattr(cfg, "AI_API_KEY", "sk-ant-whatever")
    r = client.get("/readyz")
    assert r.json()["checks"]["ai"]["editor"]["isolated"] is False
    assert r.status_code == 503, "η ανάμειξη παρόχων πέρασε ως έτοιμη"

    monkeypatch.setattr(cfg, "DEEPSEEK_API_KEY", "sk-deepseek-key")
    r = client.get("/readyz")
    assert r.json()["checks"]["ai"]["editor"]["isolated"] is True


def test_readyz_reports_domain_purchase_disabled():
    """Η αυτόματη αγορά domain πρέπει να φαίνεται ΚΛΕΙΣΤΗ από έξω."""
    checks = client.get("/readyz").json()["checks"]["registrar"]
    assert checks["auto_purchase"] is False, "ενεργή αυτόματη αγορά domain"


# --------------------------------------------------------- 5xx visibility
def test_unhandled_error_is_logged_and_returns_reference(capsys):
    """Ελεγχόμενη αποτυχία: μη χειρισμένη εξαίρεση σε πραγματικό route."""
    @app.get("/__monitoring_probe__")
    def _boom():
        raise ValueError("σκόπιμη αποτυχία ελέγχου")

    r = client.get("/__monitoring_probe__")
    assert r.status_code == 500
    ref = r.json().get("ref")
    assert ref and len(ref) == 8, "η απάντηση δεν έδωσε αναγνωριστικό αναφοράς"

    logged = capsys.readouterr().out
    assert "[5xx]" in logged, "το σφάλμα δεν έφτασε ποτέ στα logs"
    assert f"rid={ref}" in logged, "log και απάντηση δεν συνδέονται"
    assert "/__monitoring_probe__" in logged
    assert "ValueError" in logged


def test_error_response_hides_internal_details():
    """Ο πελάτης δεν βλέπει ποτέ stack trace ή μήνυμα εξαίρεσης."""
    @app.get("/__monitoring_probe2__")
    def _boom2():
        raise ValueError("ΑΠΟΡΡΗΤΗ ΕΣΩΤΕΡΙΚΗ ΛΕΠΤΟΜΕΡΕΙΑ")

    body = client.get("/__monitoring_probe2__").text
    assert "ΑΠΟΡΡΗΤΗ" not in body
    assert "Traceback" not in body
    assert "ValueError" not in body


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
