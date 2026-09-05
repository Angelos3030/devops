#!/usr/bin/env python3
"""ΜΟΝΟ το hero και το product demo. Η υπόλοιπη σελίδα μένει ανέγγιχτη.

    python scripts/kimi_hero.py

Στοχευμένη αντικατάσταση ΕΝΟΣ section. Ό,τι νέο στιλ προστίθεται είναι
scoped στο `.hero` και στο demo — η νέα design language δεν διαχέεται στις
υπόλοιπες ενότητες πριν εγκριθεί οπτικά.
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
sys.path.insert(0, str(ROOT))

OUT = ROOT / "research" / "homepage-redesign"
SRC = OUT / "homepage-v2.html"
DEST = OUT / "homepage-v3.html"
BASE_URL = "https://api.moonshot.ai/v1"
MODEL = "kimi-k3"
REASONING_EFFORT = "high"
FENCE = re.compile(r"^```[a-z]*\n?|```$", re.M)

SYSTEM = """Είσαι senior front-end designer. Αντικαθιστάς ΕΝΑ section μιας
υπάρχουσας σελίδας και προσθέτεις το στιλ του. Δεν σχεδιάζεις ξανά τη σελίδα.

Ό,τι νέο CSS γράφεις είναι scoped στο `.hero` και στα στοιχεία του demo. ΔΕΝ
αλλάζεις καθολικά tokens, δεν αγγίζεις τις υπόλοιπες ενότητες, δεν αλλάζεις το
footer ή το nav πέρα από ό,τι ζητείται ρητά.

ΑΠΑΡΑΒΑΤΟ ΟΡΙΟ ΑΛΗΘΕΙΑΣ: το demo είναι ΕΠΙΔΕΙΞΗ πραγματικών, ήδη υπαρκτών site.
ΑΠΑΓΟΡΕΥΟΝΤΑΙ: μπάρες φόρτωσης, «το AI δημιουργεί», σωματίδια, ψεύτικη
παραγωγή σε πραγματικό χρόνο, εφέ εντυπωσιασμού, play button ως κύρια
αλληλεπίδραση. Καμία επινοημένη κριτική, αριθμός ή ποσοστό."""


def _key() -> str:
    for line in (ROOT / ".env").read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(r"^KIMI_API_KEY=(.*)$", line.strip())
        if m:
            return m.group(1).strip().strip('"').strip("'")
    raise SystemExit("Λείπει το KIMI_API_KEY από το .env")


def as_json(text: str) -> dict:
    text = FENCE.sub("", text.strip()).strip()
    i, j = text.find("{"), text.rfind("}")
    if i < 0 or j <= i:
        raise SystemExit("δεν βρέθηκε JSON στην απάντηση")
    return json.loads(text[i:j + 1])


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


SPEC = """=== ΤΙ ΦΤΙΑΧΝΕΙΣ ===

ΜΟΝΟ το `<section class="hero">` και το product demo μέσα του, μαζί με το CSS
και το JS τους. Οι υπόλοιπες ενότητες της σελίδας ΔΕΝ αλλάζουν.

=== ΔΙΑΤΑΞΗ (desktop 1440) ===

Δύο στήλες: αριστερά κείμενο ≈420px (34%), δεξιά preview ≈810px (**62%**).
Το preview είναι ο πρωταγωνιστής· το κείμενο υποχωρεί οπτικά.

Σειρά στην αριστερή στήλη:

  eyebrow  «Η επιχείρησή σου αξίζει καλύτερη βιτρίνα.»   13px/600, tracking .08em
  h1       «Το site της επιχείρησής σου,
            χωρίς να ασχολείσαι με το site.»              56px/660, lh 1.08
  lede     «Εσύ μας λες τι κάνεις. Εμείς αναλαμβάνουμε
            κατασκευή, φιλοξενία, Local SEO και αλλαγές.» 19px/450, lh 1.55
  CTA      [Ξεκίνα — πρώτος μήνας δωρεάν] (indigo γεμάτο)
           [Δες παραδείγματα] (ήπιο, με ζεστό border)     16px/620
  τιμή     «€14,99 / μήνα · πρώτος μήνας δωρεάν»          17px/500
  strip    «Κατασκευή · Hosting · Local SEO · Αλλαγές»    14px/500, λεπτοί διαχωριστές

Τα κείμενα ΑΥΤΟΥΣΙΑ. Καμία παραλλαγή. ΟΧΙ «από €14,99».

Δεξιά στήλη: οι τέσσερις επιλογές ΠΑΝΩ από το πλαίσιο, μετά το πλαίσιο browser,
και από κάτω μικρή λεζάντα με badge «ΠΑΡΑΔΕΙΓΜΑ».

=== ΤΥΠΟΓΡΑΦΙΑ — ΚΑΝΕΝΑ WEIGHT 800 ===

