# Vitrina Agent Ecosystem

> Product thesis: η Vitrina δεν είναι website builder. Είναι ένα approval-first,
> vertical-aware AI operating system που αναλαμβάνει επαναλαμβανόμενη digital-agency
> εργασία για μικρές επιχειρήσεις και αποδεικνύει την αξία της με leads, κρατήσεις,
> κριτικές και έσοδα.

## 1. Η στρατηγική απόφαση

Οι μεγάλοι builders έχουν ήδη site generation, CRM, SEO, analytics και marketing tools.
Το moat της Vitrina δεν είναι ο αριθμός των agents. Είναι ο κλειστός κύκλος:

`observe -> diagnose -> propose -> approve -> execute -> verify -> measure -> learn`

Κάθε agent πρέπει να έχει business KPI, σαφή όρια αυτονομίας και audit trail. Αν ένα βήμα
είναι deterministic (publish API, DNS check, schema validation), γίνεται με κανονικό κώδικα.
LLM χρησιμοποιείται μόνο για κρίση, σύνθεση, ταξινόμηση ή δημιουργία.

### Επίπεδα αυτονομίας

- **A0 — Advisory:** αναφορά/πρόταση μόνο.
- **A1 — Draft:** δημιουργεί draft, πάντα approval πριν την εκτέλεση.
- **A2 — Guarded:** εκτελεί χαμηλού ρίσκου ενέργειες μέσα σε policies και αναστρέψιμα όρια.
- **A3 — Autonomous:** προγραμματισμένη λειτουργία, monitoring, retries και rollback.

Ποτέ A3 για ad spend, νομικές δηλώσεις, δημόσιες απαντήσεις σε κρίση, αλλαγή τιμών,
refunds, domain transfer ή διαγραφή δεδομένων.

## 2. Core agents

| Agent | Αποστολή | Trigger | Input -> Output | APIs | Auto / Approval | Value | Difficulty | MVP -> Future |
|---|---|---|---|---|---|---|---|---|
| **Brand Agent** | Δημιουργεί brand system και φωνή | onboarding ή rebrand | intake, φωτογραφίες, κλάδος -> brand profile, logo directions, palette, type, voice | image generation, asset storage | A1 / ναι | High | M | 3 brand routes -> πλήρες adaptive brand governance |
| **Theme Builder Agent** | Μετατρέπει references σε reusable Vitrina themes | νέο structural use case | URLs/screenshots/spec -> responsive theme + tokens + tests | browser, image analysis, repo | A1 / internal review | High | H | spec-first theme -> component synthesis και automated visual diff |
| **Website Generator Agent** | Δημιουργεί πλήρες vertical-aware site | νέο onboarding/approved redesign | brand, services, assets, locality -> ranked sites | content model, image, storage | A1 / ναι | Very High | H | curated templates -> compositional generation με constraints |
| **Website QA Agent** | Αποδεικνύει ότι το site λειτουργεί | κάθε preview/deploy | URL/build -> screenshots, failures, pass/fail report | Playwright, Lighthouse | A3 / όχι για tests | Very High | M | responsive/forms/links -> visual regression + conversion journey tests |
| **SEO Agent** | Βελτιστοποιεί technical και on-page SEO | deploy + monthly audit | pages, services, location -> metadata/schema/headings/alts | Search Console, PageSpeed | A2 / approval για νέο copy | High | M | rules + report -> continuous opportunity queue |
| **Social Media Agent** | Παράγει και προγραμματίζει channel-native content | calendar/offer/event | brand, assets, calendar -> post/creative/schedule | Meta, TikTok, LinkedIn, GBP | A1/A2 / configurable | High recurring | H | FB/IG drafts -> multi-channel learning calendar |
| **Competitor Agent** | Βρίσκει gaps και winning patterns | onboarding + quarterly | competitors, SERPs, reviews -> gap map and actions | search, browser, SEO data | A0 / όχι | High | M | manual URLs -> local market graph |
| **Review Intelligence Agent** | Μετατρέπει reviews σε product/marketing insight | new reviews + monthly | reviews -> themes, FAQ, landing ideas, service issues | Google, Meta, TripAdvisor | A0 / όχι | High recurring | M | sentiment/themes -> root-cause and revenue correlation |
| **Ads Agent** | Προτείνει και βελτιστοποιεί paid campaigns | campaign request or proven organic winner | goal, audience, offer, budget -> campaign drafts | Meta Marketing, Google Ads | A1 / πάντα για launch/spend | Very High | H | drafts only -> guarded optimization with hard caps |
| **Analytics Agent** | Εξηγεί τι άλλαξε και τι πρέπει να γίνει | weekly/monthly/anomaly | GA4, GSC, calls, forms -> plain-Greek diagnosis | GA4, GSC, Clarity/PostHog | A0 | Very High recurring | H | weekly report -> causal experiments and forecasting |
| **Accessibility Agent** | Ελέγχει και διορθώνει WCAG θέματα | deploy/theme change | DOM/CSS/content -> violations and patches | axe, Playwright | A2 for safe fixes | Medium/High | M | automated audit -> assistive-tech journeys |
| **Performance Agent** | Προστατεύει Core Web Vitals | deploy + field regression | traces/assets/CWV -> optimized code/assets | PageSpeed, CrUX, browser | A2 / review for structural changes | High | H | image/cache audit -> autonomous budgets and rollback |
| **Content Agent** | Δημιουργεί χρήσιμο conversion/local content | approved plan, season, SEO gap | brand, expertise, keywords -> pages/blogs/FAQ | CMS, GSC, search | A1 / ναι | High recurring | M | service pages -> topic authority engine |
| **Booking Agent** | Ελέγχει και διαχειρίζεται booking journeys | deployment + synthetic schedule | slots/forms/email/CRM -> booking test/result | calendar, email, CRM | A2 tests; approval for real booking | High | H | synthetic bookings -> capacity-aware scheduling |
| **Maintenance Agent** | Προλαμβάνει τεχνικές βλάβες | daily/weekly cron | domains, pages, forms -> incident or auto-fix | DNS, SSL, uptime, email | A3 for reversible fixes | High recurring | M | checks/alerts -> self-healing runbooks |
| **Security Agent** | Μειώνει exposure και secret risk | PR/deploy/weekly | code, headers, deps, config -> findings/patches | dependency scanners, CSP, GitHub | A2 / approval for risky fix | Very High | H | headers/secrets/deps -> continuous attack-surface management |

