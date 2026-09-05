# Χρέωση + Domain/DNS — έλεγχος ετοιμότητας παραγωγής

**Ημερομηνία:** 2026-08-30 · **Περιβάλλον:** staging (Supabase staging + Stripe test mode)
**Χωρίς deploy, χωρίς push, χωρίς αγορά domain, χωρίς πραγματική κάρτα, χωρίς εγγραφή σε παραγωγή.**

---

## Ετυμηγορία

| περιοχή | κατάσταση |
|---|---|
| **DOMAIN AVAILABILITY SEARCH** | **READY για gTLD · NOT READY για `.gr`** — χτίστηκε σε αυθεντική πηγή· το `.gr` περιμένει λογαριασμό registrar (§Α) |
| **MANUAL DOMAIN FULFILLMENT** | **READY** — ροή αιτήματος, κατάσταση, επανέλεγχος και ουρά operator, 45/45 (§Β) |
| **AUTOMATIC PURCHASE** | **DISABLED** — επαληθευμένα ανενεργό (§Γ) |
| **STRIPE** | **NOT READY** — δύο P0· το ένα διορθώθηκε εδώ, το άλλο είναι εμπορική απόφαση |
| **DOMAIN (σύνδεση/DNS end-to-end)** | **NOT READY** — λειτουργεί, αλλά χειροκίνητα και χωρίς κατάσταση |
| **DNS AUTOMATION** | **NOT READY** — ο αυτοματισμός στον κώδικα στοχεύει λάθος αρχιτεκτονική |
| **CUSTOM DOMAIN** | **NOT READY** — δουλεύει, αλλά μόνο με άνθρωπο στη διαδικασία |

### Τελική ετυμηγορία: **NO-GO**

Η Vitrina **δεν** μπορεί σήμερα να πάρει με ασφάλεια πληρώνοντα πελάτη από το
checkout ως το ενεργό domain. Δύο ανεξάρτητοι λόγοι, ο καθένας αρκετός:

1. **Διαφημίζεται «πρώτος μήνας δωρεάν» που δεν υπάρχει.** Ο πελάτης
   υπογράφει checkbox για δωρεάν μήνα και χρεώνεται €14.99 αμέσως.
2. **Το domain δεν ενεργοποιείται μόνο του.** Κάθε πληρωμένη παραγγελία
   περιμένει άνθρωπο να αγοράσει χειροκίνητα και να τρέξει CLI.

Ένα τρίτο, που **βρέθηκε και διορθώθηκε σε αυτόν τον έλεγχο**, θα ήταν από
μόνο του καταστροφικό: ο webhook έσκαγε σε κάθε νέο πελάτη.

---

## Τι μετρήθηκε

| σουίτα | αποτέλεσμα | αρχείο |
|---|---|---|
| **Διαθεσιμότητα + αίτημα domain** | **45/45** | `availability_e2e.py` |
| Stripe E2E (υπογεγραμμένα webhooks, staging DB) | **20/25** | `stripe_e2e.py` |
| Domain/DNS + ασφάλεια | **24/29** | `domain_security_e2e.py` |
| Διαθεσιμότητα (unit, χωρίς δίκτυο) | **14/14** | `tests/test_domain_availability.py` |
| Συμβόλαιο webhook (regression) | **4/4** | `tests/test_stripe_webhook_contract.py` |
| Υπάρχουσες σουίτες μετά τις αλλαγές | **10/10 OK** | claim, upload, storage, provider, kernel, migration, intake, recommendation |

Οι δικλείδες που ελέγχθηκαν πριν από κάθε γραφή: `VITRINA_ENV=staging`,
`sk_test_`, και **απουσία** `SUPABASE_URL_PRODUCTION` από το μηχάνημα — η
εγγραφή σε παραγωγή είναι αρχιτεκτονικά αδύνατη, όχι απλώς απαγορευμένη.

---

# Α. DOMAIN AVAILABILITY SEARCH

## Α.1 Το εύρημα που καθορίζει τα πάντα: το `.gr` δεν έχει αυθεντικό δημόσιο πρωτόκολλο

Δεν το υπέθεσα — το μέτρησα, και σε **τρία** ανεξάρτητα σημεία:

| έλεγχος | αποτέλεσμα |
|---|---|
| IANA RDAP bootstrap (`data.iana.org/rdap/dns.json`, έκδοση 2026-07-23) | `.gr` **δεν υπάρχει**· `.com`, `.net`, `.org`, `.shop` υπάρχουν |
| IANA TLD record για `gr` (`whois.iana.org`) | οργανισμός ICS-FORTH GR, πεδίο **`whois:` ΚΕΝΟ** |
| υποψήφιοι WHOIS hosts | `whois.nic.gr`, `whois.ics.forth.gr`, `whois.forth.gr` **δεν λύνονται**· `whois.grnet.gr` λύνεται αλλά **δεν απαντά στη θύρα 43** |

Άρα: για `.gr` **δεν υπάρχει δωρεάν αυθεντικός έλεγχος**. Απαιτείται λογαριασμός
registrar. Αντίθετα, για τα gTLD το RDAP είναι αυθεντικό, δωρεάν και γρήγορο —
μετρημένο ζωντανά:

```
google.com                  HTTP 200 → ΠΙΑΣΜΕΝΟ   60ms
zzq7xaudit-nope-9f3k2.com   HTTP 404 → ΕΛΕΥΘΕΡΟ   61ms
wikipedia.org               HTTP 200 → ΠΙΑΣΜΕΝΟ  843ms
google.gr                   ΧΩΡΙΣ RDAP
```

## Α.2 Τι χτίστηκε — `src/domain_availability.py`

```
πελάτης γράφει «  https://WWW.Καφέ-Μήτσος.GR/menu »
   → normalize_domain()   NFC → αφαίρεση scheme/www/path/θύρας → IDN punycode
                          → έλεγχος κάθε label (LDH, 1-63, όχι παύλα σε άκρα)
   → dispatch ανά κατάληξη
        έχει RDAP;  →  RDAP: 200 = πιασμένο · 404 = ελεύθερο
                                429/403/5xx/timeout = ΑΓΝΩΣΤΟ
        αλλιώς      →  registrar API· χωρίς ρυθμισμένο registrar = ΑΓΝΩΣΤΟ
   → Availability(status, source, checked_at, reason)
```