Manrope. Επιτρεπτά βάρη: 400, 450, 500, 550, 600, 620, 660, 700.
Το 700 ΜΟΝΟ στον αριθμό τιμής. Το bold είναι εργαλείο ιεραρχίας, όχι προεπιλογή.

=== ΠΑΛΕΤΑ (scoped στο hero) ===

  #FBFAF8  φόντο hero            #18171C  πρωτεύον κείμενο
  #FFFFFF  επιφάνεια πλαισίου    #66636D  δευτερεύον κείμενο
  #4F39F6  brand / ενεργό chip   #3F2BD8  hover
  #F0EDFF  απαλό indigo          #0E9E8F  teal — ΜΟΝΟ online/active/included
  #EDE8DF  ζεστά borders (ΟΧΙ γκρι κουτιά)

=== ΟΙ ΤΕΣΣΕΡΙΣ ΕΠΙΛΟΓΕΣ ===

Κομμωτήριο · Ταβέρνα · Οδοντιατρείο · Υδραυλικός

Refined, ΟΧΙ τεράστια pills: padding ≈10px 18px, border-radius 10px.
Ανενεργό: φόντο #FBFAF8, border #EDE8DF, κείμενο #18171C.
Ενεργό: φόντο #4F39F6, κείμενο λευκό, πολύ διακριτική λάμψη.
Μετάβαση χρώματος 120ms.

Στην αλλαγή: εξερχόμενο fade-out 160ms + translateX 12px · εισερχόμενο fade-in
220ms · αλλάζει ΚΑΙ το κείμενο της μπάρας διεύθυνσης.

=== ΤΑ ASSETS (πραγματικές λήψεις, υπάρχουν ήδη) ===

  επάγγελμα      | full-page (για κύλιση)   | mobile 390
  Κομμωτήριο     | shots/salon-full.jpg     | shots/salon-mobile.jpg
  Ταβέρνα        | shots/taverna-full.jpg   | shots/taverna-mobile.jpg
  Οδοντιατρείο   | shots/dentist-full.jpg   | shots/dentist-mobile.jpg
  Υδραυλικός     | shots/plumber-full.jpg   | shots/plumber-mobile.jpg

Τα full-page είναι πλάτους 1280 και ύψους 3158–5417px. Η κύλιση γίνεται με
μετακίνηση της εικόνας μέσα σε πλαίσιο με `overflow:hidden` — `transform:
translateY(...)`, ΠΟΤΕ αλλαγή `top`.

Μπάρα διεύθυνσης ανά επάγγελμα: `getvitrina.gr · κομμωτήριο` κ.ο.κ.

=== ΤΟ PRODUCT DEMO — 11,5 δευτερόλεπτα ===

Ο επισκέπτης πρέπει να έχει δει ΠΡΑΓΜΑΤΙΚΟ site μέσα στα πρώτα ~2,5s.
Το WOW είναι το site, όχι το typing.

  0,0–0,6s   εμφανίζεται πεδίο με «Πες μας τι κάνεις»
  0,6–1,8s   γρήγορο typing «Έχω κομμωτήριο στη Γλυφάδα» (~50ms/χαρακτήρα)
  1,8–2,3s   μετάβαση: το πεδίο σβήνει, η μπάρα διεύθυνσης γράφεται
  2,3–3,2s   ΤΟ ΠΡΑΓΜΑΤΙΚΟ SITE εμφανίζεται (opacity 0→1, scale .98→1)
  3,2–6,5s   ελεγχόμενη κύλιση μέσα στο site, ease-in-out
  6,5–8,5s   το mobile στιγμιότυπο του ΙΔΙΟΥ site γλιστρά μέσα, δεξιά κάτω
  8,5–10,5s  κάρτα τέλους «Η επιχείρησή σου, online. €14,99 / μήνα»
  10,5–11,5s ηρεμία

ΜΕΤΑ ΤΟ ΠΡΩΤΟ ΠΛΗΡΕΣ LOOP: το demo ΣΤΑΜΑΤΑ στο πραγματικό site. Δεν
επαναλαμβάνεται συνεχώς και δεν τραβά άλλο την προσοχή.

ΑΝ Ο ΧΡΗΣΤΗΣ ΠΑΤΗΣΕΙ ΕΠΑΓΓΕΛΜΑ: το autoplay σταματά ΑΜΕΣΩΣ, εμφανίζεται το
αντίστοιχο πραγματικό site, και ο έλεγχος περνά σε αυτόν οριστικά.

`prefers-reduced-motion: reduce`: ΚΑΘΟΛΟΥ autoplay. Δείχνεται απευθείας το
πραγματικό site του κομμωτηρίου, στατικά. Καμία σκηνή, καμία κίνηση.

Χωρίς JavaScript η σελίδα πρέπει να δείχνει το πραγματικό site — το demo είναι
προσθήκη, όχι προϋπόθεση.

