# Vitrina — έτοιμο site για τον Έλληνα μικροεπαγγελματία

> Ο πελάτης δίνει 4 στοιχεία, βλέπει το site του σε 2 λεπτά, το εγκρίνει και βγαίνει
> live σε δικό του `.gr`. Από εκεί και μετά το αλλάζει μόνος του από το dashboard.
> **€14.99/μήνα.**

Αυτό το αρχείο είναι **οι οδηγίες χρήσης**: πώς το τρέχεις, τι κάνεις κάθε μέρα,
πώς ανεβάζεις πελάτη. Για το «γιατί» και το πλάνο → [docs/](docs/) και [STATUS.md](STATUS.md).

---

## 1. Τι τρέχει πού

| Κομμάτι | Τι κάνει | Πού ζει |
|---|---|---|
| **API** (`src/`) | FastAPI: onboarding, δεδομένα πελατών, dashboard, posts | Railway → `devops-production-d563.up.railway.app` |
| **Sites** (`sites/`) | Ένα Next.js app που σερβίρει **όλα** τα sites πελατών | Railway → `sites-production-da56.up.railway.app` |
| **Worker** (`infra/`) | Στέλνει τα domain πελατών στο Sites app | Cloudflare |
| **Βάση** | Πελάτες, περιεχόμενο, συνδρομές, παραγγελίες | Supabase |

Ένα Next.js app σερβίρει όλους τους πελάτες. **Δεν χτίζουμε site ανά πελάτη** — το
domain λέει ποιος είναι ο πελάτης, και το ίδιο app φορτώνει τα δικά του δεδομένα.

## 2. Στήσιμο τοπικά

```bash
git clone <repo> && cd greek-smb-agent
pip install -r requirements.txt
cp .env.example .env          # συμπλήρωσε τα κλειδιά (§8)

# API στο :8000
uvicorn src.main:app --reload --port 8000

# Sites στο :3000 (άλλο τερματικό)
cd sites && npm install && npm run dev
```

Άνοιξε http://localhost:3000 — ο demo switcher με όλα τα templates.

**Ποτέ μη βάλεις κλειδί σε chat, commit ή screenshot.** Μόνο στο `.env` (είναι
στο `.gitignore`) και στα Railway variables.

## 3. Νέος πελάτης — η διαδρομή

1. **Εγγραφή.** Ο πελάτης δίνει όνομα, επάγγελμα, πόλη, τηλέφωνο, email.
2. **Σχέδια.** Το σύστημα διαλέγει μόνο του 3-4 templates που ταιριάζουν στο
   επάγγελμά του και γράφει το ελληνικό κείμενο. Χωρίς AI κλειδί δουλεύει
   κανονικά με έτοιμα πρότυπα ανά επάγγελμα.
3. **Επιλογή.** Βλέπει τα σχέδια στο `/choose/{client_id}` και πατάει ένα.
4. **Domain.** Διαλέγει από τις προτάσεις και πληρώνει. **Το αγοράζεις εσύ**
   χειροκίνητα (§4) — δεν έχουμε ακόμα registrar API.
5. **Live.** Μία εντολή και το site βγαίνει στον αέρα.
6. **Dashboard.** Μπαίνει στο `/dashboard` με Google ή email και το αλλάζει μόνος του.

Στείλε του και τους δύο οδηγούς — είναι τα δύο πράγματα που δεν κάνουμε εμείς γι' αυτόν:
- `/odigos/google` — προφίλ Google Maps + κριτικές
- `/odigos/facebook` — σελίδα Facebook + posts + πληρωμένη προβολή

## 4. Καθημερινή δουλειά: παραγγελίες domain

```bash
python scripts/orders.py
```

**Τρέξ' το κάθε μέρα.** Δείχνει ποιος πλήρωσε και περιμένει. Για κάθε παραγγελία:

1. Αγόρασε το domain στον registrar (~3 λεπτά).
2. Βάλε το domain σε zone στο Cloudflare, με τα nameservers που σου δίνει.
3. Τρέξε την εντολή που σου τυπώνει το `orders.py`:

```bash
python scripts/link_domain_cf.py to-domain-tou.gr --dry-run   # δες τι θα κάνει
python scripts/link_domain_cf.py to-domain-tou.gr             # κάν' το
```

Το script βάζει **πρώτα** το Worker route, περιμένει να απαντήσει, και **μετά**
γυρίζει το DNS. Αν κάτι αποτύχει, επαναφέρει το DNS μόνο του.

> ⚠️ **Μην τρέξεις ποτέ αυτό το script σε domain που είναι ήδη live** για να
> «δοκιμάσεις κάτι». Το site πέφτει. Δοκίμασε σε δικό μας υποτομέα.

## 5. Πριν από κάθε deploy

```bash
python scripts/e2e.py            # όλα (φτιάχνει & σβήνει δοκιμαστικό πελάτη)
python scripts/e2e.py --quick    # χωρίς εγγραφή, πιο γρήγορο
```

Ελέγχει ό,τι βλέπει πραγματικός πελάτης: εγγραφή, σχέδια, ασφάλεια,
ζωντανό site, χάρτης, schema, robots/sitemap ανά domain, και τα 22 templates.
Επιστρέφει `1` αν κάτι έσπασε. **Τρέξ' το πριν και μετά το deploy.**

```bash
cd sites && npx next build       # ότι χτίζει το frontend
```

Το deploy γίνεται με `git push` — το Railway χτίζει και τα δύο services μόνο του.

## 6. Πακέτα

| Πακέτο | Τιμή | Τι περιλαμβάνει |
|---|---|---|
| **Site** | €14.99/μήνα | Site, domain, hosting, απεριόριστες αλλαγές από το dashboard |
| **Posts** | €29.99/μήνα | + 7 έτοιμα posts κάθε εβδομάδα, με οδηγίες προβολής |
| **Ads** | €99/μήνα + budget | + διαχείριση διαφημίσεων |

