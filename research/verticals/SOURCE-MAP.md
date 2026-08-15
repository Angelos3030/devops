# Source map — πριν από κάθε discovery

**Ημερομηνία:** 2026-08-15
**Γιατί υπάρχει:** τα V1/V2/V3 έψαξαν σε κατάλογο **γενικών agency templates** και
έδωσαν 24 υποψήφιους με **0 PORT_OK**. Το πρόβλημα δεν ήταν το φίλτρο· ήταν η πηγή.

## Κανόνας πηγών (νέος, δεσμευτικός)

1. **Vertical-specific πρώτα.** Κατάλογος ή σελίδα αφιερωμένη στο επάγγελμα.
2. **Γενικά agency/business templates ΔΕΝ μπαίνουν** σε batch vertical, εκτός αν
   η **αποδοσμένη** αρχιτεκτονική ήδη ταιριάζει χωρίς δομικό επανασχεδιασμό.
3. **Καμία επανεξέταση** ήδη ταξινομημένων (βλ. `CANDIDATE-CLASSIFICATION.md`).
4. **Τα URL επαληθεύονται πριν** σταλούν στο DeepSeek — μία πηγή ανά κλήση.

## Αποκλεισμένα οικοσυστήματα (ανά vertical, μετά τη μέτρηση)

| Οικοσύστημα | Αποκλείεται για | Λόγος |
|---|---|---|
| `themefisher.com/bootstrap-templates` | restaurant, cafe/bakery, dentist | Μετρήθηκε: μόνο γενικά agency/business· 24 υποψήφιοι → 0 PORT_OK |
| `gethugothemes.com/products` | ίδια | Ίδιος κατάλογος, Hugo έκδοση |
| GitHub γενική αναζήτηση | όλα | V1: 0/30 από τα δημοφιλέστερα — μαθήματα, tutorials, χωρίς άδεια |
| `learning-zone/website-templates` | όλα | Aggregator 170+ templates τρίτων χωρίς καμία άδεια |

> Το Themefisher **δεν** αποκλείεται καθολικά: έδωσε τα `blue-onepage`,
> `grecko-table` και `thomson-stylist`. Αποκλείεται ως **γενική** πηγή για τα
> τρία verticals όπου αποδείχθηκε άγονο.

## Επαληθευμένα οικοσυστήματα (HTTP 200 από αυτό το περιβάλλον, 15/8)

| Studio | Vertical-specific διαδρομές | Τυπική άδεια | Σημείωση |
|---|---|---|---|
| ⭐ **Templatemo** | `/tag/<vertical>` ✓ | εμπορική, **credit αφαιρείται** | **Καλύτερη μετρημένη πηγή: 8 υποψήφιοι → 2 PORT_OK** |
| ⭐ **Tooplate** | `/tag/<vertical>` ✓ | εμπορική, **credit αφαιρείται** | Ίδια άδεια· μικρότερος όγκος ανά vertical |
| **Colorlib** | `/wp/free-<vertical>-website-templates/` ✓ | CC BY 3.0 | → LICENSE_REVIEW· 0 ευρήματα στο food |
| ⚠️ **ThemeWagon** | `/?s=<vertical>` ✓ (μόνο search· τα `/theme-category/` και `/theme-tag/` δίνουν 404) | **aggregator** | Αναδιανέμει ξένα templates — **προέλευση πρώτα**, αλλιώς PROVENANCE_BLOCKED. Ίδιο μοτίβο με το αποκλεισμένο `learning-zone` |
| **Untree.co** | `/templates/` ✓ | CC BY 3.0 | → LICENSE_REVIEW |
| **Start Bootstrap** | `/themes` ✓ | **MIT** | καλύτερη άδεια, αλλά γενικά |
| **BootstrapMade** | ✓ | free **με υποχρεωτική απόδοση** | αφαίρεση = αγορά |
| **Cruip** | ✓ | ποικίλλει ανά template | επαλήθευση ανά template |

