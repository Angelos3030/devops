# Runbook: ελεγχόμενη εκκίνηση παραγωγής (beta 1–3 πελάτες)

**RC:** `release/prelaunch-2026-09` @ `7a8b974e0a1d1ddeb0845e085df63acbfa0c6885`
**Σύνταξη:** 2026-09-05, από read-only preflight. **Δεν εκτελέστηκε τίποτα.**

Αυτό είναι λίστα εκτέλεσης χειριστή, όχι αρχιτεκτονικός έλεγχος. Κάθε βήμα που
**μεταβάλλει** την παραγωγή έχει `[ ] ΕΓΚΡΙΣΗ ΧΕΙΡΙΣΤΗ` ακριβώς από πάνω. Χωρίς
αυτό το τσεκάρισμα, το βήμα δεν τρέχει.

Για τη λεπτομέρεια της βάσης, ο κανονικός οδηγός παραμένει το
`docs/24-PRODUCTION-MIGRATION-RUNBOOK.md` (βήματα Α–Θ). Η ΦΑΣΗ Β εδώ τον καλεί,
δεν τον αντιγράφει.

---

## 0. Τι υπάρχει σήμερα στην παραγωγή (μετρημένο, 2026-09-05)

### Τοπολογία

| Στοιχείο | Πραγματική τιμή | Πηγή μέτρησης |
|---|---|---|
| Railway project | `fulfilling-smile` `2c75c49e-…` | Railway GraphQL |
| Environment | `production` `cd172187-…` | Railway GraphQL |
| Service API | `devops` `7f3c7476-…`, root `/`, `/healthz`, ON_FAILURE x3 | `railway.toml` + API |
| Service frontend | `sites` `80f0b283-…`, root `sites/`, `npm run start`, **χωρίς healthcheck** | `sites/railway.toml` + API |
| Marketing site | Cloudflare Pages project `vitrina` → `vitrina-7uq.pages.dev` | CF API |
| Auto-deploy | **και τα δύο** services: `Angelos3030/devops` branch **`main`** | Railway repoTriggers |
| Replicas | 1 ανά service | Railway serviceInstances |

### DNS (ζώνη `getvitrina.gr`, Cloudflare, read-only)

| Record | Στόχος | Κατάσταση |
|---|---|---|
| `getvitrina.gr`, `www` | `vitrina-7uq.pages.dev` (proxied) | HTTP 200 |
| `api.getvitrina.gr` | `cfcwhplk.up.railway.app` → devops | HTTP 200, cert VALID, propagated |
| `app.getvitrina.gr` | `11o1xa75.up.railway.app` | **ΣΠΑΣΜΕΝΟ** — βλ. Υ1 |
| `koutrakiskouzines.gr`, `www` | sites (ξεχωριστή ζώνη) | cert VALID — ο πρώτος πραγματικός tenant |
| MX / SPF / DMARC | Google Workspace, `p=none` | ενεργά |

### Τι τρέχει τώρα

| | Παραγωγή σήμερα | RC |
|---|---|---|
| commit | `69f7b51c3` (main, **2026-08-22**) | `7a8b974` |
| billing foundation (0009/0010) | **ΟΧΙ** | ΝΑΙ |
| P0 fix του webhook | **ΟΧΙ** | ΝΑΙ |
| P1 social / email privacy | **ΟΧΙ** | ΝΑΙ |
| domain availability | **ΟΧΙ** | ΝΑΙ |

---

## 1. Πίνακας πυλών

| # | Πύλη | Κατάσταση | Τεκμήριο |
|---|---|---|---|
| G1 | RC κλειδωμένο και ταυτόσημο με το remote | **PASS** | `7a8b974`, working tree καθαρό |
| G2 | Στοίβα migrations 0000→0010 σε άδεια βάση | **PASS** | `tests/test_migration_chain.py` (18) |
| G3 | Baseline adoption ασφαλής και fail-closed | **PASS** | `tests/test_baseline_adoption.py` (31) |
| G4 | Απομόνωση tenant | **PASS** | 21 endpoints × 4 = 84 έλεγχοι |
| G5 | Webhook: υπογραφή, idempotency, άγνωστος πελάτης | **PASS** | 0010 + `test_webhook_unknown_client.py` (11) |
| G6 | Ο λογαριασμός Stripe μπορεί να δεχθεί χρήματα | **FAIL** | `details_submitted=false`, `charges_enabled=false` |
| G7 | Η παραγωγή είναι σε Stripe LIVE | **FAIL** | `STRIPE_SECRET_KEY` = `sk_test_` |
| G8 | Το webhook endpoint ακούει όσα events χρειάζεται ο κώδικας | **FAIL** | 3 από 6 |
| G9 | Ο chat editor λειτουργεί στην παραγωγή | **FAIL** | `DEEPSEEK_API_KEY` MISSING → 502 |
| G10 | Ο RC είναι deployed | **FAIL** | παραγωγή = 22 Αυγ |
| G11 | Η κατάσταση migration της παραγωγής είναι γνωστή | **ΑΓΝΩΣΤΗ** | κανένα production credential τοπικά |
| G12 | Το dashboard είναι προσβάσιμο σε branded domain | **FAIL** | `app.getvitrina.gr` σπασμένο |
| G13 | Υπάρχει παρακολούθηση σφαλμάτων | **ΚΕΝΟ** | κανένα Sentry/OTel/alerting |

