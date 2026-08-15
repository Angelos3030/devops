# V1+V2 Restaurant / taverna / cafe / bakery — discovery με vertical-specific πηγές

**Ημερομηνία:** 2026-08-15 · **Στάδιο:** discovery μόνο. **Καμία υλοποίηση.**
Προηγούμενο: [`CANDIDATE-CLASSIFICATION.md`](CANDIDATE-CLASSIFICATION.md) (0 PORT_OK από γενική πηγή)

## Το αποτέλεσμα του νέου κανόνα πηγών, σε έναν αριθμό

| Πηγή | Τύπος | Ευρήματα | Vertical-specific; |
|---|---|---|---|
| Themefisher Bootstrap *(παλιό, γενική πηγή)* | γενικός agency κατάλογος | 8 | **0** |
| **Templatemo** `/tag/restaurant` | studio, δικά του templates | **8** | **8** |
| **ThemeWagon** `?s=restaurant` | aggregator | 12 (+40 εκκρεμή) | 12 |
| **Tooplate** `/tag/restaurant` | studio, δικά του templates | 1 | 1 |
| **Colorlib** restaurant list | studio | 0 | — |

**21 μοναδικοί υποψήφιοι, όλοι HTTP 200, όλοι νέοι** (slug-exact dedupe έναντι
`CANDIDATE-CLASSIFICATION.md`, `BATCH-A.md`, `LICENSE-GATE.md`, `THIRD-PARTY.md`,
`index.js`, και των αρχικών summaries V1/V2 → **καμία σύμπτωση**).

Ο κανόνας πηγών δούλεψε: η ίδια ερώτηση σε vertical-specific καταλόγους έδωσε
**21 food-specific** αντί για 8 γενικά agency templates.

## 🔑 Εύρημα άδειας — λύνει την εκκρεμή εμπορική απόφαση

Και τα δύο παραγωγικά studios επιτρέπουν **ρητά** αφαίρεση credit, verbatim:

| Studio | Δήλωση (αυτούσια) |
|---|---|
| **Tooplate** | «Feel free to use our templates for your commercial or non-commercial websites.» · «**You may remove any credit link and you do not need to provide a link back to our website.**» |
| **Templatemo** | «All 100% free for commercial, personal, or learning purposes.» · «Can I remove credit links from templates? **Yes, you can remove all credit links.**» |

Αυτό είναι **καλύτερη θέση από κάθε CC BY studio** που εξετάστηκε ως τώρα
(HTML5 UP, Colorlib, Untree, BootstrapMade). Η εκκρεμής απόφαση «credit σε κάθε
site πελάτη» **δεν χρειάζεται να ληφθεί** για αυτό το vertical.

⚠️ Η δήλωση είναι σε επίπεδο site, όχι αρχείο `LICENSE`. Παραμένει υποχρεωτική η
κατά-template επαλήθευση στη σελίδα του, όπως έγινε ήδη για το 417 Grill
(«commercial or non-commercial sites») και το Sweet Bakery («commercial project»).

## Υποψήφιοι — προς αξιολόγηση, ΟΧΙ ταξινομημένοι

### Templatemo (studio, credit removable) — προτεραιότητα

| # | Template | URL |
|---|---|---|
| 1 | 417 Grill | https://templatemo.com/tm-417-grill |
| 2 | 459 Pizza | https://templatemo.com/tm-459-pizza |
| 3 | 466 Cafe House | https://templatemo.com/tm-466-cafe-house |
| 4 | 507 Victory | https://templatemo.com/tm-507-victory |
| 5 | 515 Eatery | https://templatemo.com/tm-515-eatery |
| 6 | 539 Simple House | https://templatemo.com/tm-539-simple-house |
| 7 | 558 Klassy Cafe | https://templatemo.com/tm-558-klassy-cafe |
| 8 | 613 Frost Bakery | https://templatemo.com/tm-613-frost-bakery |

### Tooplate (studio, credit removable)

| # | Template | URL |
|---|---|---|
| 9 | Sweet Bakery | https://www.tooplate.com/view/2168-sweet-bakery |

> **Σημείωση προέλευσης:** το Sweet Bakery είχε απορριφθεί στο **αρχικό** V1 run με
> «no explicit license» — από **σελίδα καταλόγου**, με το ελαττωματικό κριτήριο που
> απέρριψε επίσης τα Blue και Airspace. Δεν είναι στα 11 ταξινομημένα, άρα **δεν
> είναι επανεξέταση ταξινομημένου υποψηφίου**· είναι ανάκτηση ψευδώς αρνητικού.

