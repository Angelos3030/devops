"""Vitrina premium site generator.

Turns a client intake dict into 3 approved premium layouts (studio / commerce /
atelier), fully static HTML, zero API tokens. Content is filled deterministically;
the LLM (optional) only needs to supply per-client copy/services if available,
otherwise per-profession defaults are used.

Public API:
    generate_variants(intake) -> {"studio": html, "commerce": html, "atelier": html}
    recommend_layout(intake)  -> "studio" | "commerce" | "atelier"
    build_gallery_page(intake, slug, out_dir) -> writes 3 sites + approve page
"""
from __future__ import annotations

import html as _html
import re
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "skills" / "vitrina-design-system" / "templates"

LAYOUTS = ("studio", "commerce", "atelier", "bold", "trust", "noir", "fresh")

LAYOUT_META = {
    "studio":   {"label": "Editorial", "desc": "Ζεστό, καλλιτεχνικό, με μεγάλη τυπογραφία και έμφαση στα έργα."},
    "commerce": {"label": "Conversion", "desc": "Φωτεινό, με κριτικές και δυνατά CTA — φτιαγμένο να πουλάει."},
    "atelier":  {"label": "Minimal",    "desc": "Καθαρό, premium, με τεράστιες φωτογραφίες και πολύ λευκό."},
    "bold":     {"label": "Bold",       "desc": "Ζωντανό, με έντονα χρώματα και χαρακτήρα — για μοντέρνα brands."},
    "trust":    {"label": "Classic",    "desc": "Κλασικό, επαγγελματικό, navy & serif — για κύρος και εμπιστοσύνη."},
    "noir":     {"label": "Noir",       "desc": "Σκούρο, luxury, με χρυσές πινελιές — για premium & φωτογραφικά brands."},
    "fresh":    {"label": "Fresh",      "desc": "Απαλό, μοντέρνο, στρογγυλεμένο — για wellness, υγεία, μοντέρνα cafés."},
}

# ---------------------------------------------------------------------------
# SVG icon set (assigned to services by index)
# ---------------------------------------------------------------------------
_ICONS = [
    '<path d="M3 9h18M9 21V9M3 5h18v16H3z"/>',
    '<rect x="4" y="3" width="16" height="18" rx="1"/><path d="M12 3v18"/>',
    '<path d="M4 20h16M6 20V8l6-4 6 4v12"/>',
    '<path d="M14 3l7 7-4 4-7-7zM11 6L3 14v7h7l8-8"/>',
    '<rect x="3" y="4" width="18" height="16" rx="1"/><path d="M3 10h18"/>',
    '<path d="M12 2v20M2 12h20"/>',
    '<path d="M21 10c0 7-9 12-9 12s-9-5-9-12a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
    '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
]


# ---------------------------------------------------------------------------
# Templating engine: {{SCALAR}} + loop blocks <!--#key-->...<!--/key-->
# ---------------------------------------------------------------------------
_LOOP_RE = re.compile(r"<!--#(\w+)-->(.*?)<!--/\1-->", re.DOTALL)
_VAR_RE = re.compile(r"{{\s*(\w+)\s*}}")


def _fill_vars(fragment: str, ctx: dict[str, Any]) -> str:
    def repl(m: re.Match[str]) -> str:
        key = m.group(1)
        val = ctx.get(key, "")
        return "" if val is None else str(val)
    return _VAR_RE.sub(repl, fragment)


def render(template: str, ctx: dict[str, Any]) -> str:
    """Expand loop blocks first, then scalar vars."""
    def loop_repl(m: re.Match[str]) -> str:
        key, inner = m.group(1), m.group(2)
        items = ctx.get(key) or []
        out = []
        for i, item in enumerate(items):
            local = {**ctx, **item, "_i": i, "_n": f"{i + 1:02d}"}
            out.append(_fill_vars(inner, local))
        return "".join(out)

    rendered = _LOOP_RE.sub(loop_repl, template)
    rendered = _fill_vars(rendered, ctx)
    return rendered


# ---------------------------------------------------------------------------
# Intake normalization
# ---------------------------------------------------------------------------
def _e(value: Any) -> str:
    return _html.escape(str(value if value is not None else "")).strip()


def _normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", str(value).casefold())
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


def _profession(intake: dict[str, Any]) -> str:
    text = _normalize_text(" ".join(str(intake.get(k, "")) for k in ("type", "trade", "description", "name")))
    if any(w in text for w in (
        "νυχι", "νυχαδ", "μανικιουρ", "πεντικιουρ", "nail", "nixia", "nyxia", "nuxia",
    )):
        return "nails"
    return _vertical(intake)