**ΕΤΥΜΗΓΟΡΙΑ: NO-GO για λήψη χρημάτων.** Ο κώδικας είναι έτοιμος· η **παραγωγή**
δεν είναι. Έξι μπλοκαριστές, από τους οποίους ο Μ1 είναι εξωτερικός και μπορεί να
κρατήσει μέρες. Κανένας δεν απαιτεί αλλαγή πηγαίου κώδικα.

---

## 2. Μπλοκαριστές

### Μ1 — Ο λογαριασμός Stripe δεν είναι ενεργοποιημένος `ΕΞΩΤΕΡΙΚΟΣ`

Μετρήθηκε στο `acct_1RNgjS…` (GR, EUR, standard):

    details_submitted : false
    charges_enabled   : false
    payouts_enabled   : false

Καμία πραγματική χρέωση δεν είναι δυνατή. Απαιτεί υποβολή στοιχείων επιχείρησης
στο Stripe Dashboard και έγκριση από το Stripe. **Δεν το λύνει καμία ρύθμιση εδώ.**
Ξεκίνησέ το ΠΡΩΤΟ — όλα τα υπόλοιπα τελειώνουν σε ώρες, αυτό όχι.

### Μ2 — Η παραγωγή είναι σε Stripe TEST

`STRIPE_SECRET_KEY` της παραγωγής ξεκινά με `sk_test_`. Άρα και τα τέσσερα
`STRIPE_PRICE_*` είναι TEST prices και το `STRIPE_WEBHOOK_SECRET` είναι TEST
endpoint secret. Σε LIVE mode **τίποτα από αυτά δεν ισχύει**: prices, webhook
endpoint και secret δημιουργούνται ξανά.

Τι υπάρχει σήμερα σε TEST (πρότυπο για τη LIVE αναδημιουργία):

| Προϊόν | Ποσό | Περίοδος |
|---|---|---|
| Vitrina — Website | 1499 EUR cents | month |
| Vitrina Starter | 990 | month |
| Vitrina Social | 4900 | month |
| Vitrina Premium | 7900 | month |

Το `price_1RO1s2…` «Premium VoyageAI» είναι ξένο κατάλοιπο — **δεν** μεταφέρεται.

### Μ3 — Το webhook endpoint ακούει 3 από 6 events

Το `src/stripe_webhook.py` χειρίζεται έξι τύπους. Το υπάρχον endpoint
(`https://api.getvitrina.gr/stripe/webhook`) είναι εγγεγραμμένο σε τρεις.

| Event | Στο endpoint | Το χρειάζεται ο κώδικας | Τι χάνεται χωρίς αυτό |
|---|---|---|---|
| `customer.subscription.created` | ναι | ναι | — |
| `customer.subscription.updated` | ναι | ναι | — |
| `customer.subscription.deleted` | ναι | ναι | — |
| `checkout.session.completed` | **όχι** | ναι | η σύνδεση πελάτη → stripe_customer |
| `invoice.paid` | **όχι** | ναι | επιβεβαίωση ανανέωσης |
| `invoice.payment_failed` | **όχι** | ναι | **κανένα `past_due`** — κάρτα που κόβεται περνά απαρατήρητη |

### Μ4 — Ο chat editor είναι νεκρός στην παραγωγή

`DEEPSEEK_API_KEY` **MISSING** στο service `devops`. Η αλυσίδα, ιχνηλατημένη:

1. `meta_oauth.py:813` → `DeepSeekSiteEditingModel()` χωρίς ορίσματα
2. `AI_BASE_URL` και `ANTHROPIC_BASE_URL` κενά → `base_url = https://api.deepseek.com/v1`
3. `api_key = cfg.AI_API_KEY` = `sk-ant-…`
4. `model.py:174`: πρόθεμα `sk-ant-` και το endpoint δεν είναι anthropic →
   δοκιμάζει `cfg.DEEPSEEK_API_KEY`, που είναι **κενό** → κρατά το κλειδί Anthropic
5. Anthropic κλειδί σε DeepSeek endpoint → **401** → `plan_edit` → `None`
6. `meta_oauth.py:817` → **HTTP 502** σε κάθε μήνυμα πελάτη

Αυτό είναι ακριβώς το σφάλμα που ήδη περιγράφει το σχόλιο στο `config.py:41`
(«Μετρήθηκε: κάθε μήνυμα πελάτη στον βοηθό γύριζε 502»). Η διόρθωση είναι
**μόνο μεταβλητή περιβάλλοντος** — ο κώδικας δεν αλλάζει.