**Τρία αποτελέσματα, ποτέ δύο.** Το `unknown` είναι πλήρης απάντηση, όχι
σφάλμα προς απόκρυψη. Κάθε αποτυχία παρόχου δίνει `unknown` — μετρήθηκε για
timeout, 502, 503, 429, 403, πτώση δικτύου, απρόσμενη εξαίρεση και αποτυχία
του ίδιου του IANA bootstrap. **Καμία δεν δίνει `available`.**

## Α.3 Η εικασία DNS καταργήθηκε στην πηγή της

Ο παλιός `DnsRegistrar` ρωτούσε το DNS για SOA και θεωρούσε το NXDOMAIN
«μάλλον ελεύθερο». Το DNS δεν ξέρει τι είναι **κατοχυρωμένο** — ξέρει τι είναι
**ρυθμισμένο**. Παρκαρισμένο domain δεν έχει DNS, οπότε φαινόταν ελεύθερο και
ο πελάτης πλήρωνε €24 για κάτι που δεν μπορούσε να πάρει.

Τώρα επιστρέφει `available: None`. Ο κώδικας DoH αφαιρέθηκε· υπάρχει test που
το επιβάλλει (`test_no_doh_lookup_left_in_the_code`).

## Α.4 Ποιον registrar για το `.gr` — έρευνα

| πάροχος | `.gr` | availability API | registration API | DNS API | sandbox | κρίση |
|---|---|---|---|---|---|---|
| **Openprovider** | **ναι — διαπιστευμένος `.gr` registrar** | ναι, `POST /v1/domains/check`, Bearer auth, OpenAPI spec | ναι, REST | ναι | **ναι**, `api.sandbox.openprovider.nl:8480/v1beta/` με ελεύθερη εγγραφή | **ΠΡΟΤΕΙΝΕΤΑΙ** |
| **Pointer.gr** | ναι (ελληνικός) | ναι, `domain-check` (XML) | ναι — **ήδη υλοποιημένο** στο `registrar_pointer.py`, δοκιμασμένο στο sandbox | όχι (μόνο NS) | ναι, αλλά **επιστρέφει `available: 0` για τα πάντα** | εφεδρεία· η διαθεσιμότητα δεν επαληθεύεται πριν την παραγωγή |
| **Papaki** | ναι | **καμία τεκμηριωμένη προγραμματιστική διεπαφή** — το «Domain Names search API for Simple Resellers» είναι ενσωματώσιμη φόρμα, και ο `.gr` έλεγχός τους περιγράφεται ως **χειροκίνητος** («we manually review your domain registration request») | δεν τεκμηριώνεται δημόσια | — | — | **ΑΚΑΤΑΛΛΗΛΟ** |
| RDAP | **όχι** | ναι για gTLD, δωρεάν, χωρίς λογαριασμό | — | — | — | **ήδη σε χρήση** για gTLD |

Το υπάρχον `PapakiRegistrar` έχει **μαντεμένα** endpoints — η ίδια του η
τεκμηρίωση το παραδέχεται. Δεν χρησιμοποιήθηκε και δεν πρέπει.

**Κόστος/απαιτήσεις Openprovider:** `.gr` περίπου **€12,50 ανά διετία** (το
μητρώο δέχεται ΜΟΝΟ διετίες). Χρειάζεται λογαριασμό reseller· το sandbox είναι
ελεύθερο για δοκιμή. Δεν άνοιξα λογαριασμό και δεν αγόρασα τίποτα.

## Α.5 Έλεγχοι — `availability_e2e.py`, **45/45**

| ομάδα | τι επαληθεύτηκε |
|---|---|
| αυθεντικό αποτέλεσμα | πιασμένο → `unavailable`· ελεύθερο → `available`· η πηγή είναι το μητρώο· υπάρχει χρονοσήμανση |
| `.gr` | **ποτέ** ψεύτικο `available`· δηλώνεται ρητά η αιτία |
| άκυρη είσοδος | **11/11** απορρίπτονται (κενό, `.gr`, `a..gr`, `-x.gr`, `x-.gr`, χωρίς κατάληξη, path traversal, >63, `ελ`, `http://`, `@@@.gr`) |
| ελληνικά / IDN | punycode σωστό· ο πελάτης βλέπει το δικό του κείμενο· **NFC**: δύο γραφές → ένα punycode· θόρυβος καθαρίζεται |
| αποτυχίες παρόχου | timeout, 5xx, 429, δίκτυο κάτω, απρόσμενο, αποτυχία bootstrap → **όλα `unknown`** |
| κατάργηση εικασίας | ο `DnsRegistrar` δεν αποφαίνεται· δεν έμεινε κώδικας DoH |
| endpoint | τρεις σαφείς καταστάσεις· άκυρο μέσα σε λίστα δεν ρίχνει τα υπόλοιπα |

Μόνιμα unit tests: `tests/test_domain_availability.py` (**14**), χωρίς δίκτυο.

## Ετυμηγορία Α

**READY για gTLD** (`.com/.net/.org/.shop`…) — αυθεντικό, δωρεάν, δοκιμασμένο.
**NOT READY για `.gr`**, που είναι η αγορά μας: επιστρέφει τίμια `unknown`
μέχρι να ρυθμιστεί λογαριασμός Openprovider. Το UI **δεν επιτρέπεται** να
παρουσιάσει το `unknown` ως ελεύθερο.

---

# Β. MANUAL DOMAIN FULFILLMENT — READY

## Β.1 Η ροή

```
POST /domain/request  {client_id, domain, claim_token?}
  → ταυτοποίηση κατόχου (σύνδεση Ή claim token — το funnel είναι site-first)
  → normalize + έλεγχος διαθεσιμότητας
  → unavailable → HTTP 409, ΚΑΜΙΑ παραγγελία
  → unknown     → καταγράφεται ρητά ότι ΔΕΝ επιβεβαιώθηκε, ο operator το βλέπει
  → available   → domain_orders: status = pending_fulfillment
                  + availability, availability_source, availability_checked_at,
                    requested_at, client_id, domain      (amount_cents = 0)
  ΚΑΜΙΑ ΑΓΟΡΑ. Επαληθεύτηκε: 0 κλήσεις σε register_domain.

operator, πριν αγοράσει:
  db.record_fulfillment_check(order_id, νέος έλεγχος)
  → ακόμα ελεύθερο  → μένει pending_fulfillment  (fulfillment_availability=available)
  → πιάστηκε        → status = unavailable_at_fulfillment + αιτία
```

