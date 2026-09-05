#!/usr/bin/env python3
"""Δεύτερο πέρασμα στην ΥΠΑΡΧΟΥΣΑ αρχική — στοχευμένη βελτίωση, όχι redesign.

    python scripts/kimi_refine.py

Το μοντέλο παίρνει το τρέχον HTML και CSS και τα ΕΠΕΞΕΡΓΑΖΕΤΑΙ σύμφωνα με
εγκεκριμένο σχέδιο ανά ενότητα. Δεν παράγει νέα σελίδα, δεν αλλάζει concept,
παλέτα, σειρά ενοτήτων ή το interaction των τεσσάρων επαγγελμάτων.
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
SRC = OUT / "homepage.html"
DEST = OUT / "homepage-v2.html"
BASE_URL = "https://api.moonshot.ai/v1"
MODEL = "kimi-k3"
REASONING_EFFORT = "high"
FENCE = re.compile(r"^```[a-z]*\n?|```$", re.M)

SYSTEM = """Είσαι senior front-end designer. Κάνεις ΣΤΟΧΕΥΜΕΝΗ ΒΕΛΤΙΩΣΗ σε
υπάρχουσα σελίδα, με βάση εγκεκριμένο σχέδιο ανά ενότητα.

ΔΕΝ σχεδιάζεις ξανά. ΔΕΝ αλλάζεις concept, βασική παλέτα, σειρά ενοτήτων ή το
interaction των τεσσάρων επαγγελμάτων. Ό,τι δεν αναφέρει το σχέδιο μένει ως έχει.

Δουλεύεις σαν designer που ανοίγει υπάρχον αρχείο και το βελτιώνει — όχι σαν
κάποιος που ξεκινά από λευκή σελίδα.

ΑΠΑΡΑΒΑΤΟ ΟΡΙΟ ΑΛΗΘΕΙΑΣ: μόνο τα γεγονότα που ήδη υπάρχουν στη σελίδα ή δίνονται
ρητά. Καμία επινοημένη κριτική, βαθμολογία, αριθμός πελατών, ποσοστό, βραβείο ή
σύγκριση τιμών. Καμία υπόσχεση λειτουργίας που δεν υπάρχει."""


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
        # 429 = προσωρινή υπερφόρτωση· η υπηρεσία λέει «ξαναδοκίμασε». Διαφέρει
        # από απόρριψη παραμέτρου, όπου καμία επανάληψη δεν βοηθά.
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


PLAN = """=== ΕΓΚΕΚΡΙΜΕΝΟ ΣΧΕΔΙΟ ΒΕΛΤΙΩΣΗΣ ===

Μετρήθηκε στην τρέχουσα σελίδα: hero 835px / πυκνότητα 0.42 · examples 908px /
0.26 · scope 507px / 0.74 · steps 412px / 0.66 · pricing 611px / 0.46 ·
final-cta 631px / 0.20. Το preview πιάνει 43% του πλάτους, οι κάρτες 39%. Όλες
οι ενότητες έχουν σχεδόν ίδιο padding 96/96 — ομοιόμορφος, νεκρός ρυθμός.

1. HERO
   Το μάτι πρέπει να πάει ΠΡΩΤΑ στο αποτέλεσμα.
   · preview: από 43% σε **55–60%** του πλάτους (≈800–860px στα 1440)
   · η στήλη κειμένου συρρικνώνεται σε ≈340px ώστε να μην ανταγωνίζεται
   · ΝΕΟ κείμενο, ακριβώς αυτό:
       h1:    «Το site της επιχείρησής σου, χωρίς να ασχολείσαι με το site.»
       lede:  «Εσύ μας λες τι κάνεις. Εμείς αναλαμβάνουμε κατασκευή,
               φιλοξενία, Local SEO και αλλαγές.»
     Το «Η επιχείρησή σου αξίζει καλύτερη βιτρίνα.» ΜΕΝΕΙ, αλλά ως ΜΙΚΡΟ brand
     statement (eyebrow πάνω από τον τίτλο), όχι πρωταγωνιστής.
   · κάτω από τα CTA: «€14,99/μήνα · πρώτος μήνας δωρεάν»
     ΑΚΡΙΒΩΣ έτσι — ΟΧΙ «από €14,99». Υπάρχει μία τιμή.
   · από κάτω ΜΟΝΟ ένα λεπτό trust strip σε μία γραμμή, με λεπτούς διαχωριστές:
       «Κατασκευή · Hosting · Local SEO · Αλλαγές»
     Τέσσερις λέξεις. Κανένα κουτάκι, κανένα εικονίδιο.
   · padding-bottom 104 → 72