Το `/healthz` λέει `configured: true` και **δεν το πιάνει**: ελέγχει μόνο το
`src/ai.py` (Anthropic), όχι τη διαδρομή του editor. Βλ. Κ3.

### Μ5 — Ο RC δεν είναι deployed

Παραγωγή: `main @ 69f7b51c3`, 22 Αυγούστου. Λείπουν migrations 0009/0010, το P0
του webhook, τα P1 social/email, το domain availability.

**Και τα δύο services κάνουν auto-deploy στο push του `main`.** Άρα το merge
**είναι** το deploy. Δεν υπάρχει ξεχωριστή πύλη «τώρα κάνε deploy» — γι' αυτό η
ΦΑΣΗ Β τελειώνει πριν αγγίξει κανείς το `main`.

### Μ6 — Η κατάσταση migration της παραγωγής είναι άγνωστη

`SUPABASE_URL_PRODUCTION`, `SUPABASE_KEY_PRODUCTION`, `DATABASE_URL_PRODUCTION`
απουσιάζουν τοπικά (fail-closed, εκ σχεδιασμού) και ο Supabase MCP server είναι
αποσυνδεδεμένος. **Δεν έγινε καμία ανάγνωση της βάσης παραγωγής.** Η ΦΑΣΗ Β δεν
μπορεί να προγραμματιστεί συγκεκριμένα πριν ο χειριστής δώσει το
`DATABASE_URL_PRODUCTION` στο βήμα Β0.

---

## 3. Υψηλής προτεραιότητας (όχι μπλοκαριστές χρημάτων)

### Υ1 — `app.getvitrina.gr` είναι σπασμένο

    SEC_E_WRONG_PRINCIPAL — το πιστοποιητικό δεν αφορά αυτό το όνομα
    11o1xa75.up.railway.app → HTTP 404

Η αιτία: **δεν υπάρχει** custom domain `app.getvitrina.gr` σε κανένα Railway
service. Το CNAME και το `_railway-verify.app` TXT είναι κατάλοιπα από domain που
αφαιρέθηκε. Το σωστό origin του `sites` είναι `sites-production-da56.up.railway.app`
(HTTP 200) — αυτό ακριβώς που έχει ήδη ως default το `APP_BASE_URL`.

Σημασία: το `app.getvitrina.gr` είναι στη λίστα CORS του `meta_oauth.py:49` και
το προτείνει το `sites/railway.toml`. Κάθε σύνδεσμος προς αυτό αποτυγχάνει.

Για beta 1–3 πελατών **δεν είναι μπλοκαριστής** — το raw Railway URL δουλεύει.
Γίνεται μπλοκαριστής μόνο αν σταλεί branded link σε πελάτη.

### Υ2 — `VITRINA_ENV` δεν ορίζεται στην παραγωγή

Ανεκτό: το `src/env.py` κάνει default σε `production`. Και τα σκέτα
`SUPABASE_URL`/`SUPABASE_KEY` **γίνονται δεκτά**, γιατί το `_pick` έχει ρητό
fallback όταν `_DB_ENV == production` **και** `_ON_SERVER` (η Railway ορίζει
πάντα `RAILWAY_*`). Επαληθεύτηκε: `SUPABASE_KEY` = JWT με `role=service_role`.

Παρ' όλα αυτά, όρισέ το ρητά στο βήμα Α7: μια σιωπηλή προεπιλογή που κρατά τη
βάση παραγωγής είναι κακή θέση για να βρεθείς σε incident.

---

## 4. Πίνακας μεταβλητών περιβάλλοντος

Υπηρεσία **devops** (FastAPI). Καμία τιμή δεν καταγράφηκε — μόνο κατάσταση.

