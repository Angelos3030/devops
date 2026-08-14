# Salon / Barber / Beauty — license gate και πρώτο port

**Ημερομηνία:** 2026-08-14. Κάθε άδεια επαληθεύτηκε στο **ίδιο το repository**
(αρχείο `LICENSE`, `README`, ή το header του `style.css`), όχι από badge.

## Αποτέλεσμα ανά υποψήφιο

| # | Πηγή | Άδεια που βρέθηκε | Απόφαση |
|---|---|---|---|
| 1 | [EleganceSalon](https://github.com/hassanwaheedali/EleganceSalon) | **Καμία.** `LICENSE` → **404**. README: «MIT License — See LICENSE file for details *(or feel free to adapt as needed)*» και «available as a **portfolio demonstration**» | **LICENSE BLOCKED** |
| 2 | [Bro Barbershop](https://github.com/motopress/bro-barbershop) | **GPL-2.0-or-later** (header `style.css`: «GNU General Public License v2 or later», MotoPress) | **BLOCKED** — απόφαση ιδιοκτήτη: όχι copyleft |
| 3 | [Blue](https://github.com/themefisher/blue-bootstrap) | **MIT** — Themefisher | ✅ **PORTED** |
| 4 | [Spa Online Booking](https://github.com/watchout254/Spa-online-booking-website) | **MIT** — «Copyright (c) 2022 watchout254» | ✅ ΕΠΙΤΡΕΠΤΟ — εκκρεμεί port |
| 5 | [Salon Management System](https://github.com/Abhisheksingh0303/Salon-Management-System) | **Καμία** | **LICENSE BLOCKED** |
| 6 | [Pronto](https://github.com/SGrappelli/pronto) | **MIT** | ✅ ΕΠΙΤΡΕΠΤΟ — εκκρεμεί port |
| 7 | Aroma Beauty & Spa — [συλλογή](https://github.com/learning-zone/website-templates) | **Καμία**, καμία δήλωση όρων, **καμία αναφορά προέλευσης** για 170+ templates τρίτων | **LICENSE BLOCKED** |
| 8 | Beauty Salon — ίδια συλλογή | ίδιο | **LICENSE BLOCKED** |
| 9 | [Go-Barber](https://github.com/mauricioromagnollo/go-barber) | MIT στο repo, **αλλά** το design δεν αποδεικνύεται δικό του | **BLOCKED — προέλευση** |
| 10 | [IsabelRubim Barbershop](https://github.com/IsabelRubim/barbershop) | MIT στο repo, ίδιο πρόβλημα | **BLOCKED — προέλευση** |

## Προέλευση — τα τρία που ζητήθηκε να ερευνηθούν

**#4 Spa Online Booking — ΤΕΚΜΗΡΙΩΘΗΚΕ.** Η περιγραφή του repo λέει «revamp of a
previously done spa website by **Daniel Mukenya** back in 2022» και το README
δηλώνει author «Daniel Mukenya» με email επικοινωνίας. Το `LICENSE` γράφει
«Copyright (c) **2022** watchout254». Το έτος ταιριάζει με το αρχικό έργο και ο
κάτοχος του repo δημοσιεύει ο ίδιος το όνομά του ως δημιουργό: ίδιο πρόσωπο,
δική του δουλειά, δικαίωμα να την αδειοδοτήσει. **Επιτρεπτό.**

**#9 Go-Barber — ΔΕΝ ΤΕΚΜΗΡΙΩΘΗΚΕ.** Το «GoBarber» είναι το γνωστό project του
bootcamp GoStack της Rocketseat· το εύρος (web + mobile + server, TypeORM,
Unform, Yup) είναι ακριβώς η ύλη του. Το README αναφέρει «Figma» ως εργαλείο
αλλά **δεν πιστώνει κανέναν σχεδιαστή** και δεν δηλώνει πουθενά ότι το layout
είναι δικό του. Το MIT καλύπτει τον κώδικα που έγραψε — όχι κατ' ανάγκη το
design που του δόθηκε. **Ασαφές ⇒ BLOCKED.**

**#10 IsabelRubim Barbershop — ΔΕΝ ΤΕΚΜΗΡΙΩΘΗΚΕ.** Ίδιο μοτίβο, ίδιο project
(«GoBarber» και στο δικό του README), καμία δήλωση για την προέλευση του design.
**Ασαφές ⇒ BLOCKED.**

> Κανένα μπλοκαρισμένο δεν μετατράπηκε σε «inspired by». Έξι θέσεις παραμένουν
> κενές και περιμένουν αντικαταστάτες.

---

## Ολοκληρωμένο port: **Blue → `blue-onepage`**

Το πρωτότυπο **κατέβηκε, σερβιρίστηκε τοπικά και φωτογραφήθηκε** σε 1440 και 390
πριν γραφτεί γραμμή κώδικα. Χρειάστηκε scroll πριν την αποτύπωση: το template
χρησιμοποιεί `wow.js`/`animate.css` και οι μισές ενότητες είναι `opacity:0` μέχρι
να μπουν στο viewport — χωρίς αυτό, το «πρωτότυπο» θα ήταν άδειες ζώνες.

**Τι μεταφέρθηκε πιστά:** σκούρο sticky nav με logo αριστερά και uppercase links
δεξιά · full-bleed hero με σκούρο πέπλο, λεπτός uppercase τίτλος με text-shadow,
pill CTA, πλαϊνά βέλη · μπλε ζώνη δύο στηλών με στρογγυλή εικόνα και outline
κουμπί · κεντραρισμένοι τίτλοι ενοτήτων με κοντή γραμμή από κάτω · τέσσερις
υπηρεσίες με στρογγυλά περιγράμματα εικονιδίων που γεμίζουν στο hover · πλέγμα
έργων 3×2 με κενά 10px και zoom στο hover · γκρι ζώνη · δίστηλη επικοινωνία ·
χάρτης · σκούρο footer. Βάση 14px, `line-height 1.8`, container 1170px,
Open Sans 300/400/700 — όλα από το πρωτότυπο.

### Αποκλίσεις — και οι πέντε τεκμηριωμένες

| Απόκλιση | Γιατί |
|---|---|
| Μπλε **#009ee3 → #0079a8** | Λευκό σε #009ee3 = **2,9:1**, κάτω από WCAG AA. Ίδια απόχρωση, αναγνώσιμη. |
| Γκρι ζώνη **#9a9a9a → --vt-ink-soft** | Λευκό σε #9a9a9a = **2,6:1**. Ίδιος ρόλος, σκουρότερη. |
| **«What people say» παραλείπεται** | Ψεύτικες μαρτυρίες απαγορεύονται (DECISIONS §D4). Ο κώδικας τις δέχεται μόνο με αληθινά δεδομένα. |
| **«Price» παραλείπεται** | Ίδιο — ψεύτικες τιμές απαγορεύονται. |
| **Φόρμα → μπλοκ επικοινωνίας** | Η αρχική φόρμα ποστάρει σε PHP που δεν έχουμε. Κουμπί που δεν στέλνει τίποτα είναι χειρότερο από καθόλου κουμπί. Ίδια δίστηλη σύνθεση. |

Οι δύο παραλείψεις εξηγούν τη διαφορά ύψους: **6417px** το πρωτότυπο, **3421px**
το port.

### Assets

**Καμία** demo φωτογραφία, γραμματοσειρά ή εικονίδιο δεν αντιγράφηκε. Οι εικόνες
έρχονται από το media pipeline του Vitrina με δηλωμένη προέλευση· τα εικονίδια
των υπηρεσιών είναι δικά μας inline SVG (το πρωτότυπο χρησιμοποιεί Font Awesome,
που έχει δική του άδεια). Το Open Sans υπάρχει ήδη self-hosted με ελληνικό
subset — δεν κατέβηκε από Google Fonts.

### QA

| Έλεγχος | Desktop 1440 | Mobile 390 |
|---|---|---|
| Ύψος | 3421px | 5157px |
| Οριζόντιο overflow | 0 | 0 |
| Σπασμένες εικόνες | 0/10 | 0/10 |
| `h1` | 1 | 1 |
| Console errors | 0 | 0 |
| Tap targets < 40px | 2 (βέλη slider, `aria-hidden`) | 2 |

Spine guard: 49/49 ταυτότητες, πλήρης αντίθεση. Trust guard: καθαρός.
Registry: 54 themes × 4 σημεία, πλήρες coverage.

**Δύο σφάλματα δικά μου, διορθωμένα:** (1) το κείμενο του hero ήταν μέσα σε κάθε
slide → **3 × h1** και ύψος 16924px· μεταφέρθηκε σε ένα overlay. (2) Έτρεξα
`next build` στο ίδιο `NEXT_DIST_DIR` με τον dev server και του διέλυσα τα chunks
— ξεχωριστός φάκελος ανά διεργασία, όπως λέει το CLAUDE.md.

Screenshots: [`fidelity/`](fidelity/) — `blue-original-{desktop,mobile}.jpg` και
`blue-vitrina-{desktop,mobile}.jpg`.
