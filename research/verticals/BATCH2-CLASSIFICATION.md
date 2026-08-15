# Batch 2 — 29 υποψήφιοι, 12 οικογένειες

**Ημερομηνία:** 2026-08-15 · Πηγή: κατηγορία **Α** μόνο (βλ. [`LICENSE-MAP.md`](LICENSE-MAP.md))
Επιλογή: [`batch2-selection.json`](batch2-selection.json) · Μετρικές: `sites/artifacts/fidelity/cand-metrics.json`

**Απόδοση 29/29** σε 1440×1024 και 390×844. Μηδέν σπασμένες εικόνες, μηδέν
οριζόντια υπερχείλιση σε όλα. Άδεια: όλα από Templatemo/Tooplate → εμπορική με
αφαιρέσιμο credit, **0 LICENSE_BLOCKED**.

## Σφάλμα αποτύπωσης που διορθώθηκε πριν από κάθε κρίση

Η πρώτη λήψη έβγαλε το **Gymso Fitness με κενές ενότητες**. Δεν έφταιγε το
template: οι `wow.js`/`AOS` κρατούν `opacity:0` μέχρι το στοιχείο να μπει στο
viewport, και το `fullPage` screenshot γυρίζει στην κορυφή πριν ενεργοποιηθούν.
Χωρίς τη διόρθωση θα το είχα χαρακτηρίσει σπασμένο. Το `shot-batch.mjs` τώρα
εξουδετερώνει τα animations πριν από τη λήψη — και τα **29 ξαναποτυπώθηκαν**.

Αυτό είναι το ίδιο μοτίβο που είχε εμφανιστεί στο Blue (Batch A). Δεύτερη φορά
που μια «άδεια σελίδα» ήταν σφάλμα μέτρησης, όχι πραγματικότητα.

---

## Κριθέντα οπτικά (6)