2. TO INTERACTION ΤΩΝ ΤΕΣΣΑΡΩΝ ΕΠΑΓΓΕΛΜΑΤΩΝ — ΜΕΝΕΙ, ΑΝΑΒΑΘΜΙΖΕΤΑΙ
   Είναι το καλύτερο στοιχείο της σελίδας. ΜΗΝ το αλλάξεις δομικά.
   Αναβάθμισε ΜΟΝΟ τη μετάβαση, από απλή εναλλαγή εικόνας σε:
   · εξερχόμενη: fade-out 160ms + slide 12px
   · εισερχόμενη: fade-in 220ms + slide, ease-out
   · αλλάζει ΚΑΙ το κείμενο στη μπάρα διεύθυνσης του browser frame ανά επάγγελμα
   · ενεργό chip: μετάβαση χρώματος 120ms

3. EXAMPLES — αίσθηση portfolio, όχι σειρά από screenshots
   · ενεργή κάρτα ≈70–75% του διαθέσιμου πλάτους· η επόμενη ορατή ≈20%, κομμένη
     από την άκρη του δοχείου
   · οι κάρτες αποκτούν το ΙΔΙΟ browser chrome με το hero
   · βάθος: ανενεργές scale 0.92, opacity 0.7, μετατόπιση −24px ώστε να χώνονται
     πίσω από την ενεργή· η ενεργή παίρνει υπερυψωμένη σκιά
   · scroll-snap track, τα υπάρχοντα βέλη μένουν
   · ύψος 908 → ≈760px

4. ΤΙ ΑΝΑΛΑΜΒΑΝΟΥΜΕ — οπτική εξήγηση αντί για τρεις επίπεδες γραμμές
   Πέτα την τωρινή μορφή. Τρία ΤΕΚΜΗΡΙΑ που ΔΕΙΧΝΟΥΝ αντί να περιγράφουν:
   · Φιλοξενία → μίνι browser frame με πράσινη τελεία και «getvitrina.gr»,
     με τη φράση «online, χωρίς να κάνεις τίποτα»
   · Local SEO → στυλιζαρισμένη σειρά αποτελέσματος αναζήτησης με ΑΛΗΘΙΝΟ
     κείμενο: «Ταβέρνα Ο Λεωνίδας · Λαδάδικα, Θεσσαλονίκη».
     ΑΠΑΓΟΡΕΥΕΤΑΙ βαθμολογία, αστέρια, θέση κατάταξης ή αριθμός επισκεπτών.
   · Απεριόριστες αλλαγές → ανταλλαγή δύο μηνυμάτων:
     «Άλλαξε το ωράριο σε 12:00–01:00» → «Έγινε.»
   Διάταξη ασύμμετρη σε δύο στήλες: αριστερά τίτλος και μία γραμμή, δεξιά τα
   τρία τεκμήρια με λεπτούς διαχωριστές. ΟΧΙ πλέγμα τριών ίσων καρτών.
   · ύψος ≈560px

5. ΠΩΣ ΛΕΙΤΟΥΡΓΕΙ — μία συνεχής διαδρομή
   · μία οριζόντια γραμμή με τρεις κόμβους:
     «Μας λες» → «Εμείς φτιάχνουμε» → «Μένουμε μαζί σου»
   · μία σύντομη πρόταση ανά κόμβο, όχι παράγραφος
   · ΙΔΙΟ φόντο με την ενότητα 4, ώστε να διαβάζεται ως συνέχεια και όχι ως
     απομονωμένη ενότητα
   · ύψος 412 → ≈260px

