"""
Έτοιμα posts για τον πελάτη — χωρίς να χρειάζεται έγκριση από τη Meta.

Ο πελάτης ανοίγει το dashboard, βλέπει την εβδομάδα του έτοιμη, αντιγράφει και
δημοσιεύει. Η αυτόματη δημοσίευση (Meta App Review) είναι ξεχωριστό βήμα που
αργεί εβδομάδες· αυτό δίνει την αξία από σήμερα.

Ίδιο μοτίβο με το site_copy: ντετερμινιστικά πρότυπα ανά επάγγελμα που δουλεύουν
πάντα, και προαιρετικό «γυάλισμα» από AI αν υπάρχει κλειδί.
"""
from __future__ import annotations

import json
import random
from typing import Any

from . import ai

# Γωνίες που δουλεύουν για τοπικές επιχειρήσεις. Κάθε μία απαντά σε διαφορετικό
# λόγο που κάποιος επιλέγει μαγαζί: απόδειξη, πρόσωπο, χρησιμότητα, πρόσκληση.
_ANGLES = [
    ("Η δουλειά μας", "Δείξε ΜΙΑ πρόσφατη δουλειά. Φωτογραφία πριν/μετά αν γίνεται."),
    ("Ποιοι είμαστε", "Μια φωτογραφία σου στη δουλειά + δύο κουβέντες γιατί το κάνεις."),
    ("Συμβουλή", "Μια πρακτική συμβουλή που μπορεί να εφαρμόσει σήμερα ο πελάτης."),
    ("Ερώτηση πελάτη", "Μια ερώτηση που σου κάνουν συχνά, με την απάντησή σου."),
    ("Πίσω από τις σκηνές", "Κάτι από την καθημερινότητα — υλικά, εργαλεία, προετοιμασία."),
    ("Πρόσκληση", "Ξεκάθαρο κάλεσμα: τηλέφωνο, ωράριο, πού θα σε βρουν."),
    ("Ευχαριστώ", "Ευχαριστίες σε πελάτη ή στη γειτονιά — κρατάει τη σχέση ζεστή."),
]

# Ιδέες ανά επάγγελμα (κλειδιά ίδια με το _vertical του premium_generator).
_IDEAS: dict[str, list[str]] = {
    "food": ["Το πιάτο της ημέρας", "Πώς φτιάχνουμε τη σπεσιαλιτέ μας",
             "Τα φρέσκα υλικά της εβδομάδας", "Το τραπέζι σας περιμένει"],
    "cafe": ["Ο καφές της ημέρας", "Τα γλυκά βγήκαν από τον φούρνο",
             "Η γωνιά μας το πρωί", "Τι πίνουν οι τακτικοί μας"],
    "beauty": ["Πριν & μετά", "Το look της εβδομάδας", "Πώς κρατάς το χρώμα",
               "Τα προϊόντα που εμπιστευόμαστε"],
    "trade": ["Η δουλειά της εβδομάδας", "Πώς καταλαβαίνεις ότι θες υδραυλικό",
              "Τι κάνεις μέχρι να έρθουμε", "Δωρεάν εκτίμηση"],
    "wood": ["Η κατασκευή της εβδομάδας", "Από το σχέδιο στο έπιπλο",
             "Ποιο ξύλο για ποια χρήση", "Μέτρημα χώρου"],
    "medical": ["Η συμβουλή πρόληψης", "Τι να περιμένεις στο ραντεβού",
                "Ο χώρος μας", "Πότε πρέπει να έρθεις"],
    "professional": ["Τι πρέπει να ξέρεις πριν υπογράψεις", "Συχνή ερώτηση",
                     "Προθεσμίες που δεν πρέπει να χάσεις", "Πρώτη συνάντηση"],
    "gym": ["Η άσκηση της εβδομάδας", "Πρόοδος μέλους", "Λάθος που κάνουν οι περισσότεροι",
            "Δωρεάν δοκιμαστικό"],
    "garage": ["Το πρόβλημα της εβδομάδας", "Πότε θέλει service", "Τι σημαίνει αυτό το λαμπάκι",
               "Έλεγχος πριν το ταξίδι"],
    "rooms": ["Η θέα σήμερα", "Τι να δεις στην περιοχή", "Το πρωινό μας",
              "Διαθεσιμότητα"],
    "farm": ["Από το χωράφι", "Πώς παράγεται", "Η διαφορά στη γεύση", "Παραγγελίες"],
}

