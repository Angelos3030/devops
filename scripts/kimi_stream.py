#!/usr/bin/env python3
"""ΤΕΛΙΚΗ ΔΟΚΙΜΗ ΒΙΩΣΙΜΟΤΗΤΑΣ — ίδιο δημιουργικό brief, streaming μεταφορά.

    python scripts/kimi_stream.py --model kimi-k2.7-code-highspeed --budget 1200

Αλλάζουν ΜΟΝΟ δύο πράγματα σε σχέση με την αποτυχημένη προσπάθεια: `stream:true`
και το highspeed μοντέλο. Το brief μένει αυτούσιο — καμία απλοποίηση, κανένας
περιορισμός του Vitrina.

Η υπόθεση: χωρίς stream το `timeout` μετρά αναμονή για ΠΡΩΤΟ byte. Το μοντέλο
συλλογιζόταν πάνω από 900 δευτερόλεπτα πριν στείλει οτιδήποτε, οπότε η κλήση
πέθαινε ακόμη κι αν η παραγωγή επρόκειτο να πετύχει. Με stream μετράμε τι
συμβαίνει αντί να μαντεύουμε.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.kimi_freehand import SYSTEM, brief, _key  # noqa: E402

BASE_URL = "https://api.moonshot.ai/v1"
OUT = ROOT / "research" / "kimi-freehand"
FENCE = re.compile(r"^```[a-z]*\n?|```$", re.M)


def ask(key: str, model: str, user: str, deadline: float,
        max_tokens: int = 32000) -> tuple[str, dict, dict]:
    """Streaming, ΜΙΑ απόπειρα, σκληρό όριο τοίχου. Καμία αυτόματη επανάληψη."""
    body = json.dumps({
        "model": model, "temperature": 1, "max_tokens": max_tokens,
        "stream": True, "stream_options": {"include_usage": True},
        "messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": user}],
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "Accept": "text/event-stream"})

    t0 = time.time()
    chunks: list[str] = []
    usage: dict = {}
    finish = "unknown"
    timing: dict = {"ttft": None, "t1k": None}
    try:
        with urllib.request.urlopen(req, timeout=240) as resp:
            for line in resp:
                if time.time() > deadline:
                    finish = "deadline"
                    break
                s = line.decode("utf-8", "replace").strip()
                if not s.startswith("data:"):
                    continue
                data = s[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    ev = json.loads(data)
                except json.JSONDecodeError:
                    continue
                if ev.get("usage"):
                    usage = ev["usage"]
                for ch in ev.get("choices", []):
                    piece = (ch.get("delta") or {}).get("content") or ""
                    if piece:
                        if timing["ttft"] is None:
                            timing["ttft"] = round(time.time() - t0, 1)
                        chunks.append(piece)
                        # ~4 χαρακτήρες ανά token: χονδρικό αλλά σταθερό μέτρο
                        if timing["t1k"] is None and sum(map(len, chunks)) >= 4000:
                            timing["t1k"] = round(time.time() - t0, 1)
                    if ch.get("finish_reason"):
                        finish = ch["finish_reason"]
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        raise SystemExit(f"HTTP {exc.code}: {detail}")
    except (urllib.error.URLError, TimeoutError) as exc:
        finish = f"transport: {str(exc)[:80]}"

    timing.update(total=round(time.time() - t0, 1), finish_reason=finish,
                  chars=sum(map(len, chunks)))
    return "".join(chunks), usage, timing


def as_json(text: str) -> dict:
    """Το stream δίνει σκέτο κείμενο· απομονώνουμε το JSON σώμα."""
    text = FENCE.sub("", text.strip()).strip()
    i, j = text.find("{"), text.rfind("}")
    if i < 0 or j <= i:
        raise SystemExit("δεν βρέθηκε JSON στην απάντηση")
    return json.loads(text[i:j + 1])


STEP_MARKUP = """=== ΒΗΜΑ 1 ΑΠΟ 2: Η ΔΟΜΗ ===