### ThemeWagon (aggregator — προέλευση πρώτα)

| # | Template | URL |
|---|---|---|
| 10 | Coffo | https://themewagon.com/themes/coffo/ |
| 11 | Lounge | https://themewagon.com/themes/lounge/ |
| 12 | Sarab | https://themewagon.com/themes/sarab/ |
| 13 | SpiceHaven | https://themewagon.com/themes/spicehaven/ |
| 14 | Yummy Red | https://themewagon.com/themes/yummy-red/ |
| 15 | Restaurant Tailwind | https://themewagon.com/themes/restaurant-tailwind/ |
| 16 | Delfood | https://themewagon.com/themes/delfood-free-responsive-bootstrap-… |
| 17 | Restoran | https://themewagon.com/themes/restoran-free-responsive-… |
| 18–21 | 4 × «free-bootstrap-4/5-html5-restaurant-…» | (γενικά ονόματα καταλόγου) |

⚠️ **Το ThemeWagon είναι aggregator**, όχι δημιουργός. Αναδιανέμει templates
τρίτων — το ίδιο μοτίβο με το `learning-zone/website-templates` που **έχει ήδη
αποκλειστεί** στο `SOURCE-MAP.md`. Κάθε υποψήφιος από εδώ χρειάζεται εντοπισμό του
**αρχικού δημιουργού** πριν από κάθε άλλη κρίση, αλλιώς PROVENANCE_BLOCKED.
Τα τέσσερα με γενικά ονόματα (#18–21) είναι πιθανότατα διπλότυπα μεταξύ τους.

### 40 μη αναλυμένα (δεν χάνονται σιωπηλά)

Το ThemeWagon run σταμάτησε στο όριο κόστους με **40 HIGH/MEDIUM υποψήφιους
χωρίς βαθιά ανάλυση** → [`../v01-food-themewagon/shortlist_pending.json`](../v01-food-themewagon/shortlist_pending.json).
Τα ονόματά τους είναι σχεδόν όλα παραλλαγές του «free-bootstrap-4-html5-restaurant-website-template»
— δηλαδή ο ίδιος aggregator θόρυβος. **Δεν αξίζει δεύτερο call** πριν λυθεί η προέλευση.

## Κόστος

| Run | Task id | $ |
|---|---|---|
| Tooplate | `v01-food-tooplate` | ~0,008 |
| Templatemo | `v01-food-templatemo` | ~0,021 |
| Colorlib | `v01-food-colorlib` | ~0,018 |
| ThemeWagon | `v01-food-themewagon` | ~0,044 |
| **Σύνολο** | | **~$0,091** |

Μία πηγή ανά κλήση, όπως ζητήθηκε — καμία transient JSON αποτυχία.

---

# Ταξινόμηση των 9 studio υποψηφίων

Και τα 9 **αποδόθηκαν** τοπικά (9/9) σε 1440×1024 και 390×844 και κρίθηκαν από τα
screenshots, όχι από τις περιγραφές του καταλόγου.
Μετρικές: [`../../sites/artifacts/fidelity/food-metrics.json`](../../sites/artifacts/fidelity/food-metrics.json) ·
εικόνες: `sites/artifacts/fidelity/food-<name>-{desktop,mobile}.jpg`

## Άδεια: 9/9 καθαρά

Κάθε σελίδα δηλώνει αυτούσια «You are allowed to download, edit and use this
*<X>* HTML CSS layout for your **commercial** or non-commercial sites.»
**0 LICENSE_BLOCKED.** Δύο templates (Klassy Cafe, Simple House) απαγορεύουν
επιπλέον την **αναδιανομή του ZIP σε άλλο template site** — δεν μας αφορά: το
Vitrina παραδίδει sites πελατών, δεν αναδιανέμει templates.

## Αποτέλεσμα

| # | Template | Ταξινόμηση | Λόγος σε μία γραμμή |
|---|---|---|---|
| 613 | **Frost Bakery** | ✅ **PORT_OK** | Το μόνο σύγχρονο σχέδιο του batch· φέρνει δομή που λείπει |
| 558 | **Klassy Cafe** | ✅ **PORT_OK** | Επαγγελματικό split hero + μενού με τιμές· καθαρό ταίριασμα σε ταβέρνα/καφετέρια |
| 459 | Pizza | ⛔ QUALITY_REJECT | Σωστή δομή αλλά κοινότοπη — δεν προσθέτει τίποτα στα 56 |
| 515 | Eatery | ⛔ QUALITY_REJECT | 2018, **overflow 15px**, 7 × `h1`, testimonials + chefs |
| 466 | Cafe House | ⛔ QUALITY_REJECT | Bootstrap 3.3.5 (2015), skeuomorphic, ασύμβατες εικόνες |
| 507 | Victory | ⛔ FIT_REJECT | Ό,τι απομένει μετά την αφαίρεση είναι πολύ λίγο· `h1`=0 |
| 539 | Simple House | ⛔ FIT_REJECT | Είναι σελίδα μενού, όχι site: χωρίς επικοινωνία/CTA/ωράριο |
| 417 | Grill | ⛔ FIT_REJECT | Καλάθι + λογαριασμός + blog — ίδιο μοτίβο με το Aviato |
| — | Sweet Bakery | ⛔ FIT_REJECT | Add to Cart + αντίστροφη μέτρηση + «Only 7 left in stock» |

**2 PORT_OK στα 9** — ακριβώς μέσα στο μετρημένο εύρος «1–3 ανά vertical», και τα
**πρώτα μη μηδενικά** για V1/V2.

---

## ✅ PORT_OK — αιτιολόγηση

### 613 Frost Bakery → υποψήφιο για ζαχαροπλαστείο / παγωτό / φούρνο

Το μόνο template του batch που είναι **σύγχρονου σχεδιασμού**, όχι απλώς
συντηρημένο: σταθερή πλαϊνή πλοήγηση με ωράριο στη βάση της, παστέλ παλέτα σε
θερμό off-white, display serif με πλάγια έμφαση δεύτερης γραμμής, 3D σφαίρες
αντί για stock φωτογραφία στο hero, κάρτες με badge, εποχιακά tabs.

**Δομή που λείπει από τη συλλογή:** το «4 βήματα με αριθμημένους κύκλους δίπλα σε
sticky κάρτα σύνοψης» και τα **εποχιακά tabs** δεν υπάρχουν σε κανένα από τα 56.
Αυτό —όχι το χρώμα— δικαιολογεί νέο template κατά το CLAUDE.md.

**Αφαιρέσεις χωρίς δεδομένα** (προηγούμενο: Blue): κάρτα πιστότητας με σφραγίδες,
«Book a Cart», εταιρικό footer με Careers/Press.

### 558 Klassy Cafe → υποψήφιο για ταβέρνα / καφετέρια / εστιατόριο

Ώριμο σχέδιο του 2020 που δεν έχει παλιώσει: **split hero** με χρωματικό πλακίδιο
αριστερά και slider δεξιά, ενότητα «about» με μετατοπισμένες μικρογραφίες, μενού
ως οριζόντιο carousel καρτών με ετικέτα τιμής, σκούρα ζώνη επικοινωνίας με
φόρμα σε λευκή κάρτα, εβδομαδιαίες προσφορές σε δύο στήλες με tabs.

**Αφαιρέσεις:** «Our Chefs» (η ενότητα ταυτότητας δέχεται μόνο `REAL_OWNER_PERSON`
κατά το `SECTION_POLICY` — μένει μόνο αν ο πελάτης δώσει αληθινές φωτογραφίες),
φόρμα κράτησης → τηλεφωνικό CTA, video modal.

## ⛔ Αιτιολόγηση κάθε απόρριψης

**459 Pizza** — δομικά είναι το καθαρότερο: hero → about → gallery → contact +
ωράριο + χάρτης, χωρίς καλάθι, blog, testimonials ή τιμές. Αλλά αυτή **είναι ήδη
η τυπική σπονδυλική στήλη** του Vitrina και το σχέδιο (comic γραμματοσειρά,
κεντραρισμένα πάντα, πλατιά κενά) δεν προσθέτει τίποτα. Το CLAUDE.md το λέει
ρητά: νέο template μόνο για **επαναχρησιμοποιήσιμη δομή που λείπει**.

**515 Eatery** — μοναδικό με **οριζόντια υπερχείλιση 15px** και 7 × `h1`. Το
ψηφιδωτό μενού χωρίς κενά είναι ενδιαφέρον, αλλά συνολικά είναι σχέδιο του 2018
με testimonials και «Meet our chefs» — δηλαδή δύο ενότητες που το συμβόλαιο
αλήθειας αδειάζει.

**466 Cafe House** — Bootstrap **3.3.5**: εικονογραφημένος πάγκος με λάμπες,
script γραμματοσειρές, ανάγλυφα κουμπιά. Και οι «Popular Items» δείχνουν
**φωτογραφίες τοπίου** για Americano/Cappuccino/Mocha.

**507 Victory** — οι τέσσερις κατηγορίες σε κύκλους και τα πιάτα της εβδομάδας
είναι χρήσιμα. Αλλά μισή σελίδα είναι κράτηση, «Get application for your phone»,
blog και newsletter — τίποτα από αυτά δεν έχει αντίστοιχο. Μετά την αφαίρεση
μένει σκελετός. Επίσης **κανένα `h1`**.

**539 Simple House** — parallax κεφαλίδα, φίλτρα κατηγοριών, πλέγμα 4×2 με τιμές,
ένα κείμενο. Τέλος. Χωρίς επικοινωνία, χωρίς CTA, χωρίς ωράριο στην αρχική.
Είναι **σελίδα καταλόγου**, όχι site πελάτη.

**417 Grill** — «My account», «(5 items) in your cart ($45.80)», αναζήτηση, blog,
testimonial, newsletter. Κατάστημα του 2016. Ίδιος λόγος που κόπηκε το Aviato.

**Sweet Bakery** — το σχέδιο είναι ικανό, αλλά η αρχιτεκτονική στηρίζεται σε
**Add to Cart**, **αντίστροφη μέτρηση προσφοράς**, «50% OFF» και «Only 7 left in
stock!». Η κατασκευασμένη σπανιότητα δεν είναι θέμα γούστου εδώ — **συγκρούεται
ευθέως με το συμβόλαιο αλήθειας**. Χωρίς αυτήν η σελίδα χάνει τον άξονά της.

---

## 🔧 Διόρθωση προηγούμενου συμπεράσματος — το Vitrina **έχει** τιμές

Στο [`CANDIDATE-CLASSIFICATION.md`](CANDIDATE-CLASSIFICATION.md) γράφτηκε «το
Vitrina δεν έχει ούτε καλάθι ούτε τιμές». Το μισό είναι λάθος. Στο
`sites/lib/demoData.js` υπάρχουν:

- **υπηρεσίες με τιμή:** `priceType: 'from' | 'fixed' | 'quote' | 'free'`,
  `priceFrom`, `price`, `duration`
- **κατάλογος ειδών:** `inventoryOptions` — `label`, `category`, `image`,
  `price`, `inventoryStatus`, `quantityAvailable`, `leadTime`

Άρα **μενού με τιμές και κατηγορίες αντιστοιχίζεται άμεσα** και δεν αποτελεί
λόγο απόρριψης. Ό,τι πραγματικά λείπει είναι **καλάθι και ταμείο** — αυτό
παραμένει ο λόγος για Aviato, Grill και Sweet Bakery.

Χωρίς αυτή τη διόρθωση, τα Klassy Cafe και Frost Bakery θα είχαν απορριφθεί για
ανύπαρκτο περιορισμό.

## ThemeWagon — δεν αποτυπώθηκε, και γιατί

Οι 12 υποψήφιοι μένουν **αταξινόμητοι εν αναμονή προέλευσης**. Το ThemeWagon
είναι aggregator: αναδιανέμει templates τρίτων, όπως το ήδη αποκλεισμένο
`learning-zone/website-templates`. Χωρίς τον αρχικό δημιουργό δεν υπάρχει άδεια
να επαληθευτεί — θα κατέληγαν PROVENANCE_BLOCKED όπως τα πέντε Themefisher με
repo 404. Ίδιο ισχύει για τα 40 του `shortlist_pending.json`, που είναι σχεδόν
όλα παραλλαγές του ίδιου ονόματος.

## Επόμενο βήμα (δεν εκτελέστηκε)

Υλοποίηση των δύο PORT_OK ως πιστά ports με σύγκριση 1440/390 — **δεν ξεκίνησε**,
δεν ήταν στο σκοπό αυτού του γύρου.
