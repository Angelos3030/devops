# Ταξινόμηση των 24 υποψηφίων (V1/V2/V3)

**Ημερομηνία:** 2026-08-15 · **Καμία νέα έρευνα** — μόνο επικύρωση των υπαρχόντων.

## Πρώτο εύρημα: 24 θέσεις = **11 μοναδικά** templates

Οι «24 υποψήφιοι» δεν είναι 24 διαφορετικά πράγματα. Τα ίδια generic Themefisher
templates εμφανίστηκαν σε **δύο ή τρία** verticals το καθένα:

| Template | Σε ποια verticals προτάθηκε |
|---|---|
| Agico, Bexer, Bingo, Bizcraft | V1 + V2 + V3 |
| Biztrox, Blue, Brandi | V1 + V2 |
| Airspace | V1 + V3 |
| Agen | V3 |
| Adrian, Aviato | V2 |

Το ότι το ίδιο template προτείνεται ταυτόχρονα για **ταβέρνα, καφετέρια και
οδοντιατρείο** είναι από μόνο του η απάντηση: πρόκειται για γενικά business
templates χωρίς vertical ταυτότητα.

---

## Ταξινόμηση ανά μοναδικό template

| # | Template | Repo | Άδεια | Απόδοση | Ταξινόμηση |
|---|---|---|---|---|---|
| 1 | **Adrian** | `themefisher/adrian-bootstrap` | — | — | ⛔ **PROVENANCE_BLOCKED** |
| 2 | **Agen** | `themefisher/agen-bootstrap` | **MIT** ✓ | ✓ 1440+390 | ⛔ **FIT_REJECT** |
| 3 | **Agico** | `themefisher/agico-bootstrap` | — | — | ⛔ **PROVENANCE_BLOCKED** |
| 4 | **Airspace** | `themefisher/airspace-bootstrap` | **MIT** ✓ | ✓ 1440+390 | ⛔ **FIT_REJECT** |
| 5 | **Aviato** | `themefisher/aviato-bootstrap` | **MIT** ✓ | ✓ 1440+390 | ⛔ **FIT_REJECT** (→ βλ. V12) |
| 6 | **Bexer** | `themefisher/bexer-bootstrap` | — | — | ⛔ **PROVENANCE_BLOCKED** |
| 7 | **Bingo** | `themefisher/bingo-bootstrap` | **MIT** ✓ | ✓ 1440+390 | ⛔ **FIT_REJECT** |
| 8 | **Bizcraft** | `themefisher/bizcraft-bootstrap` | — | — | ⛔ **PROVENANCE_BLOCKED** |
| 9 | **Biztrox** | `themefisher/biztrox-bootstrap` | — | — | ⛔ **PROVENANCE_BLOCKED** |
| 10 | **Blue** | `themefisher/blue-bootstrap` | **MIT** ✓ | ✓ (Batch A) | ✅ **PORT_OK — ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΟ** ως `blue-onepage` |
| 11 | **Brandi** | `themefisher/brandi-bootstrap` | **MIT** ✓ | ✓ 1440+390 | ⛔ **FIT_REJECT** |

**Νέα PORT_OK από τους 24: 0.**

---

## Αιτιολόγηση κάθε απόρριψης

### PROVENANCE_BLOCKED — 5 templates

`adrian`, `agico`, `bexer`, `bizcraft`, `biztrox`: το repo επιστρέφει **404**.
Εμφανίζονται στον κατάλογο του site αλλά **δεν υπάρχουν ως δημόσια repos** —
προϊόντα επί πληρωμή ή αποσυρμένα. Χωρίς πηγή δεν υπάρχει ούτε άδεια ούτε
προέλευση να επαληθευτεί. Ίδιο μοτίβο με το Brandi-**hugo** του Batch A.

### FIT_REJECT — 5 templates

Όλα MIT και όλα αποδόθηκαν πραγματικά σε 1440 και 390. Απορρίπτονται στην
**καταλληλότητα**, όχι στην άδεια ή στην ποιότητα:

**Agen** (ανατέθηκε σε V3 οδοντιατρείο) — «Creative Agency»: νέον ροζ πινελιά σε
μωβ διαστημικό φόντο, ομάδα, τιμοκατάλογος $30, blog. Το
`docs/18-VERTICAL-DESIGN-INTELLIGENCE.md` ζητά για ιατρείο «calm, clean,
reassuring» και αποφυγή επιθετικής κίνησης. Είναι το ακριβώς αντίθετο.

**Airspace** (V1 + V3) — «digital marketing & design agency»: 8 εικονίδια
υπηρεσιών, «Fun Facts About Us» με μετρητές (99 Cups of Coffee, 125 Projects
Completed) και testimonial. Ταυτότητα διαφημιστικής, όχι ταβέρνας ή ιατρείου.
Επιπλέον **επικαλύπτεται** με το ήδη υλοποιημένο `airspace-office`.

**Aviato** (V2 καφετέρια/φούρνος) — πλήρες **e-commerce κατάστημα ρούχων**:
καλάθι, αναζήτηση, κατηγορίες προϊόντων, πλέγμα με **τιμές $200**, newsletter,
Instagram feed. Ένας φούρνος δεν είναι κατάστημα με καλάθι, και το Vitrina δεν
έχει ούτε καλάθι ούτε τιμές.
→ **Παραπομπή:** είναι πραγματικά καλό και αξίζει εξέταση στο **V12 Retail /
local shop** όταν ανοίξει εκείνο το vertical. Δεν το ταξινομώ PORT_OK εδώ γιατί
δεν ανήκει στο vertical που του ανατέθηκε.

**Bingo** (V1+V2+V3) — γενική «agency»: μετρητές (150 Happy Clients, 250 Cups of
Coffee), testimonial, blog. Αφαιρώντας ό,τι απαγορεύει το συμβόλαιο αλήθειας
μένει ένα άχρωμο πλέγμα χαρακτηριστικών.

**Brandi** (V1+V2) — creative portfolio του 2015: φίλτρα έργων, «Meet Our Team»,
«Some Fun Facts» (3043 hours, 6134 awards won), φόρμα. Ίδιο πρόβλημα, με
επιπλέον παλαιότητα σχεδίου.

---

## Το ουσιαστικό συμπέρασμα

Η διόρθωση του worker **ήταν σωστή** — σταμάτησε να πετάει υλικό για άδεια που
δεν φαινόταν. Αλλά αποκάλυψε τον πραγματικό περιορισμό:

> Ο κατάλογος Bootstrap της Themefisher αποτελείται σχεδόν αποκλειστικά από
> **γενικά agency/business templates**. Δεν περιέχει templates εστιατορίου,
> καφετέριας ή ιατρείου.

Άρα τα αρχικά μηδενικά των V1/V2/V3 ήταν **εν μέρει τεχνούργημα** (λάθος
κριτήριο) και **εν μέρει αληθινά** (δεν υπάρχει vertical-specific υλικό εκεί).

**Συνέπεια για τη μέθοδο:** δεν αρκεί να διορθωθεί το φίλτρο — πρέπει να
αλλάξουν οι **πηγές**. Ένας κατάλογος γενικών business templates δεν πρόκειται να
δώσει ταβέρνα ή οδοντιατρείο όσες φορές κι αν τον ρωτήσουμε. Για τα επόμενα
verticals χρειάζονται πηγές με vertical-specific συλλογές.

Screenshots: `sites/artifacts/fidelity/cand-*-original-{desktop,mobile}.png`