✅ **Λύθηκε (15/8):** τα Templatemo και Tooplate επιτρέπουν **ρητά αφαίρεση
credit** — «You may remove any credit link…» / «Yes, you can remove all credit
links.» Η εκκρεμής απόφαση περί απόδοσης ισχύει μόνο για τα **CC BY** studios
(HTML5 UP, Colorlib, Untree, BootstrapMade). Ξεκίνα πάντα από τα δύο πρώτα.

---

## Χάρτης ανά ανέγγιχτο vertical

| # | Vertical | Προτιμώμενες πηγές | Όροι αναζήτησης | Ήδη γνωστά / παραπομπές |
|---|---|---|---|---|
| **1+2** | **Restaurant / taverna / cafe / bakery** | Tooplate `/tag/restaurant`, Templatemo `/tag/restaurant`, Colorlib restaurant list, ThemeWagon `?s=restaurant` | restaurant, taverna, cafe, bakery, coffee shop, pizzeria, food menu | `grecko-table` ήδη υλοποιημένο (Grecko/Themefisher). **Απαγορευμένα:** τα 11 ταξινομημένα |
| 4 | Pharmacy | Tooplate/Templatemo `/tag/medical`, Colorlib medical | pharmacy, drugstore, chemist, medical retail | Προσοχή: αποφυγή «clinic» templates με ιατρικούς ισχυρισμούς |
| 5 | Gym / fitness | Colorlib gym list, ThemeWagon `?s=gym`, Tooplate `/tag/sport` | gym, fitness, crossfit, yoga studio, personal trainer | — |
| 7 | Carpenter / maker | ThemeWagon `?s=carpenter`, Templatemo `/tag/construction` | carpenter, woodwork, joinery, furniture maker, craft | `constra-build` (Constra) ήδη υλοποιημένο από παράλληλο agent |
| 8 | Home trade / technician | Templatemo `/tag/construction`, ThemeWagon `?s=plumber` | plumber, electrician, handyman, repair service, emergency | `callout`, `forge`, `motor` ήδη στη βιβλιοθήκη |
| 9 | Lawyer / accountant / consultant | Tooplate `/tag/business`, Start Bootstrap | law firm, attorney, accountant, consulting, advisory | `marble`, `signature`, `airspace-office`, `bigspring-advisory` ήδη· **υψηλός κορεσμός** |
| 10 | Hospitality / rooms | Colorlib hotel list, Tooplate `/tag/hotel` | hotel, guesthouse, rooms, villa, bnb, resort | `aegean` ήδη |
| 11 | Garage / automotive | ThemeWagon `?s=automotive`, Templatemo `/tag/car` | auto repair, garage, car service, tyre, mechanic | `motor` ήδη |
| 12 | **Retail / local shop** | Tooplate `/tag/shop`, ThemeWagon `?s=ecommerce` | shop, store, boutique, retail, product showcase | ➡️ **Aviato** (`themefisher/aviato-bootstrap`, MIT, ήδη αποδοσμένο σε 1440/390) — παραπομπή από V2, **έτοιμο για αξιολόγηση εδώ** |
| 13 | Farm / producer | ThemeWagon `?s=agriculture`, Templatemo `/tag/farm` | farm, agriculture, organic, winery, olive oil, producer | `terra` ήδη |

## Dedupe — τι ΔΕΝ ξαναμπαίνει ποτέ

Πριν από κάθε νέο batch, έλεγχος έναντι:
- `research/verticals/CANDIDATE-CLASSIFICATION.md` — 11 ταξινομημένα
- `research/salon-batch/BATCH-A.md` + `LICENSE-GATE.md` — 20 ταξινομημένα
- `licenses/THIRD-PARTY.md` — ό,τι έχει ήδη πορταριστεί
- `sites/lib/templates/index.js` — 56 εγγεγραμμένα themes