| Μεταβλητή | Πηγή παραγωγής | Απαιτείται | Ετοιμότητα |
|---|---|---|---|
| `SUPABASE_URL` | Railway (legacy όνομα) | ΝΑΙ | PRESENT — γίνεται δεκτό μέσω fallback |
| `SUPABASE_KEY` | Railway (legacy όνομα) | ΝΑΙ | PRESENT — JWT `role=service_role` |
| `STRIPE_SECRET_KEY` | Railway | ΝΑΙ | **PRESENT αλλά TEST — Μ2** |
| `STRIPE_WEBHOOK_SECRET` | Stripe Dashboard → Railway | ΝΑΙ | **PRESENT αλλά TEST — Μ2** |
| `STRIPE_PRICE_SITE` | Stripe → Railway | ΝΑΙ | **PRESENT αλλά TEST price — Μ2** |
| `STRIPE_PRICE_STARTER` / `_SOCIAL` / `_PREMIUM` | Stripe → Railway | προαιρετικό στο beta | PRESENT αλλά TEST |
| `AI_API_KEY` | Railway | ΝΑΙ | PRESENT (`sk-ant-`) — VALID, βλ. σημείωση |
| `AI_PROVIDER` | Railway | ΝΑΙ | `= anthropic` |
| `ANTHROPIC_API_KEY` | Railway | όχι (το σκιάζει το `AI_API_KEY`) | PRESENT, μη-`sk-ant-` πρόθεμα — καθάρισέ το |
| `DEEPSEEK_API_KEY` | **λείπει** | **ΝΑΙ** | **MISSING — Μ4** |
| `AI_BASE_URL` / `AI_MODEL` | — | όχι | MISSING (σωστό: τα defaults δίνουν DeepSeek στον editor) |
| `VITRINA_ENV` | **λείπει** | συνιστάται | MISSING — default `production`, βλ. Υ2 |
| `APP_BASE_URL` | **λείπει** | συνιστάται | MISSING — default `sites-production-da56…` (σωστό σήμερα) |
| `DOMAIN_REGISTRAR` | **λείπει** | όχι | MISSING — default `dns`, η αγορά μένει κλειστή |
| `CF_API_TOKEN` / `CF_ACCOUNT_ID` | Railway | ΝΑΙ (domain activation) | PRESENT |
| `META_APP_ID` / `META_APP_SECRET` | Railway | όχι στο beta | PRESENT |

Σημείωση `AI_API_KEY`: το live `/healthz` επιστρέφει `configured: true`,
`provider: anthropic`, `model: claude-haiku-4-5`, `last_error: null` — το κλειδί
δουλεύει. (Απευθείας probe με `claude-3-5-haiku-20241022` γύρισε 404 επειδή ο
λογαριασμός δεν έχει εκείνο το μοντέλο, όχι επειδή το κλειδί είναι άκυρο.)

Υπηρεσία **sites** (Next.js). Τα `NEXT_PUBLIC_*` ενσωματώνονται στο **build** —
αλλαγή τους απαιτεί redeploy, όχι restart.

| Μεταβλητή | Ετοιμότητα |
|---|---|
| `NEXT_PUBLIC_API_BASE` | `= https://devops-production-d563.up.railway.app` — δουλεύει· το branded `api.getvitrina.gr` θα ήταν καθαρότερο |
| `NEXT_PUBLIC_SUPABASE_URL` | PRESENT |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | PRESENT, **μη-JWT μορφή** — επαλήθευσε ότι είναι publishable key (`sb_publishable_…`) και όχι λάθος τιμή |

---

## ΦΑΣΗ Α — PRE-FLIGHT

Στόχος: να μη μείνει τίποτα άγνωστο πριν αγγίξουμε βάση ή χρήματα.
Τα Α1–Α4 δεν μεταβάλλουν τίποτα. Τα Α5–Α8 μεταβάλλουν και έχουν πύλη.

### Α1. Ο λογαριασμός Stripe (ΞΕΚΙΝΑ ΑΠΟ ΕΔΩ — έχει εξωτερικό χρόνο)

- [ ] Stripe Dashboard → Activate account: στοιχεία επιχείρησης, ΑΦΜ, IBAN
- [ ] Επιβεβαίωση ότι `charges_enabled` και `payouts_enabled` έγιναν `true`

Επαλήθευση (read-only, με το LIVE κλειδί μόλις υπάρχει):

    curl -s https://api.stripe.com/v1/account -H "Authorization: Bearer $SK_LIVE"

**STOP αν** `charges_enabled=false`. Δεν προχωρά τίποτα άλλο που αφορά χρήματα.

### Α2. Το RC είναι αυτό που νομίζουμε

    git fetch origin
    git rev-parse release/prelaunch-2026-09 origin/release/prelaunch-2026-09
    git status --porcelain

**STOP αν** τα δύο SHA διαφέρουν ή το working tree δεν είναι καθαρό.

### Α3. Οι τοπικές πύλες περνούν πάνω στο RC

    python -m pytest tests/test_migration_chain.py tests/test_baseline_adoption.py \
      tests/test_webhook_unknown_client.py tests/test_stripe_webhook_contract.py \
      tests/test_tenant_isolation_sweep.py tests/test_social_normalization.py \
      tests/test_public_email_privacy.py -q

**STOP σε οποιαδήποτε αποτυχία.** Δεν «διορθώνεται το test».

### Α4. Ό,τι τρέχει τώρα, τρέχει

    curl -s -o /dev/null -w "%{http_code}" https://api.getvitrina.gr/healthz   # 200
    curl -s -o /dev/null -w "%{http_code}" https://getvitrina.gr               # 200
    curl -s -o /dev/null -w "%{http_code}" https://koutrakiskouzines.gr        # 200

Κατέγραψε τα. Είναι η γραμμή βάσης για το «τι χάλασε» στη ΦΑΣΗ Δ.

### Α5. Δημιουργία LIVE products/prices

