# -*- coding: utf-8 -*-
"""ΚΑΝΟΝΙΚΗ ΠΗΓΗ — τι μπορεί να αλλάξει ο πελάτης, ανά theme.

Μία εγγραφή ανά εμπορικό theme. Δεν αντιγράφεται πουθενά αλλού: το
`scripts/apply_theme_library.py` το μεταφράζει ΚΑΙ στο frontend registry
(`sites/lib/templates/index.js`) ΚΑΙ στο backend (`src/theme_capabilities.py`).
Αν τα δύο αποκλίνουν, το `tests/test_theme_capabilities.py` κόβει.

ΠΩΣ ΠΡΟΕΚΥΨΕ. Οπτική αξιολόγηση 58 themes × αρχικό + 2 παλέτες, desktop και
mobile, με το demo business του δικού του vertical (CLAUDE.md §7β). Η αντίθεση
είχε ήδη επαληθευτεί 0/58 σε 6 παλέτες × 2 viewports πριν γίνει η κρίση:
κανένα theme δεν αποκλείεται για λόγους προσβασιμότητας — μόνο για ταυτότητα.

  A  η παλέτα διαβάζεται ως σκόπιμη σχεδίαση      -> και οι 5
  B  μόνο ορισμένες οικογένειες στέκουν οπτικά    -> υποσύνολο
  C  η αλλαγή είναι αόρατη ή καταστρέφει ταυτότητα-> κανένας έλεγχος
"""

ALL_PALETTES = ("warm", "forest", "ocean", "rose", "mono")
ALL_PAIRS = ("editorial", "modern", "friendly", "classic")
# Η τυπογραφία δεν είναι ναι/όχι: 32 themes έχουν ΜΙΑ όψη — δεν υπάρχει
# ξεχωριστή γραμματοσειρά τίτλων, άρα τα ζεύγη που αλλάζουν μόνο τίτλους
# (editorial, classic) δεν έχουν πού να φανούν. Μετρήθηκε ανά ζεύγος.

