# Verticals — συνολική πρόοδος

Πηγή λίστας: `docs/18-VERTICAL-DESIGN-INTELLIGENCE.md` (13 vertical families).
Ροή ανά vertical: **DeepSeek research → license/quality gate → manifest**.
Τα manifests: `research/verticals/vNN-<vertical>.md`.

**Τελευταία ενημέρωση:** 2026-08-15

| # | Vertical | PORT_OK | Κατάσταση | Εξαιρέσεις | Ημ/νία |
|---|---|---|---|---|---|
| 1 | Restaurant / taverna | **0** | ⚠️ ξανατρέξιμο | Grecko ήδη υλοποιημένο· έτρεξε με **λάθος κριτήριο** | 14/8 |
| 2 | Cafe / bakery | **0** | ⚠️ ξανατρέξιμο | 4 × LICENSE_REVIEW (CC BY 3.0)· **λάθος κριτήριο** | 14/8 |
| 3 | Dentist / medical | **3 υποψήφιοι** | ✅ ερευνήθηκε | Agen/Airspace/Bingo MIT ✓ — εκκρεμεί port· 3 × repo 404 | 15/8 |
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

**Σύνολο υλοποιημένων PORT_OK: 3** · **επαληθευμένοι υποψήφιοι έτοιμοι για port: 3** (V3)

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
**Τα V1 και V2 πρέπει να ξανατρέξουν** — τα μηδενικά τους δεν είναι αξιόπιστα.

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
