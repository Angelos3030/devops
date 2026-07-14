# 📍 STATUS — Πού σταματήσαμε (handoff για συνέχεια)

> Διάβασε ΑΥΤΟ πρώτο αν συνεχίζεις από άλλο account/session.
> Κρατιέται ενημερωμένο σε κάθε σημαντικό βήμα.

**Τελευταία ενημέρωση:** 2026-07-10
**Φάση:** Design Engine + onboarding + approve + Railway deploy (Online) + React dashboard (login).
Επόμενο: enable Google provider στο Supabase Auth, `dashboard/.env`, deploy dashboard σε
`app.getvitrina.gr`. (Optional: valid `ANTHROPIC_API_KEY` για AI copy.)
**🖥️ React Dashboard (2026-07-10):** ✅ Νέο `dashboard/` = Vite + React + Supabase Auth (Google login).
   Owner decision: React ΜΟΝΟ για app layer (login + πίνακας πελάτη)· τα generated sites ΜΕΝΟΥΝ static.
   Έμπνευση amboras.com (AI e-commerce, generative A/B). `Login.jsx` (Google) + `Dashboard.jsx`
   (lookup πελάτη από email → N design options με preview iframes → «Επιλογή»/approve → deployed_url).
   API: `GET /clients/lookup?email=` + `db.get_clients_by_email`. CORS +localhost:5173/app.getvitrina.gr.
   `npm run build` OK. Setup: Supabase→Auth→Providers→Google, `dashboard/.env` (VITE_* publishable key),
   `npm run dev`. Deploy: Cloudflare Pages (output `dist/`).
**🚂 Railway (2026-07-10):** ✅ Service `devops` **Online** στο project `fulfilling-smile`, 11 env vars set
   (CF/Meta/Stripe/Supabase). Μένει: public URL test + custom domain `api.getvitrina.gr` + payment method
   (trial credit low). `main.py` σερβίρει όλα τα endpoints (22 routes).
**🎨 Design engine — variants σε `sites` table (2026-07-10):** τα 3 designs αποθηκεύονται στον ΥΠΑΡΧΟΝΤΑ
   `sites` (preset=layout, url='preview'/'selected') → ΔΕΝ χρειάζεται migration/DDL/DB-password.
   `web/preview.html` = hosted magic-link approve page. Deploy-on-approve (wrangler, χρειάζεται setup στο
   Railway). Tests: offline 47/47 + live Supabase 7/7 + boot 22 routes. Supabase project ήταν paused → Resume.
