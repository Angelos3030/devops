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


def parse_failures(log: str, css: str) -> list[dict[str, Any]]:
    """ΟΛΑ τα ζεύγη που κόβει ο guard, όχι μόνο το πρώτο.

    Ο solver είναι αριθμητικός και κοστίζει μηδέν tokens, οπότε δεν υπάρχει
    λόγος να διορθώνεται ένα token ανά γύρο. Μετρήθηκε στο clean-work: τέσσερις
    γύροι — 27 λεπτά και όλο το budget — για τέσσερις παραβάσεις, και η
    τελευταία έμεινε στο 4.48 έναντι 4.5. Αστοχία 0,02 μονάδων.
    """
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    pairs: list[tuple[str, str, str, str]] = []
    for line in log.splitlines():
        if "✗" in line:
            pairs += _FAIL.findall(line)
    m = _LOWEST.search(log)
    if m:
        pairs.append((m.group(2), m.group(3), m.group(1), "4.5"))
    for fg, bg, got, need in pairs:
        if fg in seen:
            continue
        fg_val, bg_val = token_value(css, fg), token_value(css, bg)
        if not (fg_val and bg_val and _HEX.match(fg_val) and _HEX.match(bg_val)):
            continue
        seen.add(fg)
        out.append({"fg_token": fg, "bg_token": bg, "fg_value": fg_val,
                    "bg_value": bg_val, "measured": float(got), "required": float(need)})
    return out


def apply_token(css: str, token: str, value: str) -> str:
    """Αντικαθιστά ΜΟΝΟ τη δήλωση αυτού του token. Καμία άλλη αλλαγή."""
    if not _HEX.match(value.strip()):
        raise ValueError(f"μη έγκυρη τιμή χρώματος: {value!r}")
    pattern = re.compile(rf"(--vt-{re.escape(token)}\s*:\s*)([^;]+)(;)")
    if not pattern.search(css):
        raise ValueError(f"το token --vt-{token} δεν υπάρχει στο φύλλο στυλ")
    return pattern.sub(lambda m: m.group(1) + value.strip() + m.group(3), css, count=1)


PROMPT = """Contrast fix. Return one replacement hex for the foreground token.

--vt-{fg_token} = {fg_value}  on  --vt-{bg_token} = {bg_value}
measured {measured}:1, need >= {required}:1

Keep the same hue family; adjust lightness only.
JSON only: {{"token":"--vt-{fg_token}","value":"#RRGGBB"}}"""


def verify(candidate: str, bg_value: str, required: float) -> tuple[bool, float]:
    try:
        ratio = contrast(candidate, bg_value)
    except Exception:  # noqa: BLE001
        return False, 0.0
    return ratio >= required, ratio


# Κατηγορίες αποτυχίας. ΚΑΜΙΑ δεν γράφει στον δίσκο.
NO_WRITE = "NO_WRITE"


def parse_response(raw: str | None, expect_token: str | None = None) -> tuple[str | None, str]:
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
    if expect_token is not None:
        got = str(data.get("token", "")).strip().lstrip("-").removeprefix("vt-")
        if got and got != expect_token:
            return None, f"λάθος token: ζητήθηκε {expect_token!r}, ήρθε {got!r}"
    return value, ""


# ---------------------------------------------------------------- ντετερμινιστική λύση
#
# Γιατί έφυγε το μοντέλο από εδώ: μετρήθηκε σε τέσσερα τρεξίματα ότι το
# `finish_reason` έβγαινε πάντα `length` και το `content` κενό — ο συλλογισμός
# γέμιζε ΟΠΟΙΟΔΗΠΟΤΕ budget (300→300 reasoning tokens, 1000→1000). Η εργασία
# όμως είναι κλειστού τύπου: «σκούρυνε αυτό το χρώμα μέχρι η αντίθεση να φτάσει
# 4,5:1». Δεν χρειάζεται κρίση — χρειάζεται αριθμητική.

