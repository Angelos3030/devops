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
