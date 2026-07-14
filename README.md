# Παρέα AI — AI για τον Έλληνα μικροεπαγγελματία

> Ένας AI agent που **φτιάχνει & συντηρεί website** και **ποστάρει κάθε μέρα μόνος του**
> στο Facebook/Instagram, για μικρά ελληνικά μαγαζιά. Managed, ελληνικά, all-in-one.

## Η ιδέα με μία πρόταση
Ο καφετζής/μάστορας/ταβερνιάρης δίνει €49/μήνα και έχει site + καθημερινά posts
χωρίς να κάνει τίποτα. Το site είναι το δόλωμα — **το social media auto-posting είναι το ταμείο.**

## Γιατί στέκει
1. **Recurring revenue** — μηνιαία συνδρομή με πραγματικό νόημα (κάθε μέρα δουλειά).
2. **Καθημερινό pain** που το AI λύνει αληθινά (κείμενα + εικόνες + προγραμματισμός).
3. **Business πελάτης** που πληρώνει (έξοδο επιχείρησης) και δεν μπορεί να το κάνει μόνος.
4. **Ελληνικό moat** — γλώσσα, τόνος, `.gr`, τοπικά templates. Οι ξένοι γίγαντες δεν το έχουν.

## Πού είναι η αξία (όχι ο κώδικας)
Σχεδόν όλα τα building blocks υπάρχουν **έτοιμα & δωρεάν** (skills, MCP, Agent SDK).
Το moat σου είναι: **ελληνική εξειδίκευση + διανομή + managed μοντέλο.** Ο κώδικας είναι το 20%.

> 📍 **Συνεχίζεις από άλλο account/session;** Διάβασε πρώτα το **[STATUS.md](STATUS.md)** —
> καταγράφει πάντα πού σταματήσαμε & τι ακολουθεί.

## Δομή τεκμηρίωσης
| Αρχείο | Περιεχόμενο |
|--------|-------------|
| [docs/01-ARCHITECTURE.md](docs/01-ARCHITECTURE.md) | Η αρχιτεκτονική: agents, skills, ροή δεδομένων |
| [docs/02-SKILLS.md](docs/02-SKILLS.md) | Ποια skills, πώς γράφονται, πώς φορτώνονται |
| [docs/03-TECH-STACK.md](docs/03-TECH-STACK.md) | Τεχνολογίες, μοντέλα, APIs, υποδομή |
| [docs/04-BUILD-PLAN.md](docs/04-BUILD-PLAN.md) | Βήμα-βήμα πλάνο υλοποίησης (φάσεις) |
| [docs/05-COSTS-PRICING.md](docs/05-COSTS-PRICING.md) | Κόστος ανά πελάτη & μοντέλο τιμολόγησης |
| [docs/06-RISKS-LEGAL.md](docs/06-RISKS-LEGAL.md) | Ρίσκα (Meta review, GDPR) & πώς τα λύνεις |
| [docs/07-VERTICALS.md](docs/07-VERTICALS.md) | Έτοιμα patterns/presets ανά επάγγελμα (smart defaults) |
| [docs/08-VALIDATION.md](docs/08-VALIDATION.md) | Validation pitch & ερωτήσεις (Εβδομάδα 0) |
| [skills/greek-website/PRESETS.md](skills/greek-website/PRESETS.md) | Πλήρης κατάλογος ΟΛΩΝ των επαγγελμάτων + SEO keywords |
| [skills/local-seo-gr/SKILL.md](skills/local-seo-gr/SKILL.md) | SEO best practices (local SEO, schema.org) για κάθε site |
| ⭐ [docs/09-MASTER-PLAN.md](docs/09-MASTER-PLAN.md) | **ΤΟ ΠΛΗΡΕΣ ΒΗΜΑ-ΒΗΜΑ ΠΛΑΝΟ** (μηδέν → πελάτες) |
| [docs/10-TOKEN-EFFICIENCY.md](docs/10-TOKEN-EFFICIENCY.md) | Τέλεια ιεραρχία για λιγότερα tokens (κόστος) |
| [docs/11-EXTERNAL-SKILLS.md](docs/11-EXTERNAL-SKILLS.md) | Ποια έτοιμα skills να τραβήξεις (curated shortlist) |
| [docs/12-META-APP-REVIEW.md](docs/12-META-APP-REVIEW.md) | Meta App Review βήμα-βήμα (FB/IG posting άδεια) |
| [docs/13-META-GROWTH-ADS.md](docs/13-META-GROWTH-ADS.md) | Growth: Organic → Promoted posts → Full Facebook Ads (μετά MVP) |
| [docs/14-DOMAIN-AUTOMATION.md](docs/14-DOMAIN-AUTOMATION.md) | Domain suggestions, Stripe checkout, Papaki registrar adapter, Cloudflare DNS |

