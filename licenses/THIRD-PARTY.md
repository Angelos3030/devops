# Third-party design references — Batch B master themes

Οι άδειες επαληθεύτηκαν **στο ίδιο το αρχείο LICENSE κάθε repository**, όχι από
badge, όχι από τη σελίδα του demo, όχι από τα metadata του GitHub μόνο.
Ημερομηνία ελέγχου: **2026-08-13**.

---

## MIT — επιτρέπεται επαναχρησιμοποίηση κώδικα, με διατήρηση σημείωσης

Οι παρακάτω άδειες είναι MIT και επιτρέπουν ρητά εμπορική χρήση, τροποποίηση και
μεταπώληση, **με τον όρο** ότι διατηρείται η σημείωση πνευματικών δικαιωμάτων.
Αυτό το αρχείο είναι η διατήρηση αυτής της σημείωσης.

### Educenter → Vitrina `educenter-campus`
- Πηγή: https://github.com/themefisher/educenter-bootstrap
- Άδεια: MIT
- Copyright: **Themefisher (2016 – present)**

### Vex → Vitrina `vex-counter`
- Πηγή: https://github.com/themefisher/vex-hugo
- Άδεια: MIT
- Copyright: **Themefisher (2018 – present)**

### Airspace → Vitrina `airspace-office`
- Πηγή: https://github.com/themefisher/airspace-hugo
- Άδεια: MIT
- Copyright: **Themefisher (2018 – present)**

### Constra *(ανατέθηκε και στα δύο batch — υλοποιήθηκε από τον παράλληλο agent ως `constra-build`)*
- Πηγή: https://github.com/themefisher/constra-bootstrap
- Άδεια: MIT
- Copyright: **Themefisher (2016 – present)**

### My Real Estate *(ανατέθηκε και στα δύο batch — υλοποιήθηκε από τον παράλληλο agent ως `property-atlas`)*
- Πηγή: https://github.com/TheMostafax/My_Real_Estate
- Άδεια: MIT
- Copyright: **Mostafa Hassan (2023)**

> Το κείμενο της άδειας MIT: https://opensource.org/license/mit

---

## ΑΝΤΙΦΑΤΙΚΗ ΑΔΕΙΑ — καμία επαναχρησιμοποίηση κώδικα

### FreightEdge → Vitrina `freight-lane` *(ανεξάρτητη αναδημιουργία)*
- Πηγή: https://github.com/themixlyweb/nextjs-logistics-website-template

Η άδεια **αντιφάσκει με τον εαυτό της**:

| Πηγή μέσα στο ίδιο repository | Τι λέει |
|---|---|
| `LICENSE` + GitHub metadata | MIT (`spdx_id: MIT`) |
| `README.md` | «This template is licensed under the MIT License.» |
| `README.md` | «You may use this version for **personal and educational purposes**.» |
| `README.md` (πίνακας σύγκρισης) | «Commercial Use Allowed» **μόνο** στην Themixly Full Version· «Commercial license» αποκλειστικό της επί πληρωμή έκδοσης |

**Απόφαση: VISUAL REFERENCE ONLY.** Το Vitrina πουλάει sites σε πελάτες· δεν
μπορεί να στηριχτεί στην επιεικέστερη ανάγνωση όταν ο ίδιος ο εκδότης δηλώνει
δύο αρχεία παρακάτω ότι η εμπορική χρήση απαιτεί αγορά. Δεν αντιγράφηκε **καμία**
γραμμή κώδικα, markup, CSS ή asset. Κρατήθηκε μόνο η γενική ιδέα ενός site
μεταφορών — που δεν ανήκει σε κανέναν — και υλοποιήθηκε από το μηδέν.

Αν ποτέ χρειαστεί ο κώδικάς τους, ο δρόμος είναι η αγορά της Full Version και
νέα καταγραφή εδώ.

---

## Τι ΔΕΝ μεταφέρθηκε από κανένα υποψήφιο

- **Καμία demo φωτογραφία.** Οι εικόνες των templates συνοδεύονται συνήθως από
  δική τους άδεια (ή καμία) και **δεν** καλύπτονται από το MIT του κώδικα. Το
  Vitrina χρησιμοποιεί το δικό του media pipeline με δηλωμένη προέλευση
  (`src/media_semantics.py`).
- **Κανένα λογότυπο, εικονίδιο ή γραμματοσειρά** τρίτου.
- **Κανένα κείμενο** — ούτε ως αφετηρία.
- **Κανένας ισχυρισμός**: counters («100+ projects»), testimonials, λογότυπα
  πελατών, badges επιτυχίας. Απαγορεύονται χωρίς δεδομένα intake
  (`docs/ai/DECISIONS.md` §D4) και επιβάλλονται από το `sites/tests/trust_guard.mjs`.
