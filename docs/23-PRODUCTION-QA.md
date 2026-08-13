# 23 — Production QA

Τι τρέχει μετά από κάθε deploy, και **γιατί υπάρχει κάθε έλεγχος**.

```bash
node sites/tests/production_qa.mjs                     # getvitrina.gr
node sites/tests/production_qa.mjs --url <url>         # άλλη σελίδα
node sites/tests/production_qa.mjs --skip-lighthouse   # γρήγορο πέρασμα
```

## Release gate πριν από deploy

```bash
npm --prefix sites run qa:release
python -m unittest tests.test_vertical_routing
```

Το `qa:release` είναι ο deterministic πυρήνας του Website QA Agent. Ελέγχει:

- semantic media routing: οι fallback φωτογραφίες ανήκουν στο επάγγελμα,
- identity precedence: το επάγγελμα υπερισχύει των ονομάτων υπηρεσιών
  (`Οδοντιατρείο` + `Αισθητική οδοντιατρική` παραμένει health),
- τη διαδρομή επιλογή theme -> live editor -> palette/typography,
- την ανάκτηση pending site μετά από Google/email authentication,
- production build όλων των routes.

Το Python suite ελέγχει ανεξάρτητα το backend intake και το ranking των themes.
Backend και Sites πρέπει να αναπτύσσονται από το ίδιο commit. Αν αναπτυχθεί μόνο
το ένα, η αρχική μπορεί να προτείνει theme που δεν εμφανίζεται στον chooser.

Έξοδος `0` = καθαρό, `1` = κάτι έσπασε. **Δεν δίνεται link πριν βγει καθαρό.**

## Δύο επίπεδα, κανένα δεν αντικαθιστά το άλλο

**Playwright — συμπεριφορά.** Πιάνει ό,τι το Lighthouse δεν βλέπει: hover/focus,
reduced motion, τη ροή του prompt, σπασμένες εικόνες, κενά iframes.

**Lighthouse — μετρήσιμη ποιότητα.** Performance, accessibility, best practices, SEO,
Core Web Vitals.

Το Lighthouse είναι **επιπλέον** πύλη ποιότητας, όχι αντικαταστάτης. Ένα site μπορεί να
βγάλει 100 και να έχει αόρατο κουμπί ή κενό πλαίσιο.

## Thresholds

Αφήνουν περιθώριο για τη διακύμανση του Lighthouse (±5 μονάδες μεταξύ εκτελέσεων).
Στόχος: να πιάνουμε **οπισθοδρομήσεις**, όχι να κυνηγάμε τεχνητά 100άρια.

| | mobile | desktop | σημερινή τιμή |
|---|---|---|---|
| Performance | ≥ 85 | ≥ 95 | 97 / 100 |
| Accessibility | ≥ 95 | ≥ 95 | 100 / 100 |
| Best Practices | ≥ 95 | ≥ 95 | 100 / 100 |
| SEO | ≥ 95 | ≥ 95 | 100 / 100 |

| Core Web Vital | mobile | desktop | σημερινή τιμή |
|---|---|---|---|
| LCP | ≤ 2500ms | ≤ 1500ms | 1,2s / 0,3s |
| CLS | ≤ 0,05 | ≤ 0,05 | 0 / 0 |
| TBT | ≤ 350ms | ≤ 150ms | 200ms / 0ms |

**Γιατί όχι 100 παντού:** το mobile performance είναι ευαίσθητο στο δίκτυο και στην
προσομοίωση CPU· ένα όριο στο 95 θα έσπαγε τυχαία. Το **SEO στο 95** είναι σκόπιμα υψηλό —
πουλάμε SEO. Το **accessibility στο 95** επίσης: είναι φθηνό να το κρατάς ψηλά και αφορά
πραγματικούς χρήστες.

**Speed Index: χωρίς όριο.** Αναφέρεται αλλά δεν κόβει — σε lab κυμαίνεται από 0,4s έως 5s
για την ίδια σελίδα. Όριο εκεί θα παρήγαγε ψεύτικες αποτυχίες.

## Οι έλεγχοι συμπεριφοράς

Σε **1440 / 768 / 390**:

- οριζόντιο overflow
- CLS από `PerformanceObserver`
- console errors
- αιτήματα 4xx/5xx
- σπασμένες εικόνες **μετά από `img.decode()`**
- κάθε εικόνα με `width`/`height`
- iframes τρίτων

Και μία φορά: hover-scroll, το ίδιο με πληκτρολόγιο (`focus`), `prefers-reduced-motion`,
τα 6 demo links, η ροή prompt → δημιουργία.

## Μαθήματα που έγιναν έλεγχοι

Κάθε ένα προήλθε από πραγματικό bug που έφτασε στην παραγωγή.

### Lazy εικόνες: πάντα `img.decode()` πριν κρίνεις

Το `!img.complete || img.naturalWidth === 0` επιστρέφει **true για εικόνες που ακόμα
φορτώνουν**. Με lazy loading και γρήγορο scroll, το QA ανέφερε 4 σπασμένες εικόνες που
ήταν μια χαρά.

```js
await page.evaluate(() => Promise.all([...document.images].map(i => i.decode().catch(() => null))))
const broken = await page.evaluate(() => [...document.images].filter(i => i.naturalWidth === 0).length)
```

Ισχύει και αντίστροφα: χωρίς `decode()` μια πραγματικά σπασμένη εικόνα μπορεί να περάσει
αν το test τρέξει πριν αποτύχει το αίτημα.