=== ΤΕΧΝΙΚΑ ===

Το demo με CSS + λίγο inline JS. Καμία βιβλιοθήκη, κανένα βίντεο.
Μόνο `transform` και `opacity` για την κίνηση.
Το demo ΔΕΝ επιτρέπεται να καλύπτει κείμενο ή CTA.
Καμία οριζόντια υπερχείλιση σε 1440 και 390.

Mobile 390: σειρά h1 → lede → CTA → τιμή → strip → ΜΕΓΑΛΟ preview (πλήρες
πλάτος μείον 16px). Οι τέσσερις επιλογές ως οριζόντια κυλιόμενη σειρά πάνω από
το πλαίσιο. ΚΑΜΙΑ πλωτή μπάρα πάνω από το preview. Στόχοι αφής ≥44px."""


def main() -> int:
    html = SRC.read_text(encoding="utf-8")
    m_hero = re.search(r'<section class="hero".*?</section>', html, re.S)
    m_css = re.search(r"<style>(.*?)</style>", html, re.S)
    if not (m_hero and m_css):
        raise SystemExit("δεν απομονώθηκε το hero ή το css")
    hero_now, css_now = m_hero.group(0), m_css.group(1)
    hero_css = "\n".join(l for l in css_now.splitlines()
                         if any(k in l for k in ("hero", "chip", "browser", "preview",
                                                 "badge", "trust", "lede")))
    print(f"τρέχον hero: {len(hero_now)} χαρ. · σχετικό css: {len(hero_css)} χαρ.", flush=True)

    key = _key()
    deadline = time.time() + 1800
    t0 = time.time()

    step1 = (SPEC + "\n\n=== ΤΟ ΤΡΕΧΟΝ HERO (αντικαθίσταται) ===\n" + hero_now +
             "\n\n=== ΒΗΜΑ 1 ΑΠΟ 2 ===\n"
             "Επίστρεψε το ΝΕΟ `<section class=\"hero\">…</section>` και το inline "
             "`<script>` του demo. Τίποτα άλλο από τη σελίδα.\n\n"
             'Απάντησε ΜΟΝΟ με JSON: {"hero": "…", "script": "<script>…</script>", '
             '"notes": ["…"]}')
    raw1, u1, t1 = ask(key, step1, deadline)
    print("ΒΗΜΑ 1:", json.dumps(t1, ensure_ascii=False), flush=True)
    (OUT / "v3-step1.txt").write_text(raw1, encoding="utf-8")
    d1 = as_json(raw1)
    hero_new = d1.get("hero", "")
    if "<section" not in hero_new:
        raise SystemExit("το βήμα 1 δεν επέστρεψε hero")

    step2 = (SPEC + "\n\n=== ΤΟ ΝΕΟ HERO ΣΟΥ ===\n" + hero_new +
             "\n\n=== ΤΟ ΥΠΑΡΧΟΝ CSS ΤΟΥ HERO (αντικαθίσταται) ===\n" + hero_css +
             "\n\n=== ΒΗΜΑ 2 ΑΠΟ 2 ===\n"
             "Επίστρεψε ΜΟΝΟ το CSS για το νέο hero και το demo, scoped στο `.hero`. "
             "Θα προστεθεί στο τέλος του υπάρχοντος φύλλου και πρέπει να υπερισχύει "
             "χωρίς `!important`. Συμπεριέλαβε τα breakpoints και το "
             "`prefers-reduced-motion`.\n\n"
             'Απάντησε ΜΟΝΟ με JSON: {"css": "…", "interactions": ["…"]}')
    raw2, u2, t2 = ask(key, step2, deadline)
    print("ΒΗΜΑ 2:", json.dumps(t2, ensure_ascii=False), flush=True)
    (OUT / "v3-step2.txt").write_text(raw2, encoding="utf-8")
    css_new = as_json(raw2).get("css", "")
    if not css_new.strip():
        raise SystemExit("το βήμα 2 δεν επέστρεψε css")

    out = html.replace(hero_now, hero_new + "\n" + d1.get("script", ""))
    out = out.replace("</style>", "\n/* ── HERO v3 ── */\n" + css_new + "\n</style>", 1)
    DEST.write_text(out, encoding="utf-8")

    meta = {"model": MODEL, "bytes": len(out.encode("utf-8")),
            "runtime_total": round(time.time() - t0, 1),
            "timing": {"step1": t1, "step2": t2},
            "usage": {k: u1.get(k, 0) + u2.get(k, 0)
                      for k in ("prompt_tokens", "completion_tokens")},
            "notes": d1.get("notes")}
    (OUT / "meta-v3.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False),
                                      encoding="utf-8")
    print(json.dumps({k: meta[k] for k in ("bytes", "runtime_total", "usage")},
                     ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