# Per-profession default copy + service fallbacks (used when intake lacks them).
_PROFESSION_COPY = {
    "wood": {
        "hero_word": "μέτρο", "kicker_suffix": "Ξυλουργικό εργαστήριο",
        "services": [
            ("Εντοιχισμός κουζίνας", "Τοποθέτηση με σωστές ενώσεις και πρακτική διάταξη για καθημερινή χρήση."),
            ("Ντουλάπες & αποθήκευση", "Λύσεις που αξιοποιούν κάθε εκατοστό — εγκατάσταση, επισκευή, προσαρμογή."),
            ("Ξύλινα κρεβάτια & έπιπλα", "Ανθεκτικές κατασκευές που ταιριάζουν στο ύφος του χώρου σου."),
            ("Μερεμέτια & λουστράρισμα", "Μικρές επισκευές και ανανεώσεις σε έπιπλα, πόρτες και ράφια."),
        ],
    },
    "food": {
        "hero_word": "μεράκι", "kicker_suffix": "Παραδοσιακή κουζίνα",
        "services": [
            ("Σπιτικό φαγητό", "Καθημερινά πιάτα με φρέσκα υλικά και συνταγές που αγαπήσαμε."),
            ("Σχάρα & μεζέδες", "Ψητά της ώρας και μεζέδες για παρέα και κρασί."),
            ("Delivery & take away", "Το φαγητό σου ζεστό, όπου κι αν είσαι."),
            ("Εκδηλώσεις", "Τραπέζια για γιορτές, οικογενειακά και μικρές γιορτές."),
        ],
    },
    "cafe": {
        "hero_word": "άρωμα", "kicker_suffix": "Καφετέρια",
        "services": [
            ("Specialty coffee", "Espresso, cappuccino και φίλτρου με προσεκτικά επιλεγμένους κόκκους."),
            ("Ροφήματα", "Ζεστά και κρύα ροφήματα για κάθε στιγμή της ημέρας."),
            ("Brunch & snacks", "Πρωινές επιλογές και ελαφριά συνοδευτικά για τον καφέ."),
            ("Take away", "Γρήγορη παραλαβή καφέ και ροφημάτων από το κατάστημα."),
        ],
    },
    "bakery": {
        "hero_word": "φρεσκάδα", "kicker_suffix": "Φούρνος & αρτοποιείο",
        "services": [
            ("Φρέσκο ψωμί", "Καθημερινό ψήσιμο με επιλογές για το οικογενειακό τραπέζι."),
            ("Σφολιάτες & πρωινό", "Φρέσκες αλμυρές και γλυκές επιλογές από νωρίς το πρωί."),
            ("Γλυκά ημέρας", "Μικρές δημιουργίες που ετοιμάζονται καθημερινά."),
            ("Παραγγελίες", "Προϊόντα για το σπίτι, το γραφείο και μικρές εκδηλώσεις."),
        ],
    },
    "dentist": {
        "hero_word": "φροντίδα", "kicker_suffix": "Ιατρείο",
        "services": [
            ("Προληπτικός έλεγχος", "Τακτικός έλεγχος και καθοδήγηση για σωστή φροντίδα."),
            ("Θεραπείες", "Σύγχρονες, ανώδυνες θεραπείες με εξατομικευμένη προσέγγιση."),
            ("Αισθητική", "Διακριτικές λύσεις που ανεβάζουν την αυτοπεποίθησή σου."),
            ("Παιδική φροντίδα", "Φιλική προσέγγιση για τους μικρούς μας ασθενείς."),
        ],
    },
    "doctor": {
        "hero_word": "υγεία", "kicker_suffix": "Ιατρείο",
        "services": [
            ("Ιατρική αξιολόγηση", "Λήψη ιστορικού, κλινική εξέταση και καθαρή ενημέρωση για τα επόμενα βήματα."),
            ("Πρόληψη & παρακολούθηση", "Τακτικός έλεγχος και εξατομικευμένη παρακολούθηση της υγείας σας."),
            ("Διαγνωστική καθοδήγηση", "Υπεύθυνη αξιολόγηση εξετάσεων και παραπομπή όπου χρειάζεται."),
            ("Ραντεβού", "Οργανωμένη εξυπηρέτηση κατόπιν ραντεβού και σαφείς οδηγίες επίσκεψης."),
        ],
    },
    "beauty": {
        "hero_word": "στιλ", "kicker_suffix": "Studio ομορφιάς",
        "services": [
            ("Κούρεμα & styling", "Σχεδιασμός look που σου ταιριάζει και κρατάει."),
            ("Βαφή & περιποίηση", "Χρώμα, θεραπείες και φροντίδα για υγιή μαλλιά."),
            ("Νύχια", "Manicure, pedicure και σχέδια για κάθε περίσταση."),
            ("Περιποίηση προσώπου", "Καθαρισμοί και θεραπείες για λαμπερή επιδερμίδα."),
        ],
    },
    "nails": {
        "hero_word": "λεπτομέρεια", "kicker_suffix": "Nail studio",
        "services": [
            ("Manicure", "Περιποίηση άκρων και προσεγμένο χρώμα με επιλογές για κάθε ύφος."),
            ("Pedicure", "Ολοκληρωμένη φροντίδα και περιποίηση σε καθαρό, άνετο περιβάλλον."),
            ("Ημιμόνιμο & gel", "Εφαρμογές με έμφαση στη σωστή προετοιμασία και το καθαρό αποτέλεσμα."),
            ("Nail art", "Μίνιμαλ ή δημιουργικά σχέδια προσαρμοσμένα στο προσωπικό σας στιλ."),
        ],
    },
    "aesthetics": {
        "hero_word": "λάμψη", "kicker_suffix": "Κέντρο αισθητικής",
        "services": [
            ("Περιποίηση προσώπου", "Εξατομικευμένα πρωτόκολλα φροντίδας σύμφωνα με τις ανάγκες της επιδερμίδας."),
            ("Περιποίηση σώματος", "Συνεδρίες ευεξίας και αισθητικής σε ήρεμο, φροντισμένο περιβάλλον."),
            ("Αποτρίχωση", "Σύγχρονες επιλογές αποτρίχωσης με υπεύθυνη ενημέρωση πριν από κάθε συνεδρία."),
            ("Συμβουλευτική", "Αξιολόγηση αναγκών και πρόταση κατάλληλου πλάνου περιποίησης."),
        ],
    },
    "pet": {
        "hero_word": "φροντίδα", "kicker_suffix": "Περιποίηση κατοικιδίων",
        "services": [
            ("Μπάνιο & στέγνωμα", "Καθαρισμός με προϊόντα κατάλληλα για το τρίχωμα."),
            ("Κούρεμα", "Κούρεμα ράτσας ή απλό φρεσκάρισμα, με ραντεβού."),
            ("Νύχια & αυτιά", "Βασική περιποίηση με ηρεμία και υπομονή."),
            ("Περιποίηση γάτας", "Ήσυχη διαδικασία σε ξεχωριστή ώρα."),
        ],
    },
    "massage": {
        "hero_word": "ηρεμία", "kicker_suffix": "Massage & wellness",
        "services": [
            ("Χαλαρωτικό μασάζ", "Ήπιες τεχνικές για αποφόρτιση και βαθιά χαλάρωση."),
            ("Deep tissue", "Στοχευμένη συνεδρία προσαρμοσμένη στις ανάγκες και τις αντοχές σας."),
            ("Αθλητικό μασάζ", "Φροντίδα πριν ή μετά την άσκηση με έμφαση στις καταπονημένες περιοχές."),
            ("Wellness rituals", "Ολοκληρωμένες εμπειρίες ευεξίας σε ήσυχο και ασφαλές περιβάλλον."),
        ],
    },
    "retail": {
        "hero_word": "επιλογή", "kicker_suffix": "Κατάστημα",
        "services": [
            ("Νέες αφίξεις", "Φρέσκες επιλογές που ανανεώνονται τακτικά στο κατάστημά μας."),
            ("Προσωπική εξυπηρέτηση", "Σε βοηθάμε να βρεις αυτό που ταιριάζει στις ανάγκες και το ύφος σου."),
            ("Παραγγελίες", "Επικοινώνησε μαζί μας για διαθεσιμότητα, κράτηση ή ειδική παραγγελία."),
            ("Παραλαβή από το κατάστημα", "Γρήγορη συνεννόηση και εύκολη παραλαβή από τον χώρο μας."),
        ],
    },
    "realestate": {
        "hero_word": "χώρος", "kicker_suffix": "Ακίνητα",
        "services": [
            ("Πώληση ακινήτου", "Οργάνωση της παρουσίασης και της διαδικασίας πώλησης με καθαρή ενημέρωση."),
            ("Ενοικίαση", "Συντονισμός ενδιαφερομένων και υποστήριξη έως την ολοκλήρωση της μίσθωσης."),
            ("Αναζήτηση ακινήτου", "Καταγραφή αναγκών και επιλογές που ανταποκρίνονται στα κριτήριά σας."),
            ("Υποστήριξη εγγράφων", "Οργάνωση των απαραίτητων στοιχείων σε συνεργασία με τους αρμόδιους επαγγελματίες."),
        ],
    },
    "professional": {
        "hero_word": "εμπιστοσύνη", "kicker_suffix": "Γραφείο",
        "services": [
            ("Συμβουλευτική", "Καθαρή καθοδήγηση στα θέματα που σε απασχολούν."),
            ("Διεκπεραίωση", "Αναλαμβάνουμε τη γραφειοκρατία από την αρχή ως το τέλος."),
            ("Υποστήριξη", "Είμαστε δίπλα σου σε κάθε βήμα, με σαφήνεια."),
            ("Εξειδίκευση", "Λύσεις προσαρμοσμένες στη δική σου περίπτωση."),
        ],
    },
    "rooms": {
        "hero_word": "φιλοξενία", "kicker_suffix": "Διαμονή",
        "services": [
            ("Άνετη διαμονή", "Καθαροί, προσεγμένοι χώροι με όλα τα βασικά για μια ξεκούραστη διαμονή."),
            ("Τοποθεσία", "Εύκολη πρόσβαση και χρήσιμες πληροφορίες για την περιοχή και τις παραλίες."),
            ("Παροχές", "Αναλυτική ενημέρωση για εξοπλισμό, άφιξη, αναχώρηση και διαθέσιμες παροχές."),
            ("Κρατήσεις", "Άμεση επικοινωνία για διαθεσιμότητα, τιμές και επιβεβαίωση κράτησης."),
        ],
    },
    "gym": {
        "hero_word": "δύναμη", "kicker_suffix": "Fitness studio",
        "services": [
            ("Personal training", "Προπόνηση προσαρμοσμένη στο επίπεδο, τον χρόνο και τους στόχους σας."),
            ("Ομαδικά προγράμματα", "Μικρά οργανωμένα τμήματα με καθοδήγηση και σωστή τεχνική."),
            ("Ενδυνάμωση", "Πρόγραμμα δύναμης και λειτουργικής άσκησης με σταδιακή πρόοδο."),
            ("Αξιολόγηση στόχων", "Πρώτη συνάντηση για να σχεδιάσουμε ένα ρεαλιστικό πλάνο άσκησης."),
        ],
    },
    "garage": {
        "hero_word": "αξιοπιστία", "kicker_suffix": "Συνεργείο αυτοκινήτων",
        "services": [
            ("Service αυτοκινήτου", "Προγραμματισμένη συντήρηση σύμφωνα με τις ανάγκες του οχήματος."),
            ("Διάγνωση βλάβης", "Έλεγχος και σαφής ενημέρωση πριν προχωρήσει οποιαδήποτε εργασία."),
            ("Φρένα & αναρτήσεις", "Έλεγχος, επισκευή και αντικατάσταση κρίσιμων εξαρτημάτων ασφάλειας."),
            ("Ελαστικά", "Έλεγχος κατάστασης, αλλαγή και σωστή τοποθέτηση ελαστικών."),
        ],
    },
    "farm": {
        "hero_word": "τόπος", "kicker_suffix": "Ελληνική παραγωγή",
        "services": [
            ("Τα προϊόντα μας", "Παραγωγή με έμφαση στην προέλευση, την εποχικότητα και την ποιότητα."),
            ("Η καλλιέργεια", "Υπεύθυνες πρακτικές και φροντίδα σε κάθε στάδιο της παραγωγής."),
            ("Από τον παραγωγό", "Άμεση διάθεση και καθαρή ενημέρωση για διαθεσιμότητα και συσκευασίες."),
            ("Χονδρική συνεργασία", "Επικοινωνία για επαγγελματικές παραγγελίες και σταθερές συνεργασίες."),
        ],
    },
    "trade": {
        "hero_word": "συνέπεια", "kicker_suffix": "Τεχνικός",
        "services": [
            ("Άμεση εξυπηρέτηση", "Γρήγορη ανταπόκριση για επείγοντα περιστατικά."),
            ("Επισκευές", "Αξιόπιστες επισκευές με καθαρή συνεννόηση."),
            ("Συντηρήσεις", "Προληπτικός έλεγχος για να αποφεύγονται μεγαλύτερες ζημιές."),
            ("Νέες εγκαταστάσεις", "Οργάνωση και υλοποίηση εργασιών από την αρχή."),
        ],
    },
}