Δώσε το σημασιολογικό HTML της σελίδας σου — ΧΩΡΙΣ CSS, χωρίς <style>.
Τα class names είναι δικά σου· θα τα στιλίσεις εσύ στο επόμενο βήμα.

Η διαίρεση είναι καθαρά μηχανική — μια πλήρης σελίδα μαζί με το φύλλο στυλ δεν
χωρά σε μία απάντηση. Δεν περιορίζει καμία σχεδιαστική σου επιλογή.

Απάντησε ΜΟΝΟ με JSON:
{"body": "<header>…</header><main>…</main><footer>…</footer>",
 "head_extra": "<link…> για γραμματοσειρές αν θέλεις",
 "title": "…",
 "art_direction": "η καλλιτεχνική σου κατεύθυνση",
 "signature_ideas": ["…", "…", "…"],
 "palette": "τα χρώματα που διάλεξες"}"""

STEP_CSS = """=== ΒΗΜΑ 2 ΑΠΟ 2: ΤΟ ΣΤΙΛ ===

Γράψε ΟΛΟΚΛΗΡΟ το CSS για τη δομή που μόλις έγραψες: τρεις σκόπιμες συνθέσεις
(desktop / tablet / 390px), η κίνησή σου, τα micro-interactions,
`prefers-reduced-motion`, ορατό focus.

Απάντησε ΜΟΝΟ με JSON:
{"css": "…όλο το φύλλο στυλ…",
 "responsive_strategy": "…", "motion_strategy": "…", "interactions": ["…"]}"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="kimi-k2.7-code-highspeed")
    ap.add_argument("--budget", type=float, default=1200.0)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    key = _key()
    base = brief()
    deadline = time.time() + args.budget
    print(f"μοντέλο={args.model} · όριο={int(args.budget)}s", flush=True)

    raw1, u1, t1 = ask(key, args.model, base + "\n\n" + STEP_MARKUP, deadline)
    print("ΒΗΜΑ 1:", json.dumps(t1, ensure_ascii=False), flush=True)
    (OUT / "step1.txt").write_text(raw1, encoding="utf-8")
    if not raw1.strip():
        raise SystemExit(f"ΒΗΜΑ 1 χωρίς έξοδο — {t1}")
    d1 = as_json(raw1)
    body = d1.get("body", "")
    if "<" not in body:
        raise SystemExit("το βήμα 1 δεν επέστρεψε δομή")

    raw2, u2, t2 = ask(key, args.model,
                       base + "\n\n" + STEP_CSS + "\n\n=== Η ΔΟΜΗ ΣΟΥ ===\n" + body,
                       deadline)
    print("ΒΗΜΑ 2:", json.dumps(t2, ensure_ascii=False), flush=True)
    (OUT / "step2.txt").write_text(raw2, encoding="utf-8")
    d2 = as_json(raw2)
    css = d2.get("css", "")
    if not css.strip():
        raise SystemExit("το βήμα 2 δεν επέστρεψε CSS")

    html = ("<!doctype html>\n<html lang=\"el\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            f"<title>{d1.get('title', 'Οδοντιατρείο Παπαδοπούλου')}</title>\n"
            f"{d1.get('head_extra', '')}\n<style>\n{css}\n</style>\n</head>\n"
            f"<body>\n{body}\n</body>\n</html>\n")
    (OUT / "raw.html").write_text(html, encoding="utf-8")

    meta = {
        "model": args.model,
        "bytes": len(html.encode("utf-8")),
        "timing": {"step1": t1, "step2": t2},
        "usage": {k: u1.get(k, 0) + u2.get(k, 0)
                  for k in ("prompt_tokens", "completion_tokens")},
        "art_direction": d1.get("art_direction"),
        "signature_ideas": d1.get("signature_ideas"),
        "palette": d1.get("palette"),
        "responsive_strategy": d2.get("responsive_strategy"),
        "motion_strategy": d2.get("motion_strategy"),
        "interactions": d2.get("interactions"),
    }
    (OUT / "design.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False),
                                     encoding="utf-8")
    print(json.dumps({"bytes": meta["bytes"], "usage": meta["usage"],
                      "ideas": meta["signature_ideas"]}, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
