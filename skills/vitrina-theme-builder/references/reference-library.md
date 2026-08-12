# Reference library

Ό,τι έχει αναλυθεί, ώστε να μην ξαναναλύεται. Πριν από κάθε κύκλο: διάβασε αυτό
πρώτα και ζήτα **νέες** πηγές.

Ποιότητα 1–5 = πόσο χρήσιμη ήταν η πηγή **για εμάς**, όχι πόσο ωραίο είναι το site.

Η βιβλιοθήκη χωρίζεται σε τέσσερις κατηγορίες. Η διάκριση δεν είναι ποιοτική —
είναι **πρόσβασης**. Μια πηγή στο *Pending Commercial Review* δεν απορρίφθηκε·
απλώς δεν μπορούμε να τη δούμε νόμιμα ακόμη.

- **Accessible Sources** — αναλύθηκαν, μετρήθηκαν, αξιοποιήθηκαν
- **Pending Commercial Review** — αξιόλογες, αλλά τα demos δεν είναι δημόσια
- **Open Source Sources** — δημόσιος κώδικας και δημοσιευμένα design systems
- **Real Business References** — πραγματικές ελληνικές επιχειρήσεις

---

# Accessible Sources

## Design systems — η μηχανική της συνέπειας

Ερώτημα: πώς κρατούν τα premium συστήματα ενιαία γλώσσα σε δεκάδες templates;