# Safe, vertical-specific defaults for sparse onboarding prompts. These describe
# the category without inventing facts about the actual business. Contact data,
# opening hours, reviews and exact location are deliberately never fabricated.
_VERTICAL_DEFAULTS = {
    "wood": ("Κατασκευές στα μέτρα του χώρου σου.", "Η λεπτομέρεια φαίνεται στο αποτέλεσμα.", "Ζήτησε προσφορά για την κατασκευή σου."),
    "food": ("Γεύσεις που φέρνουν την παρέα στο ίδιο τραπέζι.", "Φαγητό φτιαγμένο για να το μοιράζεσαι.", "Κλείσε το τραπέζι σου."),
    "cafe": ("Καφές, γεύση και μια όμορφη στάση μέσα στην ημέρα.", "Μια γωνιά για τον καφέ σου.", "Πέρνα για τον επόμενο καφέ σου."),
    "bakery": ("Φρέσκες δημιουργίες, κάθε μέρα.", "Η γειτονιά ξυπνά με άρωμα φρεσκοψημένου ψωμιού.", "Κάνε την παραγγελία σου."),
    "dentist": ("Σύγχρονη οδοντιατρική φροντίδα με καθαρή ενημέρωση.", "Το χαμόγελό σου, σε καλά χέρια.", "Κλείσε το ραντεβού σου."),
    "doctor": ("Υπεύθυνη ιατρική φροντίδα με επίκεντρο τον άνθρωπο.", "Η σωστή φροντίδα αρχίζει με προσεκτική ακρόαση.", "Κλείσε το ραντεβού σου."),
    "pharmacy": ("Καθημερινή φροντίδα και υπεύθυνη ενημέρωση.", "Το φαρμακείο της γειτονιάς σου.", "Επικοινώνησε με το φαρμακείο."),
    "beauty": ("Περιποίηση που αναδεικνύει το προσωπικό σου στιλ.", "Η λεπτομέρεια κάνει τη διαφορά.", "Κλείσε το ραντεβού σου."),
    "nails": ("Περιποιημένα άκρα με καθαρό, προσωπικό στιλ.", "Η ομορφιά βρίσκεται στη λεπτομέρεια.", "Κλείσε το ραντεβού σου."),
    "aesthetics": ("Φροντίδα προσώπου και σώματος προσαρμοσμένη σε εσένα.", "Η σωστή περιποίηση ξεκινά από τις δικές σου ανάγκες.", "Κλείσε μια πρώτη συμβουλευτική."),
    "pet": ("Φροντίδα για τον σκύλο και τη γάτα σου, με ηρεμία και ραντεβού.", "Κάθε ζώο έχει τον δικό του ρυθμό.", "Κλείσε ραντεβού για το κατοικίδιό σου."),
    "massage": ("Χρόνος για αποφόρτιση, ισορροπία και ευεξία.", "Μια εμπειρία φροντίδας με τον δικό σου ρυθμό.", "Κλείσε τη συνεδρία σου."),
    "retail": ("Επιλεγμένα προϊόντα και προσωπική εξυπηρέτηση.", "Επιλογές που ταιριάζουν στη δική σου καθημερινότητα.", "Ρώτησέ μας για διαθεσιμότητα."),
    "realestate": ("Καθαρές επιλογές για την επόμενη κίνησή σου.", "Κάθε ακίνητο ξεκινά από τις πραγματικές σου ανάγκες.", "Πες μας τι ακίνητο αναζητάς."),
    "professional": ("Καθαρή καθοδήγηση για κάθε επόμενο βήμα.", "Εξειδίκευση με συνέπεια και σαφή επικοινωνία.", "Κλείσε μια πρώτη συνάντηση."),
    "rooms": ("Άνετη διαμονή και ξεκάθαρη επικοινωνία πριν από την άφιξη.", "Μια διαμονή που ξεκινά με σωστή φιλοξενία.", "Ρώτησε για διαθεσιμότητα."),
    "gym": ("Προπόνηση με στόχο, καθοδήγηση και συνέπεια.", "Η πρόοδος χτίζεται σε κάθε προπόνηση.", "Κλείσε το δοκιμαστικό σου."),
    "garage": ("Σωστός έλεγχος και καθαρή ενημέρωση για το αυτοκίνητό σου.", "Ξέρεις τι χρειάζεται το όχημά σου πριν ξεκινήσει η εργασία.", "Κλείσε ραντεβού για έλεγχο."),
    "farm": ("Προϊόντα με καθαρή προέλευση και φροντίδα στην παραγωγή.", "Από τον τόπο μας, με σεβασμό σε κάθε στάδιο.", "Ρώτησε για τα διαθέσιμα προϊόντα."),
    "trade": ("Τεχνική εργασία με σωστή συνεννόηση και συνέπεια.", "Λύσεις που εξηγούνται καθαρά πριν ξεκινήσει η εργασία.", "Ζήτησε εκτίμηση για την εργασία σου."),
}


def _optional(value: Any) -> str:
    """Return empty for UI placeholder values accidentally persisted as data."""
    raw = str(value or "").strip()
    return "" if raw.casefold() in {"—", "-", "n/a", "none", "null"} else raw

# Neutral fallback hero images (Unsplash) when the client has not uploaded photos yet.
_DEFAULT_HERO = {
    "wood": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1800&q=80",
    "food": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=1800&q=80",
    "cafe": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=1800&q=80",
    "bakery": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=1800&q=80",
    "dentist": "https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=1800&q=80",
    "doctor": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1800&q=80",
    "pet": "https://images.unsplash.com/photo-1601758228041-f3b2795255f1?auto=format&fit=crop&w=1800&q=80",
    "beauty": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=1800&q=80",
    "nails": "https://images.unsplash.com/photo-1604654894610-df63bc536371?auto=format&fit=crop&w=1800&q=80",
    "aesthetics": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=1800&q=80",
    "massage": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874?auto=format&fit=crop&w=1800&q=80",
    "retail": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1800&q=80",
    "realestate": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1800&q=80",
    "professional": "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1800&q=80",
    # Ήταν τροπικό resort με φοίνικες και ξύλινα μπανγκαλόου. Το vertical ήταν
    # σωστό, η ήπειρος όχι: για ξενοδοχείο στην Πάρο διαβάζεται αμέσως ως ξένο
    # stock. Κυκλαδίτικη εικόνα, ίδια κατεύθυνση με το mediaFallback.js.
    "rooms": "https://images.unsplash.com/photo-1601581875309-fafbf2d3ed3a?auto=format&fit=crop&w=1800&q=80",
    "gym": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=1800&q=80",
    "garage": "https://images.unsplash.com/photo-1487754180451-c456f719a1fc?auto=format&fit=crop&w=1800&q=80",
    "farm": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1800&q=80",
    "trade": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=1800&q=80",
}

# Which layout suits each profession best (recommended first in chooser).
_LAYOUT_BY_PROFESSION = {
    "wood": "studio",
    "food": "studio",
    "cafe": "studio",
    "bakery": "studio",
    "dentist": "atelier",
    "doctor": "atelier",
    "beauty": "bold",
    "nails": "bold",
    "aesthetics": "fresh",
    "massage": "fresh",
    "retail": "bold",
    "realestate": "atelier",
    "professional": "trust",
    "rooms": "atelier",
    "gym": "bold",
    "garage": "commerce",
    "farm": "studio",
    "trade": "commerce",
}


def recommend_layout(intake: dict[str, Any]) -> str:
    return _LAYOUT_BY_PROFESSION.get(_profession(intake), "studio")


# ---------------------------------------------------------------------------
# Smart-match: ποια React templates δείχνουμε στον πελάτη (sites/lib/templates)
# ---------------------------------------------------------------------------

