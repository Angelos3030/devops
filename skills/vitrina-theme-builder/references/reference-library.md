# Reference library

Ό,τι έχει αναλυθεί, ώστε να μην ξαναναλύεται. Πριν από κάθε κύκλο: διάβασε αυτό
πρώτα και ζήτα **νέες** πηγές.

Ποιότητα 1–5 = πόσο χρήσιμη ήταν η πηγή **για εμάς**, όχι πόσο ωραίο είναι το site.

---

## Κύκλος 2026-08-11 — «μία γλώσσα σε πολλά themes»

Ερώτηση του κύκλου: πώς κρατούν τα premium συστήματα ενιαία σχεδιαστική γλώσσα σε
δεκάδες templates, αφήνοντας σε κάθε vertical δική του προσωπικότητα;

### ✅ Δεκτές

| Πηγή | Tier | Vertical | Q | Δυνατά | Αδύναμα |
|---|---|---|---|---|---|
| [Astra Global Color Palette](https://wpastra.com/docs/astra-global-color-palette-settings/) | 1 | — (σύστημα) | 5 | 9 αριθμημένα slots `--ast-global-color-0..8`· κάθε ρύθμιση είτε **δένεται** στο slot είτε γίνεται custom | το custom override σπάει σιωπηλά τη σύνδεση — καμία προειδοποίηση |
| [Kadence Color Palette](https://www.kadencewp.com/help-center/docs/kadence-theme/how-to-use-the-kadence-theme-color-palette/) | 1 | — (σύστημα) | 5 | `--global-palette1..9` **+ σημασιολογικά ψευδώνυμα** (Light=9, Dark=3, Highlight=1)· Style Guide ως ξεχωριστή οθόνη | τα ψευδώνυμα είναι λίγα· δεν καλύπτουν borders/soft ink |
| [Radix Themes — Color](https://www.radix-ui.com/themes/docs/theme/color) | 3 | — (σύστημα) | 5 | κλίμακα 12 βημάτων με **δεσμευμένο σκοπό ανά βήμα** (1-2 φόντα, 3-5 interactive, 6-8 γραμμές, 9-10 solid, 11-12 κείμενο)· accent+gray ζεύγος· μία αλλαγή prop ξαναβάφει τα πάντα | φτιαγμένο για app UI, όχι για marketing sites με φωτογραφίες |
| [Material 3 — Color roles](https://m3.material.io/styles/color/roles) | 3 | — (σύστημα) | 5 | ρόλοι αντί για ονόματα χρωμάτων· **ζεύγη `on-`** που εγγυώνται αντίθεση εξ ορισμού | βαρύ για μικρή βιβλιοθήκη· δεν χρειαζόμαστε όλη την ταξινομία |
| [Vercel Geist — Colors](https://vercel.com/geist/colors) | 3 | — (σύστημα) | 4 | 10 βήματα με χαρτογραφημένο σκοπό (100 default → 200 hover → 400-600 borders → 900-1000 κείμενο) | ίδιος περιορισμός με Radix: product UI |

**Σύγκλιση και στις πέντε:** τα templates **δεν ορίζουν χρώματα**. Καταναλώνουν
tokens με δεσμευμένο σκοπό. Η προσωπικότητα ζει σε τυπογραφία, ρυθμό, εικόνα και
κίνηση — **ποτέ σε νέα ονόματα χρωμάτων**.

### ❌ Απορρίφθηκαν

| Πηγή | Λόγος |
|---|---|
| [Kadence starter templates](https://www.kadencewp.com/kadence-starter-templates/) | 301 → σελίδα μεταπωλητή· μηδέν μηχανική |
| [Astra website templates](https://wpastra.com/website-templates/) | marketing· «300+ templates» χωρίς καμία δομή |
| [GeneratePress site library](https://generatepress.com/site-library/) | marketing· «80+ starter sites» χωρίς σύστημα |
| [Blocksy](https://creativethemes.com/blocksy/) | HTTP 403 |

**Μάθημα:** οι εμπορικές σελίδες των builders δεν περιγράφουν ποτέ το σύστημά τους.
Πήγαινε κατευθείαν στα docs τους. Πέρασε στο `SKILL.md §0`.

Σταμάτησα στις 9 πηγές αντί για 10–15: η απάντηση είχε συγκλίνει σε τέσσερα
ανεξάρτητα συστήματα και η δέκατη θα επαναλάμβανε την ίδια μηχανική.

### Τι έγινε με αυτή τη γνώση

Υλοποιήθηκε ως **Vitrina Spine** — ένδεκα ρόλοι με δεσμευμένο σκοπό, με τα ζεύγη
`on-` του Material και τη λογική «ένα swap ξαναβάφει τα πάντα» του Radix, χωρίς
την ταξινομία που δεν χρειαζόμαστε. Μεταφέρθηκαν `clinic-triage` και `callout`.

Τρία πράγματα φάνηκαν μόνο επειδή μετρήθηκαν, και ισχύουν για κάθε μελλοντικό theme:

- το ωμό accent **ως κείμενο σε σκούρη ζώνη** απέτυχε σε 6 στις 7 παλέτες
- το `accent-ink` πρέπει να μετριέται στη **σκουρότερη** επιφάνεια, όχι στη λευκή
- το `on-accent` **δεν είναι πάντα λευκό** — πάνω σε amber είναι σκούρο

### Δεν αναλύθηκαν ακόμη

Awwwards, siteinspire, land-book, lapa, godly, cssdesignawards, onepagelove,
base44, linear, stripe, raycast, framer showcase, webflow made-in-webflow.
Χρήσιμα για **αισθητική κατεύθυνση ανά vertical**, όχι για το ερώτημα αυτού του
κύκλου. Το `SKILL.md §0` ήδη προειδοποιεί ότι δεν έχουν τοπικές επιχειρήσεις.

---

## Κύκλος 2026-08-11β — οι εννέα WordPress builders

Καθαρά έρευνα: κανένας κώδικας, κανένα theme. Ερώτηση: τι φτιάχνουν πραγματικά
οι μεγάλοι builders για τοπικές επιχειρήσεις, και τι από αυτό αξίζει.

### Βαθμολογία (χρησιμότητα για εμάς, όχι ομορφιά)

| Builder | Q | Templates προσβάσιμα; | Γιατί |
|---|---|---|---|
| **Astra** (`websitedemos.net/<vertical>-0N/`) | 5 | ✅ δημόσια | Πραγματικά τοπικά verticals, άμεσα μετρήσιμα. Ήδη η πηγή #1 του §0. |
| **Avada** (`avada.website/<vertical>/`) | 5 | ✅ δημόσια | 100+ demos στο ίδιο μοτίβο URL. Και blog posts «deconstructing» που εξηγούν section-section το **γιατί**. Δεύτερη πηγή για τοπικά. |
| **GeneratePress** | 5 | ⚠️ μερικώς | Services 2.0 ειδικά για τοπικές υπηρεσίες (ηλεκτρολόγος, κηπουρός, λογιστής) + το καθαρότερο μοντέλο συνέπειας που είδαμε (κάτω). |
| **Kadence** | 4 | ⚠️ μέσω plugin | `--global-palette1..9` + σημασιολογικά ψευδώνυμα· ξεχωριστή οθόνη **Style Guide**. |
| **Blocksy** | 3 | ❌ 403 | 25+ starter sites· 8 slots + global colors ανά ρόλο (κείμενο, σύνδεσμοι, περιγράμματα, headings, φόντο). Το site μπλοκάρει fetch. |
| **Bricks** | 2 | ❌ πίσω από το προϊόν | 8 design sets (Karlson/Auron/Velora/Liv/Sizzle/Reality/Digital) + **Wireframes: 180+ modular sections**. Η ιδέα «βιβλιοθήκη ενοτήτων» είναι σωστή· τα demos δεν ανοίγουν. |
| **Breakdance** | 2 | ❌ πίσω από το προϊόν | 100+ layout components, «Global Styles» χωρίς δημοσιευμένη μηχανική. Το `/samba/` είναι σελίδα πώλησης, όχι το kit. |
| **Elementor** | 2 | ❌ μέσα στον editor | 30+ container kits, 100+ section kits. Καμία δημόσια πληροφορία για design tokens. |
| **Oxygen** | 2 | ❌ | Class-first, «variables» για global τιμές. Εργαλείο developer· δεν προσφέρει έτοιμη σχεδιαστική γνώση. |

**Κανόνας που προκύπτει:** οι builders χωρίζονται σε αυτούς που **δημοσιεύουν τα
demos τους** (Astra, Avada) και σε αυτούς που τα κρύβουν πίσω από την άδεια
(Bricks, Breakdance, Elementor, Oxygen). Μόνο οι πρώτοι είναι αξιοποιήσιμοι για
μέτρηση. Μη χάνεις κύκλο στους δεύτερους.

### Ο κοινός σκελετός των τοπικών υπηρεσιών

Μετρήθηκε στο **ίδιο vertical από δύο ανεξάρτητους builders** — Avada Plumber και
Astra Plumber-02. Παρότι διαφέρουν αισθητικά (μπλε/φωτεινό vs μαύρο/editorial),
η δομή είναι σχεδόν ταυτόσημη:

```
sticky nav + κουμπί CTA
hero: φωτογραφία + κάρτα φόρμας που «κάθεται» πάνω της + τηλέφωνο έκτακτης ανάγκης
about / why-us με εικόνες
πλέγμα υπηρεσιών, ΑΡΙΘΜΗΜΕΝΟ 01–06
testimonials
ζώνη CTA με τηλέφωνο
fat footer πολλών στηλών
```

Το `callout` μας έχει ήδη 7 από τα 8. Δεν είναι σύμπτωση — είναι σύγκλιση.

### ✅ Αξίζουν

1. **Triage επιπέδου υπηρεσίας** (Avada: *One-off Repairs · Care Plan ·
   Installations*). Δεν είναι ισχυρισμός, είναι η δομή της προσφοράς — τίμιο και
   δυνατό. Χωρίζει την πρόθεση πριν από τη λίστα υπηρεσιών.
2. **Κουμπί «όλες οι υπηρεσίες»** μετά από 6 κάρτες. Λύνει το πρόβλημα του
   μεταβλητού πλήθους που ήδη μας απασχολεί (2/4/6/9).
3. **Στρώμα κοινών κλάσεων πάνω από τα tokens** (GeneratePress `.gbp-section`,
   `.gbp-card`, `.gbp-button--primary`). Ο spine έλυσε το χρώμα· η **δομή**
   (πλάτη, ρυθμός, κάρτες, κουμπιά) είναι ακόμη ανά theme.
4. **Κανόνας κληρονομιάς**: «ένα pattern που εισάγεται ΔΕΝ αντικαθιστά υπάρχον
   global style — κληρονομεί από αυτό». Ακριβώς η πειθαρχία που λείπει από τη
   legacy γέφυρα με τα `!important`.
5. **Style Guide ως ξεχωριστή οθόνη** (Kadence). Θα ήταν εξαιρετικό εσωτερικό QA:
   μία σελίδα που δείχνει όλους τους ρόλους του spine σε κάθε παλέτα.

### ❌ Δεν αξίζουν

1. **Σειρές με σήματα κριτικών** (Astra Plumber-02: Google, BBB, Facebook, Yelp).
   Ψεύτικα στοιχεία εμπιστοσύνης — απαγορευμένα ρητά.
2. **Ισχυρισμοί μακροβιότητας στο hero** («Serving our clients for over 25 years»).
   Invented facts.
3. **Πυκνότητα κειμένου lorem ipsum.** Και τα δύο demos έχουν μπλοκ που καμία
   πραγματική μικρή επιχείρηση δεν γεμίζει. Ο έλεγχος του §2 ισχύει.
4. **Ύψος σελίδας ~4.850px** και στα δύο. Ο πελάτης μας δεν έχει τόσο περιεχόμενο.
5. **30 media queries** (Avada) με device-specific breakpoints αντί content-driven.
6. **Φόρμα callback ως προεπιλογή στο hero.** Δεν υπάρχει endpoint για leads· ο
   κανόνας «χωρίς παραλήπτη → κάρτα κλήσης» μένει.
7. **Cookie banner** που σκεπάζει το hero (Avada). Μηδέν third-party ⇒ χωρίς banner.

### Screenshots

Εκτός repo, σε `%TEMP%/vitrina-refs/`: `avada-plumber`, `astra-plumber02`,
`breakdance-samba` (desktop/tablet/mobile + measurements.json). Υλικό ανάλυσης —
δεν γίνονται ποτέ commit.

### Δεν λύθηκε

Bricks, Breakdance, Elementor, Oxygen: τα templates δεν είναι δημόσια. Για να
αναλυθούν χρειάζεται άδεια — απόφαση του ιδιοκτήτη, όχι δική μου.
