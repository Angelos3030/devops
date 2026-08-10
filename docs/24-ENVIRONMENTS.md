# 24 — Περιβάλλοντα & Migrations

Πού τρέχει τι, πώς δεν θα σβήσουμε πελάτες, και πώς αλλάζει το σχήμα της βάσης.

## Τα τρία περιβάλλοντα

| | βάση | Stripe | καταστροφικά |
|---|---|---|---|
| `dev` (τοπικά) | **staging** | test | ✅ |
| `staging` | staging | test | ✅ |
| `production` | production | live | ❌ |

Το `dev` **δεν** έχει δική του βάση: δείχνει στη staging. Έτσι μια δοκιμή στο
μηχάνημά σου δεν μπορεί να γράψει σε αληθινό πελάτη.

## Δύο ανεξάρτητα επίπεδα ασφάλειας

**1. Λογικό.** Το `VITRINA_ENV` και το `src/env.py`. Αν λείπει, θεωρείται
**production** — fail-closed, ώστε ένα ξεχασμένο flag να μπλοκάρει, όχι να επιτρέψει.

**2. Credentials.** Τα κλειδιά κάθε περιβάλλοντος έχουν **διαφορετικά ονόματα**:
`SUPABASE_URL_STAGING` έναντι `SUPABASE_URL_PRODUCTION`. Το τοπικό `.env` περιέχει
μόνο τα `_STAGING`.

Το δεύτερο είναι που μετράει. Ένα λογικό guard το παρακάμπτει ένα λάθος `export`·
credentials που **δεν υπάρχουν στο μηχάνημα** δεν τα παρακάμπτει τίποτα.

```python
from src import env
env.require("staging")                       # σταματά αλλού
env.require_destructive(args.confirm_staging)  # + ρητή σημαία
url, key = env.supabase()                    # του τρέχοντος περιβάλλοντος
print(env.banner())                          # 🧪 VITRINA_ENV=staging · βάση: staging
```

## Διπλός guard για ό,τι σβήνει

Δεν αρκεί το σωστό περιβάλλον. Χρειάζεται **και** ρητή σημαία:

```bash
VITRINA_ENV=staging python scripts/cleanup_abandoned.py --delete --confirm-staging
```

Χωρίς `--confirm-staging` σταματά. Ένα cron που ξαναέτρεξε ή ένα tab-complete από
το ιστορικό δεν σβήνει τίποτα σιωπηλά.

## Migrations

```bash
python scripts/migrate.py --status                        # τι έχει τρέξει
VITRINA_ENV=staging    python scripts/migrate.py --apply
VITRINA_ENV=production python scripts/migrate.py --apply --confirm-production
```

Σειρά — **αμετάβλητα αρχεία**, ποτέ επεξεργασία εφαρμοσμένου:

```
db/migrations/
  0001_schema.sql          βασικοί πίνακες
  0002_site_variants.sql   τα 3 designs ανά πελάτη
  0003_domains.sql         domains πελατών
  0004_domain_orders.sql   παραγγελίες domain
  0005_social_engine.sql   ουρά δημοσιεύσεων
  0006_rls_policies.sql    row-level security — ΠΑΝΤΑ τελευταίο
```

Ο πίνακας `schema_migrations` κρατά έκδοση + checksum. Αν πειράξεις εφαρμοσμένο
αρχείο, ο runner το αναφέρει ως `⚠️ ΑΛΛΑΞΕ` — φτιάξε **νέο** αρχείο.

### Καταστροφικές αλλαγές: expand → migrate → contract

Ποτέ σε μία έκδοση. Τρία ξεχωριστά releases:

| release | migration | τι κάνει |
|---|---|---|
| N | `0007_add_new_column.sql` | **expand** — νέα στήλη, γράφουν και τα δύο |
| N+1 | `0008_backfill.sql` | **migrate data** |
| N+2 | `0009_drop_old.sql` | **contract** — αφού ο παλιός κώδικας δεν τρέχει πουθενά |

Γιατί: το rollback κώδικα γίνεται ασφαλές. Η παλιά έκδοση βρίσκει πάντα το σχήμα
που περιμένει. Δεν χρειάζεται ποτέ rollback βάσης — που δεν υπάρχει.

## Όρια του staging

- **Ποτέ custom domains πελατών.** Ο Cloudflare Worker μένει κλειδωμένος στο
  production Railway URL.
- **Ποτέ κλήση σε πραγματικό registrar** (Pointer/Papaki). Mock adapter.
- **Μόνο Stripe test mode**, με δικά του price IDs και webhook secret.

## Production QA: read-only

Μετά το deploy τρέχει `sites/tests/production_qa.mjs` στην παραγωγή. Είναι
**αποκλειστικά read-only** — ο έλεγχος της ροής κόβει το `POST /start` και
επαληθεύει το σώμα του αιτήματος αντί να δημιουργήσει πελάτη.

Αν αποτύχει κρίσιμος έλεγχος: **rollback του deployment**, καμία ενέργεια στη βάση.

## Μετάβαση — τι εκκρεμεί

Μέχρι να στηθεί το staging Supabase, το `_pick()` επιτρέπει fallback από
`SUPABASE_URL_PRODUCTION` στο σκέτο `SUPABASE_URL`, ώστε το Railway να συνεχίσει
να δουλεύει. **Αυτό σημαίνει ότι ένα τοπικό `.env` με `SUPABASE_URL` δείχνει
ακόμα στην παραγωγή.**

Μόλις υπάρχει staging:
1. Στο τοπικό `.env`: `VITRINA_ENV=dev` + μόνο τα `*_STAGING` κλειδιά
2. **Σβήσε** τα production κλειδιά από το τοπικό `.env`
3. Στο Railway production: πρόσθεσε τα `*_PRODUCTION` και αφαίρεσε το fallback