Ο έλεγχος γίνεται στο [`_has_posts_plan()`](src/meta_oauth.py) — η ενεργή συνδρομή
υπερισχύει, το `clients.plan` είναι το fallback. Χωρίς πακέτο Posts ο πελάτης
βλέπει **ένα δείγμα** και πρόταση αναβάθμισης, όχι κλειδωμένο κενό.

**Το Stripe είναι σε test mode επίτηδες.** Δεν το ανοίγουμε πριν τελειώσουν τα tests.

## 7. Τα templates

22 React templates στο [sites/lib/templates/](sites/lib/templates/) — δομικά
διαφορετικά, με δικά τους ελληνικά fonts και χρώματα, όχι recolors.

Το `recommend_templates()` στο [src/premium_generator.py](src/premium_generator.py)
διαλέγει ποια θα δει ο πελάτης ανάλογα με το επάγγελμα (ταβέρνα → `ember`,
κομμωτήριο → `bloom`, συνεργείο → `motor`…).

**Δεν προσθέτουμε άλλα templates.** 22 φτάνουν· η δουλειά τώρα είναι διανομή.

Δες ένα: http://localhost:3000/preview/ember?biz=taverna

## 8. Μεταβλητές περιβάλλοντος

Υποχρεωτικές:

| | |
|---|---|
| `SUPABASE_URL`, `SUPABASE_KEY` | βάση + auth |
| `APP_BASE_URL` | το public URL του API |

Προαιρετικές — **το σύστημα δουλεύει χωρίς αυτές**:

| | |
|---|---|
| `ANTHROPIC_API_KEY` | AI κείμενα & chat-to-edit. Χωρίς αυτό: έτοιμα πρότυπα ανά επάγγελμα |
| `ANTHROPIC_BASE_URL`, `ANTHROPIC_MODEL` | μόνο για εναλλακτικό provider (π.χ. Azure) |
| `CF_API_TOKEN`, `CF_ACCOUNT_ID` | σύνδεση domain πελατών |
| `STRIPE_*` | πληρωμές (test mode) |
| `META_APP_ID`, `META_APP_SECRET` | αυτόματο posting — περιμένει App Review |

Ένα `ANTHROPIC_API_KEY` που δεν δουλεύει **δεν ρίχνει τίποτα**: κάθε AI κλήση
πέφτει σιωπηλά πίσω στα πρότυπα. Θέλει κλειδί `sk-ant-…` από το console.anthropic.com,
ή —για Azure Foundry— **και** `ANTHROPIC_BASE_URL` **και** πραγματικό deployment του μοντέλου.

## 9. Όταν κάτι σπάσει

| Σύμπτωμα | Αιτία |
|---|---|
| **«The train has not arrived»** | Το Railway δεν ξέρει αυτό το domain. Λείπει το Worker route ή το DNS δείχνει αλλού. |
| **522 σε domain πελάτη** | Το DNS γύρισε πριν σερβίρει ο Worker. Επανέφερε το DNS και ξαναδοκίμασε με `--dry-run`. |
| **«Το site δεν είναι διαθέσιμο»** | Ο πελάτης δεν βρέθηκε από το domain — τσέκαρε τη στήλη `domain` στη βάση. |
| **Dashboard: «Failed to fetch»** | CORS — το origin του sites app πρέπει να ταιριάζει στο `allow_origin_regex`. |
| **«provider is not enabled»** | Το Google OAuth δεν είναι ενεργό στο Supabase. |
| **Login πάει σε localhost** | Λάθος Site URL στις ρυθμίσεις Supabase Auth. |
| **Ο βοηθός δεν απαντά** | Δεν υπάρχει έγκυρο `ANTHROPIC_API_KEY`. Η καρτέλα «Στοιχεία» δουλεύει κανονικά. |

## 10. Τεκμηρίωση

| Αρχείο | Περιεχόμενο |
|---|---|
| [STATUS.md](STATUS.md) | **Πού σταματήσαμε** — διάβασέ το πρώτο σε νέο session |
| [docs/01-ARCHITECTURE.md](docs/01-ARCHITECTURE.md) | Αρχιτεκτονική & ροή δεδομένων |
| [docs/05-COSTS-PRICING.md](docs/05-COSTS-PRICING.md) | Κόστος ανά πελάτη & τιμολόγηση |
| [docs/06-RISKS-LEGAL.md](docs/06-RISKS-LEGAL.md) | GDPR, Meta review, νομικά |
| [docs/07-VERTICALS.md](docs/07-VERTICALS.md) | Presets ανά επάγγελμα |
| [docs/09-MASTER-PLAN.md](docs/09-MASTER-PLAN.md) | Το πλήρες πλάνο |
| [docs/12-META-APP-REVIEW.md](docs/12-META-APP-REVIEW.md) | Meta App Review βήμα-βήμα |
| [docs/14-DOMAIN-AUTOMATION.md](docs/14-DOMAIN-AUTOMATION.md) | Domains: προτάσεις → πληρωμή → DNS |
| [docs/emails-reseller.md](docs/emails-reseller.md) | Επαφές registrar (Papaki, Pointer) |

## 11. Τι εκκρεμεί

- **Meta App Review** — χωρίς αυτό δεν ποστάρουμε αυτόματα ([docs/12](docs/12-META-APP-REVIEW.md))
- **Registrar API** — Papaki/Pointer· μέχρι τότε αγοράζουμε χειροκίνητα
- **Stripe live mode** — κλειστό μέχρι να τελειώσουν τα tests
- **Anthropic API key** — προαιρετικό, αλλά ξεκλειδώνει chat-to-edit και AI κείμενα