| Οικογένεια | Υποψήφιος | Ταξινόμηση | Γιατί |
|---|---|---|---|
| **Medical** | [Medic Care](https://templatemo.com/tm-565-medic-care) | ✅ **PORT_OK** | Ήρεμο μπλε/λευκό, ένας γιατρός, ωράριο + διεύθυνση. Ταιριάζει στο «calm, clean, reassuring» του `docs/18`. Φέρνει **εναλλασσόμενο timeline** που λείπει |
| Medical | [Health](https://www.tooplate.com/view/2098-health) | ⛔ **FIT_REJECT** | Πολυϊατρείο: 3 γιατροί, τμήματα, «Latest News». Ο Έλληνας πελάτης είναι μονοπρόσωπο ιατρείο· μετά τις αφαιρέσεις μένει σκελετός. Επίσης 7 × `h1` |
| **Fitness** | [Gymso Fitness](https://www.tooplate.com/view/2121-gymso-fitness) | ✅ **PORT_OK** | **Εβδομαδιαίο πρόγραμμα σε πλέγμα** — δομή ανύπαρκτη στα 56 και ακριβώς ό,τι χρειάζεται γυμναστήριο/σχολή χορού. Μαθήματα με τιμή → services model |
| **Property** | [Villa Agency](https://templatemo.com/tm-591-villa-agency) | ✅ **PORT_OK** · ↪️ **REDIRECT_TO_VERTICAL: property** | Είχε μπει λάθος στο hospitality: είναι **μεσιτικό**, όχι ξενοδοχείο. Κάρτες ακινήτου με τιμή/τ.μ./δωμάτια + φίλτρα → `inventoryOptions`. Το μόνο listing-driven theme |
| **Trades** | [Clean Work](https://www.tooplate.com/view/2137-clean-work) | ✅ **PORT_OK** | Κάρτες υπηρεσίας με **τιμή + διάρκεια** — η ακριβέστερη αντιστοίχιση στο `priceFrom`/`duration` που έχει βρεθεί. Ωράριο εξυπηρέτησης, τηλέφωνο στην κορυφή |
| **Automotive** | [Garage](https://www.tooplate.com/view/2109-garage) | ⛔ **FIT_REJECT** | **Αγορά κλασικών αυτοκινήτων**: αναζήτηση με εύρος τιμής, «Post New Car», dealers, ταξινόμηση. Δεν είναι συνεργείο· το `motor` καλύπτει ήδη το επάγγελμα |
| **Retail** | [Moso Interior](https://www.tooplate.com/view/2135-moso-interior) | ✅ **PORT_OK** · ↪️ **REDIRECT_TO_VERTICAL: retail** | Είχε μπει στο construction. Είναι **κατάστημα προϊόντων με τιμές και κατηγορίες αλλά ΧΩΡΙΣ καλάθι** — το μοναδικό μοτίβο retail που υποστηρίζει το Vitrina. Η κάρτα «Ωράριο» πάνω από φωτογραφία είναι δομή που λείπει |

### Αφαιρέσεις που απαιτεί το συμβόλαιο αλήθειας στα PORT_OK

| Theme | Τι φεύγει | Κανόνας |
|---|---|---|
| Medic Care | «Our Patients» μαρτυρίες, φόρμα ραντεβού | `SECTION_POLICY.testimonial = frozenset()` · δεν υπάρχει ροή κράτησης |
| Gymso | Δύο γυμναστές | `team` δέχεται μόνο `REAL_OWNER_PERSON` |
| Villa Agency | Μετρητές «34 κτίρια / 12 χρόνια / 24 βραβεία» | Χωρίς τεκμήριο στο intake δεν αποδίδονται |
| Clean Work | Αστέρια αξιολόγησης, «Happy Customers», λογότυπα «Trusted by companies» | Επινοημένες κριτικές· ξένα σήματα χωρίς τεκμήριο |

Και στα τέσσερα οι αφαιρέσεις είναι **ενότητες χωρίς δεδομένα**, το ίδιο
προηγούμενο με το Blue — όχι αναδιάταξη αρχιτεκτονικής.

---

## Αποτυπωμένα, ΜΗ κριθέντα οπτικά (23)

Δεν τα ταξινομώ. Ένα «πράσινο επειδή δεν κοίταξα» είναι ακριβώς η αποτυχία που
απαγορεύει το CLAUDE.md. Έχουν **αποδοθεί και επαληθευτεί τεχνικά** (0 σπασμένες,
0 overflow) και οι εικόνες υπάρχουν — μένει μόνο η οπτική κρίση.

| Οικογένεια | Εκκρεμείς | Screenshot |
|---|---|---|
| Events | venue, leadership_event, wedding_lite, event_invitation | `cand-<name>.jpg` |
| Tourism | journey, woox_travel, adventure, flight, compass | ” |
| Retail | sixteen_clothing, video_catalog, catalog_z, zay_shop, hexashop, little_fashion | ” |
| Beauty | beauty, barber_shop, glossy_touch | ” |
| Construction | moso_interior, kool_form_pack | ” |
| Education | grad_school | ” |
| Trades | electric_xtra | ” |
| Music | modern_musician | ” |

**Σημείωση για το retail:** έξι από τα επτά είναι e-commerce με καλάθι
(`cart=true` στις μετρικές). Με βάση το προηγούμενο Aviato/Grill/Sweet Bakery
είναι πιθανότατα FIT_REJECT, αλλά **δεν το δηλώνω χωρίς να τα δω**.

**Σημείωση προέλευσης:** το Garage έχει στο footer «Designed by Web Domus Italia
– Web Agency». Το studio το διαθέτει ως δικό του. Δεν επηρέασε την ταξινόμηση
(απορρίφθηκε στην καταλληλότητα), αλλά αν κάποιο άλλο Tooplate template δείξει
ξένη υπογραφή, χρειάζεται έλεγχος προέλευσης πριν από port.

---

# Οι 22 εκκρεμείς — ταξινομήθηκαν

**Ημερομηνία:** 2026-08-15 · συνέχεια από το NEXT_ACTION.

Έξι κρίθηκαν με **οπτικό έλεγχο**. Δώδεκα κρίθηκαν από το **αποδοσμένο
περιεχόμενο και τις μετρικές** — όχι από αισθητική εκτίμηση: όταν η ίδια η
σελίδα γράφει «our website is under construction» ή «Buy Tickets», η
καταλληλότητα κρίνεται χωρίς να χρειάζεται γούστο. Τέσσερα παραμένουν αδήλωτα.

## ✅ PORT_OK (2)

| Υποψήφιος | Vertical | Γιατί |
|---|---|---|
| [Barber Shop](https://templatemo.com/tm-586-barber-shop) | beauty | Σταθερή πλαϊνή πλοήγηση, υπηρεσίες ως κάρτες εικόνας με τιμή, **τιμοκατάλογος με διάστικτες γραμμές** (δομή που λείπει), κάρτα «OPEN DAILY», υποκαταστήματα. Αφαιρούνται: «Get 32% Discount / Promo Code», «Hurry Up!», φόρμα κράτησης, οι δύο κουρείς |
| [Compass](https://templatemo.com/tm-609-compass) | ↪️ **content/editorial** | Το καλύτερα σχεδιασμένο του batch: full-bleed hero με αριθμό τεύχους, drop caps, pull quotes σε πλάγια serif, αριθμημένα κεφάλαια με γεωγραφικά metadata, masonry «Field Notes». **Δεν** είναι tourism — δεν έχει εκδρομές, τιμές ή κρατήσεις |

> ⚠️ **Προϋπόθεση για το Compass:** η ταυτότητά του **είναι** το μακρύ κείμενο.
> Με φτωχό intake καταρρέει. Πρέπει να προτείνεται μόνο όταν υπάρχει πραγματικό
> αφηγηματικό υλικό (οινοποιείο, αγροτουρισμός, boutique κατάλυμα, φωτογράφος).
> Αυτό είναι περιορισμός αντιστοίχισης, όχι αναδιάταξη αρχιτεκτονικής.

## ⛔ FIT_REJECT (12)

| Υποψήφιος | Γιατί |
|---|---|
| **Grad School** | Πλατφόρμα online μαθημάτων: εγγραφή λογαριασμού και **αντίστροφη μέτρηση «win $326»** — ίδιο μοτίβο κατασκευασμένης πίεσης με το Sweet Bakery. `h1`=0 |
| **Adventure** | Γενικό agency με όνομα «adventure»: «Social Media / Web Marketing», «Our Team», showcase με **γραφεία και laptops**. Ίδιο μοτίβο με Airspace/Bingo. `h1`=9 |
| **Journey** | Το hero είναι **μηχανή διαθεσιμότητας** (προορισμός/δωμάτια/ενήλικες/παιδιά/check-in). Το Vitrina δεν έχει κρατήσεις· χωρίς αυτήν μένει διάταξη χρωματικών μπλοκ του 2016 |
| **Electric Xtra** | Παρά το όνομα: «FUTURE IS NOW — next dimension of digital innovation». Tech/SaaS, όχι ηλεκτρολόγος. Μπήκε λάθος από τη λέξη «electric» |
| **Venue** | «Popular / Most Visited / Blog Entries / Best Finder For You» — **κατάλογος-ευρετήριο**, όχι site επιχείρησης |
| **Leadership Event** | Συνέδριο 2022 με ομιλητές, πρόγραμμα, τιμολόγηση και **Buy Tickets**. Δεν είναι ελληνική μικρή επιχείρηση |
| **Wedding Lite** | «Bratt Jolie — We're getting married — RSVP». Πρόσκληση **του ζευγαριού**, όχι site wedding planner ή κτήματος |
| **Glossy Touch** | Επίδειξη glass morphism, συνολικό ύψος **1569px** — μία οθόνη χωρίς δομή επιχείρησης |
| **Sixteen Clothing** | «FLASH DEALS / LAST MINUTE DEALS» — e-commerce προσφορών με κατασκευασμένη πίεση. `h1`=0 |
| **Zay Shop** | Αυτοπεριγράφεται «Zay eCommerce — Tiny and Perfect eCommerce Template». Καλάθι |
| **Hexashop** | «Men's / Women's / Kid's … Purchase Now!» — πλήρες e-shop |
| **Catalog-Z** | Γκαλερί φωτογραφιών με **«9.906 views»** ανά άλμπουμ — επινοημένες μετρήσεις· και δεν είναι retail |

## ⛔ QUALITY_REJECT (2)

| Υποψήφιος | Γιατί |
|---|---|
| **Little Fashion** | Επαγγελματικό αλλά **πλεονάζει με το Moso Interior** στο ίδιο vertical και δεν φέρνει δομή που λείπει. Ίδιο σκεπτικό με το 459 Pizza |
| **Flight** | **Οριζόντια υπερχείλιση 407px στα 390** — σφάλμα στο υποχρεωτικό viewport, όχι θέμα γούστου. Επιπλέον `h1`=0 |

## ⛔ NOT_A_WEBSITE (2)

| Υποψήφιος | Γιατί |
|---|---|
| **Kool Form Pack** | «Notify me — our website is **under construction**» με αντίστροφη μέτρηση. Σελίδα αναμονής |
| **Event Invitation** | «You're Invited — join us for an exceptional gathering». Πρόσκληση μίας εκδήλωσης |

## ⏳ Αδήλωτα (4)

**Δεν τα είδα, άρα δεν τα ταξινομώ.** Είναι αποτυπωμένα και τεχνικά καθαρά·
μένει μόνο η οπτική κρίση:

`woox_travel` (tourism) · `beauty` (beauty) · `modern_musician` (music) ·
`video_catalog` (→ πιθανό redirect σε creative)

## Αποτέλεσμα ανά vertical

| Vertical | PORT_OK | Κατάσταση |
|---|---|---|
| Beauty | +1 (Barber Shop) | σύνολο **4** |
| Content / editorial | +1 (Compass, redirect) | **νέο vertical** |
| Education | 0 | ⚠️ **SOURCE_GAP** — ο μόνος υποψήφιος ήταν πλατφόρμα μαθημάτων |
| Tourism | 0 | ⚠️ **SOURCE_GAP** — 4/5 απορρίφθηκαν, 1 αδήλωτο |
| Events | 0 | ⚠️ **SOURCE_GAP** — και τα 4 ήταν συνέδριο, πρόσκληση ή ευρετήριο |
| Retail | 0 νέα | Το Moso Interior παραμένει το μόνο· 6/6 τα υπόλοιπα με καλάθι ή πλεονασμό |
| Trades | 0 νέα | Το Clean Work παραμένει το μόνο |
| Carpenter | 0 | ⚠️ **SOURCE_GAP** — ο μόνος υποψήφιος ήταν σελίδα «under construction» |
| Music | — | 1 αδήλωτο |