## Β.2 Γιατί δύο χωριστά πεδία διαθεσιμότητας

Το `availability` είναι **τι είδε ο πελάτης** — απόδειξη, δεν ξαναγράφεται
ποτέ. Το `fulfillment_availability` είναι **τι ίσχυε τη στιγμή της αγοράς**.
Επαληθεύτηκε ότι ο επανέλεγχος δεν επικαλύπτει τον πρώτο:
`πελάτης=available · operator=unavailable`.

Η κατάσταση `unavailable_at_fulfillment` είναι καθαρή: ούτε `failed` (δεν
φταίει τεχνικό σφάλμα) ούτε `active` (δεν αποκτήθηκε). Ο operator ξέρει ότι
χρειάζεται επιστροφή χρημάτων ή νέα επιλογή.

## Β.3 Σχήμα — `db/migrations/0006_domain_availability.sql`

Μόνο προσθετικές αλλαγές· εφαρμόστηκε στο staging. Περιλαμβάνει:

- τα έξι νέα πεδία με σχόλια στη βάση
- **λεξιλόγιο καταστάσεων** ως `CHECK … NOT VALID` (ισχύει για νέες γραμμές,
  δεν μπορεί να αποτύχει σε υπάρχοντα δεδομένα)
- index ουράς: `(status, requested_at) WHERE status='pending_fulfillment'`
- **μοναδικό index**: ένα ανοιχτό αίτημα ανά `(client_id, domain)`

## Β.4 Έλεγχοι

| σενάριο | αποτέλεσμα |
|---|---|
| διαθέσιμο domain → αίτημα | ✓ `pending_fulfillment`, όλα τα πεδία γεμάτα, €0 |
| **καμία αγορά** | ✓ 0 κλήσεις `register_domain` |
| μη διαθέσιμο | ✓ HTTP 409, καμία γραμμή |
| διπλό αίτημα | ✓ ίδια παραγγελία, όχι δεύτερη γραμμή |
| δύο πελάτες | ✓ χωριστές παραγγελίες |
| ο Α ζητά για τον Β | ✓ HTTP 404, καμία γραμμή στον Β |
| χωρίς ταυτοποίηση | ✓ HTTP 401 |
| διαθεσιμότητα άλλαξε πριν την εκτέλεση | ✓ `unavailable_at_fulfillment` + αιτία, ο πρώτος έλεγχος ανέπαφος |
| ακόμα ελεύθερο στον επανέλεγχο | ✓ μένει `pending_fulfillment` |
| ουρά operator | ✓ δείχνει διαθεσιμότητα **και** χρόνο ελέγχου |

Το τελευταίο ήταν **πραγματικό κενό που βρέθηκε εδώ**: το
`list_domain_orders` επέλεγε σταθερή λίστα στηλών που δεν περιλάμβανε τα νέα
πεδία — ο operator θα έβλεπε ουρά χωρίς την πληροφορία που του χρειάζεται.
Διορθώθηκε, και η ουρά ταξινομείται πλέον με `requested_at` (παλαιότερο
πρώτο), σύμφωνα με το index.

## Ετυμηγορία Β: **READY**

Με μία προϋπόθεση: όσο το `.gr` δίνει `unknown`, ο operator πρέπει να ελέγχει
**χειροκίνητα** τη διαθεσιμότητα πριν αγοράσει — που ούτως ή άλλως το απαιτεί
η διαδικασία.

---

# Γ. AUTOMATIC PURCHASE — DISABLED

Επαληθεύτηκε ότι **δεν μπορεί** να συμβεί, σε τρία επίπεδα:

```
✓ DOMAIN_REGISTRAR=dns → register_domain σηκώνει σφάλμα
✓ /domain/purchase χωρίς admin token → HTTP 403 (DOMAIN_ADMIN_TOKEN κενό → πάντα 403)
✓ Papaki credentials = placeholder κείμενο· Pointer credentials ΚΕΝΑ
✓ /domain/request: 0 κλήσεις register_domain
```

Καμία αγορά domain δεν επιχειρήθηκε σε κανένα σημείο αυτού του ελέγχου.

---

# STRIPE — NOT READY

## Διαδρομή υλοποίησης

```
web/connect.html
  → POST /create-checkout            src/meta_oauth.py:92
      stripe.checkout.Session.create(mode=subscription)
      metadata.client_id  +  subscription_data.metadata.client_id
  → (ο πελάτης πληρώνει στο Stripe)
  → POST /stripe/webhook             src/stripe_webhook.py:35
      stripe.Webhook.construct_event(payload, sig, WEBHOOK_SECRET)
      ├ customer.subscription.created/updated → upsert_subscription + set_client_status
      ├ customer.subscription.deleted         → set_client_status(cancelled)
      └ checkout.session.completed            → link_client_email  [+ domain fulfilment]
  → GET  /clients/{id}/account       src/meta_oauth.py:493   (entitlement)
  → POST /clients/{id}/billing-portal                        (ακύρωση/αλλαγή)
```

## P0-1 — Ο webhook έσκαγε σε ΚΑΘΕ νέο πελάτη (ΒΡΕΘΗΚΕ ΚΑΙ ΔΙΟΡΘΩΘΗΚΕ)

Το `requirements.txt` έγραφε `stripe>=8.0.0` **χωρίς άνω όριο**. Δεν υπάρχει
lockfile, οπότε κάθε build του Railway τραβούσε την τελευταία έκδοση —
εγκατεστημένη εδώ: **15.2.0**.

Από το stripe-python 12 και μετά το `StripeObject` **έπαψε να είναι `dict`**:

```
StripeObject είναι dict;  False
έχει .get;                False
o.get("metadata", {})  →  AttributeError: get
```