def _rgb(hex_colour: str) -> tuple[float, float, float]:
    h = hex_colour.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def _hex(r: float, g: float, b: float) -> str:
    return "#" + "".join(f"{max(0, min(255, round(c * 255))):02x}" for c in (r, g, b))


def to_hsl(hex_colour: str) -> tuple[float, float, float]:
    r, g, b = _rgb(hex_colour)
    hi, lo = max(r, g, b), min(r, g, b)
    light = (hi + lo) / 2
    if hi == lo:
        return 0.0, 0.0, light
    d = hi - lo
    sat = d / (2 - hi - lo) if light > 0.5 else d / (hi + lo)
    if hi == r:
        hue = ((g - b) / d) % 6
    elif hi == g:
        hue = (b - r) / d + 2
    else:
        hue = (r - g) / d + 4
    return hue * 60, sat, light


def from_hsl(hue: float, sat: float, light: float) -> str:
    c = (1 - abs(2 * light - 1)) * sat
    x = c * (1 - abs((hue / 60) % 2 - 1))
    m = light - c / 2
    seg = int(hue // 60) % 6
    r, g, b = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][seg]
    return _hex(r + m, g + m, b + m)


def solve(fg_value: str, bg_value: str, required: float,
          steps: int = 24) -> tuple[str | None, str]:
    """Η ΜΙΚΡΟΤΕΡΗ αλλαγή φωτεινότητας που φτάνει το κατώφλι.

    Η απόχρωση και ο κορεσμός διατηρούνται **εξ ορισμού** — μεταβάλλεται μόνο
    το L του HSL. Δυαδική αναζήτηση, όχι αυθαίρετα βήματα: βρίσκουμε το L που
    είναι πλησιέστερα στο αρχικό και ήδη περνά.

    Επιστρέφει (τιμή, σφάλμα). Fail closed: αν καμία τιμή του χώρου δεν φτάνει
    το κατώφλι, επιστρέφει (None, αιτία) και δεν γράφεται τίποτα.
    """
    if not (_HEX.match(fg_value.strip()) and _HEX.match(bg_value.strip())):
        return None, "μη έγκυρο hex στην είσοδο"
    if contrast(fg_value, bg_value) >= required:
        return None, "NO_CHANGE — το ζεύγος ήδη περνά"

    # Μικρό περιθώριο: ο guard στρογγυλοποιεί στα 2 δεκαδικά και μια λύση
    # ακριβώς στο 4.50 μπορεί να διαβαστεί ως 4.49. Στοχεύουμε λίγο πιο μέσα.
    required = required + 0.05
    hue, sat, light = to_hsl(fg_value)
    # ΚΑΙ ΤΙΣ ΔΥΟ κατευθύνσεις. Η παλιά ευρετική («φόντο πιο ανοιχτό από το
    # κείμενο; σκούρυνε — αλλιώς φώτισε») έστελνε το λευκό κείμενο να γίνει πιο
    # λευκό: μετρήθηκε στο clean-work, όπου λευκό πάνω σε ανοιχτό γαλάζιο
    # #7cb8eb κηρύχθηκε «αδύνατο» ενώ σκούρο κείμενο στο ίδιο φόντο δίνει ~10:1.
    # Τρία από τα τέσσερα ζεύγη του theme ήταν άλυτα για τον ίδιο λόγο.
    solutions: list[float] = []
    for target in (0.0, 1.0):
        if contrast(from_hsl(hue, sat, target), bg_value) < required:
            continue
        lo, hi = light, target      # lo δεν περνά, hi περνά
        for _ in range(steps):
            mid = (lo + hi) / 2
            if contrast(from_hsl(hue, sat, mid), bg_value) >= required:
                hi = mid
            else:
                lo = mid
        solutions.append(hi)
    if not solutions:
        return None, (f"αδύνατο: ούτε το L=0.0 ούτε το L=1.0 φτάνουν {required}:1 "
                      f"με φόντο {bg_value}")
    # Η μικρότερη δυνατή μετακίνηση από την αρχική φωτεινότητα.
    best = min(solutions, key=lambda l: abs(l - light))
    return from_hsl(hue, sat, best), ""