# Όλα τα διαθέσιμα React archetypes (πρέπει να ταιριάζουν με TEMPLATE_KEYS στο index.js).
# Κάθε id που μπορεί να επιλεγεί. Αν λείπει, το /select-design
# απαντά HTTP 400 ακόμη κι αν το theme αποδίδεται κανονικά.
REACT_TEMPLATES = (
    "aegean",
    "airspace-office",
    "area-first",
    "bakery-editorial",
    "barber-shop",
    "beauty-atelier",
    "bento",
    "bigspring-advisory",
    "billys-barber",
    "bloom",
    "blue-onepage",
    "callout",
    "canvas",
    "chapter-snap",
    "cinematic",
    "clean-work",
    "clinic-triage",
    "coast",
    "constra-build",
    "counter-menu",
    "directory-index",
    "dispatch",
    "editorial",
    "educenter-campus",
    "elegance-salon",
    "ember",
    "forge",
    "freight-lane",
    "frost-bakery",
    "grecko-table",
    "grid",
    "gymso-fitness",
    "heritage-bakery",
    "horizontal-story",
    "infinite",
    "kinetic",
    "klassy-cafe",
    "living",
    "longform",
    "magazine",
    "marble",
    "medic-care",
    "microbakery-lab",
    "morning-journal",
    "moso-interior",
    "motor",
    "neighborhood-market",
    "novena-care",
    "poster",
    "price-first",
    "property-atlas",
    "pulse",
    "quiet",
    "runway",
    "scandinavian-coffee",
    "sidebar",
    "signature",
    "split",
    "terra",
    "thomson-stylist",
    "type-gallery",
    "vertical-snap",
    "vex-counter",
    "villa-agency",
    "volt",
    "warmth",
)
# Ο κατάλογος που βλέπει ο πελάτης: κάθε εμπορικό theme που πέρασε QA.
# ΔΕΝ περιλαμβάνει τα αρχέτυπα συμβατότητας του MAP.
LAUNCH_REACT_TEMPLATES = (
    "aegean",
    "airspace-office",
    "area-first",
    "bakery-editorial",
    "barber-shop",
    "beauty-atelier",
    "bigspring-advisory",
    "billys-barber",
    "bloom",
    "blue-onepage",
    "callout",
    "canvas",
    "chapter-snap",
    "cinematic",
    "clean-work",
    "clinic-triage",
    "coast",
    "constra-build",
    "counter-menu",
    "directory-index",
    "dispatch",
    "educenter-campus",
    "elegance-salon",
    "ember",
    "forge",
    "freight-lane",
    "frost-bakery",
    "grecko-table",
    "gymso-fitness",
    "heritage-bakery",
    "horizontal-story",
    "infinite",
    "kinetic",
    "klassy-cafe",
    "living",
    "marble",
    "medic-care",
    "microbakery-lab",
    "morning-journal",
    "moso-interior",
    "motor",
    "neighborhood-market",
    "novena-care",
    "price-first",
    "property-atlas",
    "pulse",
    "quiet",
    "runway",
    "scandinavian-coffee",
    "signature",
    "terra",
    "thomson-stylist",
    "type-gallery",
    "vertical-snap",
    "vex-counter",
    "villa-agency",
    "volt",
    "warmth",
)
# ΠΡΟΣΟΧΗ: νέο theme χρειάζεται ΚΑΙ εγγραφή εδώ ΚΑΙ στο _TEMPLATES_BY_VERTICAL.
# Το `recommend_templates` φιλτράρει με αυτή τη λίστα, οπότε theme που λείπει από
# εδώ δεν προτείνεται ΠΟΤΕ — ακόμα κι αν είναι πρώτο στο vertical mapping.
# Το sites/lib/verticalProfiles.js είναι ΑΛΛΟ αντίγραφο, για το Next.js.

# Λεπτομερέστερο vertical ΜΟΝΟ για template matching — δεν αγγίζει το _profession()
# (που τροφοδοτεί το _PROFESSION_COPY και θα έσκαγε με άγνωστο key).
_VERTICAL_RULES = (
    ("gym", ("γυμναστηρ", "gym", "fitness", "crossfit", "pilates", "yoga", "γιογκα", "προπονητ", "trainer")),
    ("garage", ("συνεργει", "φανοποι", "βουλκανιζ", "garage", "service αυτοκιν", "μηχανικ αυτοκιν", "ελαστικ")),
    ("farm", ("παραγωγ", "ελαιολαδ", "ελαιωνα", "μελισσοκομ", "μελι", "οινοποι", "κρασ", "τυροκομ", "αγροτ", "κτημα", "farm", "winery")),
    ("rooms", ("δωματ", "ξενωνα", "ξενοδοχ", "καταλυμ", "hotel", "rooms", "villa", "βιλα", "airbnb", "τουρισ")),
    ("bakery", ("ζαχαροπλαστ", "φουρν", "αρτοποι", "bakery", "patisserie", "ψωμ")),
    ("cafe", ("καφε", "cafe", "coffee", "espresso", "brunch", "creperie", "κρεπερ", "παγωτ")),
    ("food", ("ταβερν", "εστιατορ", "taverna", "restaurant", "μεζε", "ψησταρι", "σουβλα", "grill", "pizza", "πιτσαρ", "μπαρ", "cocktail bar", "wine bar")),
    ("dentist", ("οδοντ", "dentist", "dental")),
    ("pharmacy", ("φαρμακει", "φαρμακοποι", "pharmacy", "drugstore", "παραφαρμακ", "δερμοκαλλυν")),
    ("doctor", ("ιατρ", "doctor", "γιατρ", "κλινικ", "φυσικοθεραπ", "physio", "διαιτολογ", "ψυχολογ", "κτηνιατρ")),
    ("aesthetics", ("αισθητικ", "beauty clinic", "κεντρο ομορφια", "μακιγι", "laser αποτριχ")),
    ("pet", ("pet grooming", "petshop", "pet shop", "κατοικιδ", "σκυλ", "γατ",
             "grooming", "groomer", "κτηνιατ", "εκπαιδευτ σκυλ", "τετραποδ")),
    ("massage", ("μασαζ", "massage", "spa", "wellness")),
    ("beauty", ("κομμωτ", "beauty", "hair", "salon", "barber", "κουρει", "νυχι", "νυχαδ", "μανικιουρ", "πεντικιουρ", "nail", "nixia", "nyxia", "nuxia")),
    ("retail", ("καταστημα", "retail", "store", "boutique", "μπουτικ", "ανθοπωλ", "λουλουδ", "ρουχ", "υποδημα", "παπουτσ", "κοσμημ", "οπτικ", "βιβλιοπωλ", "δωρα")),
    ("wood", ("ξυλουργ", "μαραγκ", "wood", "carpenter", "επιπλ", "κουζιν")),
    ("realestate", ("ακινητ", "μεσιτ", "real estate", "realestate", "πωλησ ακινητ", "ενοικιασ ακινητ")),
    ("professional", ("δικηγ", "λογιστ", "lawyer", "accountant", "συμβουλ", "μηχανικ", "αρχιτεκτ", "ασφαλισ", "notary", "συμβολαιογρ")),
    ("trade", ("υδραυλικ", "ηλεκτρολ", "ελαιοχρωματ", "μαστορ", "τεχνιτ", "ψυκτικ", "αλουμιν", "σιδηρ", "πλακα", "μονωσ", "κλιματισ", "plumber", "electrician")),
)


# Όταν δεν αναγνωρίζουμε το επάγγελμα, ΔΕΝ πέφτουμε σε «τεχνίτη»: τα templates
# του είναι σκούρα και βιομηχανικά, δηλαδή το χειρότερο δυνατό λάθος για ένα
# νυχάδικο ή ένα ανθοπωλείο. Το «professional» είναι καθαρό και ουδέτερο —
# άσχημα ταιριαστό, αλλά ποτέ προσβλητικά λάθος.
_VERTICAL_FALLBACK = "professional"

_AI_VERTICALS = [v for v, _ in _VERTICAL_RULES]


def _vertical_by_ai(text: str) -> str | None:
    """Τελευταία γραμμή άμυνας για επαγγέλματα που δεν πιάνουν οι λέξεις-κλειδιά.

    Οι λέξεις καλύπτουν τα συνηθισμένα δωρεάν και ακαριαία· το AI καλείται ΜΟΝΟ
    για την ουρά («νυχάδικο», «στούντιο πιλάτες», «κατάστημα υποδημάτων»).
    Αν δεν υπάρχει κλειδί ή απαντήσει κάτι άγνωστο, γυρνάμε στο fallback.
    """
    try:
        from . import ai
        if not ai.available():
            return None
        out = ai.complete(
            "Κατατάσσεις ελληνικές μικρές επιχειρήσεις σε κατηγορία. "
            "Απαντάς ΜΟΝΟ με μία λέξη από τη λίστα, χωρίς τίποτα άλλο.",
            f"Επιχείρηση: «{text[:200]}»\n\n"
            f"Κατηγορίες: {', '.join(_AI_VERTICALS)}",
            max_tokens=10)
        guess = (out or "").strip().lower().strip(".")
        return guess if guess in _AI_VERTICALS else None
    except Exception:  # noqa: BLE001 — ποτέ να μη ρίξει το onboarding
        return None


