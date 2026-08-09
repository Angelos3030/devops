---
name: vitrina-theme-builder
description: Build a new production-ready Vitrina theme from a reference website URL. Use whenever the owner sends "New theme | Vertical: X | Reference: URL", sends a reference site to turn into a theme, or asks for a new template for the Vitrina collection. Enforces machine-first capture, compact analysis with explicit approval before code, and distillation of enterprise patterns down to SMB scale.
---

# Vitrina Theme Builder

**Trigger:** `New theme | Vertical: dentist | Reference: https://…`

Τίποτα άλλο δεν χρειάζεται. Αυτό το skill είναι όλη η διαδικασία.

> Extract the best design patterns, discard enterprise complexity, build the best possible SMB theme.

## Low-token κανόνες

- Homepage **μόνο**. Κανένα crawl, εκτός αν το ζητήσει ρητά.
- Διάβασε **2 screenshots** (desktop, mobile). Το tablet μόνο αν κάτι δεν βγάζει νόημα.
- Διάβασε **`reference.json`**, όχι το πλήρες `measurements.json`.
- Μην ξαναδιαβάζεις αρχεία που ήδη ξέρεις και δεν άλλαξαν.
- Μην εξηγείς ξανά αρχιτεκτονική, μην επαναλαμβάνεις το protocol, μην γράφεις status reports.
- Μόνο ό,τι χρειάζεται για **απόφαση ή implementation**.

## 1. Capture

```bash
node sites/scripts/capture_reference.mjs <url> --name <slug> --compact
```

Γράφει εκτός repo: `desktop/tablet/mobile.png` + `reference.json` (colors, fonts, type scale,
spacing, containers, radii, shadows, breakpoints, sections, sticky, interactions).

Δεν φορτώνει (login/bot) → σταμάτα, ζήτα screenshots.

## 2. Analysis — ΜΟΝΟ αυτό το format

```
Keep:
Adapt:
Discard:
Sections:
Design tokens:
Customizable:
Locked:
Risks/constraints:
```

**Keep** = αξία και σε μικρή επιχείρηση, αυτούσιο.
**Adapt** = καλή ιδέα, λάθος κλίμακα — γράψε το *γιατί*.
**Discard** = υπάρχει μόνο επειδή είναι enterprise/portal.

Έλεγχος: *μπορεί ένας Έλληνας οδοντίατρος με 6 υπηρεσίες και 8 φωτογραφίες να το γεμίσει;*
Όχι → Discard ή Adapt. Ποτέ Keep.

Discard κατά κανόνα: portal nav, βιβλιοθήκες περιεχομένου, ευρετήρια προσωπικού, δεκάδες
τοποθεσίες, login, ζώνες με στήλες από links, footer 40+ links.

### Μόνιμα Adapt — εγκεκριμένα, μη ρωτάς ξανά

Ισχύουν σε **κάθε** reference, ακόμα κι αν το reference κάνει το αντίθετο:

- **Hero πάντα με primary CTA** (το `CLAUDE.md` το απαιτεί στο πρώτο viewport)
- **Sticky nav**, ακόμα κι αν το reference δεν έχει
- **Ρυθμός section 90px** αντί για τον σφιχτότερο enterprise ρυθμό
- **Carousel/λίστες τοποθεσιών → gallery πελάτη**
- **Hero όχι full-screen** — να φαίνεται η επόμενη ενότητα

**Σταμάτα. Περίμενε approval.** Ούτε μία γραμμή κώδικα πριν.

Αν η δομή ταυτίζεται με υπάρχον theme → πες το τώρα.

## 3. Build

Πιστότητα σε: layout, αναλογίες, spacing, ιεραρχία, type scale, responsive, interaction model.
Καμία «βελτίωση» πέρα από τα δηλωμένα Adapt.

**Ποτέ** proprietary κώδικας, logo, κείμενα, φωτογραφίες. Μόνο σχεδιαστική λογική.
Captures **εκτός repo**.

Data contract (`sites/lib/templates/`):
```
NAME TRADE CITY AREAS PHONE PHONE_INTL ADDRESS HOURS YEAR LOGO INITIAL
KICKER TAGLINE INTRO HERO_TITLE HERO_WORD HERO_IMAGE STORY_IMAGE STORY_TITLE
SERVICES_TITLE SERVICES_EYEBROW SERVICES_NAV GALLERY_TITLE GALLERY_EYEBROW
CTA_TITLE PRIMARY_CTA SECONDARY_CTA SIGNATURE BOOKING_URL GBP_URL GEO_LAT GEO_LNG
services[{title,desc}]  story[{p}]  gallery[{image,title}]
```
Shared: `FindUs`, `CallBar`, `Brand`. Μηδέν hardcoded business δεδομένα.

## 4. Metadata (ο editor οδηγείται από εδώ, ποτέ από hardcoded conditions)

Στο `TEMPLATE_META` (`sites/lib/templates/index.js`):

```js
'theme-id': {
  label: '…', desc: '…', category: 'health', style: 'clinical-calm',
  customizable: { palette: true, fontPair: false },
  variants: { hero: ['image-left', 'image-right'] },
  sections: ['hero', 'triage', 'services', 'gallery', 'ribbon', 'findus'],
  requiredAssets: { minGallery: 3 },
  imageRatios: { hero: '16/9', gallery: '3/2' },
  tokens: { display: '…', body: '…', accent: '#…' },
}
```

`customizable: false` = το theme **σπάει** με άλλη τιμή. Να είσαι ειλικρινής.
Εγγραφή σε `TEMPLATES`, `TEMPLATE_KEYS`, `TEMPLATE_META` (+ `artDirection.js` αν έχει gallery).

## 5. Αρχιτεκτονική

Δεν αλλάζει για να χωρέσει theme. Πραγματικό limitation → σταμάτα, εξήγησε, πρότεινε τη
**μικρότερη** αλλαγή, περίμενε έγκριση.

## 6. Quality gate

```bash
node sites/tests/design_guard.mjs
cd sites && npx next build
```
Πιστό στο reference · 1440/768/390 χωρίς overflow · όμορφο με άλλα δεδομένα · μηδέν
copyrighted assets · μηδέν third-party requests · tap targets ≥44px · ένα `h1` · CTA/`tel:` λειτουργικά.

Αν νέο theme ξεπερνά υπάρχον αδύναμο → **πρότεινε** μετακίνηση στο `LEGACY_TEMPLATE_KEYS`.
Μην το κάνεις μόνος σου.