_SYSTEM = (
    "Είσαι Έλληνας social media copywriter για μικρές τοπικές επιχειρήσεις. "
    "Γράφεις σύντομα, ζεστά, ανθρώπινα ελληνικά — όπως θα μιλούσε ο ίδιος ο "
    "ιδιοκτήτης. ΟΧΙ εταιρικά κλισέ, ΟΧΙ υπερβολές, ΟΧΙ αγγλισμοί. "
    "Επιστρέφεις ΜΟΝΟ έγκυρο JSON."
)


def _fallback_caption(idea: str, hint: str, d: dict[str, Any]) -> str:
    name, city = d.get("NAME", ""), d.get("CITY", "")
    phone = d.get("PHONE", "")
    return (f"{idea}\n\n{hint}\n\n📍 {city}" + (f"  ·  📞 {phone}" if phone else "")
            + f"\n\n— {name}")


def _hashtags(d: dict[str, Any]) -> list[str]:
    city = str(d.get("CITY", "")).replace(" ", "")
    trade = str(d.get("TRADE", "")).split()[0] if d.get("TRADE") else ""
    tags = [t for t in (city, trade, f"{trade}{city}") if t]
    return ["#" + t for t in tags][:3]


# Ποιο post αξίζει να πληρώσει ο πελάτης για προβολή. Κρατάμε τα ποσά μικρά και
# την ακτίνα τοπική: μια ταβέρνα δεν κερδίζει τίποτα διαφημιζόμενη σε άλλη πόλη.
_BOOST = {
    "Η δουλειά μας": ("8-10€", "3-5 χλμ γύρω από το μαγαζί", "Δείχνει απόδειξη — το πιο πειστικό"),
    "Πρόσκληση": ("10-15€", "5 χλμ · ηλικίες 25-60", "Ξεκάθαρο κάλεσμα, φέρνει τηλέφωνα"),
}


def week_plan(data: dict[str, Any], vertical: str = "trade") -> list[dict[str, Any]]:
    """Επτά posts — ένα ανά ημέρα. Δουλεύει πάντα, ακόμα και χωρίς AI."""
    ideas = _IDEAS.get(vertical, _IDEAS["trade"])
    rnd = random.Random(f"{data.get('NAME')}-{vertical}")   # σταθερό ανά πελάτη
    city = data.get("CITY", "")
    plan = []
    for i, (angle, hint) in enumerate(_ANGLES):
        idea = ideas[i % len(ideas)] if i < len(ideas) else rnd.choice(ideas)
        post = {
            "day": ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο", "Κυριακή"][i],
            "angle": angle,
            "idea": idea,
            "photo_hint": hint,
            "caption": _fallback_caption(idea, hint, data),
            "hashtags": _hashtags(data),
        }
        if angle in _BOOST:
            amount, audience, why = _BOOST[angle]
            post["boost"] = {
                "amount": amount,
                "audience": audience.replace("το μαγαζί", f"το μαγαζί ({city})") if city else audience,
                "why": why,
                "how": "Πάτα «Ενίσχυση δημοσίευσης» κάτω από το post στο Facebook.",
            }
        plan.append(post)
    return plan


def enrich_with_ai(plan: list[dict[str, Any]], data: dict[str, Any]) -> list[dict[str, Any]]:
    """Ξαναγράφει τις λεζάντες με AI. Σε οποιοδήποτε σφάλμα κρατάει τις αρχικές."""
    if not ai.available():
        return plan

    brief = {"name": data.get("NAME"), "trade": data.get("TRADE"), "city": data.get("CITY"),
             "phone": data.get("PHONE"), "tagline": data.get("TAGLINE")}
    asks = [{"day": p["day"], "angle": p["angle"], "idea": p["idea"]} for p in plan]
    user = (
        f"Επιχείρηση: {json.dumps(brief, ensure_ascii=False)}\n\n"
        f"Γράψε μία λεζάντα για κάθε post (2-4 προτάσεις, πρώτο πρόσωπο, να μπορεί "
        f"να τη δημοσιεύσει ως έχει). Μην επαναλαμβάνεις το όνομα σε κάθε post.\n"
        f"{json.dumps(asks, ensure_ascii=False, indent=1)}\n\n"
        f'Επίστρεψε ΜΟΝΟ JSON: {{"captions": ["...", ... 7 συνολικά]}}'
    )
    out = ai.complete_json(_SYSTEM, user, max_tokens=2000)
    caps = (out or {}).get("captions", [])
    if not caps:
        return plan     # κρατάμε τις έτοιμες λεζάντες — ο πελάτης δεν μένει με άδειο

    for p, cap in zip(plan, caps):
        if isinstance(cap, str) and cap.strip():
            p["caption"] = cap.strip()
    return plan