- [ ] **ΕΓΚΡΙΣΗ ΧΕΙΡΙΣΤΗ** — δημιουργία LIVE products/prices

Στο **LIVE mode** του Dashboard, δημιούργησε ξανά (τα TEST prices δεν μεταφέρονται):

- [ ] `Vitrina — Website` : 14,99 EUR / μήνα, recurring, interval_count 1
- [ ] (προαιρετικά για beta) Starter 9,90 / Social 49,00 / Premium 79,00
- [ ] Κατέγραψε τα νέα `price_…` ids

**STOP αν** το ποσό δεν είναι ακριβώς `1499` cents EUR/month.

### Α6. Δημιουργία LIVE webhook endpoint

- [ ] **ΕΓΚΡΙΣΗ ΧΕΙΡΙΣΤΗ** — δημιουργία LIVE endpoint

- [ ] URL: `https://api.getvitrina.gr/stripe/webhook`
- [ ] Events — **και τα έξι**, όχι τρία:
      `checkout.session.completed`, `customer.subscription.created`,
      `customer.subscription.updated`, `customer.subscription.deleted`,
      `invoice.paid`, `invoice.payment_failed`
- [ ] Κατέγραψε το `whsec_…` (LIVE)

**STOP αν** λείπει έστω ένα event. Το `invoice.payment_failed` είναι η μόνη
ένδειξη ότι κόπηκε η κάρτα πελάτη.

### Α7. Ενημέρωση μεταβλητών Railway (service `devops`)

- [ ] **ΕΓΚΡΙΣΗ ΧΕΙΡΙΣΤΗ** — γράψιμο μεταβλητών παραγωγής

Κάθε αλλαγή προκαλεί **redeploy** του service. Κάν' τες μαζί, όχι μία-μία.

- [ ] `STRIPE_SECRET_KEY` → LIVE `sk_live_…`
- [ ] `STRIPE_WEBHOOK_SECRET` → LIVE `whsec_…` από το Α6
- [ ] `STRIPE_PRICE_SITE` (+ όποια άλλα) → LIVE price ids από το Α5
- [ ] `DEEPSEEK_API_KEY` → έγκυρο κλειδί DeepSeek **(λύνει τον Μ4)**
- [ ] `VITRINA_ENV=production` ρητά
- [ ] `APP_BASE_URL=https://sites-production-da56.up.railway.app` ρητά
- [ ] Αφαίρεση ή διόρθωση του `ANTHROPIC_API_KEY` με το ύποπτο πρόθεμα

Το κλειδί DeepSeek επαληθεύεται **πριν** μπει:

    curl -s -o /dev/null -w "%{http_code}" -X POST https://api.deepseek.com/v1/chat/completions \
      -H "Authorization: Bearer $DEEPSEEK_KEY" -H "Content-Type: application/json" \
      -d '{"model":"deepseek-chat","max_tokens":1,"messages":[{"role":"user","content":"ok"}]}'

**STOP αν** δεν επιστρέψει 200.

### Α8. Πάγωμα των αλλαγών

- [ ] Καμία άλλη συγχώνευση στο `main` όσο τρέχει το runbook — **το `main` κάνει auto-deploy**
- [ ] Ενημέρωσε τον άλλον agent / έλεγξε το `STATUS.md` για ενεργό lock

---

## ΦΑΣΗ Β — MIGRATE

Ολόκληρη η φάση εκτελείται **πριν** αγγίξει κανείς το `main`. Ο κώδικας του RC
απαιτεί τα 0009/0010· ο σημερινός κώδικας τα ανέχεται απόντα. Επομένως: βάση
πρώτα, κώδικας μετά. Το αντίστροφο αφήνει τον webhook να σκάει.

### Β0. Απόκτηση πρόσβασης (λύνει τον Μ6)

- [ ] Ο χειριστής θέτει `DATABASE_URL_PRODUCTION` **μόνο στο δικό του shell**,
      ποτέ σε αρχείο του repo
- [ ] `SUPABASE_URL_PRODUCTION` / `SUPABASE_KEY_PRODUCTION` αντίστοιχα, αν χρειαστούν

### Β1. Αντίγραφο ασφαλείας — τι σημαίνει πραγματικά

- [ ] **ΕΓΚΡΙΣΗ ΧΕΙΡΙΣΤΗ** — λήψη backup πριν από κάθε γράψιμο

- [ ] Supabase Dashboard → Database → Backups: επιβεβαίωσε ότι υπάρχει
      **σημερινό** αυτόματο backup και σημείωσε την ώρα του
- [ ] Ανεξάρτητο λογικό αντίγραφο, εκτός Supabase:

      pg_dump "$DATABASE_URL_PRODUCTION" --no-owner --no-privileges -Fc -f vitrina-preflight.dump

- [ ] Επαλήθευσε ότι το αρχείο **δεν είναι κενό** και ότι διαβάζεται:

      pg_restore --list vitrina-preflight.dump | head