Ο handler έκανε `obj.get("metadata", {})` σε τρία σημεία. Αποτέλεσμα:

| event | μονοπάτι | συνέπεια |
|---|---|---|
| `customer.subscription.created` | νέος πελάτης, δεν υπάρχει ακόμα γραμμή | `AttributeError` → **HTTP 500** |
| `checkout.session.completed` | κάθε checkout | `AttributeError` → **HTTP 500** |

Το Stripe ξαναπροσπαθεί και ξανααποτυγχάνει. **Καμία συνδρομή νέου πελάτη δεν
αποθηκευόταν ποτέ, κανένα email δεν συνδεόταν.** Ο πελάτης πλήρωνε €14.99 και
έβλεπε άδειο dashboard για πάντα. Δεν το έπιανε κανένα test επειδή κανένα test
δεν έστελνε υπογεγραμμένο event στον πραγματικό handler.

**Μετρημένη επίδραση της διόρθωσης: 6/25 → 20/25.**

Η διόρθωση: η υπογραφή εξακολουθεί να επαληθεύεται από το Stripe, αλλά τα
**δεδομένα διαβάζονται από το ίδιο το επαληθευμένο JSON** — ανεξάρτητα από
έκδοση βιβλιοθήκης.

```python
stripe.Webhook.construct_event(payload, sig, cfg.STRIPE_WEBHOOK_SECRET)  # επαλήθευση
event = json.loads(payload)                                              # δεδομένα
```

Κλειδώθηκε με `tests/test_stripe_webhook_contract.py` (4 tests): δύο
λειτουργικά που στέλνουν υπογεγραμμένα events, ένα στατικό για την
**προέλευση** του σώματος, ένα ότι η υπογραφή ελέγχεται ακόμα. Το
`requirements.txt` πήρε άνω όριο `<16.0.0`.

## P0-2 — Ο «πρώτος μήνας δωρεάν» δεν υπάρχει (ΑΝΟΙΧΤΟ)

Διαφημίζεται σε τρία σημεία:

- `web/index.html:7` — meta description: «€14,99/μήνα, πρώτος μήνας δωρεάν»
- `web/index.html:1020` — τιμοκατάλογος: «Πρώτος μήνας δωρεάν.»
- `web/connect.html:241` — **checkbox συγκατάθεσης**: «Συμφωνώ ότι **μετά τον
  δωρεάν πρώτο μήνα** η συνδρομή ανανεώνεται αυτόματα με €14.99/μήνα»

Η πραγματική ρύθμιση, διαβασμένη ζωντανά από το Stripe:

```
price_1TtT9w…  unit_amount 1499 eur   ✓ ταιριάζει το €14,99
               recurring.trial_period_days: null      ✗ κανένας δωρεάν μήνας
```

Και το session που παράγει ο **πραγματικός κώδικας** του `/create-checkout`:

```
amount_total 1499 eur · discounts [] · total_details.amount_discount 0
```

**Ο πελάτης χρεώνεται €14.99 τη στιγμή της εγγραφής**, αφού έχει τσεκάρει ότι
συμφωνεί με δωρεάν πρώτο μήνα. Αυτό δεν είναι bug υλοποίησης — είναι απόκλιση
ανάμεσα στο τι πουλάμε και τι εισπράττουμε, με γραπτή συγκατάθεση από κάτω.

**Απαιτούμενη απόφαση, όχι κώδικας:** ή μπαίνει
`subscription_data={"trial_period_days": 30}` στο `/create-checkout` (ή
`trial_period_days` στο price), ή φεύγει η υπόσχεση από τις τρεις σελίδες.
Δεν το άλλαξα: είναι εμπορική/νομική απόφαση, όχι τεχνική.

## Λοιπά ευρήματα Stripe

| # | εύρημα | σοβαρότητα | απόδειξη |
|---|---|---|---|
| S1 | **Καμία αποθήκευση event id.** Η idempotency στηρίζεται αποκλειστικά στο ότι το `upsert_subscription` είναι upsert. Κάθε μη-idempotent ενέργεια που θα προστεθεί (email, τιμολόγιο, αγορά domain) θα εκτελεστεί πολλαπλά. | P1 | το ίδιο event ×3 δεν διπλασίασε τη συνδρομή (τύχη του upsert), αλλά δεν υπάρχει πίνακας processed events |
| S2 | **Events εκτός σειράς επαναφέρουν ακυρωμένη συνδρομή.** Μετά από `subscription.deleted` (→`cancelled`), ένα καθυστερημένο `updated:active` ξαναγράφει `active`. Το `created` του event δεν συγκρίνεται ποτέ. | **P1** | μετρήθηκε: `cancelled` → `active` |
| S3 | **Άγνωστο `client_id` = poison pill.** FK violation → ανεπίληπτη εξαίρεση → HTTP 500 → το Stripe ξαναπροσπαθεί επ' άπειρον και τελικά απενεργοποιεί το endpoint, μπλοκάροντας **όλους** τους πελάτες. | **P1** | `subscriptions_client_id_fkey` → HTTP 500 |
| S4 | **`invoice.payment_failed` δεν αντιμετωπίζεται καθόλου.** Η αποτυχία ανανέωσης φαίνεται μόνο έμμεσα, όταν το Stripe στείλει `subscription.updated: past_due`. Κανένα μήνυμα, καμία αιτία, κανένα dunning. | P1 | ο handler δεν αναγνωρίζει κανένα `invoice.*` |
| S5 | **Επιστροφές/αμφισβητήσεις δεν αντιμετωπίζονται.** Καμία αναφορά σε `charge.refunded` ή `charge.dispute.created`. Πελάτης που παίρνει πίσω τα χρήματα παραμένει `active`. | P1 | καμία αναφορά σε refund/dispute στον κώδικα |
| S6 | **Το `/create-checkout` δεν γράφει τίποτα.** Ανάμεσα στο «ο πελάτης πάτησε πληρωμή» και στο webhook, το σύστημα **δεν έχει καμία εγγραφή ότι εκκρεμεί πληρωμή**. Αν το webhook χαθεί, κανείς δεν το μαθαίνει ποτέ. | P1 | δεν υπάρχει DB κλήση στο `create_checkout` |
| S7 | **Το `/create-checkout` είναι αφύλακτο.** Δέχεται οποιοδήποτε `client_id`. Τρίτος μπορεί να πληρώσει για site που δεν του ανήκει και — αν το site δεν έχει ακόμη email — να δέσει το δικό του email πάνω του (`link_client_email`) και να πάρει την πρόσβαση. | P2 | το `link_client_email` προστατεύει μόνο όσα ΕΧΟΥΝ ήδη email («kept-existing», επαληθεύτηκε) |
| S8 | **`tax_behavior: unspecified`, καμία ρύθμιση ΦΠΑ.** Πώληση σε ελληνικές επιχειρήσεις χωρίς χειρισμό ΦΠΑ/τιμολόγησης. | P2 | από το price object |

