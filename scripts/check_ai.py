#!/usr/bin/env python3
"""
Λέει αν το AI δουλεύει — και ΤΙ ακριβώς φταίει αν όχι.

    python scripts/check_ai.py

Τρέξ' το κάθε φορά που αλλάζεις πάροχο ή κλειδί. Χωρίς αυτό, ο μόνος τρόπος να
καταλάβεις ότι κάτι φταίει είναι να δεις τον πελάτη να παίρνει «Ο βοηθός δεν
είναι διαθέσιμος» — δηλαδή πολύ αργά.

Τίποτα εδώ δεν τυπώνει το κλειδί.
"""
from __future__ import annotations

import sys

sys.path.insert(0, ".")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src import ai, config as cfg  # noqa: E402

SETUP = {
    "deepseek": ("AI_BASE_URL=https://api.deepseek.com/v1", "AI_MODEL=deepseek-chat"),
    "openrouter": ("AI_BASE_URL=https://openrouter.ai/api/v1", "AI_MODEL=<owner>/<model>"),
}


def main() -> int:
    key = cfg.AI_API_KEY or ""
    p = ai.provider()

    print("Ρυθμίσεις")
    print(f"  πάροχος : {p or '—'}{'  (αυτόματη ανίχνευση)' if not cfg.AI_PROVIDER else ''}")
    print(f"  κλειδί  : {'—' if not key else f'{len(key)} χαρ., αρχίζει «{key[:7]}…»'}")
    print(f"  endpoint: {cfg.AI_BASE_URL or 'api.anthropic.com (προεπιλογή)'}")
    print(f"  μοντέλο : {ai.model()}\n")

    if not key:
        print("⚪ Δεν υπάρχει κλειδί — και δεν είναι σφάλμα.")
        print("   Τα κείμενα βγαίνουν από έτοιμα πρότυπα ανά επάγγελμα και το site")
        print("   δουλεύει κανονικά. Κλειδωμένα μένουν το chat-to-edit και οι AI λεζάντες.\n")
        print("   Για DeepSeek (φθηνό, OpenAI-συμβατό) βάλε στο .env:")
        print("     AI_API_KEY=sk-…")
        for line in SETUP["deepseek"]:
            print(f"     {line}")
        print("\n   Για Anthropic: σκέτο ANTHROPIC_API_KEY=sk-ant-… (χωρίς base URL)")
        return 0

    # Το πιο συχνό λάθος: κλειδί ενός παρόχου σε endpoint άλλου.
    if p == "anthropic" and not key.startswith("sk-ant-"):
        print("❌ Ασύμβατος συνδυασμός.")
        print("   Το κλειδί δεν είναι της Anthropic (τα δικά της αρχίζουν με «sk-ant-»)")
        print("   αλλά δεν έχει οριστεί AI_BASE_URL, οπότε στέλνουμε στην Anthropic.\n")
        print("   Διάλεξε ΕΝΑ:")
        print("   • Κλειδί sk-ant-… από console.anthropic.com")
        print("   • Ή κράτα το δικό σου και δήλωσε τον πάροχό του:")
        for line in SETUP["deepseek"]:
            print(f"       {line}")
        return 1

    print(f"Δοκιμάζω μία πραγματική κλήση στο {ai.model()}…\n")
    out = ai.complete("Απαντάς στα ελληνικά, πολύ σύντομα.",
                      "Πες μόνο τη λέξη: εντάξει", max_tokens=20)
    if out:
        print(f"✅ Δουλεύει — απάντησε: {out.strip()[:60]!r}")
        print("   Το chat-to-edit και οι AI λεζάντες είναι ενεργά.")
        return 0

    print("❌ Η κλήση απέτυχε. Το μήνυμα του παρόχου τυπώθηκε παραπάνω ([ai] …).")
    print("   Τα συνηθισμένα:")
    print("   • 401 → λάθος κλειδί, ή σωστό κλειδί σε λάθος endpoint")
    print("   • 404 / model not found → λάθος AI_MODEL για αυτόν τον πάροχο")
    print("   • insufficient balance → το κλειδί δουλεύει αλλά δεν έχει υπόλοιπο")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
