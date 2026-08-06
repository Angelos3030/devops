# 📍 STATUS — Πού σταματήσαμε (handoff για συνέχεια)

> Διάβασε ΑΥΤΟ πρώτο αν συνεχίζεις από άλλο account/session.
> Κρατιέται ενημερωμένο σε κάθε σημαντικό βήμα.

## 🟢 CURRENT HANDOFF (2026-08-06, production `main`)

Αυτό το section υπερισχύει από παλιότερα/pivot sections πιο κάτω, τα οποία μένουν μόνο ως
ιστορικό αποφάσεων.

- Όλες οι επιβεβαιωμένες αλλαγές έχουν γίνει commit και push στο `origin/main`.
- Production library: 30 renderable templates, από τα οποία ο chooser προτείνει **12 curated,
  δομικά διαφορετικά designs** ανά επάγγελμα.
- Νέα designs που ολοκληρώθηκαν στο τελευταίο batch: `cinematic`, `type-gallery`, `quiet`,
  `kinetic`, `infinite`, `living`.
- Pilot flow για 5 φίλους: `https://getvitrina.gr/connect.html?pilot=1`. Δεν ανοίγει Stripe,
  δεν αγοράζει domain και οδηγεί σε δωρεάν Railway preview μετά την επιλογή design.
- Live chooser για έλεγχο: `https://sites-production-da56.up.railway.app/choose/demo-carpenter?pilot=1`.
- API health: `https://api.getvitrina.gr/healthz` → HTTP 200.
- QA που πέρασε πριν το push: `scripts/test_design_engine.py` **88/88**,
  `sites/tests/verticalProfiles.mjs` **14 verticals + fallback**, Next production build,
  `sites/tests/design_guard.mjs` **30/30 καθαρά** σε desktop/mobile και χωρίς third-party requests.
- Τα customer sites παραμένουν tracker-free. **Δεν βάζουμε cookie banner** όσο δεν υπάρχουν
  μη αναγκαία cookies/analytics.

### Επόμενες εργασίες — να μη γίνουν διπλά

1. Μαζεύουμε πραγματικό feedback από τους 5 pilot χρήστες και διορθώνουμε μόνο επαναλαμβανόμενα προβλήματα.
2. Stripe: παραμένει test mode μέχρι τελικό checkout/refund/webhook production test.
3. Meta: business verification → access verification → App Review → test Page/IG dry-run → test post.
4. Domains: χειροκίνητη αγορά μέχρι να δοθούν registrar/reseller credentials και public API access.
5. Google Business Profile: concierge verification στην αρχή· automation μόνο μετά από GBP API approval.
6. Vertical demos: χρησιμοποιούμε το `docs/21-VERTICAL-REFERENCE-LIBRARY.md` ως research baseline
   και σχεδιάζουμε πρώτα τη σωστή conversion architecture ανά επάγγελμα, μετά τα themes.

### Νέα vertical demos

- Υπάρχουν πλέον **14 πλήρεις επαγγελματικές οικογένειες** και κάθε εισαγόμενο επάγγελμα
  αντιστοιχίζεται στην καταλληλότερη: ξυλουργός, εστίαση, κομμωτήριο, οδοντίατρος,
  ιατρείο, αισθητική, μασάζ, καφέ/αρτοποιείο, επαγγελματικές υπηρεσίες, τεχνίτες,
  καταλύματα, γυμναστήριο, συνεργείο και παραγωγός. Το `generic` μένει μόνο για άγνωστες
  μελλοντικές κατηγορίες.
- Δημόσιες category pages υπάρχουν για όλες τις οικογένειες, μαζί με τις νέες
  `/gia/xylourgos` και `/gia/odontiatros`.
- `aesthetics` → `/preview/bloom?biz=aesthetics` και `/gia/aisthitiki`.
- `massage` → `/preview/living?biz=massage` και `/gia/masaz`.
- `physician` → `/preview/marble?biz=physician` και `/gia/iatreio`.
- Τα `Bloom`, `Living`, `Marble` παίρνουν πλέον επαγγελματικά labels και CTA από τα business
  data. Δεν επιτρέπονται hard-coded φράσεις τύπου «καλούδια» ή «υλικά» σε άσχετα verticals.
- Το `sites/tests/verticalContent.mjs` επιβεβαιώνει ότι και τα 14 demos έχουν πλήρες κείμενο,
  τουλάχιστον 4 υπηρεσίες, 3 εικόνες και 2 story paragraphs, καθώς και σωστό CTA ανά vertical.
- Τελευταίο QA: design engine **88/88**, vertical profiles **14/14**, vertical content **14/14**,
  Next production build και browser design guard **30/30** χωρίς προβλήματα αντίθεσης,
  missing fonts, broken images, trackers ή cookies.
