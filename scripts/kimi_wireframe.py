#!/usr/bin/env python3
"""Υλοποίηση του κλειδωμένου wireframe πρώτου viewport.

    python scripts/kimi_wireframe.py

Πηγή αλήθειας: research/homepage-redesign/wireframe-hero.html (κλειδωμένο).
Έξοδος:        research/homepage-redesign/hero-locked.html

ΜΟΝΟ το πρώτο viewport. Τίποτα από κάτω. Οι συντεταγμένες του wireframe είναι
συμβόλαιο, όχι πρόταση.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "homepage-redesign"
DEST = OUT / "hero-locked.html"
META = OUT / "hero-locked.meta.json"

BASE_URL = "https://api.moonshot.ai/v1"
MODEL = "kimi-k3"
REASONING_EFFORT = "high"
FENCE = re.compile(r"^```[a-z]*\n?|```$", re.M)

SYSTEM = """Είσαι senior front-end engineer. Υλοποιείς ΕΝΑ κλειδωμένο wireframe
με ακρίβεια pixel. Δεν το βελτιώνεις, δεν το επανασχεδιάζεις, δεν προσθέτεις
τίποτα που δεν υπάρχει σε αυτό.

Οι αριθμοί που σου δίνονται είναι ΣΥΜΒΟΛΑΙΟ. Αν κάτι σου φαίνεται λάθος, το
υλοποιείς όπως δόθηκε και το αναφέρεις σε σχόλιο HTML στο τέλος του αρχείου.

ΟΡΙΟ ΑΛΗΘΕΙΑΣ: μην επινοήσεις κανέναν αριθμό πελατών, ποσοστό, κριτική,
βραβείο, αποτέλεσμα ή δυνατότητα. Μην υπονοήσεις ότι δημιουργείται site
αυτόματα σε πραγματικό χρόνο — δεν υπάρχει τέτοια λειτουργία.

