#!/usr/bin/env python3
"""
Λέει αν το AI κλειδί δουλεύει — και ΤΙ ακριβώς φταίει αν όχι.

    python scripts/check_ai.py

Τρέξ' το κάθε φορά που αλλάζεις το ANTHROPIC_API_KEY. Χωρίς αυτό ο μόνος
τρόπος να καταλάβεις ότι κάτι φταίει είναι να δεις τον πελάτη να παίρνει
«Ο βοηθός δεν είναι διαθέσιμος» — δηλαδή πολύ αργά.

Τίποτα εδώ δεν τυπώνει το κλειδί.
"""
from __future__ import annotations

import sys

sys.path.insert(0, ".")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src import config as cfg  # noqa: E402


def main() -> int:
    key = cfg.ANTHROPIC_API_KEY or ""
    base = cfg.ANTHROPIC_BASE_URL or ""
    model = cfg.MODEL_CHEAP

    print("Ρυθμίσεις")
    print(f"  κλειδί  : {'—' if not key else f'{len(key)} χαρ., αρχίζει «{key[:7]}…»'}")
    print(f"  endpoint: {base or 'api.anthropic.com (προεπιλογή)'}")
    print(f"  μοντέλο : {model}\n")

    if not key:
        print("⚪ Δεν υπάρχει κλειδί.")
        print("   Δεν είναι σφάλμα: τα κείμενα βγαίνουν από έτοιμα πρότυπα ανά")
        print("   επάγγελμα. Κλειδωμένα μένουν το chat-to-edit και τα AI κείμενα.")
        return 0

    # Το πιο συχνό λάθος: κλειδί άλλου provider σε endpoint της Anthropic.
    if not key.startswith("sk-ant-") and not base:
        print("❌ Ασύμβατος συνδυασμός.")
        print("   Το κλειδί δεν είναι της Anthropic (τα δικά της αρχίζουν με «sk-ant-»)")
        print("   αλλά το ANTHROPIC_BASE_URL είναι κενό, οπότε στέλνουμε στην Anthropic.")
        print("\n   Διάλεξε ΕΝΑ:")
        print("   • Κλειδί sk-ant-… από console.anthropic.com → Settings → API Keys")
        print("   • Ή κράτα το δικό σου και βάλε ΚΑΙ ANTHROPIC_BASE_URL ΚΑΙ")
        print("     ANTHROPIC_MODEL (το ακριβές όνομα του deployment σου)")
        return 1

    try:
        import anthropic
    except ImportError:
        print("❌ Λείπει η βιβλιοθήκη: pip install anthropic")
        return 1

    kw = {"api_key": key}
    if base:
        kw["base_url"] = base
    try:
        r = anthropic.Anthropic(**kw).messages.create(
            model=model, max_tokens=20,
            messages=[{"role": "user", "content": "Πες μόνο: εντάξει"}])
        print(f"✅ Δουλεύει — απάντησε: {r.content[0].text.strip()!r}")
        print("   Το chat-to-edit και τα AI κείμενα είναι ενεργά.")
        return 0
    except Exception as e:  # noqa: BLE001
        name, msg = type(e).__name__, str(e)
        print(f"❌ {name}")
        low = msg.lower()
        if "authentication" in low or "401" in low or "invalid x-api" in low:
            print("   Το κλειδί απορρίφθηκε. Λάθος κλειδί ή λάθος endpoint.")
        elif "deploymentnotfound" in low or "404" in low:
            print(f"   Το endpoint απάντησε αλλά δεν έχει το μοντέλο «{model}».")
            print("   Σε Azure Foundry: φτιάξε deployment και βάλε το ΟΝΟΜΑ ΤΟΥ")
            print("   DEPLOYMENT στο ANTHROPIC_MODEL (όχι το όνομα του μοντέλου).")
        elif "connection" in low:
            print("   Δεν απάντησε το endpoint — τσέκαρε το ANTHROPIC_BASE_URL.")
        elif "credit" in low or "quota" in low or "429" in low:
            print("   Το κλειδί είναι έγκυρο αλλά δεν έχει υπόλοιπο/όριο.")
        print(f"\n   {msg[:220]}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