# ── Ταξινόμηση με προτεραιότητα σήματος, όχι με σειρά κανόνων ──────────────
#
# Το παλιό `_vertical` επέστρεφε τον ΠΡΩΤΟ κανόνα με substring match. Επειδή το
# `garage` είναι γραμμένο πριν το `trade`, το «μικρό **συνεργείο** υδραυλικών»
# έβγαινε συνεργείο αυτοκινήτων — και το site πήρε φωτογραφία μηχανής. Ομοίως
# το «Pet **Spa** Λούνα» έπεφτε στο `massage` και εικονογραφήθηκε με ανθρώπινο
# μανικιούρ. Και στις δύο περιπτώσεις μια ΓΕΝΙΚΗ λέξη νίκησε μια λέξη που ορίζει
# το επάγγελμα.
#
# Τώρα κάθε ένδειξη έχει βάρος και τα συμφραζόμενα μπορούν να ακυρώσουν κατηγορία:
#   STRONG  — ορίζει το επάγγελμα («υδραυλικ», «οδοντ», «ζαχαροπλαστ»)
#   WEAK    — γενικό ουσιαστικό που εμφανίζεται σε πολλά επαγγέλματα
#             («συνεργει», «spa», «κεντρο», «studio»)
# Το πεδίο μετράει κι αυτό: `type`/`trade` είναι δήλωση επαγγέλματος, το `name`
# είναι εμπορική επωνυμία και δεν επιτρέπεται να καθορίσει μόνο του κατηγορία.

_WEAK_WORDS = frozenset((
    "συνεργει", "spa", "wellness", "κεντρο", "studio", "στουντιο", "salon",
    "boutique", "μπουτικ", "καταστημα", "store", "γραφειο", "atelier", "house",
    "lab", "club", "shop", "point", "room", "rooms", "service",
))
# Συμφραζόμενα που ΑΚΥΡΩΝΟΥΝ κατηγορίες: ένα κομμωτήριο σκύλων δεν είναι
# ανθρώπινο κομμωτήριο, όσες φορές κι αν γράφει «spa» η επωνυμία.
_CONTEXT_BLOCKS = (
    (("κατοικιδ", "σκυλ", "σκυλο", "γατα", "γατε", "γατων", "pet", " dog", "dog ",
      "cat ", "grooming", "groomer", "κτηνιατ", "ζωακ", "τετραποδ"),
     ("beauty", "nails", "massage", "aesthetics", "food", "cafe")),
)
_FIELD_WEIGHT = {"type": 3, "trade": 3, "description": 2, "name": 1}
# Μια κατηγορία δεν κερδίζει από ΜΟΝΟ ένα weak σήμα σε επωνυμία.
_MIN_SCORE = 2


def _signals(intake: dict[str, Any]) -> dict[str, int]:
    fields = {k: _normalize_text(str(intake.get(k, ""))) for k in _FIELD_WEIGHT}
    blob = " ".join(fields.values())
    blocked: set[str] = set()
    for triggers, verticals in _CONTEXT_BLOCKS:
        if any(t in blob for t in triggers):
            blocked.update(verticals)

    scores: dict[str, int] = {}
    for vertical, words in _VERTICAL_RULES:
        if vertical in blocked:
            continue
        best = 0
        for word in words:
            strength = 1 if word in _WEAK_WORDS else 4
            for field, text in fields.items():
                if word in text:
                    best = max(best, strength * _FIELD_WEIGHT[field])
        if best:
            scores[vertical] = best
    return scores


def _vertical(intake: dict[str, Any]) -> str:
    scores = _signals(intake)
    if scores:
        order = {v: i for i, (v, _) in enumerate(_VERTICAL_RULES)}
        # Ισοβαθμία → η σειρά των κανόνων, ώστε το ίδιο intake να δίνει ΠΑΝΤΑ
        # το ίδιο αποτέλεσμα (το theme selection πρέπει να είναι αναπαραγώγιμο).
        best = max(scores.items(), key=lambda kv: (kv[1], -order[kv[0]]))
        if best[1] >= _MIN_SCORE:
            return best[0]
    raw = " ".join(str(intake.get(k, "")) for k in ("type", "trade", "description")).strip()
    return (_vertical_by_ai(raw) if raw else None) or _VERTICAL_FALLBACK


# Premium-first σειρά ανά vertical. Το πρώτο = προτεινόμενο.
# Κρατάμε ολόκληρο το ranking για το chat editor, αλλά το αρχικό chooser δείχνει
# επτά καθαρές κατευθύνσεις ώστε να υπάρχει ουσιαστική επιλογή χωρίς άσχετα themes.
_TEMPLATES_BY_VERTICAL = {
    "food":         ["grecko-table", "cinematic", "bakery-editorial", "warmth", "ember", "magazine", "type-gallery", "living", "infinite", "quiet", "kinetic", "poster", "bloom"],
    "cafe":         ["counter-menu", "neighborhood-market", "scandinavian-coffee", "bloom", "cinematic", "type-gallery", "living", "quiet"],
    "bakery":       ["bakery-editorial", "morning-journal", "microbakery-lab", "heritage-bakery", "neighborhood-market", "bloom", "warmth", "type-gallery"],
    "rooms":        ["vertical-snap", "chapter-snap", "aegean", "cinematic", "infinite", "living", "quiet", "canvas", "type-gallery", "kinetic", "grid", "marble"],
    "dentist":      ["novena-care", "clinic-triage", "signature", "bigspring-advisory", "cinematic", "marble", "directory-index", "quiet", "living", "grid", "canvas", "editorial"],
    "doctor":       ["novena-care", "clinic-triage", "signature", "bigspring-advisory", "cinematic", "marble", "quiet", "editorial", "split", "grid", "living", "canvas"],
    "pharmacy":     ["quiet", "marble", "grid", "editorial", "bento", "split", "living", "clinic-triage", "sidebar", "canvas", "infinite", "type-gallery"],
    "aesthetics":   ["beauty-atelier", "bloom", "quiet", "clinic-triage", "marble", "runway", "living", "cinematic", "type-gallery", "bento", "infinite", "canvas", "magazine"],
    "pet":          ["living", "bloom", "quiet", "grid", "type-gallery", "cinematic", "infinite", "canvas", "bento", "editorial", "magazine", "split"],
    "massage":      ["living", "quiet", "signature", "aegean", "clinic-triage", "bloom", "warmth", "cinematic", "infinite", "canvas", "marble", "type-gallery", "terra", "magazine"],
    "beauty":       ["elegance-salon", "beauty-atelier", "cinematic", "signature", "price-first", "runway", "type-gallery", "living", "chapter-snap", "infinite", "kinetic", "quiet"],
    "retail":       ["bento", "grid", "type-gallery", "living", "quiet", "infinite", "canvas", "cinematic", "kinetic", "magazine", "editorial", "split"],
    "professional": ["bigspring-advisory", "property-atlas", "signature", "cinematic", "directory-index", "marble", "quiet", "grid", "infinite", "canvas", "type-gallery", "living"],
    "realestate":   ["property-atlas", "bigspring-advisory", "cinematic", "signature", "grid", "canvas", "quiet", "living", "directory-index", "marble", "editorial", "bento"],
    "trade":        ["constra-build", "callout", "cinematic", "area-first", "forge", "grid", "sidebar", "kinetic", "type-gallery", "infinite", "quiet", "living"],
    "garage":       ["motor", "kinetic", "grid", "infinite", "type-gallery", "cinematic", "quiet", "living", "canvas", "volt", "forge", "poster"],
    "gym":          ["volt", "kinetic", "type-gallery", "infinite", "runway", "grid", "cinematic", "living", "quiet", "poster", "bento", "motor"],
    "farm":         ["terra", "living", "quiet", "cinematic", "canvas", "infinite", "type-gallery", "kinetic", "grid", "editorial", "magazine", "warmth"],
    "wood":         ["constra-build", "cinematic", "horizontal-story", "forge", "canvas", "grid", "quiet", "living", "type-gallery", "infinite", "kinetic", "editorial"],
}


