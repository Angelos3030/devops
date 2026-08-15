# Verticals — συνολική πρόοδος

Πηγή λίστας: `docs/18-VERTICAL-DESIGN-INTELLIGENCE.md` (13 vertical families).
Ροή ανά vertical: **DeepSeek research → license/quality gate → manifest**.
Τα manifests: `research/verticals/vNN-<vertical>.md`.

**Τελευταία ενημέρωση:** 2026-08-15 (μετά την ταξινόμηση των 24 υποψηφίων)

➡️ **Ταξινόμηση υποψηφίων V1/V2/V3:** [`verticals/CANDIDATE-CLASSIFICATION.md`](verticals/CANDIDATE-CLASSIFICATION.md) — **κανένας δεν ξαναερευνάται**.

| # | Vertical | PORT_OK | Κατάσταση | Εξαιρέσεις | Ημ/νία |
|---|---|---|---|---|---|
| 1+2 | Restaurant / taverna / cafe / bakery | **2** | ✅ ταξινομήθηκε ξανά με vertical-specific πηγές | Γενική πηγή: 0/8. Νέες πηγές: **9 αποδόθηκαν → 2 PORT_OK** (Frost Bakery, Klassy Cafe), 3 QUALITY, 4 FIT· 12 ThemeWagon εν αναμονή προέλευσης | 15/8 |
| 3 | Dentist / medical | **0** | ✅ ταξινομήθηκε | Agen/Airspace/Bingo MIT αλλά **FIT_REJECT**· 3 × repo 404 | 15/8 |
| 4 | Pharmacy | — | ⏳ εκκρεμεί | — | — |
| 5 | Gym / fitness | — | ⏳ εκκρεμεί | — | — |
| 6 | Beauty / salon | **3** | ✅ ολοκληρωμένο | 9 × blocked (βλ. `salon-batch/`) | 13–14/8 |
| 7 | Carpenter / maker | — | ⏳ εκκρεμεί | — | — |
| 8 | Home trade / technician | — | ⏳ εκκρεμεί | — | — |
| 9 | Lawyer / accountant / consultant | — | ⏳ εκκρεμεί | — | — |
| 10 | Hospitality / rooms | — | ⏳ εκκρεμεί | — | — |
| 11 | Garage / automotive | — | ⏳ εκκρεμεί | — | — |
| 12 | Retail / local shop | — | ⏳ εκκρεμεί | — | — |
| 13 | Farm / producer | — | ⏳ εκκρεμεί | — | — |

**Σύνολο PORT_OK: 5** — οι 24 υποψήφιοι των V1/V2/V3 έδωσαν **0**· η επανεκκίνηση
του V1+V2 με **vertical-specific πηγές** έδωσε **2**.

## Ο κανόνας πηγών, μετρημένος

| Πηγή για το ίδιο vertical | Υποψήφιοι | PORT_OK |
|---|---|---|
| Themefisher Bootstrap (γενικός κατάλογος) | 8 | **0** |
| Templatemo + Tooplate (vertical-specific) | 9 | **2** |

Η αλλαγή πηγής —όχι του φίλτρου— είναι που έδωσε αποτέλεσμα.
Πλήρες: [`verticals/v01-restaurant-cafe-DISCOVERY.md`](verticals/v01-restaurant-cafe-DISCOVERY.md)

## 🔑 Η άδεια «credit» έπαψε να είναι εμπόδιο εκεί

**Tooplate:** «You may remove any credit link and you do not need to provide a
link back to our website.» · **Templatemo:** «Yes, you can remove all credit
links.» Και τα δύο επιτρέπουν ρητά εμπορική χρήση, ανά template. Καλύτερη θέση
από κάθε CC BY studio — η εκκρεμής απόφαση παρακάτω **δεν αφορά αυτές τις πηγές**.

**Σύνολο υλοποιημένων: 3** (`blue-onepage`, `billys-barber`,
`thomson-stylist` — όλα στο vertical 6).

---

## Το κύριο εύρημα, και γιατί αλλάζει τον στόχο

Ο στόχος «10 PORT_OK ανά vertical» **δεν είναι εφικτός από αυτό το οικοσύστημα**.
Τρία ανεξάρτητα δείγματα το δείχνουν:

| Δείγμα | Υποψήφιοι | Καθαροί |
|---|---|---|
| Salon batch (χειροκίνητη λίστα 10) | 10 | **1** |
| Batch A (10 ακόμη) | 10 | **2** |
| V1 restaurant — top-30 GitHub repos | 30 | **0** |

Στο V1, **κανένα** από τα 30 δημοφιλέστερα GitHub repos για «restaurant website
template» δεν πέρασε: project μαθημάτων, tutorials, ή καθόλου άδεια. Ο μόνος
καθαρός υποψήφιος ήρθε από **studio**.

**Συνέπεια για τη μέθοδο:** το GitHub γενικά είναι θόρυβος. Η αναζήτηση πρέπει να
ξεκινά από studios που ζουν από templates (Themefisher, HTML5 UP, Cruip, Tooplate,
Templatemo). Ρεαλιστική απόδοση: **1–3 καθαρά, επαγγελματικά, vertical-specific
templates ανά vertical**, όχι 10.