### iframes ξένων sites: υποθέτουμε ότι θα μείνουν κενά

Πολλά sites στέλνουν `X-Frame-Options: sameorigin` ή `frame-ancestors`. Το iframe δεν
πετάει σφάλμα ορατό στον χρήστη — **μένει λευκό**. Στην αρχική μας, το site ενός πελάτη
δεν φόρτωνε ποτέ ενώ το κείμενο δίπλα υποσχόταν «αυτό που βλέπεις είναι ζωντανό».

Κανόνας: **για ξένο περιεχόμενο χρησιμοποιούμε στιγμιότυπο + σύνδεσμο, ποτέ iframe.**
Ο έλεγχος αναφέρει κάθε iframe τρίτου ως αποτυχία.

Bonus: 6 στιγμιότυπα κοστίζουν λιγότερο από 6 iframes και δεν στέλνουν τον επισκέπτη
σε τρίτους.

### Τα tests δεν γράφουν στη βάση παραγωγής

Ο έλεγχος της ροής υπέβαλλε αληθινό prompt, άρα **δημιουργούσε πελάτη σε κάθε εκτέλεση**.
Τώρα το `POST /start` κόβεται με `page.route(...).abort()` και επαληθεύεται το σώμα του
αιτήματος. Ίδια βεβαιότητα, μηδέν εγγραφές.

Γενικός κανόνας: **αν ένας έλεγχος αγγίζει endpoint που γράφει, κόψε το αίτημα και
επαλήθευσε το ωφέλιμο φορτίο.**

### Μετά το deploy, το edge είναι στιγμιαία παλιό

Η πρώτη εκτέλεση αμέσως μετά το `wrangler pages deploy` ανέφερε accessibility 94 και
παλιό HTML· η δεύτερη 100. Το Cloudflare χρειάζεται λίγα δευτερόλεπτα.

Κανόνας: **αν το QA αποτύχει αμέσως μετά από deploy, επαλήθευσε με `curl` ότι το live HTML
έχει την αλλαγή πριν κυνηγήσεις φάντασμα.**

### Το Cloudflare Pages αφαιρεί το `.html`

Το `start.html` σερβίρεται ως `/start`. Έλεγχοι URL δέχονται και τις δύο μορφές.

## Σχέση με το `design_guard.mjs`

Το [`sites/tests/design_guard.mjs`](../sites/tests/design_guard.mjs) ελέγχει τα **templates
πελατών** (αντίθεση, fonts, trackers, σπασμένες εικόνες) σε όλη τη συλλογή. Το
`production_qa.mjs` ελέγχει το **δικό μας προϊόν**. Τρέχουν και τα δύο.

Ειρωνικά, το `design_guard` έπιανε αόρατα κουμπιά σε sites πελατών ενώ το δικό μας κύριο
κουμπί είχε αντίθεση **2,6:1** (λευκό σε `#FF7A1A`). Το βρήκε το Lighthouse. Γι' αυτό
υπάρχουν δύο επίπεδα.

## Ownership και uploads

Το upload logo/φωτογραφιών έχει δύο επιτρεπτές διαδρομές και καμία τρίτη:

- μετά το login, έγκυρο bearer token ιδιοκτήτη του συγκεκριμένου `client_id`
- πριν το login, unclaimed και unexpired claim token που εκδόθηκε από το ίδιο
  onboarding και αποθηκεύτηκε στη βάση μόνο ως SHA-256 hash

Το `tests/test_upload_authorization.py` πρέπει να παραμένει στο release gate της
API υπηρεσίας. Upload χωρίς ένα από τα δύο απορρίπτεται με `401`.

## «Target crashed» στο Playwright — πρώτα ύποπτο το harness, όχι το theme

Στις 12/8/2026 το `bakery-editorial` κράσαρε τον renderer στα 390px. Απομονώθηκε
(`sites/artifacts/crash_probe.mjs`) και **δεν είναι σφάλμα του theme**:

| υπόθεση | αποτέλεσμα |
|---|---|
| πλάτος 1440 → 900 → 600 → 500 → 430 → 390 → 360 | **όλα περνούν**, ~1,1s το καθένα |
| χωρίς φωτογραφίες (`?photos=none`) | περνά |
| με animations (χωρίς `reducedMotion`) | περνά |
| και τα 7 CafeCollection variants @390 | περνούν |
| άλλο theme (`aegean`) @390 | περνά |
| 14 διαδοχικά contexts σε **ένα** browser | περνούν |

Το crash είχε συμβεί ενώ έτρεχαν **ταυτόχρονα** δεύτερος browser και `next build`.
Δηλαδή εξάντληση μνήμης του sandbox, όχι responsive defect.

**Κανόνας:** «Target crashed» σημαίνει πρώτα *πόσοι browsers τρέχουν τώρα;* — όχι
*τι έχει το theme*. Πριν κατηγορήσεις κώδικα, τρέξε το ίδιο URL μόνο του με φρέσκο
browser. Και μη σωληνώνεις QA έξοδο σε `head`: το SIGPIPE σκοτώνει τη διεργασία και
μοιάζει με κόλλημα.

⚠️ Ο Firefox δεν είναι εγκατεστημένος σε αυτό το περιβάλλον (`npx playwright install`
αν χρειαστεί cross-engine έλεγχος).