6. PRICING — δυνατότερη στιγμή μετατροπής
   · τα €14,99 μένουν μεγάλα
   · προστίθεται ΤΙ ΑΝΤΙΚΑΘΙΣΤΑ η συνδρομή, με τίτλο «Όλα αυτά, σε μία συνδρομή»:
     Κατασκευή site · Φιλοξενία · Local SEO · Αλλαγές & συντήρηση
   · ΑΠΑΓΟΡΕΥΕΤΑΙ «θα σου κόστιζε €Χ ξεχωριστά» — δεν υπάρχει επαληθευμένο νούμερο
   · μένουν: πρώτος μήνας δωρεάν, ακύρωση όποτε θέλεις, .gr domain €24/έτος
   · ύψος 611 → ≈520px

7. FINAL CTA — ξανά συνδεδεμένο με το προϊόν
   Είναι η πιο άδεια ενότητα: 129 χαρακτήρες σε 631px.
   · αντί για μεγάλο χρωματιστό ορθογώνιο: τρία ΜΙΚΡΑ browser frames με αληθινά
     site να υποχωρούν πίσω (scale/opacity), και το κείμενο σε ανοιχτό πάνελ
     μπροστά
   · ύψος → ≈420px

8. ΡΥΘΜΟΣ — σπάσε το ομοιόμορφο 96/96
   hero 88/72 · examples 80/88 · scope 72/64 · steps 48/72 · pricing 80/80 ·
   final 72/88. Κάθε viewport μετά το hero να έχει κάτι που αξίζει να κοιτάξεις.

9. ΤΟΝΟΙ — το indigo παραμένει primary
   Δύο διακριτικοί υποστηρικτικοί, ΜΟΝΟ εκεί που βοηθούν:
   · teal #0E9E8F στο τεκμήριο «online»
   · ζεστή άμμος #F6F1E9 ως φόντο στη ζώνη των ενοτήτων 4+5
   Η σελίδα να μην είναι μόνο λευκό και μωβ.

10. MICRO-INTERACTIONS ΚΑΙ ΚΙΝΗΣΗ — συγκρατημένα
    · κάρτες: ανύψωση 4px και αλλαγή σκιάς στο hover
    · αποκαλύψεις ενοτήτων: opacity + 10px μετατόπιση, κλιμακωτά 60ms,
      με IntersectionObserver
    · όλα ανενεργά σε `prefers-reduced-motion`
    Καμία κίνηση για εντυπωσιασμό.

11. MOBILE 390
    · το preview ΠΑΡΑΜΕΝΕΙ μεγάλο: πλήρες πλάτος μείον 16px
    · ΑΦΑΙΡΕΣΕ κάθε πλωτή μπάρα τιμής ή CTA που καλύπτει το preview — γίνεται
      στατικό μπλοκ ΚΑΤΩ από αυτό
    · παραδείγματα: swipe, ενεργή ≈88vw, επόμενη να ξεμυτίζει ≈8%
    · καμία σταθερή μπάρα δεν επιτρέπεται να καλύπτει preview
    · στόχοι αφής ≥44px

=== ΤΙ ΔΕΝ ΑΛΛΑΖΕΙ ===