- Classification regression 2026-08-06: το «νυχάδικο» έπεφτε λανθασμένα στο `trade` και
  πρότεινε τεχνικά templates. Πλέον `νυχάδικο`, `nail salon`, `μανικιούρ` και `πεντικιούρ`
  ταξινομούνται ως `beauty`, με `runway` πρώτο. Άγνωστο επάγγελμα πέφτει σε ουδέτερο
  `professional` και μπορεί να ταξινομηθεί από AI fallback, ποτέ αυθαίρετα ως τεχνίτης.
- Root cause fix: το onboarding πλέον αποθηκεύει `description`, `style` και `website` στο
  `site_content`. Πριν, το background build τα έβλεπε αλλά το μεταγενέστερο `/designs` τα έχανε
  και διάβαζε μόνο `business_type="Άλλο"`. Το υπάρχον test record `maria` διορθώθηκε στη βάση
  και επαληθεύτηκε ως `beauty` με σειρά `runway`, `type-gallery`, `living`, `cinematic`.

Μην ξαναχτίσεις chooser, 12-design recommendation, vertical matching, no-photo mode ή compliance
documents. Υπάρχουν ήδη και έχουν περάσει QA.

## 🟢 DESIGN SYSTEM + ΚΟΥΤΡΑΚΗΣ E2E (2026-08-06)

- Ο production chooser δίνει πλέον **12 δομικά διαφορετικές επιλογές** ανά επάγγελμα:
  `canvas`, `runway`, `grid`, `cinematic`, `type-gallery`, `quiet`, `kinetic`, `infinite`,
  `living`, `forge`, `editorial`, `magazine` για το demo ξυλουργού, με διαφορετική κατάταξη
  για κάθε άλλο vertical.
- Vertical matching καλύπτει όλες τις επαγγελματικές οικογένειες και έχει generic fallback.
  Κανόνες: `docs/18-VERTICAL-DESIGN-INTELLIGENCE.md` και `sites/lib/verticalProfiles.js`.
- Πρώτο πραγματικό E2E fixture: **Κουτράκης Κουζίνες**, Γέρακας 15344, Αθήνα/Αττική,
  `6956 297670`, domain `koutrakiskouzines.gr`.
- Οι React previews χρησιμοποιούν πλέον αποκλειστικά τις πραγματικές φωτογραφίες στο
  `sites/public/clients/koutrakis/` (μηδέν Unsplash για `biz=carpenter`).
- Local chooser: `http://127.0.0.1:3600/choose/demo-carpenter`.
- QA: Next production build πράσινο, backend design harness 88/88, 12/12 previews HTTP 200,
  desktop/mobile visual inspection σε πραγματικές φωτογραφίες ολοκληρωμένο.
- Τελική επιλογή owner: **`canvas`**. Το live endpoint επιβεβαιώθηκε ότι επιστρέφει
  `layout: canvas` και το `https://koutrakiskouzines.gr` είναι ήδη ενεργό με SSL/HTTP 200.
- Επόμενο: επιμέρους διαμόρφωση κειμένων/sections πάνω στο live site και συγχρονισμός του
  εμπλουτισμένου local fixture με το client record.

## 🟢 ΝΕΟΤΕΡΗ ΑΠΟΦΑΣΗ (2026-08-06) — SOCIAL ΞΑΝΑ ΕΝΕΡΓΟ

Η παλιότερη οδηγία «έξω τα social» παρακάτω έχει ανακληθεί από τον owner. Χτίζουμε δικό μας
Facebook/Instagram engine, χωρίς Postiz ή τρίτο scheduler.

Ολοκληρώθηκε Social Engine v1:

- approval-first queue και authenticated approve/reject API,
- direct Meta publisher με dry-run,
- retries χωρίς διπλό post όταν πετύχει μόνο ένα δίκτυο,
- Supabase migration `add_social_engine` εφαρμοσμένη,
- RLS ενεργό και audit table `publish_logs`,
- dashboard queue UI,
- `daily_post.py` δημιουργεί draft αντί να δημοσιεύει,
- 5/5 unit tests και Next production build πράσινα.

Επόμενα: Meta App Review → test Page dry-run → Railway Cron → πραγματικό test post. Ads μόνο
σε επόμενο milestone με ξεχωριστή έγκριση και hard budget limits. Λεπτομέρειες:
`docs/18-SOCIAL-ENGINE.md`.

**Meta readiness check 2026-08-06:** local `.env` και Railway έχουν το ίδιο νέο Meta App ID
(όχι το παλιό Consumer `982863081415222`). Το live `/connect/start` κάνει redirect στο
Facebook με `instagram_basic`, `instagram_content_publish`, `pages_show_list`,
`pages_read_engagement`, `pages_manage_posts`. Privacy, terms, data-deletion και API health
επιστρέφουν όλα HTTP 200. Επόμενη ανθρώπινη ενέργεια: login με admin/tester λογαριασμό και
σύνδεση δικής μας test Page + Instagram Business· μετά τρέχουμε dry-run και test post.