## Τι πέρασε καθαρά (Stripe)

- Επαλήθευση υπογραφής: έγκυρη δεκτή· άκυρη, απούσα, λάθος μυστικό → 400
- **Replay 1 ώρας απορρίπτεται** (ανοχή 5′ του Stripe) ✓
- Συνδρομή αποθηκεύεται, ο πελάτης γίνεται `active`, το plan γράφεται
- Το email αγοράς συνδέεται· **δεύτερο email δεν αντικαθιστά το πρώτο**
- `past_due` → `paused`, επιτυχής ανανέωση → `active` ξανά
- Ακύρωση → `cancelled`
- Checkout χωρίς email, subscription χωρίς `client_id`: δεν σκάνε, δεν γράφουν
- **Απομόνωση πελατών: ο Α και ο Β έχουν χωριστές συνδρομές, καμία διασταύρωση**

---

# DOMAIN — NOT READY · DNS AUTOMATION — NOT READY · CUSTOM DOMAIN — NOT READY · AUTOMATIC PURCHASE — NOT IMPLEMENTED

## Τι υποστηρίζεται πραγματικά

| | δυνατότητα | κατάσταση |
|---|---|---|
| **A** | subdomain της Vitrina (`x.getvitrina.gr`) | **δεν υπάρχει** — το `sites/middleware.js` δεν έχει tenant scheme για υποτομείς· το δωρεάν preview είναι **διαδρομή** στο Railway URL |
| **B** | custom domain πελάτη | **υπάρχει** — CF Worker → Railway (`x-tenant-host`) → middleware → `/site/<host>` |
| **C** | αυτόματη αγορά domain | **δεν υπάρχει** — ενεργός adapter `DnsRegistrar`· το `register_domain` σηκώνει σφάλμα |
| **D** | αυτόματο DNS από την εφαρμογή | **δεν υπάρχει στην πράξη** — το `add_dns_records` καλείται ΜΟΝΟ από το μονοπάτι `papaki`, που δεν είναι ρυθμισμένο |

## Διαδρομή υλοποίησης

```
POST /domain/suggest    src/main.py:65   → dom.suggest_domains   (ελληνικό slug)
POST /domain/check      src/main.py:73   → get_registrar().check_availability
                                            DnsRegistrar → Cloudflare DoH SOA (ΕΚΤΙΜΗΣΗ)
POST /domain/create-checkout src/main.py:83
        db.create_domain_order (status=pending)
        Stripe Session mode=payment, 2400 cents, metadata.kind=domain_purchase
        db.set_domain_order_checkout (status=checkout_created)
   → πληρωμή →
POST /stripe/webhook  · kind == domain_purchase
        status=paid
        DOMAIN_REGISTRAR ∈ {manual, dns, ""} → status=pending_fulfillment
                                                print «αγόρασε ΧΕΙΡΟΚΙΝΗΤΑ»  ← ΕΔΩ ΣΤΑΜΑΤΑΕΙ
        DOMAIN_REGISTRAR == papaki           → dom.buy_and_setup(...)
                                                purchase → create_zone → add_dns → save_domain
```

Ο **πραγματικός** δρόμος που χρησιμοποιείται σήμερα είναι το χειροκίνητο
`scripts/link_domain.py` — και είναι το μόνο σημείο που ξέρει τη σωστή συνταγή
Railway (targetPort 8080, `_railway-verify` TXT, `customDomainIssueCertificate`).

## Το όριο της αγοράς — ΣΤΑΜΑΤΗΣΑ ΕΔΩ, ΟΠΩΣ ΖΗΤΗΘΗΚΕ

Καμία αγορά domain δεν επιχειρήθηκε. Επαληθεύτηκε ότι **δεν μπορεί** να συμβεί:

```
✓ registrar=dns → register_domain σηκώνει: «η αγορά χρειάζεται Papaki reseller»
✓ /domain/purchase χωρίς admin token → HTTP 403 (DOMAIN_ADMIN_TOKEN κενό → πάντα 403)
✓ τα Papaki credentials είναι κυριολεκτικά placeholder: "<το endpoint …>", "<το api key σου>"
```

Δύο adapters αγοράς υπάρχουν στον κώδικα:

- **`PapakiRegistrar`** — η ίδια η τεκμηρίωσή του λέει *«uses conservative
  conventional paths … if Papaki provides different paths/payloads, update only
  this adapter»*. Δηλαδή τα endpoints είναι **μαντεμένα** και δεν έχουν
  δοκιμαστεί ποτέ σε πραγματικό API. Δεν είναι υλοποίηση· είναι υπόθεση.
- **`PointerRegistrar`** — πραγματική υλοποίηση (`registrar_pointer.py`, 266
  γραμμές), με **sandbox by default** (`POINTER_SANDBOX != "0"`) και σωστή
  παρατήρηση ότι μόνο το registry ξέρει τη διαθεσιμότητα. Είναι ο μόνος
  ρεαλιστικός δρόμος προς αυτοματοποίηση, αλλά **δεν είναι ενεργός** και
  απαιτεί στατική IP + credentials.

Δεν ενεργοποίησα κανέναν από τους δύο.

## Ευρήματα Domain/DNS