CAPABILITIES = {
    # ── ΚΑΤΗΓΟΡΙΑ Α — και οι πέντε παλέτες ──────────────────
    'airspace-office': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'area-first': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'bakery-editorial': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'bigspring-advisory': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'billys-barber': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'bloom': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'blue-onepage': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'callout': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'canvas': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'clinic-triage': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'directory-index': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'educenter-campus': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'elegance-salon': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'ember': {
        "class": 'A', "mode": 'dark',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'freight-lane': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'frost-bakery': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'grecko-table': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'horizontal-story': {
        "class": 'A', "mode": 'dark',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'klassy-cafe': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('friendly',),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'living': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'marble': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'medic-care': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'microbakery-lab': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'motor': {
        "class": 'A', "mode": 'dark',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'novena-care': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'price-first': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'property-atlas': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'pulse': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'quiet': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'runway': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'signature': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'terra': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'thomson-stylist': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'type-gallery': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'vex-counter': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    'villa-agency': {
        "class": 'A', "mode": 'light',
        "palettes": ALL_PALETTES,
        "typography": ('modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα διαβάζεται ως σκόπιμη σχεδίαση',
    },
    # ── ΚΑΤΗΓΟΡΙΑ Β — μόνο το εγκεκριμένο υποσύνολο ─────────
    'barber-shop': {
        "class": 'B', "mode": 'light',
        "palettes": ('warm', 'rose'),
        "typography": ('modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'duotone· το πράσινο κομμωτήριο δεν στέκει',
    },
    'beauty-atelier': {
        "class": 'B', "mode": 'light',
        "palettes": (),
        "typography": ('editorial', 'modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η αλλαγή είναι πολύ αδύναμη για να δικαιολογεί έλεγχο',
    },
    'clean-work': {
        "class": 'B', "mode": 'light',
        "palettes": ('warm', 'rose', 'ocean'),
        "typography": ('modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'duotone στη φωτογραφία· το πράσινο θολώνει',
    },
    'counter-menu': {
        "class": 'B', "mode": 'dark',
        "palettes": ('mono', 'forest'),
        "typography": ('modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'το neon κίτρινο ΕΙΝΑΙ η ταυτότητα· χάνεται',
    },
    'forge': {
        "class": 'B', "mode": 'light',
        "palettes": ('warm',),
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η κίτρινη ταινία κινδύνου εξαφανίζεται — υπογραφή του theme',
    },
    'gymso-fitness': {
        "class": 'B', "mode": 'light',
        "palettes": ('warm', 'rose', 'mono'),
        "typography": ('modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα βάφει ΤΗ ΦΩΤΟΓΡΑΦΙΑ (duotone)· το πράσινο γυμναστήριο ξενίζει',
    },
    'heritage-bakery': {
        "class": 'B', "mode": 'light',
        "palettes": ('warm', 'forest'),
        "typography": ('modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'το κρεμ γίνεται ροζ και η παράδοση απαλύνει',
    },
    'kinetic': {
        "class": 'B', "mode": 'light',
        "palettes": ('warm', 'mono'),
        "typography": ('friendly',),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'το lime ΔΕΝ ακολουθεί· ροζ τίτλος με lime κουμπιά χτυπάει',
    },
    'morning-journal': {
        "class": 'B', "mode": 'light',
        "palettes": ('warm', 'rose'),
        "typography": ('modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η ζεστασιά του «φούρνου της γειτονιάς» ξεθωριάζει',
    },
    'moso-interior': {
        "class": 'B', "mode": 'light',
        "palettes": ('warm', 'rose'),
        "typography": ('modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η φωτογραφία παίρνει απόχρωση· το χρυσό kicker υποχωρεί',
    },
    'neighborhood-market': {
        "class": 'B', "mode": 'light',
        "palettes": ('warm', 'rose'),
        "typography": ('modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παιχνιδιάρικη ένταση χάνεται· το πράσινο ξενίζει',
    },
    'volt': {
        "class": 'B', "mode": 'dark',
        "palettes": ('mono',),
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'το neon lime ΕΙΝΑΙ το «volt»',
    },
    # ── ΚΑΤΗΓΟΡΙΑ Γ — χωρίς έλεγχο παλέτας ──────────────────
    'aegean': {
        "class": 'C', "mode": 'light',
        "palettes": (),
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'μόνο η πλάκα και το κουμπί — η ταυτότητα είναι η φωτογραφία',
    },
    'chapter-snap': {
        "class": 'C', "mode": 'light',
        "palettes": (),
        "typography": ('modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'το ηλεκτρικό μπλε ΔΕΝ ακολουθεί — ροζ μπάρα με μπλε μπλοκ χτυπάει',
    },
    'cinematic': {
        "class": 'C', "mode": 'dark',
        "palettes": (),
        "typography": ('editorial', 'modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η αλλαγή είναι ανεπαίσθητη — το πιάτο κυριαρχεί',
    },
    'coast': {
        "class": 'C', "mode": 'light',
        "palettes": (),
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'μόνο το κουμπί — η ταυτότητα είναι η φωτογραφία',
    },
    'constra-build': {
        "class": 'C', "mode": 'light',
        "palettes": (),
        "typography": ('modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'μόνο το κουμπί αλλάζει· η σελίδα είναι φωτογραφία',
    },
    'dispatch': {
        "class": 'C', "mode": 'dark',
        "palettes": (),
        "typography": ('modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η αλλαγή είναι ανεπαίσθητη στη σελίδα',
    },
    'infinite': {
        "class": 'C', "mode": 'dark',
        "palettes": (),
        "typography": ('editorial', 'modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'καμία ορατή διαφορά',
    },
    'scandinavian-coffee': {
        "class": 'C', "mode": 'light',
        "palettes": (),
        "typography": ('modern', 'friendly'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'μόνο ένα σήμα αλλάζει· κενή υπόσχεση',
    },
    'vertical-snap': {
        "class": 'C', "mode": 'dark',
        "palettes": (),
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'η παλέτα δεν φαίνεται — η φωτογραφία καλύπτει τα πάντα',
    },
    'warmth': {
        "class": 'C', "mode": 'light',
        "palettes": (),
        "typography": ('editorial', 'modern', 'friendly', 'classic'),   # οριστικοποιείται στο Phase 3
        "logo": True,
        "why": 'μόνο το κουμπί αλλάζει',
    },
}


def get(theme_id):
    """Οι δυνατότητες ενός theme. Άγνωστο id -> τίποτα επιτρεπτό."""
    c = CAPABILITIES.get(theme_id)
    if not c:
        return {"class": "C", "palettes": (), "typography": False, "logo": True,
                "why": "άγνωστο theme"}
    return c