| Πηγή | Q | Δυνατά | Αδύναμα |
|---|---|---|---|
| [Astra Global Color Palette](https://wpastra.com/docs/astra-global-color-palette-settings/) | 5 | 9 slots `--ast-global-color-0..8`· κάθε ρύθμιση **δένεται** ή γίνεται custom | το custom override σπάει σιωπηλά τη σύνδεση |
| [Kadence Color Palette](https://www.kadencewp.com/help-center/docs/kadence-theme/how-to-use-the-kadence-theme-color-palette/) | 5 | `--global-palette1..9` **+ σημασιολογικά ψευδώνυμα**· Style Guide ως ξεχωριστή οθόνη | τα ψευδώνυμα δεν καλύπτουν borders/soft ink |
| [Radix Themes — Color](https://www.radix-ui.com/themes/docs/theme/color) | 5 | 12 βήματα με **δεσμευμένο σκοπό ανά βήμα**· μία αλλαγή ξαναβάφει τα πάντα | φτιαγμένο για app UI, όχι marketing sites |
| [Material 3 — Color roles](https://m3.material.io/styles/color/roles) | 5 | ρόλοι αντί χρωμάτων· **ζεύγη `on-`** που εγγυώνται αντίθεση εξ ορισμού | βαριά ταξινομία για τη δική μας κλίμακα |
| [Vercel Geist — Colors](https://vercel.com/geist/colors) | 4 | 10 βήματα χαρτογραφημένα: default → hover → borders → κείμενο | ίδιος περιορισμός με Radix |
| [GenerateBlocks Pattern Library](https://generatepress.com/build-consistent-pattern-library-generateblocks-pro-generatepress/) | 5 | **Τρεις πηγές στυλ**: Theme Styles → Local → Global Styles. Κανόνας: pattern που εισάγεται **κληρονομεί**, δεν αντικαθιστά | κλάσεις WordPress-specific |

**Σύγκλιση και στις έξι:** τα templates **δεν ορίζουν χρώματα**. Καταναλώνουν
tokens με δεσμευμένο σκοπό. Η προσωπικότητα ζει σε τυπογραφία, ρυθμό, εικόνα και
κίνηση — **ποτέ σε νέα ονόματα χρωμάτων**.

## Template libraries με δημόσια demos

| Builder | Q | Πρόσβαση | Σημείωση |
|---|---|---|---|
| **Astra** | 5 | `websitedemos.net/<vertical>-0N/` | Πραγματικά τοπικά verticals, άμεσα μετρήσιμα. Πηγή #1 του `SKILL.md §0`. |
| **Avada** | 5 | `avada.website/<vertical>/` | 100+ demos, ίδιο μοτίβο URL. Και posts «deconstructing» που εξηγούν section-section το **γιατί**. |
| **GeneratePress** | 5 | μερική | Services 2.0 ειδικά για τοπικές υπηρεσίες (ηλεκτρολόγος, κηπουρός, λογιστής). |
| **Kadence** | 4 | μέσω plugin | Starter templates· η μηχανική τεκμηριώνεται δημόσια. |
| **Blocksy** | 3 | ❌ 403 στο fetch | 25+ starter sites· 8 slots + global colors ανά ρόλο (κείμενο, σύνδεσμοι, περιγράμματα, headings, φόντο). |

### Ο κοινός σκελετός των τοπικών υπηρεσιών

Μετρήθηκε στο **ίδιο vertical από δύο ανεξάρτητους builders** — Avada Plumber και
Astra Plumber-02. Διαφέρουν αισθητικά (μπλε/φωτεινό vs μαύρο/editorial)· η δομή
είναι σχεδόν ταυτόσημη:

```
sticky nav + κουμπί CTA
hero: φωτογραφία + κάρτα φόρμας πάνω της + τηλέφωνο έκτακτης ανάγκης
about / why-us με εικόνες
πλέγμα υπηρεσιών, ΑΡΙΘΜΗΜΕΝΟ 01–06
testimonials
ζώνη CTA με τηλέφωνο
fat footer πολλών στηλών
```

Το `callout` μας έχει 7 από τα 8. Δεν το αντιγράψαμε — καταλήξαμε στο ίδιο.

### ✅ Αξίζουν

1. **Triage επιπέδου υπηρεσίας** (Avada: *One-off · Care Plan · Installations*).
   Δομή της προσφοράς, όχι ισχυρισμός. Χωρίζει την πρόθεση πριν από τη λίστα.
2. **Κουμπί «όλες οι υπηρεσίες»** μετά από 6 κάρτες — λύνει το μεταβλητό πλήθος.
3. **Στρώμα κοινών κλάσεων πάνω από τα tokens** (`.gbp-section`, `.gbp-card`,
   `.gbp-button--primary`). Ο spine έλυσε το χρώμα· η **δομή** μένει ανά theme.
4. **Κανόνας κληρονομιάς**: pattern που εισάγεται κληρονομεί, δεν αντικαθιστά.
5. **Style Guide ως ξεχωριστή οθόνη** (Kadence) — εξαιρετικό εσωτερικό QA.

### ❌ Δεν αξίζουν

1. **Σειρές με σήματα κριτικών** (Google/BBB/Facebook/Yelp) — ψεύτικα trust signals.
2. **Ισχυρισμοί μακροβιότητας στο hero** («over 25 years») — invented facts.
3. **Πυκνότητα lorem ipsum** που καμία μικρή επιχείρηση δεν γεμίζει.
4. **Ύψος σελίδας ~4.850px** και στα δύο demos.
5. **30 media queries** με device-specific breakpoints αντί content-driven.
6. **Φόρμα callback ως προεπιλογή** — δεν έχουμε endpoint για leads.
7. **Cookie banner** — μηδέν third-party ⇒ δεν χρειάζεται.

### Τι έγινε με αυτή τη γνώση

Υλοποιήθηκε ως **Vitrina Spine**: έντεκα ρόλοι με δεσμευμένο σκοπό, με τα ζεύγη
`on-` του Material και τη λογική «ένα swap ξαναβάφει τα πάντα» του Radix.

Τρία πράγματα φάνηκαν μόνο επειδή μετρήθηκαν:

- το ωμό accent **ως κείμενο σε σκούρη ζώνη** απέτυχε σε 6 στις 7 παλέτες
- το `accent-ink` μετριέται στη **δυσκολότερη** επιφάνεια, όχι στην ευκολότερη
- το `on-accent` **δεν είναι πάντα λευκό** — πάνω σε amber είναι σκούρο

---

# Pending Commercial Review

Δεν απορρίφθηκαν. Τα premium demos τους **δεν είναι δημόσια** — χρειάζεται νόμιμη
πρόσβαση (άδεια). Αν αποκτηθεί, επιστρέφουν στον κύκλο ανάλυσης.

| Builder | Τι ξέρουμε | Γιατί αξίζει επιστροφή |
|---|---|---|
| **Bricks** | 8 design sets (Karlson, Auron, Velora, Liv, Sizzle, Reality, Digital) + **Wireframes: 180+ modular sections** | Η βιβλιοθήκη ενοτήτων είναι ακριβώς η δομή που μας λείπει μετά τον Color Spine. |
| **Breakdance** | 100+ layout components, UI kit «Samba», αναφορά σε «Global Styles» | Θα δείξει πώς οργανώνεται βιβλιοθήκη ενοτήτων σε κλίμακα. |
| **Elementor** | 30+ container kits, 100+ section kits, κατηγορίες ανά κλάδο | Ο μεγαλύτερος όγκος επαγγελματικών kits της αγοράς. |
| **Oxygen** | class-first workflow, «variables» για global τιμές | Η προσέγγιση developer στα tokens — χρήσιμη αντιπαραβολή. |

**Κόστος πρόσβασης:** άδεια ανά builder. Απόφαση του ιδιοκτήτη — όχι του agent.
Και αν αποκτηθεί: **μόνο σχεδιαστική λογική**, ποτέ κώδικας ή assets.

---

# Open Source Sources

Δημόσιος κώδικας και δημοσιευμένα design systems — αναλύονται ελεύθερα.

| Πηγή | Q | Κατάσταση |
|---|---|---|
| [Radix Themes](https://www.radix-ui.com/themes/docs/theme/color) | 5 | ✅ αναλύθηκε — 12-step scale |
| [Material 3](https://m3.material.io/styles/color/roles) | 5 | ✅ αναλύθηκε — ρόλοι + ζεύγη `on-` |
| [Vercel Geist](https://vercel.com/geist/colors) | 4 | ✅ αναλύθηκε — 10 βήματα |

**Δεν αναλύθηκαν ακόμη:** shadcn/ui (theming layer), Tailwind (spacing/type scale),
Open Props, Every Layout (layout primitives), USWDS και GOV.UK Design System — τα
δύο τελευταία είναι το ισχυρότερο δημόσιο υλικό για **accessibility contract**.
Προτεραιότητα όταν ξεκινήσει το δεύτερο επίπεδο design system.

---

# Real Business References

Πραγματικές ελληνικές επιχειρήσεις — για γλώσσα, δομή προσφοράς και το τι όντως
γράφουν οι πελάτες μας.

**Κενό. Δεν έχει γίνει ακόμη κύκλος.**

Γιατί έχει σημασία: όλα τα παραπάνω είναι αγγλόφωνα demos με lorem ipsum. Δεν μας
λένε πώς περιγράφει τις υπηρεσίες του ένας Έλληνας υδραυλικός, τι ωράριο γράφει,
πώς διατυπώνει τιμές, ή τι εμπιστεύεται ο πελάτης του. Είναι η μόνη πηγή που δεν
αντικαθίσταται από builders.

Όταν γίνει: **μόνο δημόσιες σελίδες**, μηδέν προσωπικά δεδομένα, μηδέν αντιγραφή
κειμένου ή φωτογραφιών — μόνο μοτίβα.

---

## Screenshots

Εκτός repo, σε `%TEMP%/vitrina-refs/`: `avada-plumber`, `astra-plumber02`,
`breakdance-samba` (desktop/tablet/mobile + `measurements.json`). Υλικό ανάλυσης —
δεν γίνονται ποτέ commit.

## Μάθημα για τη μεθοδολογία

Οι **εμπορικές σελίδες** των builders δεν περιγράφουν ποτέ το σύστημά τους. Λένε
«300+ templates» και τίποτα για το πώς κρατιούνται συνεπή. Πήγαινε στα `/docs/`,
`/help-center/` ή στα design systems. Πέρασε στο `SKILL.md §0`.

---

# Candidate Future Themes — gap analysis 2026-08-11γ

Ερώτημα: **ποια themes αξίζει να δημιουργήσουμε**, όχι πόσα μπορούμε.
Βάση σύγκρισης: τα 40 καταχωρημένα αρχέτυπα (37 ενεργά + 4 legacy).

## Τι καλύπτεται ήδη — και γι' αυτό απορρίπτεται

| Pattern | Το καλύπτει |
|---|---|
| stacked editorial · longform · magazine στήλες | `editorial` `longform` `magazine` |
| sticky conversion rail | `sidebar` |
| bento / modular πλέγμα | `bento` `neighborhood-market` |
| brutalist oversized τυπογραφία | `poster` `type-gallery` |
| ελβετικό grid · ήρεμο minimal | `grid` `quiet` |
| menu board / κατάλογος | `warmth` `counter-menu` `ember` |
| gallery έργων · portfolio | `canvas` `runway` `cinematic` `infinite` |
| motion-first | `kinetic` `living` |
| μία οθόνη, μηδέν σκρολ | `dispatch` |
| triage «τι θέλεις να κάνεις» | `clinic-triage` |
| κάρτα προσφοράς πάνω στο hero | `callout` |
| ευρετήριο τομέων | `marble` |
| ετικέτες προϊόντων | `terra` |
| process-first αφήγηση | `microbakery-lab` |

**Η αισθητική κάλυψη είναι πλήρης.** Κάθε νέο reference που είναι «άλλο χρώμα πάνω
στον ίδιο σκελετό» απορρίπτεται αυτόματα.

## References που εξετάστηκαν σε αυτόν τον κύκλο

| Reference | Αποτέλεσμα |
|---|---|
| [Astra Cleaning-04](https://websitedemos.net/cleaning-services-04/) | **Απορρίφθηκε.** Το μόνο νέο του είναι πλέγμα υπηρεσιών από φωτογραφικά πλακίδια με χρωματικό πέπλο — απαιτεί **εικόνα ανά υπηρεσία**. Ο πελάτης μας συνήθως δεν έχει καμία· στο `no-photo` mode καταρρέει. Τα υπόλοιπα είναι ο γνωστός σκελετός. |
| [Avada Plumber](https://avada.website/plumber/) | Ήδη καταγεγραμμένο. Το triage επιπέδου υπηρεσίας είναι **section**, όχι theme. |
| Open-source Next.js/Astro ([AstroWind](https://github.com/arthelokyo/astrowind), [Astroship](https://github.com/surjithctly/astroship), [Startup](https://github.com/NextJSTemplates/startup-nextjs), [Astrofy](https://github.com/manuelernestog/astrofy) — όλα MIT) | **Απορρίφθηκαν ως πηγές themes.** Το οικοσύστημα είναι SaaS / startup / portfolio. Καμία τοπική επιχείρηση — ίδιο εύρημα με τα award galleries. Οι άδειες είναι καθαρές (MIT), αλλά δεν υπάρχει τι να πάρουμε. |

## Τα πραγματικά gaps — και γιατί ΔΕΝ είναι themes

Τέσσερα UX patterns λείπουν όντως από τα 37. Και τα τέσσερα είναι **ενότητες ή
επεκτάσεις του data contract**, όχι δομικά αρχέτυπα:

| Gap | Vertical | Τι χρειάζεται | Επίπεδο |
|---|---|---|---|
| **Πριν/μετά** | αισθητική, ελαιοχρωματιστές, οδοντίατροι, ανακαινίσεις | ζεύγη εικόνων — το `gallery[{image,title}]` δεν τα υποστηρίζει | contract + section |
| **Ομάδα / πρόσωπα** | πολυϊατρείο, κομμωτήριο, δικηγορικό, coaches | `people[{name,role,photo}]` — δεν υπάρχει | contract + section |
| **Πακέτα / επίπεδα υπηρεσίας** | συντήρηση, λογιστικά, συνδρομές, καθαρισμοί | `tiers[{name,includes}]` — δεν υπάρχει | contract + section |
| **Περιοχές εξυπηρέτησης ως κύρια IA** | τεχνίτες πολλών περιοχών, delivery, σχολές οδηγών | **τίποτα — το `AREAS` υπάρχει ήδη** | section μόνο |

Ένα theme είναι δομικό αρχέτυπο. Ένα «πριν/μετά» ή ένα «πακέτα» είναι **ενότητα
που πρέπει να δουλεύει σε πολλά themes** — αν γίνει theme, το pattern κλειδώνεται
σε μία αισθητική και δεν το βλέπει ποτέ ο πελάτης που διάλεξε άλλο design.

## Πρόταση

> **No new theme justified.**

Τα gaps ανήκουν στο **Component Contract** του δεύτερου επιπέδου design system
(βλ. `skills/vitrina-design-system/ARCHITECTURE.md §3.4`), μαζί με τις αντίστοιχες
επεκτάσεις του data contract. Σειρά προτεραιότητας όταν φτάσουμε εκεί:

1. **Πακέτα/επίπεδα** — επιβεβαιωμένο από reference (Avada), καθαρά τίμιο (δομή
   της προσφοράς, όχι ισχυρισμός), και χωρίς ανάγκη φωτογραφιών
2. **Περιοχές ως IA** — μηδενικό κόστος contract, το `AREAS` υπάρχει
3. **Ομάδα** — υψηλή αξία εμπιστοσύνης, αλλά θέλει φωτογραφίες προσώπων
4. **Πριν/μετά** — ισχυρότατο conversion, αλλά **επικίνδυνο**: το `CLAUDE.md`
   απαγορεύει ρητά ψεύτικο before/after. Μπαίνει μόνο με πραγματικά ζεύγη πελάτη
   και ρητή σήμανση προέλευσης

## Τι θα άλλαζε αυτό το συμπέρασμα

Ένα reference που δείχνει **διαφορετική αρχιτεκτονική πληροφορίας**, όχι
διαφορετική ενότητα. Παραδείγματα που θα άξιζαν theme:

- σελίδα οργανωμένη γύρω από **διαθεσιμότητα/ημερολόγιο** (χρειάζεται backend
  κρατήσεων που δεν έχουμε — άρα όχι τώρα)
- σελίδα οργανωμένη γύρω από **τιμοκατάλογο** ως κύριο περιεχόμενο, όχι ως ενότητα
- σελίδα όπου η **περιοχή** είναι το πρώτο φίλτρο και όλα τα υπόλοιπα ακολουθούν

Κανένα από τα τρία δεν βρέθηκε σε αυτόν τον κύκλο.