- [ ] Αποθήκευσέ το εκτός του repo και εκτός του μηχανήματος deploy

**Τι δεν είναι backup:** ένα PITR που δεν δοκίμασες ποτέ, και ένα dump που δεν
άνοιξες. Το `pg_restore --list` είναι η ελάχιστη απόδειξη.

**Χρόνος ανάκτησης:** η επαναφορά ολόκληρης της βάσης από dump είναι λεπτά, όχι
δευτερόλεπτα. Στο beta με 1–3 πελάτες είναι αποδεκτό — κατέγραψέ το ως συνειδητή
απόφαση, όχι ως παράλειψη.

### Β2. Εκτέλεση του κανονικού οδηγού

Ακολούθησε **`docs/24-PRODUCTION-MIGRATION-RUNBOOK.md`**, βήματα Α έως Θ, ως έχει.
Τα σημεία απόφασης:

- **Α2** Η βάση είναι εκτός διαχείρισης; → αν ναι, χρειάζεται baseline adoption
- **Γ** Επαλήθευση αποτυπώματος (`db/baseline_fingerprint.json`) — μόνο ανάγνωση
- [ ] **ΕΓΚΡΙΣΗ ΧΕΙΡΙΣΤΗ** — **Δ** `python scripts/migrate.py --adopt-baseline`
- **Ε** Επαλήθευση κατάστασης — μόνο ανάγνωση
- [ ] **ΕΓΚΡΙΣΗ ΧΕΙΡΙΣΤΗ** — **ΣΤ** `python scripts/migrate.py` (0001 → 0010)
- **Ζ** Επαλήθευση μετά: ιστορικό, δεδομένα, σχήμα editor, grants, RLS, εφαρμογή

Αναμενόμενο αποτέλεσμα του ΣΤ: εφαρμόζονται όλα εκτός του `0000` (υιοθετημένο)
και του `0001` (φέρει `-- ENV: staging-only`).

**STOP conditions** — αυτούσια από τον οδηγό §Η:

- το `--adopt-baseline` **αρνήθηκε** → σταμάτα· μην το πιέσεις, μην περάσεις άλλη έκδοση
- αναντιστοιχία αποτυπώματος → η βάση δεν είναι αυτό που νομίζουμε
- αποτυχία **μέσα** στο ΣΤ → ο οδηγός §Θ3 λέει τι είναι ανακτήσιμο
- προειδοποίηση checksum για το `0003` → **αναμενόμενη**, δεν είναι σφάλμα
  (το staging κρατά δύο legacy στήλες). Δεν πειράζουμε το 0003. Ποτέ.

---

## ΦΑΣΗ Γ — DEPLOY

**Προσοχή στη μηχανική:** και τα δύο services κάνουν auto-deploy στο push του
`main`. Δεν υπάρχει «deploy button». Το merge είναι το deploy, και τρέχει και για
τα δύο ταυτόχρονα.

### Γ1. Προϋποθέσεις

- [ ] Η ΦΑΣΗ Β ολοκληρώθηκε και το βήμα Ζ του οδηγού πέρασε
- [ ] Το Α7 έχει γίνει (αλλιώς ο νέος κώδικας βρίσκει TEST κλειδιά)
- [ ] Κατέγραψε το τρέχον SHA για rollback: `69f7b51c3`

### Γ2. Συγχώνευση = deploy

- [ ] **ΕΓΚΡΙΣΗ ΧΕΙΡΙΣΤΗ** — merge RC στο `main` και push

      git checkout main
      git merge --no-ff release/prelaunch-2026-09
      git push origin main

### Γ3. Παρακολούθηση

- [ ] Railway → devops: το deployment φτάνει σε `SUCCESS`
- [ ] Railway → sites: το deployment φτάνει σε `SUCCESS`
- [ ] `curl https://api.getvitrina.gr/healthz` → 200 και `last_error: null`

**STOP αν** οποιοδήποτε service μείνει σε `FAILED` ή `CRASHED` → επαναφορά Γ.

Σημείωση: 1 replica ανά service σημαίνει σύντομη διακοπή στο rollout. Στο beta
είναι αποδεκτό· για τον πρώτο πελάτη προτίμησε ώρα εκτός αιχμής.

### Γ4. Marketing site (μόνο αν άλλαξε το `web/`)

- [ ] **ΕΓΚΡΙΣΗ ΧΕΙΡΙΣΤΗ** — `wrangler pages deploy` στο project `vitrina`
- [ ] Μετά το deploy, υποχρεωτικά: `node sites/tests/production_qa.mjs` (CLAUDE.md §7)

---

## ΦΑΣΗ Δ — VERIFY / ΠΡΩΤΟΣ ΠΕΛΑΤΗΣ

### Δ1. Smoke tests — μόνο ανάγνωση, καμία εγγραφή

