#!/usr/bin/env python3
"""ORIGINAL_VITRINA_THEME_BENCHMARK_2 — ΦΑΣΗ 1: ελεύθερος σχεδιασμός.

    python scripts/kimi_freehand.py --model kimi-k2.7-code

Το πρώτο benchmark απέτυχε ως πείραμα, όχι ως κώδικας: δώσαμε στο Kimi το
συμβόλαιο δεδομένων μας, τα κοινά components, τους έντεκα ρόλους χρώματος και
το λεξιλόγιο ενοτήτων μας. Βελτιστοποίησε ΜΕΣΑ στο design system μας και
παρήγαγε κάτι που έμοιαζε με τα υπάρχοντα themes μας.

Εδώ δεν βλέπει τίποτα δικό μας. Παίρνει επιχειρηματικό περιεχόμενο, κοινό,
εικόνες και απαιτήσεις ποιότητας — και τίποτε άλλο. Παράγει αυτόνομη σελίδα.
Η προσαρμογή στο Vitrina είναι ΞΕΧΩΡΙΣΤΗ φάση, ώστε να μπορούμε να δούμε τι
σχεδίασε πριν το αγγίξουμε.

Γράφει: research/kimi-freehand/raw.html — αυτούσιο, χωρίς καμία επεξεργασία.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

BASE_URL = "https://api.moonshot.ai/v1"
OUT = ROOT / "research" / "kimi-freehand"
A = "https://images.unsplash.com/"


def img(i: str, w: int = 1200) -> str:
    return f"{A}{i}?auto=format&fit=crop&w={w}&q=80"


def _key() -> str:
    for line in (ROOT / ".env").read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(r"^KIMI_API_KEY=(.*)$", line.strip())
        if m:
            return m.group(1).strip().strip('"').strip("'")
    raise SystemExit("⛔ Λείπει το KIMI_API_KEY")


SYSTEM = """You are the lead designer of a high-end web design studio in 2026.

A client has hired you. You have full creative control. You are not filling in
a template and you are not working inside anyone else's design system — you are
deciding what this website IS.

Your work is judged on whether an art director would believe it came from a
top-tier studio. Generic, safe, centred-everything layouts fail that test.

You write the HTML and the CSS yourself, in one self-contained file.

ABSOLUTE RULE ON HONESTY: use ONLY the business facts given to you. Never invent
testimonials, reviews, star ratings, patient counts, awards, certifications,
prices, guarantees or staff members. If your design idea needs data you were not
given, choose a different idea. This is not a style preference — inventing facts
about a real business is forbidden.

Return ONLY JSON:
{"html": "<!doctype html>…complete self-contained page…",
 "art_direction": "…your reasoning…",
 "signature_ideas": ["…", "…", "…"],
 "responsive_strategy": "…",
 "motion_strategy": "…"}"""


def brief() -> str:
    g = [
        (img("photo-1588776814546-1ffcf47267a5", 1000), "Ο χώρος μας", "Χαλάνδρι"),
        (img("photo-1606811841689-23dfddce3e95", 1000), "Σύγχρονος εξοπλισμός", "Τεχνολογία"),
        (img("photo-1609840114035-3c981b782dfe", 1000), "Θεραπείες", "Ανώδυνα"),
        (img("photo-1519494026892-80bbd2d6fd0d", 1000), "Υποδοχή", "Άνεση"),
        (img("photo-1629909613654-28e377c37b09", 1000), "Φροντίδα", "Εξατομικευμένη"),
        (img("photo-1598256989800-fe5f95da9787", 1000), "Χαμόγελο", "Αποτέλεσμα"),
    ]
    gal = "\n".join(f"  {i+1}. {u}\n     τίτλος: «{t}» · υπότιτλος: «{s}»"
                    for i, (u, t, s) in enumerate(g))
    return f"""=== Ο ΠΕΛΑΤΗΣ ===

Οδοντιατρείο Παπαδοπούλου — Χαλάνδρι, Αθήνα.
Οδοντίατρος. Λειτουργεί από το 2026 στην ίδια γειτονιά.

ΚΟΙΝΟ: γονείς και επαγγελματίες 30–55 ετών που διαλέγουν οδοντίατρο για όλη την
οικογένεια. Πολλοί έχουν άγχος με τον οδοντίατρο. Αποφασίζουν από το κινητό,
συχνά βράδυ. Θέλουν να νιώσουν ότι θα τους εξηγήσουν τι γίνεται και δεν θα
βρεθούν προ εκπλήξεων στο κόστος.

=== ΤΟ ΠΕΡΙΕΧΟΜΕΝΟ (μόνο αυτό υπάρχει· μη προσθέσεις άλλα «γεγονότα») ===

Επωνυμία: Οδοντιατρείο Παπαδοπούλου
Πόλη: Χαλάνδρι · Περιοχές: Χαλάνδρι · Αγ. Παρασκευή · Μαρούσι
Τηλέφωνο: 210 6000000 (tel:+302106000000) · Email: info@odontiatreio.gr
Ωράριο: Δευτ.–Παρ. 09:00–20:00

Επικεφαλίδα που θέλει ο πελάτης: «Σύγχρονη, ανώδυνη οδοντιατρική φροντίδα για
όλη την οικογένεια.»
Δεύτερη φράση: «Φροντίζουμε το χαμόγελό σου με σύγχρονα μέσα και ήρεμη
προσέγγιση.»
Κύρια ενέργεια: «Κλείσε ραντεβού»