**🎨 Vitrina Design Engine v2 (2026-07-09):** ✅ Template-based generator — 3 approved
   premium layouts (`studio`/editorial, `commerce`/conversion+κριτικές, `atelier`/minimal)
   στο `skills/vitrina-design-system/templates/`. Πυρήνας: `src/premium_generator.py`
   (templating engine `{{VAR}}` + loops, intake normalizer, per-profession copy defaults,
   `recommend_layout()`, `build_gallery_page()` → 3 sites + σελίδα «Approve»).
   Design DNA από το `awesome-design-html` skill (MIT) + top references (Lindauer/Austin
   Joinery). 0 tokens, χωρίς API key. Απόφαση owner: templates > AI-per-site (φθηνό/γρήγορο/
   πάντα ωραίο). ΟΧΙ React — static HTML (mass deploy Cloudflare Pages). Ένα 4ο «cinematic/
   μαύρο» layout απορρίφθηκε.
   **Onboarding (#2):** `_build_site_bg` στο `src/meta_oauth.py` παράγει πλέον τα 3 designs
   ντετερμινιστικά (αντί για blocked AI agents), μαζεύοντας uploaded φωτο/υπηρεσίες μέσω
   `_enrich_intake`. **Approve (#3):** νέα endpoints `GET /clients/{id}/designs`,
   `GET /clients/{id}/preview/{layout}`, `POST /clients/{id}/select-design`. DB helpers στο
   `src/db.py` (`save_site_variant`/`set_selected_design`) + migration `db/add_site_variants.sql`
   (πίνακας `site_variants` + `selected_layout` στον `clients`, RLS on — **ΤΡΕΞΕ ΤΟ ΣΤΟ SUPABASE**).
   **AI copy (#1, hook έτοιμο):** `src/site_copy.py` γράφει ελληνικό κείμενο ανά πελάτη με
   Haiku μόλις μπει valid key· τώρα no-op fallback (πιάνει το 401, γυρνά σε defaults).
   **Demo/proof:** `python -m scripts.generate_client_site` → `web/clients/koutrakis-auto/` +
   `koutrakis-auto-choose.html`. Επαληθεύτηκε καθαρό (0 placeholders) και σε ταβέρνα/οδοντίατρο/
   κομμωτήριο χωρίς φωτο (fallback hero + σωστό copy ανά επάγγελμα).
   **Preview + deploy-on-approve (2026-07-10):** `web/preview.html` = hosted magic-link σελίδα
   (`?client=<id>&api=<url>`) που δείχνει τα 3 designs (iframes στο `/preview/{layout}`), Approve →
   `POST /select-design` → background **auto-deploy** του επιλεγμένου σε Cloudflare Pages
   (`_deploy_selected_bg` στο `meta_oauth.py`, μέσω `deploy.deploy_site` = wrangler). Το `/designs`
   επιστρέφει τώρα και `deployed_url`· η preview.html κάνει poll μέχρι να ανέβει και δείχνει το live link.
   `db.get_live_site()` προστέθηκε. **Tests:** offline 47/47 + live 7/7 (Supabase) + boot test (21 routes)
   όλα πράσινα 2026-07-10.
**Domain checkout automation:** ✅ Προστέθηκε one-time Stripe Checkout για domain `.gr`
   στα 24€/έτος. Frontend: `connect.html` → `/domain/create-checkout`.
   Backend: `src/main.py` δημιουργεί Checkout Session με metadata `kind=domain_purchase`.
   Webhook: `src/stripe_webhook.py` στο `checkout.session.completed` γράφει `paid`.
   Αν `DOMAIN_REGISTRAR=papaki`, τρέχει `buy_and_setup()` μέσω `src/registrars.py`
   Papaki adapter και μετά Cloudflare DNS setup. Χρειάζονται Papaki reseller credentials:
   `PAPAKI_API_BASE`, `PAPAKI_API_KEY`, `PAPAKI_RESELLER_ID`, `PAPAKI_CONTACT_ID`.
   Το παλιό public GitHub link για GoldResellers JSON API φαίνεται 404, άρα πριν live
   purchase πρέπει να επιβεβαιωθούν official endpoint paths/payloads από Papaki.
   Direct `/domain/purchase` έγινε internal/admin και θέλει `DOMAIN_ADMIN_TOKEN`.
   DB migrations applied στο Supabase: `db/add_domains.sql` + `db/add_domain_orders.sql`
   (`domains`, `domain_orders`, και τα δύο με RLS enabled). Full reference και στο `db/schema.sql`.
   Διαβάστε πρώτα `docs/14-DOMAIN-AUTOMATION.md` πριν αλλάξετε domain code.
**First real prospect demo:** ✅ Κώστας Κουτράκης — domain αγοράστηκε:
   `koutrakiskouzines.gr`. Site canonical/og/json-ld ενημερώθηκαν στα local previews.
   Primary demo route: `web/clients/koutrakis-xylourgos/editorial.html`.
**External design skills decision:** ✅ Μην εισάγετε React/Next/Tailwind GitHub skills
   wholesale στο Vitrina pipeline. Παίρνουμε μόνο patterns/rules και τα γράφουμε στα
   δικά μας static HTML skills. Διαβάστε:
   `skills/vitrina-design-system/references/external-skill-ingestion.md`.
**Spec-first design workflow:** ✅ Το reusable κομμάτι από web-design είναι πλέον
   `skills/vitrina-design-system/references/design-spec.md`: 9-section spec,
   responsive breakpoints, accessibility checklist και pre-preview quality audit.
   Κάθε agent που φτιάχνει/βελτιώνει site πρέπει να γράφει spec πριν το HTML.
**Domain:** ✅ **getvitrina.gr αγοράστηκε** — μπήκε σε meta_oauth.py (redirect_uri),
   privacy-policy.md (email/brand), index.html footer (hello@getvitrina.gr).
**Supabase:** ✅ Project `vitrina` δημιουργήθηκε (`rmhgkwscchyjzjkxezuf`, EU `eu-central-1`),
   `db/schema.sql` εφαρμόστηκε ως migration `initial_vitrina_schema`, `.env` έχει
   `SUPABASE_URL` + publishable key. ✅ Domain tables applied: `domains`, `domain_orders`
   με RLS enabled. ⚠️ Supabase advisor έδειξε RLS disabled σε 7 παλιούς public tables,
   άρα θέλει ξεχωριστό security/policies pass πριν production.
**Cloudflare Pages:** ✅ Project `vitrina` δημιουργήθηκε και έγινε deploy του `web/`.
   Latest live preview: `https://15007041.vitrina-7uq.pages.dev`. Custom domains:
   ✅ `https://getvitrina.gr` live/SSL OK, ✅ `https://getvitrina.gr/privacy.html` 200,
   ✅ `https://getvitrina.gr/data-deletion.html` 200. Nameservers σε Cloudflare:
   `matteo.ns.cloudflare.com`, `poppy.ns.cloudflare.com`.
**Stripe:** ✅ Test setup έτοιμο στο `.env`: `STRIPE_SECRET_KEY` + `STRIPE_WEBHOOK_SECRET`
   αποθηκεύτηκαν (μην τα εμφανίζεις), και δημιουργήθηκαν test Prices:
   `STRIPE_PRICE_STARTER=price_1TfzYHCXhuChnUHdlQeCNrex`,
   `STRIPE_PRICE_SOCIAL=price_1TfzYICXhuChnUHdMsnpimSz`,
   `STRIPE_PRICE_PREMIUM=price_1TfzYJCXhuChnUHdxTcWlDMj`.
   Webhook endpoint: `we_1TfzYjCXhuChnUHdRhlGKae5` →
   `https://api.getvitrina.gr/stripe/webhook`.
**Growth/Facebook Ads:** ✅ Τεκμηριωμένο στο `docs/13-META-GROWTH-ADS.md`.
   Τρίπτυχο: Organic (τώρα) → Promoted posts (μήνας 3-4) → Full ads (μήνας 6+).
   Πακέτο €99–149/μήνα + ad spend. Approval flow + budget guardrails documented.
**New custom skills:** ✅ `facebook-ads-gr` + `conversion-copy-gr` δημιουργήθηκαν,
   validated, και μπήκαν σε `upload_skills.py` / `config.py` / `.env.example`.
   `conversion-copy-gr` προστέθηκε στο Website Agent. `facebook-ads-gr` ανεβαίνει τώρα,
   αλλά Ads Agent ΔΕΝ δημιουργείται πριν το post-MVP Growth phase.
**Client onboarding scope:** ✅ `docs/09-MASTER-PLAN.md` ενημερώθηκε: όταν μπαίνει πελάτης,
   πρέπει να μαζεύουμε email/contact, να διαλέγει site, να ελέγχουμε Facebook Page,
   Instagram Business, Meta Business/Ad Account, και optional business email. Pages/ad accounts
   δεν δημιουργούνται χωρίς πελάτη/admin approval.
**Client assets intake:** ✅ Προστέθηκε `client_assets` table + Supabase migration
   `add_client_assets`. API endpoints: `POST /clients/{client_id}/assets`,
   `GET /clients/{client_id}/assets`. Για MVP αποθηκεύουμε κείμενα/metadata/URLs
   και `rights_ok`; binary uploads μπαίνουν αργότερα με Supabase Storage.
**Meta review hardening:** ✅ Προστέθηκε `web/data-deletion.html`, καθαρίστηκαν
   privacy/terms από placeholders, διορθώθηκε `connect.html` brand σε Vitrina,
   και ενημερώθηκαν `legal/meta-review-submission.md` + `docs/12-META-APP-REVIEW.md`
   με review URLs και rejection checklist. Latest deploy: `https://15007041.vitrina-7uq.pages.dev`.
**GitHub/Railway source:** ✅ Το local project έγινε git repo και έγινε push στο
   `https://github.com/Angelos3030/devops` branch `main` (latest commit `8491e31`).
   `.env`, `.claude/`, `.wrangler/` αγνοούνται με `.gitignore`.
**Local smoke test:** ✅ 2026-06-12: dependencies installed locally, `src.main:app`
   imports OK, `/healthz` OK, `/domain/suggest` OK, `/onboard` δημιούργησε test client
   στο Supabase και καθαρίστηκε, Stripe Checkout URL OK. ⚠️ AI/skills site generation
   ΔΕΝ μπορεί να δοκιμαστεί ακόμα: `ANTHROPIC_API_KEY` γυρίζει `401 invalid x-api-key`,
   και `upload_skills.py` γυρίζει Anthropic beta `404 Not found`.
**Vitrina Design Engine:** ✅ 2026-06-12: προστέθηκε project skill
   `skills/vitrina-design-system/`, route-based local generator (`premium`, `warm`,
   `minimal`) και preview gallery. Local URLs: `/preview-gallery.html`,
   `/previews/taverna-premium.html`, `/previews/taverna-warm.html`,
   `/previews/taverna-minimal.html`. Smoke/validation OK.
**First real prospect demo:** ✅ 2026-06-12: Κώστας Κουτράκης, ξυλουργός/μαραγκός.
   Δημιουργήθηκαν local previews:
   `/clients/koutrakis-xylourgos.html`,
   `/clients/koutrakis-xylourgos/premium.html`,
   `/clients/koutrakis-xylourgos/warm.html`,
   `/clients/koutrakis-xylourgos/minimal.html`.
   Εκκρεμούν από πελάτη: πραγματικό τηλέφωνο, πόλη/περιοχή, φωτογραφίες δουλειών,
   domain επιλογή. Facebook/Instagram μένει για αργότερα.
**Parallel agent split:** 🔀 2026-06-12: sub-agent `Mencius`
   (`019ebb8d-e18c-7ba3-803d-77eb74e4196a`) ανέλαβε fallback local site generator.
   Owner files: `src/local_site_generator.py`, `scripts/smoke_local_site.py`,
   generated `web/local-test-taverna.html`. Μην τα πειράξετε μέχρι να επιστρέψει.
**Meta App Review audit (session 5):** ✅ Κρίσιμο bug: `pages[0]` auto-select χωρίς UI.
   Τώρα: `GET /connect/pages` + `POST /connect/finalize` + κάρτα επιλογής στο `connect.html`.
   Stale "Papaki" comment fix. `meta-review-submission.md` updated. Βλέπε assessment παρακάτω.

---

## 🎯 META APP REVIEW — Εκτίμηση Πιθανότητας Επιτυχίας

**Ποσοστό: ~80% για πρώτο pass**, αν:
- Τα test credentials είναι πραγματικός Facebook test account με Business Page + Instagram Business
- Το screencast δείχνει καθαρά την επιλογή Σελίδας (νέα κάρτα) + δημοσίευση post + το post live

### ✅ Τι είναι σωστό (πλεονεκτήματα)
| Στοιχείο | Κατάσταση |
|---|---|
| Permissions: ακριβώς 5, όλα δικαιολογημένα | ✅ |
| `pages_show_list`: τώρα πραγματικά εμφανίζει λίστα για επιλογή | ✅ (φτιάχτηκε session 5) |
| Privacy + data-deletion URLs δημόσια | ✅ |
| Token logging ασφαλές (`token=***`) | ✅ |
| Consent links πριν το OAuth button | ✅ |
| API v21.0 (current) | ✅ |
| Brand "Vitrina" παντού | ✅ |
| App description ξεκάθαρη | ✅ |

### ⚠️ Ρίσκα που μένουν
| Ρίσκο | Βαρύτητα | Λύση |
|---|---|---|
| Test credentials κενά (`[TEST_EMAIL]` κ.λπ.) | 🔴 Blockers | Συμπλήρωσε πριν submit |
| App σε Dev mode → reviewer πρέπει να είναι **Tester** στο App | 🔴 Blocker | Meta App Dashboard → Roles → Add Tester |
| `pages_read_engagement` δεν φαίνεται να χρησιμοποιείται στο screencast | 🟡 Μέτριο | Στο use-case γράψε ότι είναι **prerequisite του `pages_manage_posts`** — Meta το ξέρει αυτό |
| OAuth error page = FastAPI raw 400 (reviewer μπορεί να το δει αν πηγαίνει στραβά) | 🟢 Μικρό | Ανεκτό για MVP |
| App icon πρέπει να είναι ανεβασμένο στο Meta App Dashboard | 🟡 Μέτριο | `src/make_icon.py` → ανέβασε `web/icon-1024.png` |

### 📋 Checklist πριν κάνεις submit
- [ ] Γέμισε `[TEST_EMAIL]`, `[TEST_PASSWORD]`, `[Test Page name]`, `[@handle]` στο `legal/meta-review-submission.md`
- [ ] Βάλε τον reviewer account ως **Tester** στο Meta App (Settings → Roles)
- [ ] Ανέβασε `web/icon-1024.png` ως App Icon στο Meta App Dashboard
- [ ] Test credentials: σιγουρέψου ότι η Page είναι **Instagram Business** (linked IG account)
- [ ] Γύρισε screencast: κάμερα ανοιχτή, 2-4 λεπτά, χωρίς ήχο, δείξε **page selection card**
- [ ] Δοκίμασε τα credentials ακριβώς πριν κάνεις submit (μην έχουν λήξει)

---

> 🔀 ΠΑΡΑΛΛΗΛΗ ΕΡΓΑΣΙΑ — διαβάστε αυτό πρώτα για να ΜΗΝ επαναλάβετε δουλειά:
> - **Χρήστης (browser):** Meta App Review + DNS CNAME/nameservers + Supabase service_role key
> - **Claude (κώδικας):** db.py, daily_post.py, meta_oauth.py, setup_agents.py — ΗΔΗ ΕΝΗΜΕΡΩΜΕΝΑ
> - **Άλλος agent:** δείτε "ΤΙ ΑΚΟΛΟΥΘΕΙ" — μην ξαναγράφετε αρχεία που είναι [x]

## 🚦 COORDINATION LOCKS — για παράλληλους agents

**ΜΗΝ ΞΑΝΑΚΑΝΕΤΕ / ΜΗΝ ΠΕΙΡΑΞΕΤΕ χωρίς λόγο:**
- [x] **Premium Design Engine** (`src/premium_generator.py`, 3 templates στο
      `skills/vitrina-design-system/templates/`, `src/site_copy.py`, endpoints designs/
      preview/select-design, `db/add_site_variants.sql`). Owner: session 2026-07-09.
      Τα 3 layouts είναι approved — μην τα ξανασχεδιάσετε. Το «cinematic/μαύρο» απορρίφθηκε.
- [x] Supabase project creation + schema migration (`vitrina`, `initial_vitrina_schema`).
- [x] Cloudflare Pages project creation + landing deploy (`vitrina`, `web/`).
- [x] Pages custom domains add (`getvitrina.gr`, `www.getvitrina.gr`).
- [x] `.env` Supabase fields + Cloudflare `CF_ACCOUNT_ID`.
- [x] Direct Graph API path, Meta MCP removal, `_store_credentials`, `daily_post.py` posting flow.
- [x] New skills: `facebook-ads-gr`, `conversion-copy-gr`; μην τα ξαναδημιουργήσετε.
- [x] Client assets intake table/API (`client_assets`, `/clients/{id}/assets`).
- [x] Stripe test secret/prices/webhook setup (`.env`, test mode).
- [x] Supabase domain migrations applied (`domains`, `domain_orders`, RLS enabled).
- [x] Meta review hardening legal pages + data deletion page + latest Pages deploy (`15007041`).
- [x] GitHub repo initialized + pushed to `Angelos3030/devops` branch `main`.
- [x] Railway upload crash fix: `python-multipart>=0.0.9` υπάρχει στο remote `requirements.txt`
      (commit `8491e31`).
- [x] Local backend smoke test: health/domain/onboard/Stripe OK.
- [ ] AI skills/agents smoke test: blocked μέχρι να μπει valid Anthropic key + διαθέσιμο
      Skills/Agents beta access ή fallback runtime.
- [ ] Parallel fallback generator task: Owner `Mencius`; write scope
      `src/local_site_generator.py`, `scripts/smoke_local_site.py`.

**ΤΩΡΑ ΠΕΡΙΜΕΝΟΥΜΕ / ΘΕΛΕΙ ΧΕΙΡΟΚΙΝΗΤΟ Ή ΝΕΟ SECRET:**
- [x] **`railway.toml`** — δημιουργήθηκε (Nixpacks builder, healthcheck `/healthz`, restart policy). Procfile υπήρχε ήδη.
- [ ] **Railway backend deploy** — New Project → Deploy from GitHub. Μετά: βάλε subdomain `api.getvitrina.gr` → Railway URL.
- [x] DNS: `getvitrina.gr` + `www.getvitrina.gr` → Cloudflare IPs επαληθεύτηκαν (`104.21.5.22`, `172.67.132.194`). SSL cert **Pending Validation** — αυτόματο, αναμένεται σε λίγη ώρα.
- [ ] DNS: `api.getvitrina.gr` → Railway (λείπει ακόμα CNAME· χρειάζεται Railway public/custom-domain target).
- [ ] Supabase: βάλε `service_role` key στο server `.env`; μετά κάνε RLS/policies pass
      για τους 7 παλιούς public tables που έδειξε ο advisor.
- [x] Stripe local `.env`: test `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_*`.
      Webhook URL: `https://api.getvitrina.gr/stripe/webhook`
- [ ] Stripe/Railway: αντιγραφή των ίδιων env vars στο Railway και checkout/webhook test όταν
      σηκωθεί το `api.getvitrina.gr`.
- [ ] Meta: βάλε `META_APP_ID`, `META_APP_SECRET` · Valid OAuth Redirect URI: `https://api.getvitrina.gr/connect/callback`
- [ ] Anthropic: βάλε API key/Managed Agents access πριν τρέξει `upload_skills.py`.
- [ ] Μετά το `upload_skills.py`, βάλε και `SKILL_ADS`, `SKILL_COPY` στο Railway/.env.
- [ ] Product/onboarding UI μελλοντικά: πρόσθεσε fields/checklist για email, Facebook Page,
      Instagram Business, Meta Business/Ad Account, ads payment method, business email.
- [ ] Product/onboarding UI μελλοντικά: πρόσθεσε upload/link fields για photos, logo,
      bio/history, menu/services, price list, before/after, social links και rights confirmation.

**ΑΝ ΕΙΣΑΙ ΑΛΛΟΣ AGENT:** πριν κάνεις αλλαγή, ενημέρωσε αυτό το block με “Owner: <όνομα/session>”
και μην πειράξεις tasks που είναι ήδη `[x]`, εκτός αν υπάρχει σφάλμα και το γράψεις εδώ.

---

## ✅ ΤΙ ΕΧΕΙ ΓΙΝΕΙ

- [x] **Validation** — 3 μαγαζιά είπαν ναι (GO).
- [x] **Πλήρης τεκμηρίωση** (docs/01–12): αρχιτεκτονική, skills, tech stack, build plan,
      κόστος/τιμολόγηση, ρίσκα, verticals, validation, master plan, token-efficiency,
      external skills, Meta App Review.
- [x] **Skills (κείμενο)** γραμμένα: brand-builder-gr, greek-website (+PRESETS 30+ επαγγέλματα
      +3 HTML templates), social-post-gr, meta-publisher, local-seo-gr.
- [x] **Κώδικας scaffolding** (Python): config, db (+schema.sql), agent_runtime,
      setup_agents, upload_skills, onboard_client, daily_post, deploy, stripe_webhook.
- [x] **Meta OAuth flow** (`src/meta_oauth.py`) — Σύνδεση με Facebook → Page/IG token.
- [x] **Meta posting ΛΕΙΤΟΥΡΓΙΚΟ** (`skills/meta-publisher/publish.py`) — direct Graph API,
      FB photos/feed + IG 2-step publish.
- [x] **Legal/review κείμενα** (`legal/`): privacy-policy.md, meta-review-submission.md
      (use-case ανά permission + screencast script + reviewer instructions).
- [x] **upload_skills.py** — best-effort raw HTTP (POST /v1/skills + versions, zip έτοιμο).
- [x] **Web UI** (`web/connect.html`) — onboarding form + «Σύνδεση με Facebook».
- [x] **Landing → Connect wiring** — το `?desc=` περνά στο connect.html, αυto-ανίχνευση
      τύπου (11) + πόλης (22), πεδίο περιγραφής. Φόρμα κάνει live `POST /onboard`.
- [x] **`/onboard` endpoint** (`src/meta_oauth.py`) — `db.create_client()` + background
      site-building. CORS για getvitrina.gr. `db.create_client()` προστέθηκε.
- [x] **Legal pages** (`web/privacy.html`, `web/terms.html`) — styled, brand Vitrina,
      hello@getvitrina.gr. Για τα Meta App URLs (Settings → Basic).
- [x] **App Icon** (`src/make_icon.py` → `web/icon-1024.png` + favicon-180/32) —
      storefront λογότυπο. Ανέβασε icon-1024.png στο Meta App. Favicons στο index.html.
- [x] **QUICKSTART.md** — ακριβείς εντολές για end-to-end τρέξιμο.
- [x] **Landing page ΕΤΟΙΜΟ** (`web/index.html`) — branding «Vitrina», base44-style hero με
      prompt box + suggestion chips, φωτεινό γαλάζιο gradient, πορτοκαλί accent, λογότυπο
      μαγαζιού (SVG), GR/EN toggle, features/πώς/τιμές/CTA. Δίγλωσσο.
- [x] **Supabase project + schema** — Project `vitrina` στο EU `eu-central-1`, migration
      `initial_vitrina_schema`, πίνακες: clients, brand_profiles, sites, social_accounts,
      posts, subscriptions. `.env` ενημερώθηκε με URL + publishable key.
- [x] **Cloudflare Pages landing deploy** — Δημιουργήθηκε Pages project `vitrina`,
      ανέβηκαν τα αρχεία του `web/`, προστέθηκαν custom domains `getvitrina.gr` και
      `www.getvitrina.gr`. DNS ακόμα pending στον registrar/Cloudflare zone.
- [x] **Landing redesign pass** (`web/index.html`) — πιο πρακτικό/demo-driven hero,
      sample site + sample social post, πιο συγκεκριμένα feature copy/CTA, desktop/mobile
      browser QA, EN toggle check. Latest deploy: `https://15007041.vitrina-7uq.pages.dev`.
- [x] **Railway backend readiness** — `Procfile` δείχνει `uvicorn src.main:app --host 0.0.0.0 --port $PORT`,
      `src/main.py` ενώνει Meta OAuth/checkout + Stripe webhook σε ένα FastAPI app,
      `web/connect.html` καλεί production API `https://api.getvitrina.gr`,
      `REDIRECT_URI=https://api.getvitrina.gr/connect/callback`, CORS έχει `getvitrina.gr`,
      `www`, και Pages preview domains. Python compile OK.
- [x] **Stripe price config cleanup** — αφαιρέθηκαν τα hardcoded placeholder `price_*`
      από `meta_oauth.py`/`stripe_webhook.py`. Πλέον μπαίνουν μία φορά στο `.env`.
- [x] **Stripe test setup** — αποθηκεύτηκε test `STRIPE_SECRET_KEY`, δημιουργήθηκαν
      Starter/Social/Premium test Prices, δημιουργήθηκε webhook endpoint
      `we_1TfzYjCXhuChnUHdRhlGKae5` για `https://api.getvitrina.gr/stripe/webhook`,
      και το signing secret αποθηκεύτηκε στο `.env`.
- [x] **Growth/Facebook Ads docs** — `docs/05-COSTS-PRICING.md`, `docs/01-ARCHITECTURE.md`,
      `docs/09-MASTER-PLAN.md` ενημερώθηκαν με Ads Agent/Growth add-on, approval flow,
      budget guardrails και Meta Marketing API ως μελλοντική φάση.
- [x] **New custom skills** — `skills/facebook-ads-gr/` με 25 Facebook ad examples
      και `skills/conversion-copy-gr/` με 32 copy/CTA patterns. Και τα δύο validated
      με `quick_validate.py` (`PYTHONUTF8=1`). Upload/config/env ενημερωμένα.
- [x] **Client onboarding checklist docs** — `docs/09-MASTER-PLAN.md` έχει πλέον checklist
      για email capture, site επιλογή, Facebook Page, Instagram Business, Meta ad account,
      posts, ads readiness και business email.
- [x] **Client assets intake backend** — `db/schema.sql`, Supabase migration
      `add_client_assets`, `src/db.py`, `src/meta_oauth.py` ενημερώθηκαν για customer
      photos/logo/bio/menu/price list/before-after metadata + rights confirmation.
- [x] **Logo + photo upload** — `POST /clients/{client_id}/upload` (FastAPI + Supabase Storage).
      Client-side compression (Canvas API): logo→512px, photos→1400px, JPEG 0.82.
      connect.html: drag & drop zones, preview thumbnails, non-blocking upload μετά το onboard.
      ⚠️ Χρειάζεται Supabase bucket: Dashboard → Storage → New bucket → `client-assets` (Public: ON).
- [x] **Email field** — προστέθηκε σε `Intake` model, `db.create_client()`, και `connect.html` form.
- [x] **RLS policies** — `db/rls_policies.sql` έτοιμο: enable RLS σε όλους τους πίνακες,
      service_role bypasses αυτόματα, anon blocked. Τρέξε στο Supabase SQL Editor.
- [x] **Domain automation** — `src/domain.py`: suggest_domains (transliteration GR→ASCII),
      check_availability (Papaki API), purchase_domain, create_cloudflare_zone,
      add_dns_records (www→Pages, api→Railway), update_papaki_nameservers.
      Endpoints: `POST /domain/suggest`, `/domain/check`, `/domain/purchase`.
      DB: `domains` table + `save_domain()`/`get_domain()`. Config: `PAPAKI_API_KEY` +
      `PAPAKI_REGISTRANT_*`. ⚠️ Χρειάζεται Papaki Reseller account για live χρήση.
- [x] **Meta App Review deep audit (session 5)** — εντοπίστηκε κρίσιμο πρόβλημα:
      κώδικας έπαιρνε `pages[0]` χωρίς καθόλου UI επιλογής χρήστη. Υλοποιήθηκε
      πλήρης **page selection flow**: `GET /connect/pages` (λίστα χωρίς tokens),
      `POST /connect/finalize` (store τελικής επιλογής), νέο `#page-select-step` card
      στο `connect.html` με κάρτες ανά Σελίδα + click-to-select. `_pending` dict
      κρατά `{pages}` μεταξύ callback και επιλογής (in-process, fine for Railway).
      Επίσης: stale "Papaki API" docstring → "Cloudflare Registrar API", URL encoding
      με `urllib.parse.quote_plus` στο callback redirect.
- [x] **Meta review hardening deploy** — `web/connect.html` γράφει Vitrina,
      `web/privacy.html` και `web/terms.html` δεν έχουν placeholders, προστέθηκε
      `web/data-deletion.html`, footer link στην αρχική, και έγινε Cloudflare Pages deploy:
      `https://15007041.vitrina-7uq.pages.dev`.
- [x] **GitHub push for Railway** — προστέθηκε `.gitignore`, έγινε initial commit
      `4dde97c` και push στο `Angelos3030/devops` branch `main`. Το `.env` δεν έγινε track.
- [x] **Railway dependency fix** — προστέθηκε `python-multipart>=0.0.9` στο
      `requirements.txt` για το `/clients/{client_id}/upload` FastAPI endpoint.
- [x] **Local smoke test** — uvicorn local port 8001, `/healthz`, `/domain/suggest`,
      `/onboard`, `/create-checkout` OK. Generated demo template:
      `web/local-test-taverna.html` (untracked local artifact).
- [x] **Αποφάσεις:** ΟΧΙ runtime coordinator (κώδικας orchestrates), Haiku/Sonnet (όχι Opus),
      μόνο sites (όχι app), €9.90 δόλωμα → €49 ταμείο, 9 curated external skills.

---

## 🔜 ΤΙ ΑΚΟΛΟΥΘΕΙ (επόμενα βήματα, με σειρά)

### 🔑 Χρειάζεται εσένα (secrets / εξωτερικά)
0. [x] **Design engine live test** — ΠΕΡΑΣΕ (2026-07-10, 7/7 σε πραγματικό Supabase).
      Τα 3 designs αποθηκεύονται στον ΥΠΑΡΧΟΝΤΑ πίνακα `sites` (preset=layout, url='preview'/
      'selected') → **ΔΕΝ χρειάζεται migration/DDL/DB-password**. Το `db/add_site_variants.sql`
      έμεινε optional (μόνο αν θες dedicated πίνακα αργότερα). Το project ήταν paused → έγινε Resume.
0b.[ ] **Valid `ANTHROPIC_API_KEY`** — τώρα δίνει 401. Μόλις μπει, το `src/site_copy.py` γράφει
      αυτόματα ελληνικό κείμενο ανά πελάτη (αλλιώς δουλεύει με per-profession defaults).
1. [ ] **SSL cert** — αυτόματο, αναμένεται (Cloudflare Edge Certificates → Active)
2. [ ] **Railway deploy** — New Project → Deploy from GitHub → βάλε env vars:
      `SUPABASE_URL`, `SUPABASE_KEY` (service_role), `STRIPE_SECRET_KEY`,
      `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_*`, `META_APP_ID`, `META_APP_SECRET`,
      `ANTHROPIC_API_KEY`, `CF_API_TOKEN`, `CF_ACCOUNT_ID`
3. [ ] **Railway Custom Domain** → `api.getvitrina.gr` → CNAME στο Cloudflare DNS
4. [ ] **Supabase service_role key** → βάλε ως `SUPABASE_KEY` στο Railway/.env
      → Τρέξε `db/rls_policies.sql` στο SQL Editor
5. [x] **Supabase domain migrations** → applied `db/add_domains.sql` +
      `db/add_domain_orders.sql` στο project `rmhgkwscchyjzjkxezuf`.
6. [ ] **Meta App ID/Secret** → βάλε `META_APP_ID`, `META_APP_SECRET` + Valid OAuth Redirect URI:
      `https://api.getvitrina.gr/connect/callback`
7. [ ] **Stripe env sync** → copy test keys στο Railway, test checkout + webhook όταν ανέβει API
8. [ ] **Anthropic API key** + Managed Agents access → `ANTHROPIC_API_KEY` στο Railway
9. [ ] **Meta App Review** → ξεκίνα μόλις ανέβουν τα domains (docs/12). Πιο αργό βήμα.

### 💻 Κώδικας (να τρέξεις μετά τα keys)
10. [ ] `python -m src.upload_skills` → βάλε `SKILL_*` στο `.env` + Railway
11. [ ] `python -m src.setup_agents` → βάλε `ENV_ID`, `*_AGENT_ID` στο `.env` + Railway
12. [ ] Test `python -m src.daily_post` με 1 test πελάτη
13. [ ] Stripe + onboard τους 3 πρώτους πελάτες

### 🔜 Φάση 2 (μετά MVP)
14. [ ] `onboard_client.py` → site generation + Cloudflare Pages deploy ανά πελάτη
15. [ ] Growth/Facebook Ads — μόνο αφού δουλέψει auto-posting (docs/13)

---

## ⚠️ ΑΝΟΙΧΤΑ ΣΗΜΕΙΑ (χρειάζονται live επιβεβαίωση)

- [x] **Skills API upload shape** — `src/upload_skills.py`: SDK, `display_title`, raw files.
- [x] **Meta MCP URL** — αφαιρέθηκε. Direct Graph API επιλέχθηκε. `setup_agents.py` OK.
- [x] **Posting path** — direct Graph API (publish.py). `daily_post.py` καλεί `publish_all()`.
- [x] **`_store_credentials`** — υλοποιήθηκε: γράφει `page_token/page_id/ig_user_id` στη DB.
- [x] **`daily_post.py` bug** — διορθώθηκε: parse JSON agent output → `publish_all()` → `save_post()`.
- [x] **Cloudflare Pages deploy** — project `vitrina` δημιουργήθηκε, `web/` ανέβηκε.
- [x] **Landing redesign QA/deploy** — desktop/mobile no horizontal overflow, EN toggle OK,
      latest Cloudflare deployment `15007041`.
- [x] **Railway code prep** — `src.main:app` + `Procfile` + `railway.toml` υπάρχουν. Frontend production API:
      `https://api.getvitrina.gr`. Latest frontend deployment `15007041`.
- [x] **Stripe Dashboard values** — test `price_*` IDs και webhook signing secret μπήκαν
      στο `.env`. Το current Cloudflare Pages URL είναι static frontend, όχι FastAPI
      webhook host, άρα full webhook test μετά το Railway/API domain.
- [x] **Cloudflare DNS** — `getvitrina.gr` nameservers δείχνουν Cloudflare και το
      HTTPS site ανοίγει με 200. Εκκρεμεί μόνο `api.getvitrina.gr` προς Railway.
- [ ] **Νομικό** — μπλοκάκι/εταιρεία για έσοδα + Meta business verification (ρώτα λογιστή).
- [ ] **`redirect_uri`** — `https://getvitrina.gr/connect/callback` (ήδη στο meta_oauth.py).
      Βεβαιώσου ότι είναι στο Meta App → Valid OAuth Redirect URIs.
- [ ] **META_APP_ID / META_APP_SECRET** στο `.env` (από το Meta App Dashboard).
- [ ] **schema.sql migration** — αν έχεις ήδη `social_accounts` με `vault_id`, τρέξε τα
      ALTER TABLE comments στο db/schema.sql.
- [ ] **page_token encryption** — για production, κρυπτογράφησε πριν αποθήκευση (pgcrypto).
- [ ] **Supabase RLS/security** — advisors δείχνουν `rls_disabled_in_public` σε 7 παλιούς public πίνακες.
      Για production: βάλε `service_role` στο server `.env`, enable RLS, και φτιάξε policies
      πριν εκτεθεί οτιδήποτε σε δημόσιο frontend.
- [ ] **Growth/Facebook Ads implementation** — ΜΗΝ ξεκινήσει πριν το core MVP.
      Χρειάζεται νέα permissions/app review για Meta Marketing API (`ads_read`,
      `ads_management`) και approval workflow πριν από οποιοδήποτε spend.
- [x] **Skill validation** — `facebook-ads-gr` και `conversion-copy-gr` valid.
      Σημείωση Windows: χρειάστηκε `PYTHONUTF8=1` για τον validator λόγω ελληνικών UTF-8.
- [x] **Supabase migration `add_client_assets`** — εφαρμόστηκε στο project `rmhgkwscchyjzjkxezuf`.
- [x] **Meta review legal URLs** — `privacy.html`, `terms.html`, `data-deletion.html`
      επιστρέφουν 200 στο latest Pages preview. Domain URLs θα δοκιμαστούν όταν ενεργοποιηθούν
      οι Cloudflare nameservers.

---

## 🔒 ΑΡΧΕΙΑ ΠΟΥ ΑΛΛΑΞΑΝ (session 5 — μην ξαναγράφεις)

| Αρχείο | Τι έγινε |
|---|---|
| `src/meta_oauth.py` | `_pending` dict + `GET /connect/pages` + `POST /connect/finalize`. Callback: `pages[0]` → redirect σε `?step=select_page`. `urllib.parse.quote_plus` στο redirect URL. |
| `web/connect.html` | Νέο `#page-select-step` card + `showPageSelectStep()` + `renderPageOptions()` + `selectPage()`. `checkReturn()` handles `step=select_page`. |
| `src/main.py` | Stale "Papaki API" docstring → "Cloudflare Registrar API". |
| `legal/meta-review-submission.md` | `pages_show_list` use-case: ενημερώθηκε για πραγματική λειτουργία. Screencast step 5: περιγράφει την κάρτα επιλογής. |

## 🔒 ΑΡΧΕΙΑ ΠΟΥ ΑΛΛΑΞΑΝ (session 2 — μην ξαναγράφεις)

| Αρχείο | Τι έγινε |
|---|---|
| `src/setup_agents.py` | Αφαιρέθηκε `mcp_servers` + `image-gen`. Social Agent → JSON output. |
| `src/upload_skills.py` | Ξαναγράφηκε: SDK, `display_title`, raw files, single call. |
| `src/db.py` | `save_social_creds()` + `get_social_creds()` + `upsert_subscription()`. |
| `src/meta_oauth.py` | `_store_credentials` υλοποιήθηκε. `/create-checkout` endpoint. Redirect → connect.html?step=pay. |
| `src/meta_oauth.py` | Προστέθηκαν `/clients/{client_id}/assets` GET/POST endpoints. |
| `src/db.py` | Προστέθηκαν `save_client_asset()` + `get_client_assets()`. |
| `src/daily_post.py` | Πλήρης επιδιόρθωση: JSON parse → `publish_all()` → `save_post()`. |
| `src/stripe_webhook.py` | Bootstrap bug fix: διαβάζει `client_id` από Stripe metadata. |
| `src/main.py` | Production FastAPI entrypoint για Railway: Meta routes + Stripe webhook + `/healthz`. |
| `Procfile` | Railway start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`. |
| `db/schema.sql` | `social_accounts`: `vault_id` → `page_token`. Migration comments. |
| `db/schema.sql` | Προστέθηκε `client_assets` table για photos/logo/bio/menu/price list/assets. |
| `web/connect.html` | Step 3 payment (Stripe checkout). Auto-detect `?step=pay` return από OAuth. |
| `web/connect.html` | Brand consistency για Meta Review: Vitrina + privacy/data deletion links. |
| `web/privacy.html` | Καθαρίστηκε από placeholders, πιο σαφές Meta data usage + data deletion URL. |
| `web/terms.html` | Καθαρίστηκε από placeholders, link σε data deletion. |
| `web/data-deletion.html` | Νέα dedicated σελίδα Data Deletion Instructions για Meta. |
| `skills/social-post-gr/SKILL.md` | 15 πραγματικά few-shot posts (5 τύποι μαγαζιών, 15 θέματα). |
| `skills/facebook-ads-gr/` | Νέο skill + `references/ad-examples.md` με 25 local Facebook ad examples. |
| `skills/conversion-copy-gr/` | Νέο skill + `references/copy-patterns.md` με 32 copy/CTA examples. |
| `requirements.txt` | Προστέθηκαν `fastapi` + `uvicorn[standard]`. |
| `.env.example` | Προστέθηκαν `SKILL_BRAND/WEBSITE/SOCIAL/META/SEO/ADS/COPY`. |
| `src/upload_skills.py` | Προστέθηκαν `facebook-ads-gr`, `conversion-copy-gr` στο upload list. |
| `src/config.py` | Προστέθηκαν `SKILL_ADS`, `SKILL_COPY` στο `SKILL_IDS`. |
| `src/setup_agents.py` | Website Agent χρησιμοποιεί πλέον και `conversion-copy-gr`; Ads skill ανεβαίνει αλλά δεν φτιάχνει Ads Agent ακόμα. |
| `docs/05-COSTS-PRICING.md` | Προστέθηκε Growth/Facebook Ads pricing + unit economics. |
| `docs/01-ARCHITECTURE.md` | Προστέθηκε μελλοντικός Ads Agent + approval flow. |
| `docs/09-MASTER-PLAN.md` | Προστέθηκε ΒΗΜΑ 11 για Growth/Facebook Ads μετά το MVP. |
| `docs/12-META-APP-REVIEW.md` | Προστέθηκαν exact URLs + rejection checklist. |
| `legal/meta-review-submission.md` | Vitrina brand, exact review URLs, data deletion, stricter screencast script. |

---

## 🗂️ ΧΑΡΤΗΣ ΑΡΧΕΙΩΝ (πού είναι τι)

```
README.md            → επισκόπηση + index
STATUS.md            → ΑΥΤΟ (πού σταματήσαμε)
docs/01..12          → όλη η τεκμηρίωση (δες index στο README)
skills/              → τα custom SKILL.md (το ελληνικό moat)
src/                 → ο κώδικας (setup + runtime)
db/schema.sql        → Supabase schema
scripts/clone-skills.sh → κατεβάζει curated external skills
.env.example         → όλα τα κλειδιά
```

---

## 📝 ΚΑΝΟΝΑΣ ΓΙΑ ΣΥΝΕΧΕΙΑ
Κάθε φορά που σταματάς δουλειά: **ενημέρωσε αυτό το αρχείο** —
τι έγινε, πού σταμάτησες, τι ακολουθεί. Έτσι όποιος συνεχίσει (άλλο account/session)
ξέρει ακριβώς από πού να πιάσει.