Απαντάς ΜΟΝΟ με ένα μπλοκ ```html που περιέχει ολόκληρο το αρχείο. Καμία
εισαγωγή, κανένα σχόλιο εκτός του μπλοκ."""

SPEC = r"""=== ΤΙ ΦΤΙΑΧΝΕΙΣ ===

Ένα αυτοτελές αρχείο HTML: ΜΟΝΟ το πρώτο viewport της αρχικής σελίδας Vitrina.
Τίποτα από κάτω. Κανένα footer, καμία τιμολόγηση, κανένα FAQ, καμία δεύτερη
ενότητα. Η σελίδα τελειώνει εκεί που τελειώνει το wireframe.

Το αρχείο θα ζήσει στο research/homepage-redesign/, οπότε οι εικόνες
αναφέρονται ως shots/<αρχείο>.

=== ΚΛΕΙΔΩΜΕΝΗ ΓΕΩΜΕΤΡΙΑ — DESKTOP 1440 x 900 ===

Καμβάς 1440 x 900. ΜΙΑ οθόνη. Καμία κατακόρυφη κύλιση σε ύψος 900.

  λογότυπο «vitrina»      x 48   y 34    20px / 600
  ── ΑΡΙΣΤΕΡΗ ΛΩΡΙΔΑ, πλάτος στήλης 608 ──
  h1                      x 48   y 196   34px / 600, lh 1.18, tracking -.02em
        «Φτιάχνουμε το site.» <br> «Εσύ ασχολείσαι με» <br> «την επιχείρησή σου.»
        ΤΡΕΙΣ γραμμές με ρητά <br>. ΟΧΙ αυτόματη αναδίπλωση.
  υπότιτλος               x 48   y 340   17px / 400, δευτερεύον χρώμα
        «Πες μας με δυο λόγια τι κάνεις.»
  επιφάνεια εισόδου       x 48   y 392   608 x 180, radius 24
        λευκό #FFFFFF, border 1px solid #68655F
  placeholder             x 76   y 420   17px
        «π.χ. Έχω κομμωτήριο στη Γλυφάδα…»
  CTA ΜΕΣΑ στην επιφάνεια x 492  y 502   140 x 48, radius 10
        «Δείξε μου →»  16px / 600
  meta γραμμή 1           x 48   y 616   15px / 400
        «Site · Hosting · Local SEO · Αλλαγές»
  meta γραμμή 2           x 48   y 642   15px
        «€14,99/μήνα» σε 600 και χρώμα κειμένου, « · πρώτος μήνας δωρεάν» σε 400 δευτερεύον
  ── ΔΙΑΧΩΡΙΣΤΙΚΟ ──
  κάθετη γραμμή 1px       x 726  y 196   ύψος 508, χρώμα #E8E2D9
  ── ΔΕΞΙΑ ΛΩΡΙΔΑ ──
  ετικέτα                 x 794  y 196   17px / 500, χρώμα κειμένου
        «Πραγματικά site που φτιάξαμε.»
  πλακίδιο 1  ταβέρνα     x 794  y 252   318 x 404, radius 10
  πλακίδιο 2  κομμωτήριο  x 986  y 296   318 x 404, radius 10
  πλακίδιο 3  υδραυλικός  x 1178 y 340   318 x 404, radius 10
        Το 3ο φτάνει στο x 1497 — ΚΟΒΕΤΑΙ από την άκρη των 1440. Αυτό είναι
        σκόπιμο και ΥΠΟΧΡΕΩΤΙΚΟ: δείχνει ότι υπάρχουν κι άλλα.
  λεζάντα                 x 794  y 768   14px / 400 δευτερεύον
        «ταβέρνα · κομμωτήριο · οδοντιατρείο · υδραυλικός · καφετέρια · δωμάτια»

Σειρά στοίβαξης πλακιδίων: το 1 πίσω, το 3 μπροστά. Κάθε πλακίδιο έχει
border 1px #E8E2D9 και ΠΟΛΥ διακριτική σκιά ώστε να ξεχωρίζει από το από κάτω.
ΟΧΙ πλαίσιο browser. ΟΧΙ κάρτα-δοχείο γύρω τους. ΟΧΙ μπάρα διεύθυνσης.

=== ΚΛΕΙΔΩΜΕΝΗ ΓΕΩΜΕΤΡΙΑ — MOBILE 390 x 844 ===

  λογότυπο            x 24  y 28   18px / 600
  h1                  x 24  y 92   28px / 600, ίδιες τρεις γραμμές με <br>
  υπότιτλος           x 24  y 216  15px
  επιφάνεια εισόδου   x 24  y 264  342 x 170, radius 24
  placeholder         x 44  y 286  15px
  CTA ΜΕΣΑ            x 44  y 366  302 x 48 — ΠΛΗΡΟΥΣ ΠΛΑΤΟΥΣ μέσα στην επιφάνεια
  meta γραμμή 1       x 24  y 456  14px
  meta γραμμή 2       x 24  y 480  14px
  ετικέτα             x 24  y 534  15px / 500
  πλακίδιο 1          x 24  y 576  196 x 250
  πλακίδιο 2          x 198 y 602  196 x 250
  πλακίδιο 3          x 372 y 628  196 x 250 — φτάνει στο x 569, ΚΟΒΕΤΑΙ

Ό,τι πέφτει κάτω από τα 844 είναι αποδεκτό — το κόψιμο είναι το κάλεσμα
για κύλιση.

=== ΠΩΣ ΥΛΟΠΟΙΕΙΣ ΤΗ ΓΕΩΜΕΤΡΙΑ ===

ΜΗΝ χρησιμοποιήσεις absolute positioning για ολόκληρη τη σελίδα. Οι αριθμοί
περιγράφουν το ΑΠΟΤΕΛΕΣΜΑ στα 1440x900 και στα 390x844, όχι τη μέθοδο.

Χρησιμοποίησε flex/grid με gap και padding ώστε:
  - στα ακριβώς 1440 πλάτος, τα στοιχεία να προσγειώνονται στις τιμές ±4px
  - στα ακριβώς 390 πλάτος, το ίδιο
  - σε ενδιάμεσα πλάτη η διάταξη να παραμένει λογική (η δεξιά λωρίδα
    στοιβάζεται κάτω από την αριστερή κάτω από τα 900px πλάτος)

Τα πλακίδια είναι το μόνο σημείο που δικαιολογεί position:absolute — μέσα σε
έναν σχετικά τοποθετημένο container με ΓΝΩΣΤΟ ύψος.

=== Η ΥΠΕΡΧΕΙΛΙΣΗ ΠΟΥ ΠΡΕΠΕΙ ΝΑ ΔΟΥΛΕΨΕΙ ΣΩΣΤΑ ===

Το 3ο πλακίδιο ξεπερνά τη δεξιά άκρη. Η σελίδα ΔΕΝ επιτρέπεται να αποκτήσει
οριζόντια κύλιση εγγράφου.

  desktop: ο container της δεξιάς λωρίδας έχει overflow:hidden
  mobile:  η λωρίδα πλακιδίων έχει overflow-x:auto με
           scrollbar-width:none και -webkit-overflow-scrolling:touch

Έλεγχος που πρέπει να περνάει: document.documentElement.scrollWidth
ισούται με το πλάτος του viewport, και στα 1440 και στα 390.

=== ΕΙΚΟΝΕΣ — ΠΡΑΓΜΑΤΙΚΑ SITE, ΟΧΙ PLACEHOLDER ===

  πλακίδιο 1  shots/taverna-full.jpg   alt «Ιστοσελίδα ταβέρνας που φτιάξαμε»
  πλακίδιο 2  shots/salon-full.jpg     alt «Ιστοσελίδα κομμωτηρίου που φτιάξαμε»
  πλακίδιο 3  shots/plumber-full.jpg   alt «Ιστοσελίδα υδραυλικού που φτιάξαμε»

Είναι πλήρους σελίδας στιγμιότυπα, πολύ ψηλά. Μέσα στο πλακίδιο:
object-fit:cover και object-position:top, ώστε να φαίνεται η κορυφή του site.
loading="lazy" ΜΟΝΟ στο 3ο· τα δύο πρώτα eager. width/height attributes για
να μην υπάρχει layout shift.

=== ΠΑΛΕΤΑ — ΑΚΡΙΒΩΣ ΑΥΤΗ ===

  #FBFAF7  φόντο σελίδας        #171714  κείμενο
  #68655F  δευτερεύον κείμενο   #E8E2D9  περιγράμματα και διαχωριστικό
  #E85D3F  accent — CTA         #D94C30  hover CTA
  #F5EFE7  ζεστή επιφάνεια      #FFFFFF  ΜΟΝΟ η επιφάνεια εισόδου

Το λευκό εμφανίζεται ΜΙΑ φορά σε ολόκληρη την οθόνη: στην επιφάνεια εισόδου.
Το accent εμφανίζεται ΜΙΑ φορά: στο CTA.
Ο τίτλος και το σώμα έχουν ΤΟ ΙΔΙΟ χρώμα #171714 — η ιεραρχία γίνεται με
μέγεθος και βάρος, ΟΧΙ με ξεθώριασμα.

Το #F5EFE7 μπορεί να χρησιμοποιηθεί στο mobile ως φόντο της περιοχής
πλακιδίων. Στο desktop δεν χρειάζεται.

=== ΤΥΠΟΓΡΑΦΙΑ ===

Manrope, από Google Fonts με ελληνικό subset:
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600&display=swap">
Δήλωσε πραγματικό fallback stack.

ΜΕΓΙΣΤΟ ΒΑΡΟΣ 600. Πουθενά 700, 800 ή 900. Καμία δεύτερη οικογένεια.
Κανένα serif. Καμία condensed.

=== ΚΙΝΗΣΗ ===

Μία και μόνη: `transition: background-color .3s` στο CTA, #E85D3F → #D94C30.
ΤΙΠΟΤΑ ΑΛΛΟ. Κανένα fade-in, καμία αποκάλυψη στην κύλιση, κανένα parallax,
κανένα transform, καμία κίνηση στα πλακίδια, καμία εισαγωγική κίνηση.
Πρόσθεσε @media (prefers-reduced-motion: reduce) που μηδενίζει transitions.

=== ΠΡΟΣΒΑΣΙΜΟΤΗΤΑ ===

  - ΕΝΑ <h1>. Σημασιολογικό <header> και <main>.
  - Πραγματικό <textarea> με <label> (visually hidden) — ΟΧΙ contenteditable div.
  - Πραγματικό <button type="submit"> — ΟΧΙ <div> με onclick.
  - :focus-visible με ορατό δαχτυλίδι 2px #E85D3F, offset 2px, ΚΑΙ στο
    textarea ΚΑΙ στο κουμπί. (Το reference δεν είχε· εμείς έχουμε.)
  - Το textarea έχει ορατή κατάσταση focus: το border γίνεται #171714.
  - Στόχοι αφής ≥ 44px σε mobile. Το CTA είναι 48 — εντάξει.
  - Αντίθεση: #171714 σε #FBFAF7 και #FBFAF7 σε #E85D3F. Μην αλλάξεις χρώματα.
  - lang="el", <title>, meta description στα ελληνικά.

=== ΤΟ CTA ΔΕΝ ΚΑΝΕΙ ΤΙΠΟΤΑ ΨΕΥΤΙΚΟ ===

Είναι <form> που θα συνδεθεί αργότερα. Χωρίς JavaScript που προσποιείται
δημιουργία site, χωρίς μπάρα προόδου, χωρίς animation πληκτρολόγησης,
χωρίς «το AI σκέφτεται». Αν γράψεις καθόλου JS, μόνο για να αποτρέψεις το
submit σε άδειο πεδίο.

=== ΑΠΑΓΟΡΕΥΟΝΤΑΙ ΡΗΤΑ ===

video · typing animation · ψεύτικη παραγωγή · giant H1 · πλαίσιο browser ·
μπλε, μοβ, indigo · serif · βάρος > 600 · χάπια παντού · gradients · glow ·
glassmorphism · κάρτες SaaS · εικονίδια σε πλέγμα τριών · lorem ipsum ·
εξωτερικό tracking · οποιαδήποτε βιβλιοθήκη ή CDN πέρα από τη Google Fonts

=== ΠΑΡΑΔΟΤΕΟ ===

Ένα μπλοκ ```html με ολόκληρο το αρχείο. Στο τέλος, ένα σχόλιο HTML που
απαριθμεί κάθε σημείο όπου η υλοποίηση αποκλίνει από τους αριθμούς και γιατί.
"""


def _key() -> str:
    for line in (ROOT / ".env").read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(r"^KIMI_API_KEY=(.*)$", line.strip())
        if m:
            return m.group(1).strip().strip('"').strip("'")
    raise SystemExit("Λείπει το KIMI_API_KEY από το .env")


def ask(key: str, user: str, deadline: float,
        max_tokens: int = 64000, attempt: int = 0) -> tuple[str, dict, dict]:
    payload = {
        "model": MODEL, "temperature": 1, "max_tokens": max_tokens,
        "reasoning_effort": REASONING_EFFORT,
        "stream": True, "stream_options": {"include_usage": True},
        "messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": user}],
    }
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions", data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "Accept": "text/event-stream"})
    t0 = time.time()
    chunks: list[str] = []
    usage: dict = {}
    finish = "unknown"
    timing: dict = {"ttft": None}
    last_report = t0
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            for line in resp:
                now = time.time()
                if now > deadline:
                    finish = "deadline"
                    break
                if now - last_report > 30:
                    print(f"  … {int(now - t0)}s · {sum(map(len, chunks))} χαρακτήρες",
                          flush=True)
                    last_report = now
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
                    if ch.get("finish_reason"):
                        finish = ch["finish_reason"]
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        if exc.code == 429 and attempt == 0:
            print("  429 υπερφόρτωση — αναμονή 45s και ΜΙΑ επανάληψη", flush=True)
            time.sleep(45)
            return ask(key, user, deadline, max_tokens, attempt=1)
        raise SystemExit(f"HTTP {exc.code}: {detail}")
    except (urllib.error.URLError, TimeoutError) as exc:
        finish = f"transport: {str(exc)[:80]}"
    timing.update(total=round(time.time() - t0, 1), finish_reason=finish,
                  chars=sum(map(len, chunks)))
    return "".join(chunks), usage, timing


def extract_html(text: str) -> str:
    m = re.search(r"```html\s*\n(.*?)```", text, re.S)
    if m:
        return m.group(1).strip()
    i = text.find("<!doctype")
    if i < 0:
        i = text.find("<!DOCTYPE")
    if i < 0:
        raise SystemExit("δεν βρέθηκε HTML στην απάντηση")
    return FENCE.sub("", text[i:]).strip()


def main() -> None:
    key = _key()
    deadline = time.time() + 1500
    print(f"→ {MODEL} · reasoning={REASONING_EFFORT} · streaming", flush=True)
    raw, usage, timing = ask(key, SPEC, deadline)
    print(f"  finish={timing['finish_reason']} ttft={timing['ttft']}s "
          f"total={timing['total']}s chars={timing['chars']}", flush=True)
    if not raw.strip():
        raise SystemExit("κενή απάντηση")
    html = extract_html(raw)
    DEST.write_text(html, encoding="utf-8")
    cost = None
    if usage:
        pin = usage.get("prompt_tokens", 0) / 1e6 * 3.00
        pout = usage.get("completion_tokens", 0) / 1e6 * 15.00
        cost = round(pin + pout, 4)
    META.write_text(json.dumps(
        {"model": MODEL, "reasoning_effort": REASONING_EFFORT,
         "usage": usage, "timing": timing, "cost_usd": cost,
         "bytes": len(html.encode("utf-8"))},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✓ {DEST.name} · {len(html.encode('utf-8'))} bytes · "
          f"usage={usage} · κόστος ${cost}", flush=True)


if __name__ == "__main__":
    main()
