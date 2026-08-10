"""
Environment Manager — η μοναδική πηγή αλήθειας για το «πού τρέχω τώρα».

Κάθε script, agent και test ρωτάει ΑΥΤΟ. Ποτέ απευθείας το os.environ.

    from src import env
    env.require("staging")          # σταματά αν δεν είμαστε σε staging
    url, key = env.supabase()       # τα credentials ΤΟΥ τρέχοντος περιβάλλοντος

Δύο ανεξάρτητα επίπεδα ασφάλειας, επίτηδες:

  1. Λογικό     — `VITRINA_ENV` και `require()`. Default `production`, ώστε ένα
                  ξεχασμένο flag να ΜΠΛΟΚΑΡΕΙ τις καταστροφικές ενέργειες, όχι
                  να τις επιτρέψει.
  2. Credentials — τα κλειδιά κάθε περιβάλλοντος έχουν ΔΙΑΦΟΡΕΤΙΚΑ ονόματα
                  (`SUPABASE_URL_STAGING` / `SUPABASE_URL_PRODUCTION`). Το τοπικό
                  `.env` δεν περιέχει καθόλου production κλειδιά, οπότε ακόμα κι
                  αν το flag είναι λάθος, η σύνδεση στην παραγωγή είναι
                  ΑΔΥΝΑΤΗ — όχι απλώς απαγορευμένη.

Το δεύτερο επίπεδο είναι που μετράει: τα λογικά guards τα παρακάμπτει ένα λάθος
`export`. Τα credentials που δεν υπάρχουν στο μηχάνημα, όχι.
"""
from __future__ import annotations

import os
import sys

DEV = "dev"
STAGING = "staging"
PRODUCTION = "production"
ALL = (DEV, STAGING, PRODUCTION)

# Fail-closed: χωρίς ρητή δήλωση θεωρούμε παραγωγή, άρα «μην αγγίξεις τίποτα».
current = os.environ.get("VITRINA_ENV", PRODUCTION).strip().lower()
if current not in ALL:
    sys.exit(f"⛔ Άγνωστο VITRINA_ENV={current!r}. Επιτρεπτά: {', '.join(ALL)}")

# Το dev ΔΕΝ έχει δική του βάση: δείχνει στη staging. Έτσι μια δοκιμή τοπικά
# δεν μπορεί να γράψει σε αληθινό πελάτη ακόμα κι αν όλα τα άλλα πάνε στραβά.
_DB_ENV = {DEV: STAGING, STAGING: STAGING, PRODUCTION: PRODUCTION}[current]

is_production = current == PRODUCTION
is_staging = current == STAGING
is_dev = current == DEV

# Καταστροφικές ενέργειες (delete, reset, seed) — ποτέ στην παραγωγή.
destructive_ok = current in (DEV, STAGING)


def _pick(base: str, *, required: bool = True) -> str:
    """Κλειδί ανά περιβάλλον: `X_STAGING` / `X_PRODUCTION`, με fallback στο σκέτο `X`.

    Το fallback υπάρχει ΜΟΝΟ για την παραγωγή, όπου το Railway έχει ήδη τις
    παλιές μεταβλητές. Στο staging απαιτούμε ρητό `_STAGING` όνομα ώστε να μη
    συνδεθεί ποτέ κατά λάθος στην παραγωγή μέσω κληρονομημένης μεταβλητής.
    """
    suffix = _DB_ENV.upper()
    value = os.environ.get(f"{base}_{suffix}", "").strip()
    if not value and _DB_ENV == PRODUCTION:
        value = os.environ.get(base, "").strip()
    if not value and required:
        hint = (f"Λείπει το {base}_{suffix}." if _DB_ENV == STAGING else
                f"Λείπει το {base}_{suffix} (ή το {base}).")
        sys.exit(
            f"⛔ {hint}\n"
            f"   Τρέχεις σε VITRINA_ENV={current} → βάση: {_DB_ENV}.\n"
            f"   Αν δουλεύεις τοπικά, βάλε τα *_STAGING κλειδιά στο .env.\n"
            f"   Τα production κλειδιά ΔΕΝ πρέπει να υπάρχουν τοπικά."
        )
    return value


def supabase(required: bool = False) -> tuple[str, str]:
    """(url, service_key) του τρέχοντος περιβάλλοντος.

    `required=False` στο import του config ώστε η εφαρμογή να σηκώνεται και χωρίς
    βάση (tests, CI). Το σφάλμα έρχεται τη στιγμή της χρήσης, από το db._client().
    """
    return _pick("SUPABASE_URL", required=required), _pick("SUPABASE_KEY", required=required)


def stripe_mode() -> str:
    """Η παραγωγή είναι live· όλα τα άλλα test. Δεν διαπραγματεύεται."""
    return "live" if is_production else "test"


def require(*allowed: str) -> None:
    """Σταματά το script αν τρέχει σε λάθος περιβάλλον.

    Χρησιμοποίησέ το ΠΡΙΝ από οτιδήποτε γράφει ή σβήνει."""
    if current not in allowed:
        sys.exit(
            f"⛔ Τρέχει σε VITRINA_ENV={current}. Επιτρέπεται μόνο σε: {', '.join(allowed)}.\n"
            f"   Αν το εννοείς:  VITRINA_ENV={allowed[0]} python {' '.join(sys.argv)}"
        )


def require_destructive(confirm_flag: bool, flag_name: str = "--confirm-staging") -> None:
    """Διπλό guard για ό,τι σβήνει δεδομένα.

    Δεν αρκεί το σωστό περιβάλλον: χρειάζεται ΚΑΙ ρητή σημαία στη γραμμή εντολών.
    Έτσι ένα script που τρέχει κατά λάθος (cron, tab-complete, ιστορικό shell)
    δεν σβήνει τίποτα σιωπηλά.
    """
    require(STAGING)
    if not confirm_flag:
        sys.exit(
            f"⛔ Καταστροφική ενέργεια χωρίς επιβεβαίωση.\n"
            f"   Πρόσθεσε {flag_name} αν το εννοείς."
        )


def banner() -> str:
    """Μία γραμμή για την κορυφή κάθε script/report — να φαίνεται πάντα πού είμαστε."""
    icon = {DEV: "🔧", STAGING: "🧪", PRODUCTION: "🚨"}[current]
    return f"{icon} VITRINA_ENV={current}  ·  βάση: {_DB_ENV}  ·  stripe: {stripe_mode()}"


def print_banner() -> None:
    print(banner())