| # | Έλεγχος | Αναμενόμενο |
|---|---|---|
| 1 | `GET https://api.getvitrina.gr/healthz` | 200, `configured:true`, `last_error:null` |
| 2 | `GET https://getvitrina.gr` | 200 |
| 3 | `GET https://sites-production-da56.up.railway.app` | 200 |
| 4 | `GET https://koutrakiskouzines.gr` | 200, cert έγκυρο — **ο υπάρχων tenant δεν χάλασε** |
| 5 | `POST /stripe/webhook` χωρίς υπογραφή | 400, **όχι** 500 |
| 6 | Stripe Dashboard → Webhooks → LIVE endpoint | 0 αποτυχίες |
| 7 | Console του browser στο dashboard | καθαρή, χωρίς CORS σφάλματα |

**STOP αν** το 4 αποτύχει: χαλάσαμε πληρωμένο πελάτη. Επαναφορά αμέσως.

### Δ2. Ο chat editor ζει (η απόδειξη ότι λύθηκε ο Μ4)

- [ ] Άνοιξε το dashboard ενός **δοκιμαστικού** πελάτη
- [ ] Στείλε μήνυμα στον βοηθό, π.χ. «άλλαξε το τηλέφωνο σε 2310000000»
- [ ] Περίμενε **draft πρόταση**, όχι 502

**STOP αν** επιστρέψει 502: ο `DEEPSEEK_API_KEY` δεν εφαρμόστηκε. Μη δώσεις
πρόσβαση σε πελάτη — το chat-to-edit είναι το προϊόν.

Το συμβόλαιο του CLAUDE.md ισχύει: **draft first**. Η πρόταση εμφανίζεται στο
preview και απαιτεί ρητό «Έγκριση αλλαγών». Αν γραφτεί κάτι στη βάση χωρίς
έγκριση, αυτό είναι P0 — σταμάτα.

### Δ3. Πρώτος πραγματικός πελάτης

Ένας. Όχι τρεις ταυτόχρονα.

- [ ] Το site έχει χτιστεί και **εγκριθεί οπτικά** (CLAUDE.md §7: πραγματικός
      browser, desktop + mobile, screenshots, console καθαρή)
- [ ] Τα NAP στοιχεία είναι αληθινά· κανένα invented fact
- [ ] **ΕΓΚΡΙΣΗ ΧΕΙΡΙΣΤΗ** — αποστολή συνδέσμου checkout στον πελάτη
- [ ] Ο πελάτης ολοκληρώνει το checkout με **δική του** κάρτα
- [ ] Stripe → Subscriptions: κατάσταση `trialing`, trial **30 ημέρες**, μετά 14,99 EUR/μήνα
- [ ] Stripe → Webhooks: `checkout.session.completed` και
      `customer.subscription.created` παραδόθηκαν με **200**
- [ ] Βάση: υπάρχει γραμμή στο `subscriptions` για τον σωστό `client_id`
- [ ] Βάση: το `stripe_events` έχει `processing_status='processed'`
- [ ] **Ο πελάτης δεν βλέπει δεδομένα άλλου πελάτη** — έλεγξε με δεύτερο λογαριασμό

**STOP αν** ο webhook γυρίσει οτιδήποτε άλλο από 200. Το Stripe ξαναπροσπαθεί με
backoff έως τρεις ημέρες και μετά **απενεργοποιεί το endpoint** — τότε σταματά η
επεξεργασία για **όλους** τους πελάτες.

### Δ4. Domain πελάτη (προαιρετικό στο beta)

- [ ] Η αναζήτηση διαθεσιμότητας δουλεύει· **ποτέ** «available» από DNS ή από
      αποτυχία παρόχου — αυτά επιστρέφουν `unknown`
- [ ] Η **αυτόματη αγορά παραμένει κλειστή** — `DOMAIN_REGISTRAR` default `dns`
- [ ] Ενεργοποίηση domain μόνο μέσω `docs/14-DOMAIN-AUTOMATION.md`
- [ ] **ΕΓΚΡΙΣΗ ΧΕΙΡΙΣΤΗ** — αλλαγή DNS πελάτη
- [ ] Πύλες Railway: `targetPort` + `_railway-verify` TXT + έκδοση πιστοποιητικού
- [ ] Μετά: HTTPS, canonical, sitemap, robots, CTA

---

## Επαναφορά

| | Πότε | Ενέργεια | Χάνεται |
|---|---|---|---|
| **Α** | Αποτυχία **πριν** από το Β2 | Καμία ενέργεια — τίποτα δεν γράφτηκε | τίποτα |
| **Β** | Το `--adopt-baseline` αρνήθηκε | Σταμάτα. Μην πιέσεις. Οδηγός §Θ2 | τίποτα |
| **Γ** | Αποτυχία deployment στη ΦΑΣΗ Γ | Railway → Deployments → Rollback στο `69f7b51c3` | ο νέος κώδικας |
| **Δ** | Ο νέος κώδικας τρέχει αλλά είναι λάθος | `git revert` του merge → push → auto-deploy | ο νέος κώδικας |
| **Ε** | Αποτυχία **μέσα** στη ΦΑΣΗ Β | Οδηγός §Θ3. Κάθε migration είναι σε transaction — η αποτυχημένη δεν άφησε μισή δουλειά | το συγκεκριμένο migration |
| **ΣΤ** | Καταστροφή δεδομένων | `pg_restore` από το dump του Β1 | ό,τι γράφτηκε μετά το dump |