## 🟢 LIVE STATUS (2026-07-15) — STAGING, ΟΧΙ δημόσιο launch ακόμα (owner: «ας μην το ανοίξουμε»)

**Ό,τι είναι live τρέχει, αλλά ΔΕΝ έχει ανακοινωθεί· Stripe = TEST mode (μηδέν πραγματικά λεφτά).**
- **Landing:** getvitrina.gr (Cloudflare Pages) — τιμές **€14.99 single plan** (το €49 social έφυγε· posts=Phase 2).
- **Backend:** `devops-production-d563.up.railway.app` (FastAPI, Railway) ✅
- **Sites app:** `sites-production-da56.up.railway.app` (Next, 12 templates + showcase + /choose) ✅
- **Signup flow E2E ΔΟΥΛΕΥΕΙ:** connect.html → `/onboard` → `sites /choose/{id}` (δες 12 designs) →
  select-design → `/create-checkout {plan:site}` → **Stripe checkout URL** ✅ (τεσταρισμένο live).
- **Supabase:** RLS ON σε 9/9 πίνακες ✅. **DNS:** `api.`+`app.getvitrina.gr` CNAMEs → Railway (SSL propagates).
- **MCP/API access (Claude):** Supabase MCP, Stripe MCP, Railway GraphQL API (token σε .env), Cloudflare API.

**ΓΙΑ ΝΑ ΑΝΟΙΞΕΙ ΔΗΜΟΣΙΑ (όταν αποφασίσει ο owner):**
1. Stripe **test → live** (live secret key + live €14.99 price → `.env`/Railway).
2. **Post-payment deploy** — webhook `checkout.session.completed` → ανεβάζει το επιλεγμένο site live
   στο domain του πελάτη (τώρα το select-design ξεκινά deploy μέσω wrangler· θέλει wrangler/CF στο Railway
   ή Cloudflare Direct Upload API). ΤΕΛΕΥΤΑΙΟ τεχνικό κομμάτι.
3. connect.html API/SITES: γύρνα σε `api.`/`app.getvitrina.gr` μόλις ενεργό το SSL.
4. Google login (dashboard, όχι για αγορά).

---

## 🆕 ΝΕΟ MVP SCOPE (2026-07-15 — owner pivot) — ΥΠΕΡΙΣΧΥΕΙ

Ο owner απλοποίησε το MVP:
1. **❌ Έξω τα social** — ΜΟΝΟ website προϊόν προς το παρόν (ΜΗΝ φτιάχνεις social/ads agents).
   Ο social κώδικας μένει dormant, δεν διαγράφεται.
2. **💳 Stripe €14.99/μήνα, ΕΝΑ plan** ("site"). Έγινε: `cfg.STRIPE_PRICE_SITE`, `_PRICE_BY_PLAN["site"]`,
   `CheckoutRequest.plan` default = "site". **TODO owner:** φτιάξε το Price (€14.99/μήνα recurring) στο
   Stripe Dashboard → βάλε το id ως `STRIPE_PRICE_SITE` σε `.env`/Railway.
3. **🌐 Domain auto-purchase (Papaki)** στο signup — κώδικας υπάρχει (`src/domain.py`, `registrars.py`,
   `/domain/create-checkout` €24/έτος). **TODO owner:** Papaki reseller creds (`PAPAKI_*`).
4. **🔒 GDPR compliance** — τα customer sites είναι tracker-free, άρα **χωρίς cookie banner**.
   Υπάρχουν σαφές privacy, data-deletion (`web/data-deletion.html`) και ρητή αποδοχή για uploads.
5. **📷 Φωτο** — ο πελάτης ανεβάζει (`/clients/{id}/upload` + Supabase Storage υπάρχει)· αν δεν έχει,
   fallback σε **licensed stock** (Unsplash License = free commercial, GDPR-safe). Ο generator ήδη
   βάζει Unsplash fallback ανά επάγγελμα — κράτα ΜΟΝΟ properly-licensed πηγές.

⚠️ **✅ BACKEND LIVE (2026-07-15):** Railway paid → `devops` **Online** στο
   `https://devops-production-d563.up.railway.app`. E2E confirmed live: onboard→7 designs→Supabase→/designs.
   Fix που έγινε: `get_clients_by_email` ζητούσε ανύπαρκτη στήλη `selected_layout`. Owner: «όλα με Railway».
   (Παλιό blocker text↓ ξεπερασμένο)
   ~~Railway trial expired → OFFLINE~~. Χρειάζεται
   Railway Hobby (~€5/μ) ή migration (Render/Fly free). Χωρίς αυτό, τίποτα live. Πρόταση: sites→Vercel (free),
   backend→Railway €5 ή Render free.

