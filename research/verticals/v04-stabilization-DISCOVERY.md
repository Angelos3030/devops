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