## 3. Differentiating growth and operations agents

Οι παρακάτω agents είναι το σημείο όπου η Vitrina γίνεται agency operating system και όχι
άλλος ένας builder.

| Agent | Αποστολή | Trigger | Input -> Output | APIs | Auto / Approval | Value | Difficulty | MVP -> Future |
|---|---|---|---|---|---|---|---|---|
| **Lead Concierge Agent** | Απαντά άμεσα και συλλέγει qualified lead | form/chat/message | inquiry, services, hours -> answer, qualification, next step | site chat, Meta, WhatsApp/SMS, CRM | A2 within knowledge base / handoff for uncertainty | Very High | H | web leads -> omnichannel 24/7 receptionist |
| **Missed Call Recovery Agent** | Μετατρέπει αναπάντητες κλήσεις σε συζητήσεις | missed call event | caller/time/context -> compliant SMS + callback task | telephony, SMS, CRM | A2 with consent/template | Very High recurring | M | SMS follow-up -> voice concierge and routing |
| **Lead Scoring Agent** | Ιεραρχεί leads με βάση πιθανότητα και αξία | every new lead | source, intent, history -> score, reason, SLA | CRM, analytics, calls | A3 advisory routing | High | M | rules + explainable score -> learned LTV model |
| **Quote & Proposal Agent** | Φτιάχνει γρήγορα συνεπείς προσφορές | qualified lead | scope, price book, terms -> branded quote/draft | CRM, PDF, e-sign, email | A1 / πάντα approval | Very High | M | quote draft -> interactive proposal and deposit |
| **Follow-up Agent** | Δεν αφήνει leads να χαθούν | lead inactivity/SLA | thread, stage, policy -> personalized follow-up | email, SMS, Meta, CRM | A2 with frequency caps | Very High recurring | M | sequences -> channel/time optimization |
| **No-show Prevention Agent** | Μειώνει χαμένες κρατήσεις | appointment approaching | booking, policy, history -> reminders/confirmation | calendar, SMS/email | A3 for approved templates | Very High for bookings | M | reminders -> risk score, deposit recommendation |
| **Reactivation Agent** | Επαναφέρει παλιούς πελάτες | inactivity window/low season | customer history, consent, offer -> segment + campaign | CRM, email/SMS, ads | A1 / campaign approval | Very High recurring | M | win-back drafts -> predicted next-best action |
| **Loyalty & Referral Agent** | Αυξάνει επαναλήψεις και referrals | completed service/milestone | purchase/visit history -> reward/referral ask | POS/CRM, email/SMS | A2 within rules | High recurring | M | referral messages -> dynamic loyalty program |
| **Review Growth Agent** | Ζητά review τη σωστή στιγμή, χωρίς gating | successful transaction | customer, channel, consent -> request + tracking | Google review link, CRM, SMS | A2; strict policy | Very High local | L/M | timed request -> channel optimization |
| **Review Response Agent** | Ετοιμάζει ασφαλείς, αυθεντικές απαντήσεις | new review | review, facts, tone -> reply draft/escalation | Google, Meta, TripAdvisor | A1; A2 only positive low-risk | High recurring | M | drafts -> policy-based auto reply |
| **Local Listings Agent** | Κρατά NAP/hours/services συνεπή παντού | profile change + monthly | canonical profile -> discrepancy report/updates | GBP, Bing, Apple, directories | A1/A2 depending API | High | H | GBP audit -> multi-directory sync |
| **Local Demand Radar Agent** | Εντοπίζει αυξανόμενη ζήτηση πριν τον ανταγωνισμό | weekly | search trends, queries, season, area -> opportunities | Trends, GSC, Ads keyword data | A0 | Very High/differentiating | H | weekly radar -> neighborhood demand forecasting |
| **Seasonal Opportunity Agent** | Μετατρέπει γιορτές/καιρό/events σε έγκαιρες καμπάνιες | calendar/weather/local event | business + capacity + event -> offer/content plan | weather, calendar, local events | A1 | High recurring | M | Greek calendar rules -> predictive campaign planner |
| **Offer Architect Agent** | Σχεδιάζει προσφορά χωρίς να καταστρέφει margin | demand dip/new service | costs, capacity, audience -> offer, economics, CTA | POS/booking/CRM | A1 / πάντα approval | Very High | H | structured suggestions -> elasticity experiments |
| **Conversion Experiment Agent** | Τρέχει ασφαλή A/B tests με μία υπόθεση κάθε φορά | enough traffic + detected issue | analytics, page, hypothesis -> variant/test/result | feature flags, analytics | A1 launch / A2 stop-loss | Very High | H | CTA/headline tests -> Bayesian optimization |
| **Revenue Attribution Agent** | Συνδέει lead με πραγματικό έσοδο | conversion/transaction | source, calls, bookings, payments -> attribution and ROI | GA4, CRM, calls, Stripe/POS | A3 analysis | Very High recurring | H | first-party attribution -> incrementality model |
| **Customer Voice Agent** | Χτίζει ζωντανό knowledge base από πραγματικές συνομιλίες | weekly corpus refresh | calls/chats/emails/reviews -> objections, language, FAQs | CRM, call transcription, email | A0 | High/differentiating | H | theme extraction -> automatic copy evidence layer |
| **Service Quality Agent** | Εντοπίζει λειτουργικά προβλήματα πριν γίνουν reputation issue | repeated complaint/anomaly | reviews, cancellations, tickets -> root cause + task | reviews, CRM, booking | A0/A1 | Very High retention | H | alert and checklist -> closed-loop service recovery |
| **Capacity & Demand Agent** | Ευθυγραμμίζει marketing με διαθέσιμη δυναμικότητα | daily/weekly | bookings, staff, inventory, demand -> slots to promote/pause | booking, POS, calendar | A2 within policy | Very High/differentiating | H | capacity heatmap -> autonomous demand shaping |
| **Menu / Catalog Freshness Agent** | Αποτρέπει παλιές τιμές, λάθος διαθεσιμότητα και stale pages | catalog change/weekly | POS/catalog/site -> mismatch report/update draft | POS, ecommerce, CMS, GBP | A1/A2 | High | M/H | mismatch detection -> real-time omnichannel catalog |
| **Asset Librarian Agent** | Οργανώνει φωτογραφίες και αποδεικνύει δικαιώματα χρήσης | upload/new campaign | media, metadata, consent -> tagged library + best-use suggestions | storage, vision, EXIF | A3 tagging; approval for publish | High labor-saving | M | tags/dedup -> performance-based asset ranking |
| **UGC & Rights Agent** | Εντοπίζει UGC και παίρνει άδεια πριν τη χρήση | mention/tag/new content | post, author, policy -> permission request + rights record | Meta/TikTok, CRM | A1 | High/differentiating | H | permission workflow -> licensed UGC library |
| **Localization & Tourist Agent** | Προσαρμόζει εμπειρία σε επισκέπτες, όχι απλή μετάφραση | tourism vertical/season | Greek source, visitor mix -> localized pages/FAQs | translation, analytics, maps | A1 | High in Greece | M | EN pages -> intent-aware multilingual concierge |
| **GEO / AI Visibility Agent** | Κάνει την επιχείρηση κατανοητή σε AI search/agents | monthly + content change | entity/site/citations -> machine-readable gaps and fixes | search, schema, crawler | A2 safe structured-data fixes | Emerging high | H | entity/schema audit -> agent-readiness benchmark |
| **Compliance & Consent Agent** | Επιβάλλει GDPR/marketing consent/data-retention policies | integration/change/request | data map, consent, vendor -> block/checklist/audit evidence | CMP if needed, DB, email/SMS | A3 policy checks; legal approval for text | Very High risk reduction | H | consent ledger/DSAR workflow -> continuous compliance graph |
| **Crisis & Escalation Agent** | Αναγνωρίζει ευαίσθητες καταστάσεις και σταματά automation | negative spike, threat, medical/legal content | messages/reviews/context -> severity, pause, response brief | reviews, social, alerts | A0; always human response | Very High protection | M | kill switch + alert -> incident command center |
| **Grant & Subsidy Radar Agent** | Βρίσκει σχετικά ελληνικά/ευρωπαϊκά προγράμματα | weekly/profile change | KAD, region, size, goals -> matched opportunities/checklist | gov portals, EU feeds | A0 | High and locally unique | H | curated alerts -> eligibility and application workspace |
| **Client Success Agent** | Προβλέπει churn και δείχνει αξία στον πελάτη | monthly/risk signal | agent outcomes, usage, tickets -> value report and action plan | billing, product analytics, CRM | A2 communication within policy | Very High recurring | H | monthly proof-of-value -> churn prediction and expansion |