### 🔮 PHASE 2 (μετά το website-only MVP) — σημειωμένο

**Social / καθημερινά posts** (owner: «θα τα βάλουμε σε β φάση»):
- Ως **upsell / ανώτερο tier** (π.χ. €29-39/μ site+posts) — ΟΧΙ στο €14.99 MVP.
- Στο landing εμφανίζονται μόνο ως «🔜 Φάση 2» — ΜΗΝ τα υπόσχεσαι σαν διαθέσιμα.

**Facebook/Instagram auth — ΤΟ ΕΠΙΣΗΜΟ ΜΟΝΤΕΛΟ (owner ρώτησε «με ποιανού creds;»):**
- ΟΥΤΕ δικά σου creds, ΟΥΤΕ ο κωδικός του πελάτη. Μοντέλο: **1 δική σου Meta App «Vitrina»
  (περνάει Meta App Review μία φορά) + κάθε πελάτης OAuth («Σύνδεση με Facebook») με τα ΔΙΚΑ ΤΟΥ
  → Page Access Token ΤΗΣ ΣΕΛΙΔΑΣ ΤΟΥ → ποστάρεις εκ μέρους του.**
- Ποτέ κωδικός — μόνο OAuth token, ανακαλείται όποτε θέλει. IG: Business/Creator συνδεδεμένο με τη Σελίδα.
- Tokens: long-lived Page tokens (~60μ) + refresh.
- **Ήδη σκαρωμένο:** `src/meta_oauth.py`, `skills/meta-publisher/`, `docs/12-META-APP-REVIEW.md`.
- **Μένει Phase 2:** (1) ολοκλήρωση Meta App Review (test account + screencast), (2) σύνδεση posting
  με το React dashboard, (3) `daily_post.py` scheduler ανά πελάτη.

**💬 AI Chat Editor («μίλα στο site σου» — Lovable-style):**
- Ο πελάτης γράφει «βάλε το μενού πάνω / πιο ζεστά χρώματα / γράψε κείμενο για το about» → LLM ερμηνεύει
  + γυρνά την αλλαγή (JSON patch στα site-data / νέο copy). Το template κάνει το render (0 extra).
- **Κόστος:** Haiku ~€0,01/μήνυμα → ολόκληρο setup ~€0,15-0,20· ένας πελάτης <€1/μήνα σε AI (αμελητέο
  στα €14.99). Sonnet ~3x αν θες καλύτερη κατανόηση.
- **Guardrails (υποχρεωτικά):** rate-limit/όριο μηνυμάτων ανά πελάτη, στέλνε **structured data όχι όλο το
  HTML** στο prompt, **ΟΧΙ** AI image-gen (ακριβό — μόνο φωτο πελάτη/stock).
- **Πλοκάρισμα:** endpoint `POST /clients/{id}/chat-edit {message}` → επιστρέφει updated site-data →
  dashboard/preview κάνει re-render. Δίνει «ongoing value» = λόγος να μείνει (retention).
- Χρειάζεται valid `ANTHROPIC_API_KEY`. Καλός υποψήφιος για γρήγορο differentiator μετά το core MVP.

**🗺️ Google Business Profile (GBP) — Phase 2 managed service (owner ιδέα):**
- GBP = **ο #1 παράγοντας local SEO** (πιο σημαντικό κι απ' το site — relevance/distance/prominence).
- Δημιουργία/επαλήθευση: **concierge** (η Google επαληθεύει το φυσικό μαγαζί — δεν αυτοματοποιείται 100%).
- Διαχείριση: **Google Business Profile API** + OAuth πελάτη (ίδιο μοντέλο με Facebook) → GBP posts, ώρες,
  φωτο, κατηγορίες, reviews. Θέλει **έγκριση πρόσβασης στο GBP API** (σαν Meta review).
- Ισχυρό upsell + συνδέεται με τα posts (Google + Facebook + Instagram μαζί).

**🔍 SEO για τα sites — best practices 2026 (εφαρμογή):**
- ✅ **ΕΓΙΝΕ:** JSON-LD LocalBusiness schema (`sites/lib/seo.js` → schemaType ανά επάγγελμα +
  buildJsonLd), Open Graph + keywords (buildMetadata), `robots.js` (index /site, όχι /preview),
  semantic HTML + fluid responsive + Next SSR/ISR (Core Web Vitals).
- **TODO SEO:** NAP consistency (ίδιο Name/Address/Phone παντού), **reviews** (κρίσιμα — πρόσθεσε
  testimonials/GBP reviews), τοπικά keywords στο copy (trade+city — ήδη στο normalize), per-domain
  sitemap.xml, GBP (πάνω).

---

## ✅ LAUNCH CHECKLIST (τι μένει για live MVP) — 2026-07-15