# Λέξεις που δηλώνουν ΟΡΓΑΝΙΣΜΟ, όχι πρόσωπο. Αν υπάρχουν στην επωνυμία, η
# επιχείρηση δεν παρουσιάζεται ως ένας άνθρωπος.
_ORG_WORDS = (
    "αε", "α.ε", "επε", "ε.π.ε", "ικε", "ι.κ.ε", "οε", "ο.ε", "ομιλ", "εταιρ",
    "κεντρο", "ομαδα", "group", "clinic", "κλινικ", "studio", "salon", "shop",
    "καταστημα", "συνεργατ", "& σια", "και σια", "αφοι", "υιοι",
)
# Πρώτο πρόσωπο ενικού: ο ίδιος ο επαγγελματίας μιλάει.
_SOLO_HINTS = ("δουλευω", "αναλαμβανω", "ειμαι ", "εργαζομαι", "συνεργαζομαι",
               "ενος ατομου", "μονη μου", "μονος μου", "προσωπικα ")
# Verticals όπου η μονάδα εμπιστοσύνης ΜΠΟΡΕΙ να είναι ο άνθρωπος.
_PERSON_FIRST_VERTICALS = frozenset(("professional", "doctor", "massage", "gym"))


def _is_solo_practitioner(intake: dict[str, Any]) -> bool:
    """Είναι η επιχείρηση ΕΝΑΣ άνθρωπος; Ντετερμινιστικό, χωρίς AI.

    Δύο ανεξάρτητες ενδείξεις, καμία από τις οποίες δεν αρκεί μόνη της αν η
    επωνυμία δηλώνει οργανισμό: (α) η επωνυμία είναι ονοματεπώνυμο, (β) η
    περιγραφή μιλάει σε πρώτο πρόσωπο ενικού.
    """
    name = str(intake.get("name") or "").strip()
    norm_name = _normalize_text(name)
    if any(w in norm_name for w in _ORG_WORDS):
        return False
    # Επωνυμία που ΔΗΛΩΝΕΙ το επάγγελμα είναι εμπορική, όχι ονοματεπώνυμο:
    # «Ακίνητα Δουκάκης» και «Οδοντιατρείο Παπαδάκη» δεν είναι πρόσωπα, όσο κι αν
    # μοιάζουν μορφολογικά με δύο κεφαλαία αρχικά.
    declares_trade = any(w in norm_name for _, words_ in _VERTICAL_RULES for w in words_)
    words = [w for w in re.split(r"\s+", name) if w]
    # «Γεωργία Στεφανίδου» → δύο λέξεις με κεφαλαίο αρχικό, χωρίς εμπορικό ουσιαστικό.
    looks_like_person = (
        not declares_trade
        and 1 < len(words) <= 3
        and all(w[:1].isupper() for w in words if w[:1].isalpha())
        and not any(ch.isdigit() for ch in name)
    )
    desc = _normalize_text(" ".join(str(intake.get(k, "")) for k in ("description", "style", "about")))
    speaks_singular = any(h in desc for h in _SOLO_HINTS)
    return bool(looks_like_person or speaks_singular)


def _capability_rank(keys: list[str], intake: dict[str, Any], vertical: str) -> list[str]:
    """Μετακινεί συμβατές κατευθύνσεις μπροστά, χωρίς AI και χωρίς duplicates."""
    text = _normalize_text(" ".join(str(intake.get(k) or "") for k in ("description", "style", "features")))
    features = {str(v) for v in intake.get("features", [])} if isinstance(intake.get("features"), list) else set()
    wanted: list[str] = []
    if intake.get("media_available") is False or any(x in text for x in ("χωρις φωτο", "δεν εχω φωτο")):
        wanted.extend(["type-specimen", "directory-index", "price-first"])
    if intake.get("pricing") or "pricing" in features or any(x in text for x in ("τιμοκαταλογ", "τιμες", "κοστο")):
        wanted.append("price-first")
    if intake.get("booking") or "online-booking" in features or "ραντεβου" in text:
        wanted.extend(["beauty-atelier", "split-carousel"])
    if "service-area" in features or any(x in text for x in ("διαθεσιμοτ", "ταχυδρομ", "περιοχ εξυπηρετ")):
        wanted.append("area-first")
    if "inventory" in features:
        wanted.extend(["visual-selector", "spatial-grid"])
    if any(x in text for x in ("fullscreen", "πληρη οθον", "κινηματογραφ")):
        wanted.append("chapter-snap")
    if any(x in text for x in ("minimal", "λιτο", "οχι πολυ φανταχτερ")):
        wanted.extend(["quiet", "type-specimen"])
    if any(x in text for x in ("τολμηρ", "bold", "εντον")):
        wanted.extend(["poster", "kinetic"])

    # Το πρώτο vertical anchor διατηρείται, εκτός από service-area τεχνίτη όπου
    # η ίδια η απαίτηση είναι το conversion goal του πρώτου viewport.
    anchor = [] if (vertical == "trade" and "area-first" in wanted) else keys[:1]
    ordered = [*anchor, *wanted, *keys]
    return list(dict.fromkeys(k for k in ordered if k in keys))


def recommend_templates(intake: dict[str, Any], limit: int = 12) -> list[str]:
    """Ranked React προτάσεις, με την καταλληλότερη πρώτη.

    Η κατάταξη ήταν σταθερή ανά vertical, οπότε το `signature` έβγαινε #2 και
    ΔΕΝ επιλεγόταν ποτέ (η παραγωγή παίρνει `[0]`). Ένας μονοπρόσωπος λογιστής
    και ένα λογιστικό γραφείο δέκα ατόμων έπαιρναν το ίδιο theme, παρότι το ένα
    πουλάει άνθρωπο και το άλλο οργανισμό.

    Το σήμα είναι ντετερμινιστικό: ίδιο intake → ίδια σειρά, πάντα.
    """
    vertical = _vertical(intake)
    keys = list(_TEMPLATES_BY_VERTICAL.get(vertical, _TEMPLATES_BY_VERTICAL["trade"]))
    if (vertical in _PERSON_FIRST_VERTICALS
            and "signature" in keys
            and _is_solo_practitioner(intake)):
        keys.insert(0, keys.pop(keys.index("signature")))
    keys = _capability_rank(keys, intake, vertical)
    launch = [k for k in keys if k in LAUNCH_REACT_TEMPLATES]
    return launch[:limit]


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    return [v for v in value if isinstance(v, dict)] if isinstance(value, list) else []



def _social(value: object, host: str) -> str:
    """Κανονικοποιεί ό,τι κι αν γράψει ο πελάτης σε ασφαλές https URL — ή κενό.

    Δέχεται: πλήρες URL, «facebook.com/mypage», «@myhandle», «myhandle».
    Απορρίπτει: κενά, javascript:, ό,τι δεν καταλήγει σε αναγνωρίσιμο handle.
    Κενό σημαίνει «μην εμφανίσεις εικονίδιο» — ποτέ σπασμένος σύνδεσμος.
    """
    raw = str(value or "").strip()
    if not raw:
        return ""
    low = raw.lower()
    if low.startswith(("javascript:", "data:", "vbscript:")):
        return ""
    if low.startswith(("http://", "https://")):
        return _e(raw) if host.split(".")[0] in low else ""
    raw = raw.lstrip("@/")
    if raw.lower().startswith(host):
        return _e("https://" + raw)
    if "/" in raw or " " in raw:
        return ""
    return _e(f"https://{host}/{raw}")