## 4. Roadmap

### MVP — από site σε αξιόπιστο managed product

1. Brand, Website Generator, Website QA.
2. SEO, Accessibility, Performance, Security, Maintenance.
3. Content editor με preview/approval και audit log.
4. Lead capture + Lead Concierge (μόνο web), Follow-up drafts.
5. Βασικό Analytics report: traffic, calls/forms, uptime, actions completed.

**North-star:** ενεργό site που παράγει και δεν χάνει leads. Όχι αριθμός generated pages.

### Phase 2 — recurring growth engine

1. Social Media + Asset Librarian + approval queue.
2. Review Growth, Review Intelligence, Review Response.
3. Local Listings, Seasonal Opportunity, Local Demand Radar.
4. Booking tests, No-show Prevention, Lead Scoring, Follow-up.
5. Client Success monthly proof-of-value report.

**North-star:** qualified leads/appointments/reviews ανά πελάτη ανά μήνα.

### Phase 3 — AI digital agency

1. Competitor, Ads, Offer Architect, Conversion Experiment.
2. Revenue Attribution, Reactivation, Loyalty & Referral.
3. Customer Voice, Service Quality, Capacity & Demand.
4. Quote & Proposal, Missed Call Recovery, omnichannel Concierge.
5. GEO/AI Visibility και Localization/Tourist.