**🔑 Owner (accounts/clicks):**
- [x] ✅ **`sites/` LIVE (2026-07-15, το έκανε ο Claude 100% μέσω Railway API):**
      **https://sites-production-da56.up.railway.app** — showcase + 12 templates ζωντανά.
      Service `sites` `80f0b283-2f6d-4fd6-be04-065af6d83590`, root=`sites`,
      `NEXT_PUBLIC_API_BASE`=backend URL, deployment trigger (auto-deploy on push to main) ✓.
      **Bug που βρέθηκε από το deploy:** το middleware περνούσε το `*.up.railway.app` για custom
      domain πελάτη → rewrite του `/` στο tenant route (showcase έδειχνε «δεν είναι διαθέσιμο»).
      Fix: `sites/middleware.js` APP_HOSTS + robots/sitemap internal. Επαληθεύτηκε live ✓.
      ⚠️ **Railway API μάθημα:** `serviceInstanceDeployV2` ξαναχτίζει το ΙΔΙΟ commit — δώσε
      `commitSha:` για latest, ή φτιάξε `deploymentTriggerCreate` για auto-deploy.
- [ ] Deploy `dashboard/` (Vite) στο Railway → root `dashboard`, envs `VITE_API_BASE`, `VITE_SITES_BASE`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`
- [x] ✅ **Stripe DONE (2026-07-15, από Claude μέσω Stripe MCP):** Product `prod_UtFfvLvry7GeQK`
      («Vitrina — Website») + Price **`price_1TtT9wCXhuChnUHdbjsfPojq`** = €14.99/μήνα EUR recurring
      (**test mode**). Μπήκε σε local `.env` + **Railway** (`variableUpsert` via API).
      **LIVE TESTED:** onboard → `POST /create-checkout {plan:"site"}` → επέστρεψε έγκυρο
      `checkout.stripe.com` URL ✅. ⚠️ Για πραγματικά λεφτά: φτιάξε το ίδιο Price σε **live mode**
      και άλλαξε `STRIPE_SECRET_KEY` + `STRIPE_PRICE_SITE` σε live τιμές.
- [x] ✅ **RLS DONE (2026-07-15):** ενεργοποιήθηκε σε όλους τους 9 πίνακες μέσω Supabase MCP·
      backend επιβεβαιώθηκε ότι δουλεύει (service_role bypass) με read+write+background tests.
- [x] ✅ **MCP/API access (2026-07-15):** Supabase MCP ✓, Stripe MCP ✓, Railway API (token στο .env,
      `Authorization: Bearer`, endpoint `backboard.railway.com/graphql/v2`· project `2c75c49e-…`,
      service `devops` `7f3c7476-…`, env `cd172187-…`) ✓, Cloudflare API (`CF_API_TOKEN`) ✓.
- [ ] Supabase → Auth → enable **Google** (+ redirect URLs) → dashboard login
- [ ] Cloudflare DNS: `api.getvitrina.gr`→backend, `app.getvitrina.gr`→sites
- [ ] Papaki reseller creds (`PAPAKI_*`) → auto-domain (ή χειροκίνητα οι πρώτοι)

**💻 Code (Claude):**
- [x] **GDPR ανάλυση (2026-07-15):** ❌ **ΔΕΝ χρειάζεται cookie banner** — τα sites δεν βάζουν cookies
      ούτε tracking (banner απαιτείται μόνο για μη-απαραίτητα cookies· άσκοπο banner = χαμένο conversion).
      ⚠️ **ΤΟ ΠΡΑΓΜΑΤΙΚΟ ΘΕΜΑ:** **Google Fonts από CDN** → η IP του επισκέπτη πάει στην Google
      (γερμανική νομολογία = παραβίαση GDPR). **FIX:** self-host fonts με `next/font/google` στο
      `sites/app/layout.jsx` (αντί για `<link>`) → εκθέτει CSS vars· μετά sed στα 12 `*.module.css`:
      `'Fraunces'`→`var(--font-fraunces)`, `'Inter'`→`var(--font-inter)`, `'JetBrains Mono'`→`var(--font-mono)`,
      `'Nunito Sans'`→`var(--font-nunito)`. ⚠️ Πρόσεξε τα `subsets` (αν λείπει `greek` → fallback· τσέκαρε
      ανά font πριν build). ΑΝ αργότερα μπει analytics → ΤΟΤΕ χρειάζεται consent banner.
      Υπάρχουν ήδη: `web/privacy.html`, `web/terms.html`, `web/data-deletion.html`.
- [x] **RLS SQL έτοιμο** → `db/rls_policies.sql` (καλύπτει clients/brand_profiles/sites/client_assets/
      social_accounts/posts/subscriptions/domains/domain_orders). **Owner: τρέξ' το στο Supabase SQL Editor.**
      ⚠️ ΠΡΙΝ: βεβαιώσου ότι Railway `SUPABASE_KEY` = **service_role** JWT, αλλιώς σπάει το backend.
      Μετά: `curl .../clients/lookup?email=test@x.gr` → πρέπει 200.
- [ ] Public signup flow: getvitrina.gr → `/onboard` → dashboard/preview end-to-end
- [ ] (optional) Templates 12→15

**🔌 MCP servers (για ευκολότερο troubleshooting) — προσθέτει ο owner σε INTERACTIVE Claude Code (`claude mcp add`/`/mcp`, όχι εδώ):**
- **Supabase MCP** ⭐ (SQL/migrations/logs/tables — θα έτρεχα RLS+migrations μόνος μου). π.χ.
  `claude mcp add supabase -- npx -y @supabase/mcp-server-supabase@latest --access-token <PAT>`
- **Railway MCP** ⭐ (deploy logs + env + status — instant debugging). **Cloudflare MCP** (DNS/Pages).
- ⚠️ prod access → scoped/read-only tokens όπου γίνεται.

**🤖 LLM ΑΠΟΦΑΣΗ:** chat editor + copy = **Claude Haiku**. DeepSeek **απορρίφθηκε** (GDPR: κινεζικοί
servers για EU customer data + μικρή πτώση ελληνικής ποιότητας· το κόστος είναι ήδη ψίχουλα, ~€0,01/μήνυμα).

---

## 🌐 DOMAIN ΣΤΡΑΤΗΓΙΚΗ (owner decision 2026-07-15) — «ο καθένας το δικό του domain»

**ΟΧΙ free subdomains (getvitrina.gr) — κάθε πελάτης ΔΙΚΟ ΤΟΥ domain.**

- **📌 ΓΙΑ ΜΕΤΑ — Cloudflare for SaaS (Custom Hostnames):** ο σωστός scalable τρόπος για «πολλά
  domains πελατών → μία app». Πελάτης βάζει 1 CNAME → CF auto-SSL ανά hostname → route στο origin.
  Αυτοματοποιείται 100% via CF API (Custom Hostnames endpoint). Αποφεύγει ξεχωριστά zones +
  nameserver αλλαγές (ό,τι κάναμε για Κουτράκη ΔΕΝ κλιμακώνεται) + Railway domain limit.
  ⚠️ Θέλει ενεργοποίηση Cloudflare for SaaS (add-on ~$0.10/hostname/μήνα μετά τα δωρεάν).
  Fallback origin: το sites Railway service. **ΝΑ ΣΤΗΘΕΙ όταν αποφασίσει ο owner.**
- **ΤΩΡΑ — Papaki reseller** (για να πουλάμε .gr domains σε πελάτες χωρίς domain): κώδικας υπάρχει
  (`src/domain.py`, `src/registrars.py`, `/domain/suggest|check|create-checkout`). Θέλει: εγγραφή
  **Papaki Reseller** (Simple → search API· Gold → auto-registration), API key από reseller panel.
  Domain search (availability) = Simple Reseller· αγορά = Gold Reseller. API: github.com/papakigr/GoldResellers-JsonApi.
- **Κουτράκης (one-off):** έφερε δικό του domain → στήθηκε με ξεχωριστό CF zone + NS change (χειροκίνητο).

---

## ▶▶ MASTER HANDOFF / ΠΛΑΝΟ (2026-07-10) — διάβασε πρώτα αυτό

### Τι είναι το προϊόν
Vitrina = «**Amboras/Lovable για ελληνικά τοπικά μαγαζιά**»: ο πελάτης μπαίνει, βλέπει **πολλά όμορφα
responsive designs**, διαλέγει, και το site ανεβαίνει live + καθημερινά social posts (€49/μήνα).

### 🏗️ Αρχιτεκτονική (3 κομμάτια)
1. **Backend API** (`src/`, FastAPI) — **Online στο Railway** (service `devops`, project `fulfilling-smile`).
   Supabase DB. Endpoints: onboard, designs/preview/select-design, **site-data (JSON)**, lookup, domain, stripe.
2. **React sites** (`sites/`, Next.js 14) — **Η ΚΥΡΙΑ ΚΑΤΕΥΘΥΝΣΗ** (owner decision). Multi-tenant:
   `/site/[client]` → fetch `site-data` → render React template. Demo switcher στο `/`.
3. **React dashboard** (`dashboard/`, Vite) — Google login, ο πελάτης βλέπει/διαλέγει designs.

### ✅ Τι έχει γίνει
- **12 δομικά διαφορετικά React templates** στο `sites/lib/templates/`: **Editorial, Split, Showcase,
  Bento, Longform, Corporate, Poster, Sidebar, Grid, Coast, Magazine, Warmth** (όχι recolors — διαφορετική
  δομή). Approved από owner. Όλα στο `index.js` (TEMPLATES/TEMPLATE_KEYS/TEMPLATE_META/MAP).
- **6 demo businesses** (`sites/lib/demoData.js`): carpenter/taverna/salon/dentist/cafe/lawyer. Showcase
  δείχνει διαφορετικό επάγγελμα ανά design. `/preview/[template]?biz=`.
- **Dashboard preview → React sites** (`dashboard/src/lib/api.js` previewUrl = `SITES_BASE/site/[id]?layout=`).
- `sites/` build OK (Next 14.2.35). Τοπικά: `cd sites && npm install && npm run dev` → :3000.
- Backend `GET /clients/{id}/site-data` επιστρέφει normalized JSON (name/services[]/gallery[]/story[]).
- Παλιός static engine (`src/premium_generator.py`, 7 HTML templates) = preview/fallback, tests 87/87+7/7.
- Railway Online (11 env vars). Supabase project `vitrina` (ήταν paused→Resumed). Push σε `Angelos3030/devops` main.

### 🎯 ΠΛΑΝΟ — τι ακολουθεί (με σειρά)
1. **[templates] Φτάσε 12-15 React templates** (τώρα **10** ✅). Απομένουν distinct ιδέες: **Magazine**
   (masthead/multi-column), **Warmth** (hospitality menu-style/ταβέρνες), **Estate** (real-estate/interiors),
   **Retro**, **Mono/Terminal**. **ΒΗΜΑΤΑ για νέο template:** (a) copy π.χ. `Coast.jsx`+`Coast.module.css`
   σε νέο όνομα, (b) άλλαξε ΔΟΜΗ+CSS (όχι μόνο χρώμα), (c) πρόσθεσε στο `sites/lib/templates/index.js`
   και στα 4 σημεία (TEMPLATES, TEMPLATE_KEYS, TEMPLATE_META, MAP), (d) `cd sites && npm run build` (πρέπει
   ✓ Compiled), (e) `npm run start` → :3000 δες το switcher, (f) commit+push. Data prop shape:
   `d.NAME,CITY,TRADE,TAGLINE,PHONE,PHONE_INTL,AREAS,HOURS,KICKER,HERO_WORD,INITIAL,YEAR,STORY_TITLE,CTA_TITLE,
   HERO_IMAGE,STORY_IMAGE, d.services[{num,title,desc}], d.gallery[{image,title,sub}], d.story[{p}]`.
2. **[domain routing] ✅ DONE** — `sites/middleware.js` (custom host → `/site/[host]`) + backend
   `db.get_client_by_domain` + `_intake_from_db` resolve-by-domain. Θέλει: πραγματικός πελάτης με
   εγγραφή στον `domains` πίνακα + DNS του domain → Vercel/Cloudflare για να δουλέψει live.
2b. **[showcase] ✅ DONE** — `sites/app/page.jsx` = marketing landing (Amboras-style) που δείχνει
   curated designs (iframe cards → `/preview/[template]`). Τα `/preview/[template]` prerendered (SSG,
   ads/SEO-ready). ΓΙΑ ΔΙΑΦΗΜΙΣΕΙΣ: χρησιμοποίησε αυτή τη σελίδα + τα preview links.
3. **[deploy sites]** Cloudflare Pages ή Vercel το `sites/` (χρειάζεται Node runtime για dynamic/middleware
   → Vercel πιο εύκολο, ή Cloudflare `@cloudflare/next-on-pages`). Σύνδεσε custom domains πελατών.
4. **[dashboard link]** Το `dashboard/` «Επιλογή» να ανοίγει το React preview (`sites/site/[id]?layout=`), όχι το παλιό.
5. **[Supabase Google]** enable Google provider (Auth→Providers) + `dashboard/.env` για να δουλέψει το login.
6. **[api.getvitrina.gr]** Railway custom domain + Cloudflare CNAME. Railway trial credit low → πρόσθεσε κάρτα.
7. **[AI copy, optional]** valid `ANTHROPIC_API_KEY` → `src/site_copy.py` γράφει κείμενο ανά πελάτη (τώρα no-op fallback).

### ⚙️ Πώς τρέχεις τι
- Backend: `cd src`… `uvicorn src.main:app` (ή Railway). Tests: `python -m scripts.test_design_engine` (offline),
  `python -m scripts.smoke_design_live` (live Supabase, θέλει δίκτυο).
- React sites: `cd sites && npm run dev` → :3000 (demo switcher). Build: `npm run build`.
- Dashboard: `cd dashboard && npm run dev` → :5173.

### 🔑 Κρίσιμες αποφάσεις/κανόνες
- **React για generated sites** (τελική απόφαση owner) + για dashboard. Static engine μένει fallback.
- Templates πρέπει να είναι **δομικά διαφορετικά** («όχι ίδια με άλλα χρώματα») + **γαμάτα/responsive** (Lovable/Avada bar).
- Secrets ΜΟΝΟ σε `.env` (gitignored). Ο owner έβαλε Supabase keys σε chat μια φορά → να γίνουν rotate.
- Supabase free tier παγώνει μετά ~1 βδομάδα → Resume από dashboard.

---

**Τελευταία ενημέρωση:** 2026-07-10
**🚀 PIVOT σε React sites (2026-07-10):** Owner decision — τα generated sites γίνονται **React/Next**
   (όχι static HTML) γιατί τα HTML templates «έμοιαζαν ίδια με άλλα χρώματα». Νέο `sites/` = Next.js 14
   multi-tenant app: `GET /clients/{id}/site-data` (normalized JSON, στο `meta_oauth.py` + `db.get_client`
   + `_intake_from_db`) → `/site/[client]` dynamic route (ISR/SEO) renders React template. **3 δομικά
   ΔΙΑΦΟΡΕΤΙΚΑ archetypes** (όχι recolors): `Editorial` (stacked), `Split` (fixed sidebar), `Showcase`
   (full-bleed gallery-forward) στο `sites/lib/templates/`. Demo switcher στο `/`. `npm run build` OK
   (next 14.2.35 patched). Τοπικά: `cd sites && npm run dev` → :3000. ΣΤΟΧΟΣ: 10-15 distinct templates.
   Επόμενο: domain→client middleware, port περισσότερων archetypes, deploy (Cloudflare/Vercel).
   Ο static engine (7 HTML templates) μένει ως preview/fallback.
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
**➕ 4ο design «bold» + δυναμικό N-designs (2026-07-10):** προστέθηκε `bold.tpl.html` (vibrant,
   για beauty/μοντέρνα brands) → `LAYOUTS` = studio/commerce/atelier/bold. Το dashboard + `web/preview.html`
   δείχνουν πλέον **ΟΣΑ variants γυρίζει το API** (recommended πρώτο), όχι hardcoded — «πολλά designs να
   επιλέγει» (Amboras-style). Προσθήκη νέου template = μόνο backend (0 frontend αλλαγές). Tests: offline
   57/57 + live 7/7 (4 variants). Επόμενο extensibility: A/B (πολλά live, κρατάμε το καλύτερο).
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
### Privacy / trackers (06 Αυγούστου 2026)
- Τα customer sites έχουν self-hosted fonts, click-to-load map, κανένα analytics,
  κανένα Meta Pixel και κανένα cookie. Γι' αυτό **δεν εμφανίζουν consent banner**.
- Το global `CookieConsent` αφαιρέθηκε σκόπιμα: banner χωρίς optional trackers
  κόβει conversion και δεν προσφέρει νομικό όφελος.
- Κανένας agent δεν προσθέτει Pixel/Analytics/third-party embed στα customer sites.
- Αν προστεθεί προαιρετικό tracking μόνο στη Vitrina, απαιτεί ξεχωριστό consent
  gate πριν φορτωθεί το script, ισότιμη απόρριψη και ενημέρωση της privacy policy.
- Το `sites/tests/design_guard.mjs` παραμένει το τεχνικό quality gate: μηδενικά
  cookies και μηδενικά αιτήματα προς Google/Meta στα sites πελατών.
- Πλήρες pre-launch compliance gate: `docs/19-COMPLIANCE-LAUNCH.md`.
- Προστέθηκαν drafts DPA, subprocessor register και incident runbook στο `legal/`.
- Προστέθηκε δημόσια πολιτική ακυρώσεων/επιστροφών και ρητή αποδοχή recurring
  συνδρομής πριν από Stripe checkout.
- **BLOCKER:** πριν από πελάτες/χρεώσεις χρειάζονται νόμιμη επωνυμία, ΑΦΜ, έδρα,
  Business Verification/Access Verification και τελικός έλεγχος νομικού/λογιστή.

### Pilot 5 φίλων (06 Αυγούστου 2026)
- Τα 9 νέα designs είναι live στο Railway selector και ελέγχθηκαν ένα-ένα ως παρόντα.
- Landing, onboarding και API απαντούν 200. Το `app.getvitrina.gr` έχει ακόμη SSL issue.
- Ο owner θα δώσει το onboarding σε 5 φίλους για ανεξάρτητο mobile test, χωρίς χρέωση.
- Pilot mode υλοποιήθηκε: `connect.html?pilot=1` περνά στο selector, αποθηκεύει το
  design και ανοίγει προσωρινό Railway preview χωρίς domain ή Stripe.
- Πλήρες script, πίνακας feedback, blockers και Google plan:
  `docs/20-PILOT-5-FRIENDS.md`.

Κάθε φορά που σταματάς δουλειά: **ενημέρωσε αυτό το αρχείο** —
τι έγινε, πού σταμάτησες, τι ακολουθεί. Έτσι όποιος συνεχίσει (άλλο account/session)
ξέρει ακριβώς από πού να πιάσει.