Υπηρεσίες:
  01 Προληπτικός έλεγχος — Τακτικός έλεγχος και καθαρισμός για υγιή δόντια.
  02 Αισθητική οδοντιατρική — Λεύκανση και αποκαταστάσεις για λαμπερό χαμόγελο.
  03 Εμφυτεύματα — Σύγχρονες λύσεις για μόνιμη αποκατάσταση.
  04 Παιδοδοντία — Φιλική φροντίδα για τους μικρούς μας ασθενείς.

Κείμενο «η προσέγγισή μας» (τίτλος: «Το χαμόγελό σου, σε καλά χέρια.»):
  «Με πάνω από 15 χρόνια εμπειρία, προσφέρουμε φροντίδα με έμφαση στην πρόληψη
   και την άνεσή σου.»
  «Εξηγούμε κάθε βήμα με σαφήνεια — χωρίς άγχος, χωρίς εκπλήξεις στο κόστος.»

ΕΙΚΟΝΕΣ (χρησιμοποίησέ τις με τα URL αυτούσια):
  hero:  {img('photo-1629909613654-28e377c37b09', 1800)}
  πορτρέτο χώρου: {img('photo-1588776814546-1ffcf47267a5')}
  συλλογή:
{gal}

=== ΤΙ ΕΛΕΓΧΕΙΣ ΕΣΥ (πλήρης ελευθερία) ===

Καλλιτεχνική διεύθυνση, παλέτα, τυπογραφική ιεραρχία, σύνθεση, δομή και ΣΕΙΡΑ
ενοτήτων, ασυμμετρία, λευκός χώρος, μεταχείριση εικόνας, κάρτες ή όχι κάρτες,
πλοήγηση, συλλογή/carousel, micro-interactions, μετασχηματισμός στο κινητό,
κίνηση. Δεν υπάρχει προκαθορισμένη λίστα ενοτήτων. Αν μια συνηθισμένη ενότητα
δεν βοηθά, μη τη βάλεις.

Θέλουμε **δύο ή τρεις ξεχωριστές σχεδιαστικές ιδέες** που να θυμάται κανείς —
εσύ διαλέγεις ποιες. Παραδείγματα κατεύθυνσης, όχι εντολές: οριζόντια
αφηγηματική συλλογή, editorial τυπογραφία σε μεγάλη κλίμακα, στρωματωμένες
εικόνες, αποκαλύψεις στην κύλιση, sticky στοιχεία, ασυνήθιστο πλέγμα.

=== ΤΕΧΝΙΚΕΣ ΑΠΑΙΤΗΣΕΙΣ ===

Ένα αυτοτελές αρχείο HTML με ενσωματωμένο <style>. Χωρίς εξωτερικές
βιβλιοθήκες, χωρίς frameworks, χωρίς build. Google Fonts επιτρέπονται με <link>.

JavaScript: προτίμησε CSS. Αν κάτι το χρειάζεται πραγματικά, γράψε λίγες γραμμές
inline — αλλά η σελίδα πρέπει να είναι πλήρως λειτουργική και ΧΩΡΙΣ αυτό.

Responsive: desktop, tablet και κινητό ως ΤΡΕΙΣ σκόπιμες συνθέσεις. Στα 390px
η σελίδα πρέπει να είναι εντυπωσιακή από μόνη της, όχι σμίκρυνση. Καμία
οριζόντια κύλιση. Στόχοι αφής ≥44px.

Προσβασιμότητα: σημασιολογικό HTML, ένα <h1>, αντίθεση κειμένου τουλάχιστον
4.5:1, ορατό focus, alt σε κάθε εικόνα, και υποχρεωτικά
`@media (prefers-reduced-motion: reduce)` που μηδενίζει την κίνηση.

Γλώσσα: ελληνικά. `<html lang="el">`."""


def ask(key: str, model: str, user: str, max_tokens: int = 32000) -> tuple[str, dict]:
    body = json.dumps({
        "model": model, "temperature": 1, "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": user}],
    }).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}/chat/completions", data=body,
                                 headers={"Authorization": f"Bearer {key}",
                                          "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=900) as r:
                data = json.load(r)
            return data["choices"][0]["message"]["content"], data.get("usage", {})
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:300]
            if exc.code < 500:
                raise SystemExit(f"⛔ HTTP {exc.code}: {detail}")
            time.sleep(2 ** attempt)
        except (urllib.error.URLError, TimeoutError, KeyError):
            time.sleep(2 ** attempt)
    raise SystemExit("⛔ Το Kimi δεν απάντησε")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="kimi-k2.7-code")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    raw, usage = ask(_key(), args.model, brief())
    (OUT / "response.json").write_text(raw, encoding="utf-8")
    data = json.loads(raw)
    html = data.get("html", "")
    if "<html" not in html.lower():
        raise SystemExit("⛔ Δεν επιστράφηκε πλήρης σελίδα")
    (OUT / "raw.html").write_text(html, encoding="utf-8")

    meta = {k: data.get(k) for k in
            ("art_direction", "signature_ideas", "responsive_strategy", "motion_strategy")}
    meta["usage"] = usage
    meta["model"] = args.model
    meta["bytes"] = len(html.encode("utf-8"))
    (OUT / "design.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False),
                                     encoding="utf-8")
    print(json.dumps({"bytes": meta["bytes"], "usage": usage,
                      "ideas": meta["signature_ideas"]}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
