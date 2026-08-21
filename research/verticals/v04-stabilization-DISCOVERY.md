# Stabilization discovery — 3 νέες πηγές (2026-08-21)

**Στόχος:** τρία μοντέρνα (2024–2026), εμπορικά ασφαλή, vertical-specific sources
από **διαφορετικές οικογένειες**, ως αδοκίμαστες περιπτώσεις σταθεροποίησης.

**Αποτέλεσμα: 0 από 3 πέρασαν τον πήχη.** Ο πήχης δεν κατέβηκε.

## Τι μετρήθηκε

Δύο ανεξάρτητα περάσματα συμφώνησαν: χειροκίνητη επαλήθευση (curl, HTTP 200,
ημερομηνίες από `<meta>`) και DeepSeek research worker (`research/stabilization-3/`,
21 υποψήφιοι, $0,012). Και τα δύο κατέληξαν στο ίδιο.

### Το «μοντέρνο» και το «επαγγελματικό» έχουν αποκλίνει

| template | ημερομηνία | τομέας |
|---|---|---|
| tm-630-helix-drift | 2026-07-22 | gallery |
| tm-629-nexus-system | 2026-07-15 | industrial tech |
| tm-628-lumen-eighty | 2026-07-15 | editorial / furniture |
| tm-623-novapay | 2026-05-09 | fintech |
| tm-622-clearwave | 2026-05-06 | SaaS |
| tm-621-luminary | 2026-05-05 | SaaS B2B |
| tm-620-compression | 2026-05-04 | portfolio |
| tm-619-axis-industrial | 2026-04-26 | corporate/industrial |

Τα **τοπικά επαγγέλματα** έχουν παλιά templates:

| template | ημερομηνία | framework |
|---|---|---|
| tm-463-motor (συνεργείο) | **2015-07-17** | Bootstrap 3.3.4 |
| tm-548-training-studio (γυμναστήριο) | 2020-02-24 | Bootstrap 4.3.1 |
| tm-580-woox-travel | 2022-09-09 | Bootstrap 5.2.0 |
| tm-587-tiya-golf-club | 2023-02-20 | Bootstrap 5.3.0 |

Το ίδιο και στο tooplate: τα νεότερα (2161–2168) είναι fashion, 3D gallery,
developer portfolio, SaaS dashboard, boutique e-commerce.

## Δύο ευρήματα υποδομής

**Τα tooplate tags είναι soft 404.** Τα `/tag/spa`, `/tag/law`, `/tag/hotel`,
`/tag/farm` επιστρέφουν όλα **τα ίδια 32 αποτελέσματα** — δεν φιλτράρουν. Μόνο
το templatemo έχει αληθινά επαγγελματικά tags (`automobile`, `travel`,
`health-fitness`, `education`, `restaurant`, `cafe`).

**Το Untree.co άλλαξε καθεστώς.** Το `untree.co/templates/` κάνει 301 στο
`untree.co/`, και η σελίδα προωθεί demos `bootstrapmade.com/demo/*` (Blogy,
Invent, Logis, TheProperty, TravelTime, UpConstruction, iLanding, MinimalFolio).
Η δωρεάν άδεια BootstrapMade **απαιτεί απόδοση**, άρα απαγορεύεται για πληρωμένη
δουλειά πελάτη. Το Untree υποβαθμίζεται από «CC BY 3.0 → LICENSE_REVIEW» σε
**LICENSE_BLOCKED ecosystem** μέχρι νεότερη επαλήθευση.

**Το Start Bootstrap** σερβίρει Angular SPA (13KB κέλυφος)· ο κατάλογος δεν
διαβάζεται με curl. Άδεια MIT — η καλύτερη — αλλά ο source map ήδη το καταγράφει
ως γενικό (agency/business/portfolio), όχι vertical-specific.

## Τι ΔΕΝ έγινε

Δεν κατέβηκε ο πήχης για να συμπληρωθεί ο αριθμός τρία. Δεν χρησιμοποιήθηκαν
aggregators, δεν ξαναεξετάστηκαν ήδη ταξινομημένοι υποψήφιοι, δεν έγινε ευρεία
σάρωση 100 πηγών.

## Επιλογές που μένουν στον ιδιοκτήτη

1. **Χαλάρωση μόνο της ημερομηνίας** σε Bootstrap 5 του 2022–2023: δίνει αμέσως
   `tm-580-woox-travel` (hospitality→rooms) και `tm-587-tiya-golf-club`. Το
   σχέδιο είναι σύγχρονο· μόνο η χρονολογία δεν είναι.
2. **Νέο οικοσύστημα** με έλεγχο άδειας (π.χ. HTML5 UP — CC BY 3.0, ή αγορά
   άδειας BootstrapMade Pro).
3. **Αποδοχή** ότι η δεύτερη επιβεβαίωση σταθερότητας θα προκύψει μέσα από ένα
   περιορισμένο night batch αντί από ξεχωριστά stabilization sources.