def normalize(intake: dict[str, Any]) -> dict[str, Any]:
    prof = _profession(intake)
    copy = _PROFESSION_COPY[prof]
    tagline_default, story_title_default, cta_title_default = _VERTICAL_DEFAULTS[prof]

    # Το _optional() παντού, όχι μόνο στην πόλη: εγγραφές που γράφτηκαν πριν τη
    # διόρθωση του create_client κουβαλούν κυριολεκτικό «—» σε name/type/city.
    # Χωρίς αυτό, ένα ολόκληρο site δείχνει παύλες σαν να είναι περιεχόμενο.
    name = _e(_optional(intake.get("name") or intake.get("business_name")) or "Η Επιχείρησή σας")
    city = _e(_optional(intake.get("city") or intake.get("area")))
    trade = _e(_optional(intake.get("trade") or intake.get("type")) or copy["kicker_suffix"])
    phone_raw = _optional(intake.get("phone") or intake.get("telephone"))
    phone_digits = re.sub(r"\D", "", phone_raw)
    phone_intl = phone_digits if phone_digits.startswith("30") else ("30" + phone_digits if phone_digits else "")
    phone_disp = _e(phone_raw)
    tagline = _e(_optional(intake.get("tagline") or intake.get("style")) or tagline_default)

    areas_raw = intake.get("areas")
    areas = ([_e(_optional(a)) for a in areas_raw if _optional(a)]
             if isinstance(areas_raw, list) else ([city] if city else []))
    areas_str = " · ".join(areas[:4])

    domain = str(intake.get("site_url") or intake.get("url") or intake.get("domain") or "").strip()
    domain_disp = re.sub(r"^https?://", "", domain).rstrip("/") if domain else ""

    # services
    svc_src = _list_of_dicts(intake.get("services"))
    if svc_src:
        services = [
            {"title": _e(s.get("SERVICE_NAME") or s.get("name") or s.get("title") or "Υπηρεσία"),
             "desc": _e(s.get("SERVICE_DESC") or s.get("description") or s.get("desc") or ""),
             "price": _e(s.get("price") or ""),
             "duration": _e(s.get("duration") or "")}
            for s in svc_src
        ]
        # Το /start αποθηκεύει τίτλους υπηρεσιών με κενή περιγραφή. Χωρίς αυτό,
        # η ενότητα βγαίνει σαν αριθμημένη λίστα χωρίς περιεχόμενο. Δεν επινοούμε:
        # συμπληρώνουμε ΜΟΝΟ από τη δική μας ελεγμένη περιγραφή για τον ίδιο τίτλο.
        reviewed = {_normalize_text(t): d for t, d in copy["services"]}
        for s in services:
            if not s["desc"]:
                s["desc"] = _e(reviewed.get(_normalize_text(s["title"]), ""))
    else:
        services = [{"title": _e(t), "desc": _e(d)} for t, d in copy["services"]]
    # Το cap ήταν 6 και ήταν ΣΙΩΠΗΛΟ: ένας φούρνος με 9 προϊόντα έχανε τρία και
    # κανείς δεν το μάθαινε — ούτε εμείς, ούτε ο πελάτης. Ό,τι δήλωσε ο πελάτης
    # ανήκει στο site του. Το όριο ανεβαίνει σε ρεαλιστικό μέγιστο και ό,τι
    # περισσεύει ΔΗΛΩΝΕΤΑΙ, δεν εξαφανίζεται.
    services_total = len(services)
    services = services[:12]
    for i, s in enumerate(services):
        s["num"] = f"{i + 1:02d}"
        s["icon"] = _ICONS[i % len(_ICONS)]

    # gallery
    gal_src = _list_of_dicts(intake.get("gallery"))
    gallery = [
        {"image": _asset(str(g.get("image", ""))),
         "title": _e(g.get("title") or "Έργο"),
         "sub": _e(g.get("sub") or g.get("alt") or city),
         # Η κλάση ΔΕΝ χάνεται εδώ. Χωρίς αυτήν, κάθε πραγματική φωτογραφία
         # πελάτη έφτανε στον renderer ως άγνωστης προέλευσης — δηλαδή ως
         # δανεική — και η πολιτική `real-only` την πετούσε.
         "media_class": g.get("media_class") or None,
         "illustrative": bool(g.get("illustrative"))}
        for g in gal_src if str(g.get("image", "")).strip()
    ][:8]

    _fallback_hero = _DEFAULT_HERO.get(prof, _DEFAULT_HERO["trade"])
    # ΠΟΙΟΣ έβαλε την εικόνα, όχι μόνο ΑΝ υπάρχει. Το `normalize` γεμίζει πάντα
    # το HERO_IMAGE με stock, οπότε το JS `withMediaFallback` έβγαζε πάντα
    # `HERO_IS_REAL: true` — ακόμη και για πελάτη με μηδέν φωτογραφίες. Ένα theme
    # που ρωτά «είναι δική του η φωτογραφία;» έπαιρνε λάθος απάντηση.
    _own_hero = bool(str(intake.get("hero_image") or "").strip() or gallery)
    hero_image = _asset(str(intake.get("hero_image") or (gallery[0]["image"] if gallery else "") or _fallback_hero))
    story_image = _asset(str(intake.get("workshop_image") or intake.get("story_image")
                             or (gallery[-1]["image"] if gallery else "") or _fallback_hero))

    # reviews (commerce). fall back to neutral samples flagged as δείγμα.
    rev_src = _list_of_dicts(intake.get("reviews"))
    if rev_src:
        reviews = [
            {"text": _e(r.get("text") or ""), "author": _e(r.get("author") or "Πελάτης"),
             "area": _e(r.get("area") or city),
             "initials": _initials(str(r.get("author") or "Π"))}
            for r in rev_src
        ][:3]
    else:
        reviews = []

    if prof == "cafe":
        story_default = [
            f"Στο {name}, στην περιοχή {city}, η ημέρα ξεκινά με φρεσκοαλεσμένο καφέ και φιλική εξυπηρέτηση.",
            "Διαλέγουμε προσεκτικά τον καφέ μας και δημιουργούμε έναν χώρο για την πρωινή στάση, τη συνάντηση και τη χαλάρωση.",
        ]
    elif prof == "bakery":
        story_default = [
            f"Στο {name}, στην περιοχή {city}, το ψωμί και οι καθημερινές δημιουργίες ετοιμάζονται φρέσκα από το πρωί.",
            "Δίνουμε σημασία στις πρώτες ύλες, στη σταθερή ποιότητα και στη ζεστή εξυπηρέτηση της γειτονιάς.",
        ]
    elif prof == "rooms":
        location = f" στην περιοχή {city}" if city else ""
        story_default = [
            f"Το {name} προσφέρει οργανωμένη φιλοξενία{location}, με σαφή ενημέρωση πριν από την άφιξη.",
            "Οι επισκέπτες μπορούν να ενημερωθούν για τη διαμονή, τις διαθέσιμες παροχές και τη διαδικασία κράτησης.",
        ]
    else:
        location = f" στην περιοχή {city}" if city else ""
        story_default = [
            f"Η επιχείρηση {name}{location} δίνει προτεραιότητα στην προσωπική εξυπηρέτηση και την καθαρή ενημέρωση.",
            "Στόχος μας είναι κάθε επίσκεψη ή συνεργασία να ολοκληρώνεται με συνέπεια, φροντίδα και σεβασμό στις πραγματικές σας ανάγκες.",
        ]
    story_paras = intake.get("story_paragraphs") if isinstance(intake.get("story_paragraphs"), list) else story_default
    story_paras = [{"p": _e(p)} for p in story_paras]

    # commerce feature tiles: first 2 gallery items paired with service copy
    tiles = []
    for i, g in enumerate(gallery[:2]):
        svc = services[i] if i < len(services) else None
        tiles.append({
            "t_image": g["image"],
            "t_title": g["title"],
            "t_kicker": (svc["title"] if svc else "Έργα"),
            "t_desc": (svc["desc"] if svc else tagline),
        })

    return {
        "NAME": name, "CITY": city, "TRADE": trade, "TAGLINE": tagline,
        "INITIAL": _initials(name)[:1],
        "LOGO": _asset(str(intake.get("logo") or "")),  # uploaded logo URL ('' → wordmark)
        # Local SEO / Google Maps
        "ADDRESS": _e(_optional(intake.get("address"))),
        "GEO_LAT": str(intake.get("geo_lat") or ""),
        "GEO_LNG": str(intake.get("geo_lng") or ""),
        "GBP_URL": _e(str(intake.get("gbp_url") or "")),   # Google Business Profile
        # Επικοινωνία & social. Το _social() κρατά μόνο έγκυρα http(s) URL ώστε
        # ένα «facebook.com/…» ή σκέτο handle να μη βγάλει σπασμένο σύνδεσμο.
        "EMAIL": _e(_optional(intake.get("email"))),
        "FACEBOOK": _social(intake.get("facebook"), "facebook.com"),
        "INSTAGRAM": _social(intake.get("instagram"), "instagram.com"),
        "PHONE": phone_disp, "PHONE_INTL": phone_intl,
        "AREAS": areas_str, "DOMAIN": _e(domain_disp), "DOMAIN_URL": _e(domain or "#"),
        "HOURS": _e(_optional(intake.get("hours"))),
        "PALETTE": _e(intake.get("palette") or "original"),
        "FONT_PAIR": _e(intake.get("font_pair") or "editorial"),
        # Χωρίς πόλη, το «Ξενοδοχείο · » κρέμαγε διαχωριστικό στο πρώτο viewport.
        "KICKER": " · ".join(x for x in (trade, city) if x),
        "HERO_WORD": copy["hero_word"],
        "HERO_IMAGE": hero_image, "STORY_IMAGE": story_image,
        "HERO_IS_REAL": _own_hero, "MEDIA_ILLUSTRATIVE": not _own_hero,
        # Πόσες υπηρεσίες ΔΗΛΩΣΕ ο πελάτης — τα themes που δείχνουν λιγότερες
        # οφείλουν να το πουν, αντί να τις εξαφανίσουν.
        "SERVICES_TOTAL": services_total,

        "STORY_TITLE": _e(_optional(intake.get("story_title")) or story_title_default),
        "CTA_TITLE": _e(_optional(intake.get("cta_title")) or cta_title_default),
        "INTRO": _e(intake.get("intro") or tagline),
        "YEAR": "2026",
        "services": services, "pricingServices": services,
        "booking": {"provider": "configured" if intake.get("booking") else "demo",
                    "url": _e(str(intake.get("booking_url") or ""))},
        "features": intake.get("features") if isinstance(intake.get("features"), list) else [],
        "media_available": intake.get("media_available"),
        "gallery": gallery, "reviews": reviews, "story": story_paras,
        "tiles": tiles,
        "_recommended": recommend_layout(intake),
    }


