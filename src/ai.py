"""
Ένα σημείο για κάθε κλήση AI — με όποιον πάροχο υπάρχει διαθέσιμος.

Γιατί υπάρχει: τα κείμενα των πελατών δεν είναι δεμένα με μία εταιρεία. Το
DeepSeek, το OpenRouter και σχεδόν όλοι οι φθηνοί πάροχοι μιλάνε το πρωτόκολλο
του **OpenAI** (`POST /chat/completions`), ενώ η Anthropic έχει δικό της
(`/v1/messages`). Δεν είναι θέμα base URL — είναι άλλο σχήμα αιτήματος και
άλλο σχήμα απάντησης. Πριν από αυτό το αρχείο, τρία σημεία του κώδικα καλούσαν
απευθείας το anthropic SDK, οπότε αλλαγή παρόχου σήμαινε αλλαγή σε τρία μέρη.

Ο κανόνας που δεν αλλάζει: **αν το AI αποτύχει, το προϊόν δουλεύει.** Κάθε
συνάρτηση εδώ επιστρέφει `None` αντί να πετάξει, και ο καλών κρατάει τα έτοιμα
πρότυπα ανά επάγγελμα. Ο πελάτης δεν βλέπει ποτέ άδειο site επειδή έληξε ένα
κλειδί.

Ρύθμιση: βλ. `src/config.py` (AI_API_KEY, AI_BASE_URL, AI_MODEL, AI_PROVIDER).
Έλεγχος: `python scripts/check_ai.py`.
"""
from __future__ import annotations

import json
from typing import Any

import requests

from . import config as cfg

TIMEOUT = 90
LAST_ERROR: dict[str, str] | None = None


def provider() -> str:
    """«anthropic», «openai» ή «» αν δεν υπάρχει κλειδί."""
    if not cfg.AI_API_KEY:
        return ""
    if cfg.AI_PROVIDER in ("anthropic", "openai"):
        return cfg.AI_PROVIDER
    # Τα κλειδιά της Anthropic έχουν αναγνωρίσιμο πρόθεμα· οτιδήποτε άλλο με
    # δικό του endpoint είναι σχεδόν πάντα OpenAI-συμβατό.
    if cfg.AI_API_KEY.startswith("sk-ant-"):
        return "anthropic"
    return "openai" if cfg.AI_BASE_URL else "anthropic"


def model() -> str:
    # Προστάτευσε production από παλιό env: Anthropic key μαζί με
    # AI_MODEL=deepseek-chat δεν πρέπει να σταλεί ποτέ στο Messages API.
    if cfg.AI_MODEL and not (provider() == "anthropic" and "deepseek" in cfg.AI_MODEL.lower()):
        return cfg.AI_MODEL
    return "deepseek-chat" if provider() == "openai" else cfg.MODEL_CHEAP


def available() -> bool:
    return bool(cfg.AI_API_KEY)


def complete(system: str, user: str, max_tokens: int = 1500) -> str | None:
    """Μία ερώτηση, ένα κείμενο πίσω. `None` σε οποιοδήποτε πρόβλημα."""
    p = provider()
    if not p:
        return None
    global LAST_ERROR
    try:
        result = (_anthropic(system, user, max_tokens) if p == "anthropic"
                  else _openai(system, user, max_tokens))
        LAST_ERROR = None
        return result
    except Exception as e:  # noqa: BLE001
        # Δεν σπάμε τη ροή του πελάτη για μια αποτυχία AI — αλλά την τυπώνουμε,
        # αλλιώς ένα άκυρο κλειδί περνάει απαρατήρητο για εβδομάδες.
        print(f"[ai] {p} απέτυχε ({type(e).__name__}): {str(e)[:160]}")
        status = ""
        if isinstance(e, RuntimeError) and str(e).startswith("HTTP "):
            status = str(e).split(":", 1)[0].replace("HTTP ", "")
        LAST_ERROR = {"type": type(e).__name__, "http_status": status}
        return None


def complete_json(system: str, user: str, max_tokens: int = 1500) -> Any | None:
    """Ό,τι και το complete(), αλλά περιμένει JSON και το αποκωδικοποιεί.

    Τα μοντέλα συχνά τυλίγουν το JSON σε ```json ... ``` ή σε μια πρόταση
    εισαγωγής — κρατάμε ό,τι είναι ανάμεσα στα εξωτερικά άγκιστρα.
    """
    text = complete(system, user, max_tokens)
    if not text:
        return None
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        print(f"[ai] η απάντηση δεν είχε JSON: {text[:120]}")
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError as e:
        print(f"[ai] χαλασμένο JSON ({e}): {text[start:start + 120]}")
        return None


def _anthropic(system: str, user: str, max_tokens: int) -> str:
    # Απευθείας στο επίσημο Messages API. Αποφεύγουμε ασυμβατότητες μεταξύ
    # εκδόσεων anthropic/httpx και κρατάμε το ίδιο προβλέψιμο transport με τους
    # OpenAI-compatible providers παρακάτω.
    configured_base = cfg.AI_BASE_URL or ""
    base = ("https://api.anthropic.com"
            if "deepseek.com" in configured_base.lower()
            else configured_base or "https://api.anthropic.com")
    r = requests.post(
        f"{base}/v1/messages",
        headers={"x-api-key": cfg.AI_API_KEY,
                 "anthropic-version": "2023-06-01",
                 "Content-Type": "application/json"},
        json={"model": model(), "max_tokens": max_tokens, "system": system,
              "messages": [{"role": "user", "content": user}]},
        timeout=TIMEOUT)
    if not r.ok:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
    blocks = r.json().get("content", [])
    return "".join(b.get("text", "") for b in blocks if b.get("type") == "text")


def _openai(system: str, user: str, max_tokens: int) -> str:
    base = cfg.AI_BASE_URL or "https://api.deepseek.com/v1"
    r = requests.post(
        f"{base}/chat/completions",
        headers={"Authorization": f"Bearer {cfg.AI_API_KEY}",
                 "Content-Type": "application/json"},
        json={"model": model(), "max_tokens": max_tokens, "temperature": 0.7,
              "messages": [{"role": "system", "content": system},
                           {"role": "user", "content": user}]},
        timeout=TIMEOUT)
    if not r.ok:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
    return r.json()["choices"][0]["message"]["content"]