| # | εύρημα | σοβαρότητα | απόδειξη |
|---|---|---|---|
| D1 | **Το `buy_and_setup` δεν είναι ατομικό.** Σειρά: αγορά → zone → DNS → DB. Αν αποτύχει το zone μετά την αγορά, το domain είναι **αγορασμένο και πληρωμένο** αλλά **δεν γράφεται πουθενά**. Ο webhook το σημειώνει `failed`. Μη ανακτήσιμο χωρίς άνθρωπο. | **P0** (αν ενεργοποιηθεί αγορά) | μετρήθηκε: `purchase` κλήθηκε, `save_domain` **δεν** κλήθηκε |
| D2 | **Οι αποτυχίες DNS καταπίνονται.** Το `add_dns_records` τυπώνει `⚠️` και συνεχίζει. Μερική δημιουργία → `save_domain(status="active")`. | **P0** (αν ενεργοποιηθεί) | μετρήθηκε: η εγγραφή `api` απέτυχε, η ροή συνέχισε, το domain γράφτηκε `active` |
| D3 | **Καμία επαλήθευση πιστοποιητικού.** Το `buy_and_setup` επιστρέφει `ssl: "universal_auto"` — σταθερή συμβολοσειρά. Κανείς δεν ελέγχει αν εκδόθηκε ποτέ. | P1 | επιστρέφεται χωρίς κλήση |
| D4 | **Ο αυτοματισμός DNS στοχεύει λάθος αρχιτεκτονική.** Το `add_dns_records` γράφει `www → *.pages.dev` και `api → *.up.railway.app`. Το `sites/middleware.js` όμως εξυπηρετεί μέσω **Cloudflare Worker → Railway**, και το `scripts/link_domain.py` υλοποιεί τη σωστή συνταγή. Επιπλέον **δεν δημιουργείται καμία εγγραφή apex** — το `https://example.gr` χωρίς `www` δεν λύνεται. | **P1** | δύο ασύμβατα μονοπάτια DNS στο ίδιο repo |
| D5 | **Καμία διαδρομή αφαίρεσης/rollback.** Δεν υπάρχει `customDomainDelete`, ούτε διαγραφή DNS, ούτε endpoint αποσύνδεσης. Το μόνο που υπάρχει είναι cascade delete **ολόκληρου του πελάτη**. Πελάτης που φεύγει αφήνει το domain να δείχνει στη Vitrina για πάντα. | **P1** | αναζήτηση σε `src/` + `scripts/` |
| D6 | **Το `scripts/link_domain.py` απενεργοποιεί την επαλήθευση TLS** (`ssl.CERT_NONE`, `check_hostname=False`) ενώ στέλνει `RAILWAY_TOKEN` και `CF_API_TOKEN`. Τα διαπιστευτήρια της υποδομής ταξιδεύουν χωρίς επαλήθευση πιστοποιητικού. | **P1** | γραμμές 57-59 |
| D7 | **Το `/domain/create-checkout` είναι αφύλακτο** και δέχεται `client_id` **και** `pages_subdomain`/`railway_url` από το σώμα. Επαληθεύτηκε: ξένος άνοιξε παραγγελία domain για τον πελάτη Β. Οι τιμές φτάνουν στο metadata → `buy_and_setup` → **εγγραφή DNS**. Αν ενεργοποιηθεί το `papaki`, τρίτος πληρώνει €24 και βάζει τη Vitrina να στήσει `www.<domain> → δικός-του-host` μέσα στον δικό μας λογαριασμό Cloudflare. | **P1** (σήμερα αδρανές) | μετρήθηκε: HTTP 200, 1 παραγγελία στον Β |
| D8 | **Η διαθεσιμότητα είναι εκτίμηση.** Ο `DnsRegistrar` μαντεύει από NXDOMAIN: παρκαρισμένο domain χωρίς DNS φαίνεται «ελεύθερο». Ο πελάτης πληρώνει €24 για κάτι πιασμένο. Το πεδίο `estimate: true` επιστρέφεται σωστά — **αλλά πρέπει να φαίνεται στο UI**. | P2 | ο ίδιος ο κώδικας το δηλώνει |

## Τι πέρασε καθαρά (Domain)

- Οι προτάσεις παράγονται σωστά και είναι έγκυρα `.gr` labels
- Πιασμένο (`google.gr` → false) και ελεύθερο domain αναγνωρίζονται σωστά
- **9/9 άκυρες είσοδοι απορρίπτονται**: `.com`, ελληνικοί χαρακτήρες, πολύ
  κοντό, παύλα στην αρχή/τέλος, path traversal, >63 χαρακτήρες, υποτομέας, κενό
- Χωρίς `CF_API_TOKEN` → καθαρό, κατανοητό σφάλμα
- Το όριο της αγοράς κρατά (3/3)

---

# ΑΣΦΑΛΕΙΑ — καθαρή στη διασταύρωση πελατών

| έλεγχος | αποτέλεσμα |
|---|---|
| Ο Α βλέπει τον δικό του λογαριασμό | ✓ HTTP 200 |
| Ο Α **δεν** βλέπει τη συνδρομή του Β | ✓ HTTP 404 |
| Ο Α **δεν** ανοίγει το billing portal του Β | ✓ HTTP 404 |
| Ο Α **δεν** σκανδαλίζει publish για τον Β | ✓ HTTP 404 |
| Χωρίς σύνδεση δεν διαβάζεται λογαριασμός | ✓ HTTP 401 |

Το `require_client_access` δένει την πρόσβαση στην **ιδιοκτησία μέσω email** και
επιστρέφει **404 αντί 403**, ώστε να μη διαρρέει ποιοι πελάτες υπάρχουν. Σωστό.

*Σημείωση μεθόδου:* η επαλήθευση JWT ανήκει στο Supabase· εδώ ελέγχθηκε η
**εξουσιοδότηση**, που είναι δικός μας κώδικας, με προσομοιωμένο συνδεδεμένο χρήστη.

## Webhook

- ✓ Επαληθεύει υπογραφές Stripe
- ✓ Απορρίπτει άκυρη / απούσα / λάθος-μυστικό
- ✓ Απορρίπτει replay εκτός ανοχής 5′
- ✗ *Παρατήρηση:* κακοσχηματισμένο event αναφέρεται κι αυτό ως «invalid
  signature» — δύο διαφορετικά σφάλματα με το ίδιο μήνυμα, δυσκολεύει το debug