## 🎨 Vitrina Design Engine (template-based, 0 tokens)
Τα sites πελατών φτιάχνονται με **έτοιμα premium templates + Python fill** — όχι AI-per-site.
Φθηνό, γρήγορο, πάντα ωραίο/responsive, και **δουλεύει χωρίς API key**.

- **3 approved layouts:** `studio` (editorial), `commerce` (conversion/κριτικές), `atelier` (minimal)
  → [skills/vitrina-design-system/templates/](skills/vitrina-design-system/templates/)
- **Generator:** [src/premium_generator.py](src/premium_generator.py) — intake → 3 designs + σελίδα έγκρισης.
  Αναγνωρίζει επάγγελμα (ξυλουργός/ταβέρνα/οδοντίατρος/κομμωτήριο/δικηγόρος/τεχνικός) και προτείνει layout.
- **Onboarding:** το `/onboard` παράγει αυτόματα τα 3 designs (background), τα αποθηκεύει ως previews.
- **Approve flow:** ο πελάτης πατάει «Approve» → `POST /clients/{id}/select-design`.
- **AI copy (optional):** [src/site_copy.py](src/site_copy.py) γράφει ελληνικό κείμενο ανά πελάτη μόλις
  μπει `ANTHROPIC_API_KEY` — αλλιώς no-op με per-profession defaults.
- **Demo:** `python -m scripts.generate_client_site` → `web/clients/koutrakis-auto-choose.html`.
- **DB migration:** τρέξε [db/add_site_variants.sql](db/add_site_variants.sql) στο Supabase.

## 🚀 Multi-tenant React sites (Next.js) — `sites/`
Τα sites των πελατών παράγονται πλέον από **ένα** Next.js app (multi-tenant): `domain → βρίσκει
πελάτη → render React template + data του`. **0 build ανά πελάτη**, SSR/ISR για SEO.

- **App:** [sites/](sites/) — Next 14 App Router. `/site/[client]` (dynamic, ISR) + `/` (demo switcher).
- **Data:** API endpoint `GET /clients/{id}/site-data` → normalized JSON (name, services[], gallery[]…).
- **Templates:** **δομικά διαφορετικά** React archetypes (όχι recolors):
  `Editorial` (stacked), `Split` (fixed sidebar), `Showcase` (full-bleed gallery-forward) —
  [sites/lib/templates/](sites/lib/templates/). Στόχος: 10-15 distinct.
- **Τοπικά:** `cd sites && npm install && npm run dev` → http://localhost:3000
- **Deploy:** Cloudflare Pages/Vercel· domain → client mapping μέσω middleware (επόμενο βήμα).

> Σημ.: ο παλιός static HTML engine ([premium_generator.py](src/premium_generator.py), 7 templates)
> παραμένει για preview/fallback· η κύρια κατεύθυνση είναι πλέον React (owner decision 2026-07-10).

## Status
🟢 **Validation ΟΛΟΚΛΗΡΩΘΗΚΕ** (3 μαγαζιά είπαν ναι) → υλοποίηση σε εξέλιξη (Φάση 1).
🟢 **React sites (Next.js) end-to-end** (2026-07-10): 3 distinct templates + site-data API + build OK.

## Επόμενο βήμα
Ακολούθησε το **[docs/09-MASTER-PLAN.md](docs/09-MASTER-PLAN.md)** — το πλήρες βήμα-βήμα πλάνο.
Αυτή την εβδομάδα: ΒΗΜΑ 2 (Meta App Review — ξεκίνα σήμερα) + ΒΗΜΑ 1 (λογαριασμοί).