**North-star:** attributed incremental revenue και hours of agency work automated.

### Enterprise — multi-location control plane

1. Location graph, role-based approvals και brand governance.
2. Multi-location listings/reputation/catalog sync.
3. Shared campaign policies με local adaptation.
4. Compliance/consent, security posture και SLA dashboards.
5. API/webhooks, white-label partner console, accounting/POS/CRM connectors.

### Future vision — autonomous SMB operator

1. Demand and capacity forecasting.
2. Cross-channel budget allocation within explicit business policies.
3. Agent-ready websites για human και machine customers.
4. Local economic graph: partnerships, demand, talent, grants and suppliers.
5. A persistent digital twin of the business that can simulate an action before execution.

## 5. Agent Orchestrator

Ο Orchestrator δεν είναι ένας ακριβός LLM που «κάνει τα πάντα». Είναι state machine με
event bus, policy engine και specialist workers.

```text
Events / Cron / User request
          |
          v
  Intake + Identity + Consent
          |
          v
  Orchestrator State Machine
   | classify goal and risk
   | fetch canonical business context
   | build dependency DAG
   | enforce plan, budget and permissions
   +-------> deterministic tools (publish, DNS, tests, storage)
   +-------> specialist agents (reason/create/diagnose)
          |
          v
  Approval Gate (when required)
          |
          v
  Executor -> Verifier -> Metrics -> Audit Log -> Memory
```

### Shared contracts

Κάθε task έχει:

