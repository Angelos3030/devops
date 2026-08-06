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
    text = _normalize_text(" ".join(str(intake.get(k, "")) for k in ("type", "trade", "description")))
    if any(w in text for w in ("ταβερ", "taverna", "εστιατο", "cafe", "καφε", "restaurant", "μεζε")):
        return "food"
    if any(w in text for w in ("οδοντ", "dentist", "ιατρ", "doctor", "γιατρ")):
        return "medical"
    if any(w in text for w in (
        "κομμωτ", "beauty", "νυχι", "νυχαδ", "μανικιουρ", "πεντικιουρ",
        "nail", "nixia", "nyxia", "nuxia", "hair", "salon", "αισθητικ",
    )):
        return "beauty"
    if any(w in text for w in (
        "καταστημα", "boutique", "μπουτικ", "ανθοπωλ", "λουλουδ", "ρουχ",
        "υποδημα", "παπουτσ", "κοσμημ", "retail", "store",
    )):
        return "retail"
    if any(w in text for w in ("ξυλουργ", "μαραγκ", "wood", "carpenter", "επιπλ", "κουζιν")):
        return "wood"
    if any(w in text for w in ("δικηγ", "λογιστ", "lawyer", "accountant", "συμβουλ")):
        return "professional"
    return "trade"


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
    "medical": {
        "hero_word": "φροντίδα", "kicker_suffix": "Ιατρείο",
        "services": [
            ("Προληπτικός έλεγχος", "Τακτικός έλεγχος και καθοδήγηση για σωστή φροντίδα."),
            ("Θεραπείες", "Σύγχρονες, ανώδυνες θεραπείες με εξατομικευμένη προσέγγιση."),
            ("Αισθητική", "Διακριτικές λύσεις που ανεβάζουν την αυτοπεποίθησή σου."),
            ("Παιδική φροντίδα", "Φιλική προσέγγιση για τους μικρούς μας ασθενείς."),
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
    "retail": {
        "hero_word": "επιλογή", "kicker_suffix": "Κατάστημα",
        "services": [
            ("Νέες αφίξεις", "Φρέσκες επιλογές που ανανεώνονται τακτικά στο κατάστημά μας."),
            ("Προσωπική εξυπηρέτηση", "Σε βοηθάμε να βρεις αυτό που ταιριάζει στις ανάγκες και το ύφος σου."),
            ("Παραγγελίες", "Επικοινώνησε μαζί μας για διαθεσιμότητα, κράτηση ή ειδική παραγγελία."),
            ("Παραλαβή από το κατάστημα", "Γρήγορη συνεννόηση και εύκολη παραλαβή από τον χώρο μας."),
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

# Neutral fallback hero images (Unsplash) when the client has not uploaded photos yet.
_DEFAULT_HERO = {
    "wood": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1800&q=80",
    "food": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=1800&q=80",
    "medical": "https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=1800&q=80",
    "beauty": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=1800&q=80",
    "retail": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1800&q=80",
    "professional": "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1800&q=80",
    "trade": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=1800&q=80",
}

# Which layout suits each profession best (recommended first in chooser).
_LAYOUT_BY_PROFESSION = {
    "wood": "studio",
    "food": "studio",
    "medical": "atelier",
    "beauty": "bold",
    "retail": "bold",
    "professional": "trust",
    "trade": "commerce",
}


def recommend_layout(intake: dict[str, Any]) -> str:
    return _LAYOUT_BY_PROFESSION.get(_profession(intake), "studio")


# ---------------------------------------------------------------------------
# Smart-match: ποια React templates δείχνουμε στον πελάτη (sites/lib/templates)
# ---------------------------------------------------------------------------

# Όλα τα διαθέσιμα React archetypes (πρέπει να ταιριάζουν με TEMPLATE_KEYS στο index.js).
REACT_TEMPLATES = (
    "editorial", "split", "bento", "longform", "poster", "sidebar",
    "grid", "magazine", "warmth",
    "ember", "marble", "runway", "forge", "aegean", "bloom",
    "volt", "motor", "terra", "dispatch", "canvas",
    "cinematic", "type-gallery", "quiet", "kinetic", "infinite", "living",
)

# Λεπτομερέστερο vertical ΜΟΝΟ για template matching — δεν αγγίζει το _profession()
# (που τροφοδοτεί το _PROFESSION_COPY και θα έσκαγε με άγνωστο key).
_VERTICAL_RULES = (
    ("gym", ("γυμναστηρ", "gym", "fitness", "crossfit", "pilates", "yoga", "γιογκα", "προπονητ", "trainer")),
    ("garage", ("συνεργει", "φανοποι", "βουλκανιζ", "garage", "service αυτοκιν", "μηχανικ αυτοκιν", "ελαστικ")),
    ("farm", ("παραγωγ", "ελαιολαδ", "ελαιωνα", "μελισσοκομ", "μελι", "οινοποι", "κρασ", "τυροκομ", "αγροτ", "κτημα", "farm", "winery")),
    ("rooms", ("δωματ", "ξενωνα", "ξενοδοχ", "καταλυμ", "hotel", "rooms", "villa", "βιλα", "airbnb", "τουρισ")),
    ("cafe", ("καφε", "cafe", "coffee", "ζαχαροπλαστ", "φουρν", "αρτοποι", "bakery", "creperie", "κρεπερ", "παγωτ")),
    ("food", ("ταβερν", "εστιατορ", "taverna", "restaurant", "μεζε", "ψησταρι", "σουβλα", "grill", "pizza", "πιτσαρ", "μπαρ", "cocktail bar", "wine bar")),
    ("dentist", ("οδοντ", "dentist", "dental")),
    ("doctor", ("ιατρ", "doctor", "γιατρ", "κλινικ", "φυσικοθεραπ", "physio", "διαιτολογ", "ψυχολογ", "κτηνιατρ")),
    ("aesthetics", ("αισθητικ", "beauty clinic", "κεντρο ομορφια", "μακιγι", "laser αποτριχ")),
    ("massage", ("μασαζ", "massage", "spa", "wellness")),
    ("beauty", ("κομμωτ", "beauty", "hair", "salon", "barber", "κουρει", "νυχι", "νυχαδ", "μανικιουρ", "πεντικιουρ", "nail", "nixia", "nyxia", "nuxia")),
    ("retail", ("καταστημα", "retail", "store", "boutique", "μπουτικ", "ανθοπωλ", "λουλουδ", "ρουχ", "υποδημα", "παπουτσ", "κοσμημ", "οπτικ", "βιβλιοπωλ", "δωρα")),
    ("wood", ("ξυλουργ", "μαραγκ", "wood", "carpenter", "επιπλ", "κουζιν")),
    ("professional", ("δικηγ", "λογιστ", "lawyer", "accountant", "συμβουλ", "μηχανικ", "αρχιτεκτ", "μεσιτ", "ασφαλισ", "notary", "συμβολαιογρ")),
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


def _vertical(intake: dict[str, Any]) -> str:
    text = _normalize_text(" ".join(str(intake.get(k, "")) for k in ("type", "trade", "description", "name")))
    for vertical, words in _VERTICAL_RULES:
        if any(w in text for w in words):
            return vertical
    raw = " ".join(str(intake.get(k, "")) for k in ("type", "trade", "description")).strip()
    return (_vertical_by_ai(raw) if raw else None) or _VERTICAL_FALLBACK


# Premium-first σειρά ανά vertical. Το πρώτο = προτεινόμενο.
# Η σειρά λειτουργεί ως vertical ranking. Στον πελάτη δείχνουμε έως δώδεκα
# συμβατές και ουσιαστικά διαφορετικές επιλογές.
_TEMPLATES_BY_VERTICAL = {
    "food":         ["warmth", "ember", "magazine", "cinematic", "type-gallery", "living", "infinite", "quiet", "kinetic", "poster", "bloom", "aegean"],
    "cafe":         ["bloom", "type-gallery", "living", "infinite", "cinematic", "kinetic", "quiet", "warmth", "magazine", "poster", "ember", "bento"],
    "rooms":        ["aegean", "cinematic", "infinite", "living", "quiet", "canvas", "type-gallery", "kinetic", "grid", "marble", "magazine", "bloom"],
    "dentist":      ["marble", "quiet", "cinematic", "living", "grid", "infinite", "canvas", "type-gallery", "kinetic", "editorial", "bento", "split"],
    "doctor":       ["marble", "quiet", "editorial", "split", "cinematic", "grid", "living", "bento", "canvas", "sidebar", "infinite", "type-gallery"],
    "aesthetics":   ["bloom", "quiet", "marble", "runway", "living", "cinematic", "type-gallery", "bento", "infinite", "canvas", "magazine", "poster"],
    "massage":      ["living", "quiet", "aegean", "bloom", "warmth", "cinematic", "infinite", "canvas", "marble", "type-gallery", "terra", "magazine"],
    "beauty":       ["runway", "type-gallery", "living", "cinematic", "infinite", "kinetic", "quiet", "bloom", "canvas", "magazine", "poster", "bento"],
    "retail":       ["runway", "type-gallery", "bento", "infinite", "bloom", "canvas", "cinematic", "quiet", "kinetic", "grid", "magazine", "living"],
    "professional": ["marble", "quiet", "cinematic", "grid", "infinite", "canvas", "type-gallery", "living", "kinetic", "editorial", "sidebar", "bento"],
    "trade":        ["dispatch", "kinetic", "grid", "type-gallery", "infinite", "cinematic", "quiet", "living", "canvas", "forge", "poster", "bento"],
    "garage":       ["motor", "kinetic", "grid", "infinite", "type-gallery", "cinematic", "quiet", "living", "canvas", "volt", "forge", "poster"],
    "gym":          ["volt", "kinetic", "type-gallery", "infinite", "runway", "grid", "cinematic", "living", "quiet", "poster", "bento", "motor"],
    "farm":         ["terra", "living", "quiet", "cinematic", "canvas", "infinite", "type-gallery", "kinetic", "grid", "editorial", "magazine", "warmth"],
    "wood":         ["canvas", "runway", "grid", "cinematic", "type-gallery", "quiet", "kinetic", "infinite", "living", "forge", "editorial", "magazine"],
}


def recommend_templates(intake: dict[str, Any], limit: int = 12) -> list[str]:
    """Έως δώδεκα ranked React προτάσεις, με την καταλληλότερη πρώτη."""
    keys = _TEMPLATES_BY_VERTICAL.get(_vertical(intake), _TEMPLATES_BY_VERTICAL["trade"])
    return [k for k in keys if k in REACT_TEMPLATES][:limit]


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    return [v for v in value if isinstance(v, dict)] if isinstance(value, list) else []


def normalize(intake: dict[str, Any]) -> dict[str, Any]:
    prof = _profession(intake)
    copy = _PROFESSION_COPY[prof]

    name = _e(intake.get("name") or intake.get("business_name") or "Η Επιχείρησή σας")
    city = _e(intake.get("city") or intake.get("area") or "Αθήνα")
    trade = _e(intake.get("trade") or intake.get("type") or copy["kicker_suffix"])
    phone_raw = str(intake.get("phone") or intake.get("telephone") or "").strip()
    phone_digits = re.sub(r"\D", "", phone_raw)
    phone_intl = phone_digits if phone_digits.startswith("30") else ("30" + phone_digits if phone_digits else "")
    phone_disp = _e(phone_raw or "—")
    tagline = _e(intake.get("tagline") or intake.get("style") or "Ποιότητα και προσοχή στη λεπτομέρεια.")

    areas_raw = intake.get("areas")
    areas = [_e(a) for a in areas_raw if str(a).strip()] if isinstance(areas_raw, list) else [city]
    areas_str = " · ".join(areas[:4])

    domain = str(intake.get("site_url") or intake.get("url") or intake.get("domain") or "").strip()
    domain_disp = re.sub(r"^https?://", "", domain).rstrip("/") if domain else ""

    # services
    svc_src = _list_of_dicts(intake.get("services"))
    if svc_src:
        services = [
            {"title": _e(s.get("SERVICE_NAME") or s.get("name") or s.get("title") or "Υπηρεσία"),
             "desc": _e(s.get("SERVICE_DESC") or s.get("description") or s.get("desc") or "")}
            for s in svc_src
        ]
    else:
        services = [{"title": _e(t), "desc": _e(d)} for t, d in copy["services"]]
    services = services[:6]
    for i, s in enumerate(services):
        s["num"] = f"{i + 1:02d}"
        s["icon"] = _ICONS[i % len(_ICONS)]

    # gallery
    gal_src = _list_of_dicts(intake.get("gallery"))
    gallery = [
        {"image": _asset(str(g.get("image", ""))),
         "title": _e(g.get("title") or "Έργο"),
         "sub": _e(g.get("sub") or g.get("alt") or city)}
        for g in gal_src if str(g.get("image", "")).strip()
    ][:8]

    _fallback_hero = _DEFAULT_HERO.get(prof, _DEFAULT_HERO["trade"])
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
        reviews = [
            {"text": "Καθαρή δουλειά, στην ώρα του και σωστές τιμές. Το συνιστώ ανεπιφύλακτα.",
             "author": "Μαρία Κ.", "area": areas[0] if areas else city, "initials": "ΜΚ"},
            {"text": "Άνθρωπος με μεράκι — το αποτέλεσμα ξεπέρασε τις προσδοκίες μου.",
             "author": "Γιώργος Π.", "area": (areas[1] if len(areas) > 1 else city), "initials": "ΓΠ"},
            {"text": "Μου εξήγησε τα πάντα καθαρά, καμία κρυφή χρέωση. Θα τον ξαναφωνάξω.",
             "author": "Ελένη Δ.", "area": (areas[2] if len(areas) > 2 else city), "initials": "ΕΔ"},
        ]

    story_default = [
        f"Ο/Η {name} δουλεύει με μεράκι στην περιοχή {city}. Κάθε δουλειά ξεκινά με μια κουβέντα για το τι πραγματικά χρειάζεσαι.",
        "Χωρίς έτοιμες λύσεις, χωρίς κρυφές χρεώσεις — καθαρή τιμή, ποιοτικά υλικά και συνέπεια στον χρόνο.",
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
        "ADDRESS": _e(str(intake.get("address") or "")),
        "GEO_LAT": str(intake.get("geo_lat") or ""),
        "GEO_LNG": str(intake.get("geo_lng") or ""),
        "GBP_URL": _e(str(intake.get("gbp_url") or "")),   # Google Business Profile
        "PHONE": phone_disp, "PHONE_INTL": phone_intl,
        "AREAS": areas_str, "DOMAIN": _e(domain_disp), "DOMAIN_URL": _e(domain or "#"),
        "HOURS": _e(intake.get("hours") or "Δευτ.–Σάβ. 08:00–19:00"),
        "KICKER": f"{trade} · {city}",
        "HERO_WORD": copy["hero_word"],
        "HERO_IMAGE": hero_image, "STORY_IMAGE": story_image,
        "STORY_TITLE": _e(intake.get("story_title") or "Ένας άνθρωπος που ακούει πρώτα."),
        "CTA_TITLE": _e(intake.get("cta_title") or "Πες μας τι έχεις στο μυαλό σου."),
        "INTRO": _e(intake.get("intro") or tagline),
        "YEAR": "2026",
        "services": services, "gallery": gallery, "reviews": reviews, "story": story_paras,
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