## Διαπιστευτήρια

- ✓ Το `/site-data` δεν περιέχει κανένα μυστικό
- ✓ Κανένα `print` μυστικού σε `domain/main/stripe_webhook/registrars`
- ✓ Κανένα διαπιστευτήριο υποδομής δεν φτάνει σε AI provider
- ✗ **D6**: το `link_domain.py` στέλνει `RAILWAY_TOKEN`/`CF_API_TOKEN` με
  απενεργοποιημένη επαλήθευση TLS

---

# ΑΤΟΜΙΚΟΤΗΤΑ ΑΠΟΤΥΧΙΑΣ — η μηχανή καταστάσεων

## Συνδρομή

```
(καμία εγγραφή)          ← S6: το /create-checkout ΔΕΝ γράφει τίποτα
      │  πληρωμή
      ▼
clients.status: pending ──→ active ──→ paused ──→ active
                              │  (past_due)   (ανανέωση)
                              └──→ cancelled ──✗ S2: παλιό event το γυρνά σε active
```

**Κενά:** δεν υπάρχει κατάσταση «εκκρεμεί πληρωμή» (S6)· η ακύρωση δεν είναι
τελική (S2)· η αποτυχία πληρωμής δεν έχει αιτία (S4)· η επιστροφή χρημάτων δεν
αλλάζει τίποτα (S5).

## Domain

```
domain_orders: pending → checkout_created → paid → ┬→ pending_fulfillment  (χειροκίνητο)
                                                    ├→ active
                                                    └→ failed (+ error)

domains.status: ΠΑΝΤΑ "active"   ← μοναδική τιμή που γράφεται ποτέ
```

Ο πίνακας `domain_orders` έχει **σωστή** μηχανή καταστάσεων με αποθηκευμένο
σφάλμα. Ο πίνακας `domains` **δεν έχει καμία**: γράφεται `active` τη στιγμή που
οι DNS εγγραφές *επιχειρήθηκαν*, ανεξάρτητα από το αν πέτυχαν (D2) ή αν
εκδόθηκε πιστοποιητικό (D3).

## Μη ανακτήσιμες καταστάσεις

| σενάριο | σημερινή συμπεριφορά |
|---|---|
| Stripe OK, DB αποτυγχάνει | HTTP 500 → το Stripe ξαναπροσπαθεί → ανακτήσιμο ✓ |
| DB OK, webhook ξαναέρχεται | upsert → ανακτήσιμο ✓ (αλλά μόνο κατά τύχη, S1) |
| Άγνωστο `client_id` | **500 για πάντα** — poison pill (S3) ✗ |
| Αγορά OK, zone αποτυγχάνει | **domain αγορασμένο, καμία εγγραφή** (D1) ✗ |
| Μερική δημιουργία DNS | **σημειώνεται `active`** (D2) ✗ |
| Πιστοποιητικό δεν εκδόθηκε | **σημειώνεται `active`** (D3) ✗ |

---

# ΠΑΡΑΤΗΡΗΣΙΜΟΤΗΤΑ

| κατάσταση που ζητήθηκε | παρατηρήσιμη; |
|---|---|
| payment pending | **ΟΧΙ** — καμία εγγραφή πριν το webhook (S6) |
| payment active | ναι — `clients.status=active` + `subscriptions.status` |
| payment failed | **μερικώς** — `paused`, χωρίς αιτία· κανένα `invoice.*` (S4) |
| subscription cancelled | ναι — `cancelled` (αλλά αναστρέψιμο, S2) |
| domain requested | ναι — `domain_orders: pending/checkout_created` |
| domain configuring | **ΟΧΙ** — δεν υπάρχει τέτοια κατάσταση |
| DNS ready | **ΟΧΙ** — δεν καταγράφεται |
| SSL pending | **ΟΧΙ** — δεν καταγράφεται |
| domain active | **αναξιόπιστη** — γράφεται χωρίς απόδειξη (D2, D3) |
| domain failed | ναι για παραγγελίες (`domain_orders.status=failed` + `error`)· **όχι** για domains |

Υπάρχουν «μυστήριες καταστάσεις»: ένα domain σημειωμένο `active` που δεν
εξυπηρετεί, και μια πληρωμή που ξεκίνησε αλλά δεν άφησε ίχνος.

---

# ΑΠΑΙΤΟΥΜΕΝΕΣ ΔΙΟΡΘΩΣΕΙΣ

## Μπλοκάρουν την παραγωγή

1. **P0-2** Απόφαση για τον δωρεάν μήνα: `trial_period_days=30` ή αφαίρεση της
   υπόσχειας από `web/index.html` (×2) και `web/connect.html` (×2).
2. **S3** Πιάσε την εξαίρεση γύρω από το `upsert_subscription`· άγνωστο
   `client_id` πρέπει να καταγράφεται και να επιστρέφει 200, όχι να μπλοκάρει
   την ουρά όλων.
3. **S2** Σύγκρινε το `created` του event πριν γράψεις κατάσταση.
4. **S6** Γράψε γραμμή «εκκρεμεί πληρωμή» στο `/create-checkout`, όπως ήδη
   κάνει σωστά το `/domain/create-checkout`.
5. **S1** Πίνακας `stripe_events(event_id primary key)` με έλεγχο πριν από
   κάθε ενέργεια — απαραίτητος πριν προστεθεί οποιαδήποτε μη-idempotent ενέργεια.
6. **D6** Αφαίρεσε `ssl.CERT_NONE` από το `scripts/link_domain.py`.
7. **D7** Βάλε `require_client_access` σε `/create-checkout` και
   `/domain/create-checkout`· πάρε `pages_subdomain`/`railway_url` από τη
   ρύθμιση του server, ποτέ από το σώμα του αιτήματος.

## Πριν ενεργοποιηθεί οποιαδήποτε αυτόματη αγορά

8. **D1** Κάνε το `buy_and_setup` ανακτήσιμο: γράψε το domain **αμέσως μετά την
   αγορά**, με κατάσταση, και προχώρα σε βήματα με retry.