```json
{
  "task_id": "uuid",
  "client_id": "uuid",
  "goal": "increase_bookings",
  "trigger": "weekly_analysis",
  "inputs": [{"uri": "business://profile", "version": 12}],
  "risk": "low|medium|high",
  "approval_policy": "none|client|operator|dual",
  "budget": {"money_eur": 0, "tokens": 20000, "deadline_s": 300},
  "idempotency_key": "...",
  "expected_outputs": ["proposal", "evidence", "kpi"],
  "rollback": "action-or-null"
}
```

Κάθε result επιστρέφει `status`, structured `artifacts`, `evidence`, `confidence`,
`actions_taken`, `approval_id`, `cost`, `kpi_before`, `kpi_after` και `next_check_at`.

### Μνήμες

- **Canonical business memory:** verified στοιχεία, υπηρεσίες, τιμές, ωράριο, περιοχές.
- **Brand memory:** voice, visual tokens, forbidden phrases, approved claims.
- **Customer memory:** consented CRM facts και interaction history, με retention policy.
- **Evidence memory:** analytics, reviews, experiments και source timestamps.
- **Operational memory:** incidents, retries, approvals, costs και outcomes.

Τα generated κείμενα δεν γίνονται facts. Μόνο verified canonical data μπορεί να χρησιμοποιηθεί
σε τιμές, ιατρικούς/νομικούς ισχυρισμούς, ωράρια και πολιτικές.

### Routing και συνεργασία

Παράδειγμα «έπεσαν οι κρατήσεις»:

1. Analytics Agent επιβεβαιώνει το anomaly και εντοπίζει page/channel.
2. Booking Agent κάνει synthetic journey και ελέγχει confirmations.
3. Performance/QA ελέγχουν τεχνικό regression.
4. Competitor + Demand Radar ελέγχουν εξωτερική αλλαγή.
5. Offer Architect ή Conversion Experiment δημιουργεί μία τεκμηριωμένη πρόταση.
6. Ο πελάτης εγκρίνει αν υπάρχει δημόσια αλλαγή ή spend.
7. Executor εφαρμόζει, QA επαληθεύει, Attribution μετρά αποτέλεσμα.
8. Client Success βάζει το αποτέλεσμα στο μηνιαίο value report.

## 6. Product and revenue packaging

| Plan | Agents | Λόγος μηνιαίας πληρωμής |
|---|---|---|
| **Presence** | Website, QA, SEO, Accessibility, Performance, Maintenance, Security | Το site μένει γρήγορο, ασφαλές και σωστό |
| **Growth** | + Content, Social, Reviews, Listings, Demand Radar, monthly report | Η παρουσία παράγει συνεχή local visibility |
| **Revenue** | + Concierge, Follow-up, Booking, No-show, Reactivation, Attribution | Η Vitrina αποδεικνύει leads/κρατήσεις/έσοδο |
| **Agency** | + Ads, Experiments, Offer, Competitor, Customer Voice | Συνεχής growth λειτουργία χωρίς agency headcount |
| **Multi-location** | governance, policies, location analytics, integrations | Κεντρικός έλεγχος με τοπική εκτέλεση |

Μην πουλάμε «agents» ή «AI credits». Πουλάμε outcomes και όρια υπηρεσίας: monitored pages,
channels, leads handled, locations, campaigns και response SLA.

## 7. Τι δεν χτίζουμε ακόμα

- 40 ανεξάρτητα chatbots χωρίς κοινό state και metrics.
- Αυτόματο ad spend ή αλλαγή τιμών χωρίς approval.
- Scraping reviews/listings χωρίς επιτρεπτό API και όρους χρήσης.
- Medical/legal claims από μη επαληθευμένο generated content.
- Voice agent πριν είναι άψογα lead capture, consent, handoff και transcript auditing.
- Agents χωρίς deterministic eval, cost ceiling, idempotency και kill switch.

## 8. Η προτεινόμενη επόμενη κίνηση

Μην ξεκινήσουμε χτίζοντας άλλους 30 agents. Χτίζουμε πρώτα τον κοινό πυρήνα:

1. `agent_tasks`, `agent_runs`, `approvals`, `artifacts`, `events`, `kpi_snapshots`.
2. Policy engine για autonomy, permissions, spend και channel rules.
3. Orchestrator με 3 production workflows: **site deploy**, **weekly health**, **lead follow-up**.
4. Unified inbox/action queue στο dashboard: `Needs approval`, `Running`, `Done`, `Value`.
5. Eval suite ανά agent και συνολικό cost/value telemetry ανά πελάτη.

Μόλις αυτά δουλέψουν, κάθε νέος agent γίνεται ασφαλές plug-in στο ίδιο σύστημα αντί για νέο
σκόρπιο feature.