**Δεύτερη συνέπεια:** μόλις εξαντληθούν τα MIT studios, ο επόμενος όγκος είναι
**CC BY** (HTML5 UP) — που απαιτεί απόδοση σε κάθε site πελάτη. Αυτό είναι
εμπορική απόφαση και εμφανίστηκε ήδη στο V2.

---

## ⚠️ ΔΙΟΡΘΩΣΗ ΜΕΘΟΔΟΥ (V3) — επηρεάζει τα V1/V2

Το DeepSeek απέρριπτε υποψήφιους με «no explicit license» επειδή του δίνονταν
**σελίδες καταλόγου**, όπου η άδεια δεν αναγράφεται. Απέρριψε έτσι και το **Blue**
και το **Airspace** — αποδεδειγμένα MIT, με το Blue ήδη πορταρισμένο.

Σωστή κατανομή: **DeepSeek κρίνει μόνο καταλληλότητα** (άδεια =
`unknown-from-listing`) · **Claude επαληθεύει άδεια στο repo** · **Claude κρίνει
ποιότητα από πραγματική αποτύπωση**.

Με το διορθωμένο κριτήριο, το ίδιο vertical έδωσε **6 υποψήφιους αντί για 0**.
**Τα V1 και V2 ξανατρέχθηκαν** με τον διορθωμένο worker:

| Vertical | Πριν | Μετά |
|---|---|---|
| V1 restaurant | 0 | **8** |
| V2 cafe/bakery | 0 | **9** |
| V3 dentist | 0 | **7** |

**Επικυρώθηκαν και ταξινομήθηκαν** (15/8): οι 24 θέσεις είναι **11 μοναδικά**
templates — τα ίδια εμφανίζονταν σε 2–3 verticals. Αποτέλεσμα: **6 MIT** (5
αποδόθηκαν σε 1440/390, 1 ήδη υλοποιημένο), **5 repos 404**, και **0 νέα PORT_OK**.

**Το κρίσιμο:** η διόρθωση του worker ήταν σωστή, αλλά αποκάλυψε ότι ο κατάλογος
Bootstrap της Themefisher είναι σχεδόν αποκλειστικά **γενικά agency/business
templates** — δεν περιέχει εστιατόριο, καφετέρια ή ιατρείο. Τα μηδενικά ήταν εν
μέρει τεχνούργημα και εν μέρει αληθινά.

**Δεν αρκεί να διορθωθεί το φίλτρο — πρέπει να αλλάξουν οι ΠΗΓΕΣ** για τα
επόμενα verticals.

## Εκκρεμείς αποφάσεις (καταγράφονται, δεν μπλοκάρουν)

| Θέμα | Επιλογές |
|---|---|
| **CC BY 3.0 / HTML5 UP** (V2 και μετά) | Α. κρατάμε credit σε κάθε site · Β. αγορά άδειας αφαίρεσης · Γ. μόνο MIT/BSD/Apache |
| **Γενικά vs vertical-specific** | Τα HTML5 UP είναι εξαιρετικά αλλά γενικά· πιστό port δίνει καλό σχέδιο χωρίς vertical ταυτότητα |
| **Menzsaloon** ($37, «1 Project») | Χρειάζεται Extended/Developer άδεια για πολλαπλά sites πελατών |
| **4 Hugo themes** (Meghna/Navigator/Timer/Kross) | ENVIRONMENT_BLOCKED — θέλουν Go στο PATH ή πρόσβαση στα `demo.*` |

---

## Πώς συνεχίζει

Για κάθε εκκρεμές vertical, η εντολή είναι έτοιμη:

```bash
DEEPSEEK_MODEL_CHEAP=deepseek-v4-flash DEEPSEEK_MODEL_STRONG=deepseek-v4-pro \
python scripts/research.py \
  --task-id vertical-NN-<slug> \
  --objective "<τι ψάχνουμε + ρητή απόρριψη aggregators/μαθημάτων/χωρίς άδεια>" \
  --context "Vitrina: ΠΙΣΤΑ ports με permissive άδεια. Conversion: <…>" \
  --sources https://themefisher.com/bootstrap-templates https://gethugothemes.com/products \
            https://html5up.net/ https://www.tooplate.com/
```

**Σημείωση διαμόρφωσης:** τα ρυθμισμένα μοντέλα στο `.env`
(`deepseek-chat`/`deepseek-reasoner`) **δεν υπάρχουν πια** στο API. Τα διαθέσιμα
είναι `deepseek-v4-flash` και `deepseek-v4-pro` — γι' αυτό περνιούνται ρητά ως env
vars παραπάνω. Αξίζει μόνιμη διόρθωση στο `.env`.

Κόστος μέχρι στιγμής: **~$0,132** για τρία verticals (4 εκτελέσεις, μία απέτυχε
σε transient JSON error και επαναλήφθηκε).

**Πρώτη προτεραιότητα στη συνέχεια:** ξανατρέξιμο V1/V2 με το διορθωμένο κριτήριο,
και υλοποίηση των τριών επαληθευμένων του V3 (Agen, Airspace, Bingo).
