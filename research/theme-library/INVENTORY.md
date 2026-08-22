# Απογραφή & ενσωμάτωση βιβλιοθήκης themes — Vitrina

Ημερομηνία: 2026-08-22 · **ολοκληρωμένο**

## Τελικοί αριθμοί

```
RENDERABLE_IDS      = 68
COMMERCIAL_THEMES   = 58
QA_PASS             = 67 / 68   (μόνο το `split` κόπηκε)
LIVE_IN_SELECTOR    = 58
ARCHETYPES_INTERNAL = 10
BLOCKED             =  1   (`split` — μηδέν h1)
MASTER_PROMOTED     =  0   (3 παραμένουν εσωτερικά, τεκμηριωμένα)
```

## Τι ήταν σπασμένο και διορθώθηκε

| # | πρόβλημα | κατάσταση |
|---|---|---|
| 1 | `LAUNCH_REACT_TEMPLATES` = allowlist 12 θέσεων· 46 έτοιμα themes αόρατα | **58 πλέον προσφέρονται** |
| 2 | 15 themes αποδίδονταν αλλά το `/select-design` απαντούσε **HTTP 400** | **0 πλέον αποτυγχάνουν** |
| 3 | 31 themes χωρίς όνομα — θα φαίνονταν με ωμό id (`vex-counter`) | **0 ωμά ids στον selector** |
| 4 | 10 περιγραφές διέρρεαν υλοποίηση («Πιστό port … Templatemo») | **ξαναγράφτηκαν** |
| 5 | 36 ονόματα λατινικά, όχι ελληνικά | **58 ελληνικά ονόματα** |
| 6 | 9 themes χωρίς κατηγορία· κατηγορίες ήταν 17 εσωτερικά slugs με διπλοεγγραφή (`trade`/`trades`) | **9 εμπορικές κατηγορίες** |
| 7 | Ο πελάτης δεν είχε τρόπο να δει τη βιβλιοθήκη πέρα από τις προτάσεις | **«Δες όλα τα σχέδια (58)» + φίλτρο** |
| 8 | Τα Master themes αποδίδονταν ΠΑΝΤΑ με δεδομένα `rooms` | **το route δέχεται `?biz=`** |

## Ταξινόμηση

**A. Εμπορικά (58)** — ελληνικό όνομα, περιγραφή, κατηγορία, QA ✓, στον selector.

**B. Αρχέτυπα συμβατότητας (10)** — `editorial` `split` `showcase` `bento`
`longform` `corporate` `poster` `sidebar` `grid` `magazine`. Στόχοι του `MAP`
για τα legacy backend layout names και fallback του `pickTemplate()`. Υποδομή,
όχι προϊόν. Σημαίνονται `internal: true`, ποτέ στο `COMMERCIAL_THEMES`.

**C. Proof / πειραματικά (3)** — δεν προάγονται, με λόγο ανά περίπτωση:

| theme | έλεγχος με σωστό vertical | απόφαση |
|---|---|---|
| `MasterCinematic` | ✓ ταβέρνα, ✓ κομμωτήριο | εσωτερικό: οριζόντιο drag-scroll, μη επικυρωμένο για SMB· id συγκρούεται με το εμπορικό `cinematic` |
| `MasterEditorial` | ✗ **οδοντιατρείο: οριζόντια υπερχείλιση 1797 / 1440** | μπλοκαρισμένο σε σφάλμα |
| `MasterSpatial` | ✓ δωμάτια, ✓ ξυλουργός | εσωτερικό: ίδιο ρίσκο drag-scroll |

Για προαγωγή χρειάζονται: μετονομασία id (`master-*`), διόρθωση της
υπερχείλισης στο editorial, και product review του drag-scroll.

**D. Μπλοκαρισμένα (1)** — `split`: **μηδέν `h1`**. Είναι αρχέτυπο, οπότε δεν
εκτίθεται· το σφάλμα καταγράφεται.

## Ροή που επαληθεύτηκε

```
/choose/[client]
  ├─ «Προτεινόμενα για σένα (N)»   smart-match ανά vertical, 10–12
  └─ «Δες όλα τα σχέδια (58)»      πλήρης εγκεκριμένη βιβλιοθήκη
       └─ φίλτρο 9 κατηγοριών με πλήθος
            └─ κάρτα: ζωντανό preview ΜΕ ΤΑ ΔΕΔΟΜΕΝΑ ΤΟΥ ΠΕΛΑΤΗ,
               ελληνικό όνομα, chip κατηγορίας, περιγραφή
                 └─ επιλογή → POST /select-design → 58/58 γίνονται δεκτά
```

Το smart-match **δεν** καταργήθηκε: εξακολουθεί να επιστρέφει 10–12 σχετικά ανά
vertical. Η πλήρης βιβλιοθήκη είναι δεύτερη, ρητή διαδρομή.

## Επαληθεύσεις

- `node sites/tests/templateRegistry.mjs` → 64 themes × 4 σημεία εγγραφής ✓
- `npx next build` → Compiled successfully, 22/22 static pages ✓
- QA 68 themes σε production URL, desktop + mobile, με το demo business του
  **δικού του** vertical (CLAUDE.md §7β)
- E2E στον selector: 58 κάρτες, 9 κατηγορίες, φίλτρο, επιλογή, **0 ωμά ids,
  0 console errors**
- `/select-design`: 58/58 περνούν τον έλεγχο (πριν: 15 θα έδιναν 400)

## Αρχεία

| αρχείο | ρόλος |
|---|---|
| `research/theme-library/catalog.py` | **πηγή αλήθειας** — ονόματα, περιγραφές, κατηγορίες |
| `scripts/apply_theme_library.py` | γράφει frontend META + backend λίστες |
| `scripts/theme_library.py` | ταξινόμηση και μετρήσεις |
| `sites/artifacts/theme-qa.mjs` | QA ανά theme με σωστό vertical |
| `research/theme-library/qa.json` · `shots/` | αποτελέσματα + 68 στιγμιότυπα |
| `research/theme-library/TABLE.md` | πίνακας 58 themes προς παρουσίαση |

Το `catalog.py` είναι το μόνο σημείο που γράφεται με το χέρι. Το
`TEMPLATE_META` παράγεται — μην το επεξεργάζεσαι απευθείας.