9. **D2** Το `add_dns_records` πρέπει να **σηκώνει** σφάλμα, όχι να τυπώνει.
10. **D3** Επαλήθευσε την έκδοση πιστοποιητικού πριν γράψεις `active`.
11. **D4** Ένα μονοπάτι DNS, όχι δύο: το `scripts/link_domain.py` είναι το
    σωστό — να γίνει βιβλιοθήκη που καλεί και ο webhook. Πρόσθεσε apex.
12. **D5** Φτιάξε διαδρομή αφαίρεσης domain.
13. **S4/S5** Χειρίσου `invoice.payment_failed`, `charge.refunded`,
    `charge.dispute.created`.
14. **D8** Δείξε στο UI ότι η διαθεσιμότητα είναι εκτίμηση, ή πέρασε σε
    `PointerRegistrar` (sandbox πρώτα) για registry-authoritative έλεγχο.
15. **S8** Ρύθμισε ΦΠΑ/τιμολόγηση για ελληνικές επιχειρήσεις.

---

# ΑΡΧΕΙΑ ΠΟΥ ΑΛΛΑΞΑΝ ΣΕ ΑΥΤΟΝ ΤΟΝ ΕΛΕΓΧΟ

| αρχείο | τι |
|---|---|
| `src/stripe_webhook.py` | **P0-1**: το σώμα διαβάζεται από `json.loads(payload)`· η υπογραφή επαληθεύεται όπως πριν |
| `requirements.txt` | `stripe>=8.0.0,<16.0.0` |
| `src/domain_availability.py` | **νέο** — αυθεντική διαθεσιμότητα, τρία αποτελέσματα, IDN |
| `src/registrars.py` | ο `DnsRegistrar` δεν μαντεύει πια· ο DoH έλεγχος αφαιρέθηκε |
| `src/main.py` | `/domain/check` σε αυθεντική πηγή· **νέο** `/domain/request` (με ταυτοποίηση) |
| `src/db.py` | `create_domain_request`, `record_fulfillment_check`· η ουρά επιστρέφει τα πεδία διαθεσιμότητας |
| `db/migrations/0006_domain_availability.sql` | **νέο** — 6 πεδία, λεξιλόγιο καταστάσεων, 2 index |
| `tests/test_stripe_webhook_contract.py` | **νέο** — 4 tests |
| `tests/test_domain_availability.py` | **νέο** — 14 tests, χωρίς δίκτυο |
| `research/billing-domain/stripe_e2e.py` | **νέο** — 25 έλεγχοι σε staging |
| `research/billing-domain/domain_security_e2e.py` | **νέο** — 29 έλεγχοι |
| `research/billing-domain/availability_e2e.py` | **νέο** — 45 έλεγχοι |
| `research/billing-domain/*_results.json` | αποτελέσματα |

**Παρατήρηση εκτός σκοπού:** το `scripts/migrate.py --status` προειδοποιεί ότι
το `0003_ai_editor_revisions.sql` **άλλαξε μετά την εφαρμογή του**. Προϋπήρχε
αυτού του track και δεν το άγγιξα — αλλά σημαίνει ότι staging και παραγωγή
μπορεί να μη μοιράζονται το ίδιο σχήμα.

Καμία αλλαγή σε themes, recommendation, AI editor, homepage ή παραγωγή.
Όλες οι εγγραφές staging διαγράφηκαν (επαληθεύτηκε: 0 υπολείμματα).
Το μοναδικό Stripe test session έληξε ρητά.

---

# ΕΚΤΙΜΗΣΗ ΚΙΝΔΥΝΟΥ

| κίνδυνος | σοβαρότητα | κατάσταση |
|---|---|---|
| Χρέωση χωρίς τον διαφημισμένο δωρεάν μήνα | **κρίσιμη** — εμπορική/νομική | ανοιχτό |
| Πελάτης πληρώνει και δεν παίρνει πρόσβαση | **κρίσιμη** | **διορθώθηκε** |
| Ένα κακό event μπλοκάρει την ουρά όλων | υψηλή | ανοιχτό (S3) |
| Ακυρωμένη συνδρομή επανέρχεται μόνη της | υψηλή | ανοιχτό (S2) |
| Πληρωμή χωρίς ίχνος αν χαθεί το webhook | υψηλή | ανοιχτό (S6) |
| Πληρωμένο domain που δεν ενεργοποιείται | υψηλή | ανοιχτό — χειροκίνητο by design |
| Αγορασμένο domain χωρίς εγγραφή | κρίσιμη **αν** ανοίξει η αγορά | αδρανές (D1) |
| Ξένος στήνει DNS σε δικό του host | υψηλή **αν** ανοίξει η αγορά | αδρανές (D7) |
| Διασταύρωση δεδομένων πελατών | — | **καθαρό, 5/5** |
| Διαρροή διαπιστευτηρίων σε πελάτη/AI | — | **καθαρό** |

---

# ΣΥΣΤΑΣΗ

**NO-GO** για πληρώνοντες πελάτες.

Ο κοντινότερος ασφαλής δρόμος προς **ελεγχόμενη** παραγωγή:

1. Λύσε το P0-2 (μία απόφαση: trial ή αλλαγή κειμένου).
2. Κάνε τις διορθώσεις 2-7 — όλες μικρές, όλες στον ίδιο κώδικα.
3. Άφησε το domain **ρητά χειροκίνητο**: πες στον πελάτη «το domain σου
   ενεργοποιείται σε λίγες ώρες», κράτα το `pending_fulfillment` ως ουρά
   εργασίας, και μη διαφημίσεις αυτόματη ενεργοποίηση.
4. Μην ενεργοποιήσεις `papaki`. Αν χρειαστεί αυτοματοποίηση, ο δρόμος είναι
   `PointerRegistrar` σε sandbox, **μετά** τις διορθώσεις 8-12.

Με τα 1-3, η συνδρομή μπορεί να πουληθεί με ασφάλεια και το domain να
παραδίδεται χειροκίνητα — που είναι έντιμο και εφικτό σήμερα.

Δεν έγινε deploy, push, αγορά domain, χρέωση κάρτας ή εγγραφή σε παραγωγή.
