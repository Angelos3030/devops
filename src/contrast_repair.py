"""Στενή διόρθωση αντίθεσης: αλλάζει ΜΙΑ τιμή token, τίποτε άλλο.

Γιατί χωριστά από τον γενικό βρόχο: όταν το spine ανέφερε
`--vt-accent-ink 3.69:1 < 4.5:1`, ο worker ζητούσε **ολόκληρο** το φύλλο στυλ
ξανά. Το μοντέλο ξαναέγραφε 700 γραμμές για να αλλάξει έξι χαρακτήρες, και στην
πορεία μετακινούσε padding και πλάτη — γι' αυτό κάθε γύρος έφερνε νέες
υπερχειλίσεις. Το συναλλακτικό όριο τις απέρριπτε σωστά, αλλά η διόρθωση δεν
προχωρούσε ποτέ.

Εδώ αλλάζει **μία δήλωση μέσα στο `.root`**. Η διαφορά είναι εγγυημένα μία
γραμμή: το τεστ το επιβάλλει byte-προς-byte.
"""
from __future__ import annotations

import json
import re
from typing import Any

_HEX = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
# Παράδειγμα γραμμής guard: «✗ MedicCare: accent-ink/surface-2 3.69<4.5»
_FAIL = re.compile(r"([a-z][a-z0-9-]*)/([a-z][a-z0-9-]*)\s+([\d.]+)\s*<\s*([\d.]+)")
_LOWEST = re.compile(r"αντίθεση[^:]*:\s*([\d.]+):1\s*—\s*\S+[^)]*\)\s*([a-z][a-z0-9-]*)/([a-z][a-z0-9-]*)")


def _srgb(c: int) -> float:
    x = c / 255
    return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4


def luminance(hex_colour: str) -> float:
    h = hex_colour.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _srgb(r) + 0.7152 * _srgb(g) + 0.0722 * _srgb(b)


def contrast(fg: str, bg: str) -> float:
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return round((hi + 0.05) / (lo + 0.05), 2)


def token_value(css: str, token: str) -> str | None:
    m = re.search(rf"--vt-{re.escape(token)}\s*:\s*([^;]+);", css)
    return m.group(1).strip() if m else None


def parse_failure(log: str, css: str) -> dict[str, Any] | None:
    """Ντετερμινιστική εξαγωγή: ποιο ζεύγος, ποιες τιμές, ποιο κατώφλι."""
    pairs = []
    for line in log.splitlines():
        if "✗" in line:
            pairs += _FAIL.findall(line)
    if not pairs:
        m = _LOWEST.search(log)
        if m:
            pairs = [(m.group(2), m.group(3), m.group(1), "4.5")]
    if not pairs:
        return None
    fg, bg, got, need = pairs[0]
    fg_val, bg_val = token_value(css, fg), token_value(css, bg)
    if not (fg_val and bg_val and _HEX.match(fg_val) and _HEX.match(bg_val)):
        return None
    return {"fg_token": fg, "bg_token": bg, "fg_value": fg_val, "bg_value": bg_val,
            "measured": float(got), "required": float(need)}


def apply_token(css: str, token: str, value: str) -> str:
    """Αντικαθιστά ΜΟΝΟ τη δήλωση αυτού του token. Καμία άλλη αλλαγή."""
    if not _HEX.match(value.strip()):
        raise ValueError(f"μη έγκυρη τιμή χρώματος: {value!r}")
    pattern = re.compile(rf"(--vt-{re.escape(token)}\s*:\s*)([^;]+)(;)")
    if not pattern.search(css):
        raise ValueError(f"το token --vt-{token} δεν υπάρχει στο φύλλο στυλ")
    return pattern.sub(lambda m: m.group(1) + value.strip() + m.group(3), css, count=1)


PROMPT = """You are adjusting ONE colour token to satisfy a contrast requirement.

FAILING PAIR
  foreground  --vt-{fg_token} = {fg_value}
  background  --vt-{bg_token} = {bg_value}
  measured contrast = {measured}:1
  required minimum  = {required}:1

Return a replacement value for --vt-{fg_token} ONLY.

Constraints:
  * keep the SAME hue family and visual intent — this is the theme's identity;
    adjust lightness/saturation, do not change the colour to a different hue
  * the new value must reach at least {required}:1 against {bg_value}
  * a 6-digit hex, nothing else
  * you are NOT rewriting the stylesheet: layout, typography, selectors and every
    other token stay exactly as they are

Respond with JSON only: {{"value": "#rrggbb", "why": "one short sentence"}}"""


def verify(candidate: str, bg_value: str, required: float) -> tuple[bool, float]:
    try:
        ratio = contrast(candidate, bg_value)
    except Exception:  # noqa: BLE001
        return False, 0.0
    return ratio >= required, ratio


# Κατηγορίες αποτυχίας. ΚΑΜΙΑ δεν γράφει στον δίσκο.
NO_WRITE = "NO_WRITE"


def parse_response(raw: str | None) -> tuple[str | None, str]:
    """Επιστρέφει (τιμή, σφάλμα). Τιμή μόνο αν είναι αληθινό hex χρώμα.

    Καθαρή συνάρτηση ώστε κάθε μορφή σκουπιδιού που μπορεί να γυρίσει ένα
    μοντέλο να δοκιμάζεται χωρίς μοντέλο. Το μετρημένο περιστατικό ήταν
    `json.loads("")` — άδειο σώμα επειδή τα reasoning tokens κατανάλωσαν όλο
    το budget των 400. Το fail-closed δούλεψε· έλειπε μόνο η διάγνωση.
    """
    if raw is None or not raw.strip():
        return None, "άδειο ή κενό σώμα απάντησης"
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, f"μη έγκυρο JSON: {str(exc)[:80]}"
    if not isinstance(data, dict):
        return None, f"η απάντηση δεν είναι αντικείμενο αλλά {type(data).__name__}"
    if "value" not in data:
        return None, "λείπει το υποχρεωτικό πεδίο 'value'"
    value = data.get("value")
    if not isinstance(value, str):
        return None, f"το 'value' δεν είναι συμβολοσειρά αλλά {type(value).__name__}"
    value = value.strip()
    if not _HEX.match(value):
        return None, f"το 'value' δεν είναι hex χρώμα: {value[:24]!r}"
    return value, ""