def _initials(name: str) -> str:
    words = [w for w in re.split(r"\s+", name.strip()) if w]
    if not words:
        return "Π"
    if len(words) == 1:
        return words[0][:2].upper()
    return (words[0][0] + words[1][0]).upper()


def _asset(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if value.startswith(("http://", "https://", "/", "./", "../", "assets/")):
        return value
    return _html.escape(value)


# ---------------------------------------------------------------------------
# Public: generate
# ---------------------------------------------------------------------------
def generate(intake: dict[str, Any], layout: str) -> str:
    if layout not in LAYOUTS:
        raise ValueError(f"Unknown layout: {layout}")
    template = (TEMPLATE_DIR / f"{layout}.tpl.html").read_text(encoding="utf-8")
    ctx = normalize(intake)
    html_out = render(template, ctx)
    leftover = re.findall(r"{{[^}]+}}", html_out)
    if leftover:
        raise ValueError(f"[{layout}] unresolved placeholders: {sorted(set(leftover))}")
    return html_out


def generate_variants(intake: dict[str, Any]) -> dict[str, str]:
    return {layout: generate(intake, layout) for layout in LAYOUTS}


def build_gallery_page(intake: dict[str, Any], slug: str, out_dir: Path) -> Path:
    """Write the 3 variants + an approve/chooser page. Returns the chooser path."""
    out_dir = Path(out_dir)
    site_dir = out_dir / slug
    site_dir.mkdir(parents=True, exist_ok=True)

    variants = generate_variants(intake)
    for layout, html_out in variants.items():
        (site_dir / f"{layout}.html").write_text(html_out, encoding="utf-8")

    ctx = normalize(intake)
    recommended = ctx["_recommended"]
    ordered = [recommended] + [l for l in LAYOUTS if l != recommended]
    cards = "".join(_chooser_card(slug, layout, layout == recommended) for layout in ordered)
    chooser = _CHOOSER_SHELL.replace("{{NAME}}", ctx["NAME"]).replace("{{CARDS}}", cards)
    chooser_path = out_dir / f"{slug}-choose.html"
    chooser_path.write_text(chooser, encoding="utf-8")
    return chooser_path


def _chooser_card(slug: str, layout: str, recommended: bool) -> str:
    meta = LAYOUT_META[layout]
    badge = '<span class="rec">Προτεινόμενο</span>' if recommended else ""
    return f"""
    <article class="card">
      <div class="shot">{badge}<iframe src="{slug}/{layout}.html" title="{meta['label']}" loading="lazy" scrolling="no"></iframe></div>
      <div class="body">
        <h2>{meta['label']}</h2>
        <p>{meta['desc']}</p>
        <div class="actions">
          <a class="btn ghost" href="{slug}/{layout}.html" target="_blank">Άνοιξέ το ↗</a>
          <button class="btn fill" data-layout="{layout}" data-name="{meta['label']}">✓ Approve</button>
        </div>
      </div>
    </article>"""


_CHOOSER_SHELL = """<!DOCTYPE html>
<html lang="el"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{NAME}} — Διάλεξε design | Vitrina</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Inter,system-ui,sans-serif;background:#0e1117;color:#fff;line-height:1.55;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.wrap{width:min(1240px,calc(100% - 40px));margin-inline:auto}
header{padding:clamp(48px,8vw,86px) 0 clamp(16px,3vw,28px);text-align:center}
.eyebrow{font-weight:700;text-transform:uppercase;letter-spacing:.16em;font-size:.8rem;color:#ff9a4d}
h1{font-size:clamp(2.4rem,6vw,4rem);margin:.7rem 0;letter-spacing:-.02em}
.sub{color:rgba(255,255,255,.68);font-size:1.12rem;max-width:60ch;margin:0 auto}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px;padding-block:clamp(28px,5vw,46px) 70px}
.card{background:#171b24;border:1px solid rgba(255,255,255,.09);border-radius:18px;overflow:hidden;display:flex;flex-direction:column;transition:transform .2s,border-color .2s}
.card:hover{transform:translateY(-6px);border-color:rgba(255,154,77,.5)}
.shot{position:relative;aspect-ratio:16/10;overflow:hidden;border-bottom:1px solid rgba(255,255,255,.08)}
.shot iframe{position:absolute;top:0;left:0;width:250%;height:250%;transform:scale(.4);transform-origin:top left;border:0;pointer-events:none}
.rec{position:absolute;top:12px;left:12px;z-index:2;font-size:.72rem;font-weight:800;text-transform:uppercase;letter-spacing:.1em;padding:.35rem .7rem;border-radius:999px;background:#ff8a3d;color:#1a1204}
.body{padding:1.5rem;display:flex;flex-direction:column;gap:.5rem;flex:1}
.body h2{font-size:1.4rem}.body p{color:rgba(255,255,255,.65);font-size:.95rem;flex:1}
.actions{display:flex;gap:.6rem;margin-top:.8rem}
.btn{flex:1;text-align:center;font-weight:700;padding:.75rem;border-radius:10px;transition:.15s;font-size:.92rem;cursor:pointer;border:0;font-family:inherit}
.fill{background:#ff8a3d;color:#1a1204}.fill:hover{background:#ff9a4d}
.ghost{border:1px solid rgba(255,255,255,.2);color:#fff;background:transparent}.ghost:hover{background:rgba(255,255,255,.08)}
.toast{position:fixed;left:50%;bottom:30px;transform:translateX(-50%) translateY(120%);background:#1db954;color:#04240f;font-weight:700;padding:1rem 1.6rem;border-radius:12px;transition:transform .3s;z-index:99}
.toast.show{transform:translateX(-50%) translateY(0)}
.note{max-width:1240px;margin:0 auto 70px;padding:1.3rem 1.5rem;border:1px solid rgba(255,255,255,.1);border-radius:14px;background:rgba(255,255,255,.04);color:rgba(255,255,255,.72);font-size:.95rem}
@media(max-width:900px){.grid{grid-template-columns:1fr}}
</style></head><body>
<div class="wrap">
  <header>
    <span class="eyebrow">Vitrina · 3 προτάσεις design</span>
    <h1>{{NAME}}</h1>
    <p class="sub">Ίδιο περιεχόμενο, τρία ύφη. Δες τα και πάτα <b>Approve</b> σε αυτό που σου αρέσει — αυτό ανεβάζουμε.</p>
  </header>
  <div class="grid">{{CARDS}}</div>
  <div class="note">💡 Και τα 3 φτιάχτηκαν αυτόματα από το Vitrina design engine (static HTML, 0 dependencies). Ανεβαίνουν κατευθείαν στο Cloudflare Pages.</div>
</div>
<div class="toast" id="toast">✓ Το design εγκρίθηκε!</div>
<script>
const _q=new URLSearchParams(location.search), _api=_q.get('api'), _cid=_q.get('client');
function toast(msg){const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),3400);}
document.querySelectorAll('[data-layout]').forEach(b=>b.addEventListener('click',async()=>{
  const layout=b.dataset.layout,name=b.dataset.name;
  try{localStorage.setItem('vitrina_choice',JSON.stringify({layout,name,at:Date.now()}))}catch(e){}
  if(_api&&_cid){
    try{
      const r=await fetch(_api.replace(/\\/$/,'')+'/clients/'+_cid+'/select-design',
        {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({layout})});
      if(!r.ok)throw new Error(await r.text());
      toast('✓ Διάλεξες: '+name+' — το ανεβάζουμε!');
    }catch(err){toast('⚠️ Κάτι πήγε στραβά — δοκίμασε ξανά.');}
  }else{ toast('✓ Διάλεξες: '+name+' — το ανεβάζουμε!'); }
}));
</script>
</body></html>
"""