Το **Γ** και το **Δ** επαναφέρουν **μόνο τον κώδικα**. Τα migrations 0009/0010
είναι προσθετικά και ο παλιός κώδικας τα ανέχεται — μην επιχειρήσεις να τα
«ξεκάνεις».

---

## Παρακολούθηση: τι δεν υπάρχει

Καταγράφονται ως **LAUNCH READINESS GAP**. Δεν επινοήθηκε monitoring που δεν
υπάρχει.

- **Κ1 — Καμία καταγραφή σφαλμάτων.** Ούτε Sentry, ούτε OpenTelemetry, ούτε
  Datadog, πουθενά στο `src/` ή στο `sites/`. Ένα HTTP 500 στην παραγωγή είναι
  αόρατο μέχρι να παραπονεθεί πελάτης.
- **Κ2 — Καμία ειδοποίηση για αποτυχίες webhook.** Το Stripe απενεργοποιεί
  endpoint μετά από επίμονες αποτυχίες. Σήμερα κανείς δεν θα το μάθαινε. Στο
  beta: **έλεγχος με το μάτι στο Stripe Dashboard κάθε μέρα**, γραμμένος ως
  υποχρέωση, όχι ως καλή πρόθεση.
- **Κ3 — Το `/healthz` δεν ελέγχει ούτε βάση ούτε Stripe.** Επιστρέφει μόνο
  κατάσταση AI του `src/ai.py`. Έδειχνε `ok` όσο ο chat editor ήταν νεκρός (Μ4).
  Ο healthcheck της Railway σε αυτό στηρίζεται — άρα ένα service με νεκρή βάση
  θα θεωρούνταν υγιές.
- **Κ4 — Κανένα uptime monitor** σε `api.getvitrina.gr`, στο `sites`, ή στο
  domain του πελάτη.
- **Κ5 — Καμία διατήρηση logs** πέρα από το UI της Railway. Δεν ερωτώνται, δεν
  εξάγονται.
- **Κ6 — Το service `sites` δεν έχει healthcheck path.** Ένα crash-loop δεν
  εντοπίζεται από την πλατφόρμα.
- **Κ7 — Το `CF_API_TOKEN` δεν διαβάζει Workers routes ούτε SSL packs**
  («Authentication error»). Η κατάσταση του tenant-hosting Worker **δεν
  επαληθεύτηκε** σε αυτόν τον preflight.

Ελάχιστο συνιστώμενο για beta 1–3 πελατών, όσο τα Κ1–Κ7 μένουν ανοιχτά:
ημερήσιος χειροκίνητος έλεγχος των Stripe webhooks, των Railway deployments και
των τεσσάρων URL του Δ1.

---

## Αποφάσεις που ΔΕΝ λύνονται εδώ

- **Διατήρηση του Stripe event ledger μετά τη διαγραφή λογαριασμού.** Το 0010
  αφαίρεσε το FK ώστε το ιστορικό να επιβιώνει· η πολιτική διατήρησης είναι
  απόφαση προϊόντος/νομικής. **POST-BETA POLICY DECISION.**
- **154 grants `anon`/`authenticated` στην παραγωγή.** Εντοπίστηκαν, δεν
  αφαιρέθηκαν. Ξεχωριστή απόφαση ασφαλείας, όχι μέρος αυτής της εκκίνησης.
- **Το 0000 δεν είναι idempotent.** Γι' αυτό ακριβώς υπάρχει το baseline adoption.
- **`editorFlow.mjs`: «Logo Designer περιλαμβάνεται».** Παλιό test string,
  non-blocking. Δεν διορθώθηκε σε αυτόν τον κύκλο.

---

## Τι αποδείχθηκε ήδη (μη το ξαναδοκιμάσεις)

- Στοίβα migrations 0000 → 0010 σε άδεια βάση: 18 έλεγχοι
- Baseline adoption fail-closed, αδύνατη η υιοθέτηση αυθαίρετου migration: 31
- Απομόνωση tenant: 21 endpoints × 4 = 84 έλεγχοι, με **έγκυρα** request bodies
- Webhook: υπογραφή, replay, εκτός σειράς, άγνωστος πελάτης: 11 σενάρια
- Trial 30 ημερών και 14,99 EUR/μήνα: επαληθεύτηκε στο **ίδιο το Stripe**
- Browser QA: 144 έλεγχοι