---

# Δεύτερο πέρασμα (2026-08-21) — κάλυψη του κενού tm-588…618

Η πρώτη σάρωση είχε **κενό**: εξέτασε τα tm-619…630 (2026) και μερικά παλιά με
tags, αλλά ποτέ το ενδιάμεσο εύρος — ακριβώς εκεί που θα ζούσε το «μοντέρνο +
επαγγελματικό». Καλύφθηκε, μαζί με τρία οικοσυστήματα που δεν είχαν διαβαστεί.

## Τι βρέθηκε στο κενό

| template | ημερομηνία | τομέας | κρίση |
|---|---|---|---|
| **tm-611-maison-doree** | **2026-02-12** | κοσμηματοπωλείο | **PORT_OK** |
| tm-610-aurum-gold | 2026-02-01 | επενδύσεις σε χρυσό | DEMO_SEMANTICALLY_UNSUPPORTED |
| tm-599-noir-fashion | 2025-10-18 | fashion label | retail, ίδια οικογένεια με moso |
| tm-613-frost-bakery | — | ήδη περασμένο | — |

Τα υπόλοιπα του εύρους: SaaS, crypto, admin, portfolio, christmas.

## Τρία οικοσυστήματα που ελέγχθηκαν και αποκλείστηκαν

**Start Bootstrap** (MIT — η καλύτερη άδεια): ο κατάλογος αποδόθηκε με Playwright
αντί για curl. Είναι admin/agency/portfolio, καμία τοπική επιχείρηση. Ο source
map το είχε ήδη προβλέψει.

**GitHub API** με `license:mit`, στοχευμένα ανά επάγγελμα: επιστρέφει
αποτελέσματα, αλλά όλα ★0–2 από άγνωστους λογαριασμούς. Το `ngx-horeca`
εμφανίζεται σε **τέσσερα διαφορετικά orgs με πανομοιότυπη περιγραφή** —
καθρεφτισμός. Ένα αρχείο MIT που ανέβασε κάποιος ο οποίος δεν κατέχει τον κώδικα
**δεν παραχωρεί τίποτα**· είναι ακριβώς το «commercial-site clone concern». Ο
source map είχε ήδη μετρήσει 0/30 σε γενική αναζήτηση GitHub.

**Untree.co**: βλ. πρώτο πέρασμα — πλέον προωθεί BootstrapMade, LICENSE_BLOCKED.

## Ο ένας υποψήφιος που πέρασε

```
SOURCE_ID:        maison-doree
VERTICAL:         retail (κοσμηματοπωλείο / boutique)
VERTICAL_FAMILY:  retail
REPO_URL:         https://templatemo.com/tm-611-maison-doree
LIVE_DEMO_URL:    https://templatemo.com/templates/templatemo_611_maison_doree/index.html
LICENSE:          templatemo — «free to download for anyone», «commercial or
                  non-commercial sites», αφαίρεση credit επιτρεπτή
LAST_UPDATE:      2026-02-12
VISUAL_MODERNITY: υψηλή — 7810px, 15 εικόνες, 0 σπασμένες, 1 h1
DESIGN_DNA:       editorial πολυτελείας· ασύμμετρο hero, πίνακας προδιαγραφών
                  προϊόντος, masonry συλλογές, σκούρα ενότητα κληρονομιάς με
                  υπογραφή ιδρυτή, split craftsmanship με αριθμητικά πλακίδια
DEMO_BUSINESS:    retail
SEMANTIC_COMPATIBLE: ΝΑΙ (retail → retail)
```

**Γιατί είναι καλή περίπτωση σταθεροποίησης:** η δομή του διαφέρει ουσιωδώς από
ό,τι έχει περαστεί (split hero φαγητού, utility trades, full-bleed retail,
sidebar κομμωτηρίου). Επιπλέον **πιέζει σκόπιμα τις πύλες αλήθειας**: έχει τιμή
προϊόντος $4.850, πίνακα προδιαγραφών, τρία testimonials με ονόματα και αστέρια,
και φόρμα ραντεβού. Όλα αυτά πρέπει να αφαιρεθούν ή να αποδοθούν υπό συνθήκη —
ακριβώς ο μηχανισμός που θέλουμε να δοκιμάσουμε.

**Ρίσκο πιστότητας:** επειδή τόσο μεγάλο μέρος του DNA είναι
UNSUPPORTED_BY_PRODUCT, το τελικό theme μπορεί να βγει αισθητά πιο αραιό από το
πρωτότυπο. Αυτό είναι κρίση προϊόντος, όχι σφάλμα.

## Κατάσταση

**1 από 3.** Δεν κατέβηκε ο πήχης και δεν έγινε port — ο κανόνας λέει ότι δεν
ξεκινά κανένα port πριν επιλεγούν και τα τρία.