Το concept, η βασική παλέτα (warm white / indigo #4F39F6 / μελάνι #14141A), η
τυπογραφία Manrope, η σειρά των ενοτήτων, τα ονόματα των κλάσεων όπου δεν
χρειάζεται, οι σύνδεσμοι, τα πραγματικά στιγμιότυπα στο `shots/`, οι νομικές
σελίδες στο footer, και το interaction των τεσσάρων επαγγελμάτων."""


def main() -> int:
    html = SRC.read_text(encoding="utf-8")
    m_style = re.search(r"<style>(.*?)</style>", html, re.S)
    m_body = re.search(r"<body>(.*?)</body>", html, re.S)
    if not (m_style and m_body):
        raise SystemExit("δεν απομονώθηκαν <style> και <body> από το υπάρχον αρχείο")
    css_now, body_now = m_style.group(1).strip(), m_body.group(1).strip()
    head_extra = re.search(r'(<link[^>]*fonts[^>]*>)', html)
    print(f"τρέχον: body {len(body_now)} χαρ. · css {len(css_now)} χαρ.", flush=True)

    key = _key()
    deadline = time.time() + 1800
    t0 = time.time()

    step1 = (PLAN + "\n\n=== ΤΟ ΤΡΕΧΟΝ BODY ===\n" + body_now +
             "\n\n=== ΒΗΜΑ 1 ΑΠΟ 2 ===\n"
             "Επίστρεψε το ΑΝΑΘΕΩΡΗΜΕΝΟ body. Κράτα ό,τι δεν αγγίζει το σχέδιο "
             "ακριβώς όπως είναι, μαζί με τα ονόματα κλάσεων. Πρόσθεσε νέες κλάσεις "
             "μόνο για τα νέα στοιχεία.\n\n"
             'Απάντησε ΜΟΝΟ με JSON: {"body": "…", "changes": ["…"]}')
    raw1, u1, t1 = ask(key, step1, deadline)
    print("ΒΗΜΑ 1:", json.dumps(t1, ensure_ascii=False), flush=True)
    (OUT / "v2-step1.txt").write_text(raw1, encoding="utf-8")
    d1 = as_json(raw1)
    body_new = d1.get("body", "")
    if "<" not in body_new:
        raise SystemExit("το βήμα 1 δεν επέστρεψε body")

    step2 = (PLAN + "\n\n=== ΤΟ ΤΡΕΧΟΝ CSS ===\n" + css_now +
             "\n\n=== ΤΟ ΑΝΑΘΕΩΡΗΜΕΝΟ BODY ===\n" + body_new +
             "\n\n=== ΒΗΜΑ 2 ΑΠΟ 2 ===\n"
             "Επίστρεψε το ΑΝΑΘΕΩΡΗΜΕΝΟ, ΠΛΗΡΕΣ css. Ξεκίνα από το τρέχον και "
             "άλλαξε ό,τι ζητά το σχέδιο: μεγέθη hero, portfolio examples, τα τρία "
             "τεκμήρια, η διαδρομή, το pricing, το final CTA, ο ρυθμός padding, οι "
             "υποστηρικτικοί τόνοι, οι μεταβάσεις, το mobile.\n\n"
             'Απάντησε ΜΟΝΟ με JSON: {"css": "…", "notes": ["…"]}')
    raw2, u2, t2 = ask(key, step2, deadline)
    print("ΒΗΜΑ 2:", json.dumps(t2, ensure_ascii=False), flush=True)
    (OUT / "v2-step2.txt").write_text(raw2, encoding="utf-8")
    css_new = as_json(raw2).get("css", "")
    if not css_new.strip():
        raise SystemExit("το βήμα 2 δεν επέστρεψε css")

    title = re.search(r"<title>(.*?)</title>", html, re.S)
    out_html = ("<!doctype html>\n<html lang=\"el\">\n<head>\n<meta charset=\"utf-8\">\n"
                "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
                f"<title>{title.group(1) if title else 'Vitrina'}</title>\n"
                f"{head_extra.group(1) if head_extra else ''}\n"
                f"<style>\n{css_new}\n</style>\n</head>\n<body>\n{body_new}\n</body>\n</html>\n")
    DEST.write_text(out_html, encoding="utf-8")

    meta = {"model": MODEL, "reasoning_effort": REASONING_EFFORT,
            "bytes": len(out_html.encode("utf-8")),
            "runtime_total": round(time.time() - t0, 1),
            "timing": {"step1": t1, "step2": t2},
            "usage": {k: u1.get(k, 0) + u2.get(k, 0)
                      for k in ("prompt_tokens", "completion_tokens")},
            "changes": d1.get("changes")}
    (OUT / "meta-v2.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False),
                                      encoding="utf-8")
    print(json.dumps({k: meta[k] for k in ("bytes", "runtime_total", "usage")},
                     ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
