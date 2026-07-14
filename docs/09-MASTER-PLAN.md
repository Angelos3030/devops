# 09 — MASTER PLAN: Βήμα-Βήμα από το Μηδέν στους Πρώτους Πελάτες

> Ο πλήρης οδηγός εκτέλεσης. Κάνε τα βήματα με τη σειρά. Κάθε βήμα έχει checkbox.
> ✅ Validation: ΟΛΟΚΛΗΡΩΘΗΚΕ (3 μαγαζιά είπαν ναι) → ξεκινάμε από το ΒΗΜΑ 1.

---

## 📋 ΕΠΙΣΚΟΠΗΣΗ ΦΑΣΕΩΝ

```
ΒΗΜΑ 0:  Validation                    ✅ ΕΓΙΝΕ
ΒΗΜΑ 1:  Λογαριασμοί & εργαλεία        (1-2 μέρες)
ΒΗΜΑ 2:  Meta App Review               (ξεκίνα ΤΩΡΑ — 1-3 βδομάδες αναμονή)
ΒΗΜΑ 3:  Skills (γράψε & ανέβασε)      (2-4 μέρες)
ΒΗΜΑ 4:  Agents setup                  (1 μέρα)
ΒΗΜΑ 5:  Φάση 1 — Auto-posting MVP     (1 βδομάδα)
ΒΗΜΑ 6:  Test με 1 πραγματικό μαγαζί   (3-5 μέρες)
ΒΗΜΑ 7:  Φάση 2 — Website (3 επιλογές) (1-2 βδομάδες)
ΒΗΜΑ 8:  Πληρωμές (Stripe)             (2-3 μέρες)
ΒΗΜΑ 9:  Onboard τους 3 πελάτες        (ανά πελάτη)
ΒΗΜΑ 10: Κλίμακα & βελτίωση            (συνεχές)
ΒΗΜΑ 11: Growth add-on — Facebook Ads   (μετά το MVP)
```

---

## ΒΗΜΑ 1 — Λογαριασμοί & εργαλεία (1-2 μέρες)

- [ ] **Anthropic account** → πάρε API key + ζήτα **Managed Agents** access.
- [ ] **Python** εγκατάσταση (3.11+) + `pip install anthropic`.
- [ ] **GitHub repo** για τον κώδικα (private).
- [ ] **Supabase** project (EU region) — DB, auth, storage.
- [ ] **Cloudflare** ή **Netlify** account (για deploy των sites, API token).
- [ ] **Stripe** account (θα μπει αργότερα, στο ΒΗΜΑ 8).
- [ ] Αντέγραψε το `.env.example` → `.env` και βάλε τα κλειδιά που έχεις.

**Έλεγχος:** τρέξε ένα test call στο Claude API → παίρνεις απάντηση = ΟΚ.

---

## ΒΗΜΑ 2 — Meta App Review (ξεκίνα ΤΩΡΑ, τρέχει παράλληλα)

> ⚠️ Το πιο αργό κομμάτι. Ξεκίνα το **πρώτο** γιατί η Meta αργεί να εγκρίνει.

- [ ] **Meta for Developers** account → δημιούργησε **App** (τύπος: Business).
- [ ] Πρόσθεσε **Instagram Graph API** + **Facebook Login** products.
- [ ] Φτιάξε **Privacy Policy** (στα ελληνικά) + φιλοξένησέ την σε URL.
- [ ] Γράψε το **use-case** για το review: «εργαλείο που δημοσιεύει posts εκ μέρους
      επιχειρήσεων στις δικές τους σελίδες, με τη συγκατάθεσή τους».
- [ ] Ετοίμασε **demo video** (πώς ο πελάτης συνδέει τη σελίδα του + ποστάρει).
- [ ] Ζήτα τα permissions: `pages_manage_posts`, `pages_read_engagement`,
      `instagram_basic`, `instagram_content_publish`.
- [ ] **Submit for review** → περίμενε (συνέχισε τα άλλα βήματα στο μεταξύ).

**Σημείωση:** Όσο περιμένεις, μπορείς να δοκιμάζεις με **το δικό σου** test page/IG
(developer mode δουλεύει σε δικούς σου λογαριασμούς χωρίς review).

---

## ΒΗΜΑ 3 — Skills: γράψε & ανέβασε (2-4 μέρες)

- [ ] **Τελειοποίησε τα custom skills** (ήδη υπάρχουν σκελετοί):
  - [ ] `social-post-gr` → βάλε **10-15 πραγματικά καλά posts** (από το concierge).
  - [ ] `brand-builder-gr` → defaults τόνου/χρωμάτων ανά επάγγελμα.
  - [ ] `greek-website` + `PRESETS.md` → όλα τα επαγγέλματα (έτοιμο).
  - [ ] `meta-publisher` → οδηγίες posting.
  - [ ] `local-seo-gr` → SEO (έτοιμο).
  - [x] `conversion-copy-gr` → ελληνικά headlines/CTA/offers για sites (έτοιμο).
  - [x] `facebook-ads-gr` → Growth/Facebook Ads drafts + approval guardrails (έτοιμο).
- [ ] **Συμπλήρωσε `src/upload_skills.py`** με τα πραγματικά Skills API calls
      (beta header `skills-2025-10-02`): `POST /v1/skills` + `POST /v1/skills/{id}/versions`.
- [ ] Τρέξε `python upload_skills.py` → πάρε τα **skill_ids**.
- [ ] Αποθήκευσε τα skill_ids (στο `.env` ή config).

**Έλεγχος:** τα skills εμφανίζονται στο `GET /v1/skills`.

---

## ΒΗΜΑ 4 — Agents setup (1 μέρα)

- [ ] Βάλε τα skill_ids μέσα στο `src/setup_agents.py` (στα `skills=[...]`).
- [ ] Τρέξε `python setup_agents.py` (**ΜΙΑ ΦΟΡΑ**).
- [ ] Αποθήκευσε στο `.env`: `ENV_ID`, `ONBOARDING_AGENT_ID`, `WEBSITE_AGENT_ID`, `SOCIAL_AGENT_ID`.
- [ ] ⚠️ Μην ξανατρέξεις το setup (φτιάχνει διπλά agents).

**Έλεγχος:** `GET /v1/agents` δείχνει τους 3-4 agents σου.

---

## ΒΗΜΑ 5 — Φάση 1: Auto-posting MVP (1 βδομάδα)

> Στόχος: ένα μαγαζί ποστάρει αυτόματα κάθε μέρα στο Instagram. ΤΙΠΟΤΑ άλλο.

- [ ] **Meta MCP / Graph API σύνδεση** (developer mode προς το παρόν).
- [ ] **Vault** με τα Meta credentials (auto-refresh tokens).
- [ ] **Συμπλήρωσε `src/daily_post.py`** (ο σκελετός υπάρχει):
  - [ ] Φόρτωσε brand profile από DB.
  - [ ] Session με Social Agent → caption + εικόνα.
  - [ ] Post μέσω Meta (FB + IG).
- [ ] **Cron** (Supabase cron ή Vercel cron) → τρέχει κάθε πρωί ανά πελάτη.
- [ ] **DB schema** (Supabase): `clients`, `brand_profiles`, `posts`, `subscriptions`.

**Έλεγχος:** ορίζεις 1 test μαγαζί → το επόμενο πρωί έχει ποστάρει μόνο του. ✅

---

## ΒΗΜΑ 6 — Test με 1 πραγματικό μαγαζί (3-5 μέρες)

- [ ] Πάρε ένα από τα 3 μαγαζιά που είπαν ναι (το πιο πρόθυμο).
- [ ] Σύνδεσε τη **δική του** FB Page + IG Business (χρειάζεται το App Review για
      τρίτους — αν δεν έχει εγκριθεί ακόμα, βάλ' τον ως **test user** στην app σου).
- [ ] Άφησε το να ποστάρει 5-7 μέρες.
- [ ] **Μάζεψε feedback:** του αρέσουν τα posts; ο τόνος; οι εικόνες;
- [ ] Βελτίωσε το `social-post-gr` skill βάσει feedback (όχι κώδικα — skill).

**Gate:** αν ο πελάτης είναι ευχαριστημένος → προχώρα. Αυτό είναι το ταμείο σου.

---

## ΒΗΜΑ 7 — Φάση 2: Website (3 επιλογές) (1-2 βδομάδες)

- [ ] **Τελειοποίησε τα templates** (`taverna.html`, `dentist.html`, `mastoras.html`)
      + πρόσθεσε όσα χρειάζονται οι 3 πελάτες σου.
- [ ] **Συμπλήρωσε `src/onboard_client.py`**:
  - [ ] brand profile (Onboarding Agent).
  - [ ] preset + **3 επιλογές** site (Website Agent).
  - [ ] **interactive refinement loop** (αλλαγές σε φυσική γλώσσα).
  - [ ] εφαρμογή **SEO** (`local-seo-gr`): title/meta/schema.org.
- [ ] **Deploy tool/MCP** → Cloudflare Pages (static, HTTPS δωρεάν).
- [ ] Domain flow: agent προτείνει domains → πελάτης επιλέγει → Stripe one-time checkout
      **24€/έτος** → webhook αγοράζει/συνδέει domain και DNS.
      Για `.gr`: `DOMAIN_REGISTRAR=papaki` + Papaki reseller credentials, μετά Cloudflare DNS.

**Έλεγχος:** δίνεις τύπο μαγαζιού → παίρνεις 3 sites → διαλέγεις → αλλάζεις → live URL.

---

## ΒΗΜΑ 8 — Πληρωμές: Stripe (2-3 μέρες)

- [ ] Stripe **products/prices**:
  - [ ] Starter (site) — **€9.90/μήνα**
  - [ ] Social — **€49/μήνα**
  - [ ] Premium — **€79/μήνα**
- [ ] **Stripe Checkout** ή payment link (απλό για αρχή).
- [ ] **Webhook** Stripe → ενεργοποίηση/απενεργοποίηση πελάτη στο DB.
- [ ] **Domain fee** Stripe Checkout: one-time payment 24€/έτος πριν από αγορά domain.
- [ ] **Free trial** λογική (πρώτος μήνας δωρεάν).
- [ ] Σύνδεση: «πληρωμή ΟΚ» → ο cron αρχίζει να ποστάρει.

**Έλεγχος:** test πληρωμή (Stripe test mode) → ο πελάτης γίνεται ενεργός.

---

## ΒΗΜΑ 9 — Onboard τους 3 πελάτες (ανά πελάτη)

- [ ] Για κάθε έναν από τους 3:
  - [ ] Onboarding (στοιχεία μαγαζιού).
  - [ ] Email/contact capture: όνομα, email ιδιοκτήτη, τηλέφωνο, επωνυμία, περιοχή.
  - [ ] Client assets intake:
    - [ ] φωτογραφίες χώρου/προϊόντων/πιάτων/ομάδας
    - [ ] λογότυπο
    - [ ] βιογραφικό/ιστορία ιδιοκτήτη ή επιχείρησης
    - [ ] μενού, υπηρεσίες ή τιμοκατάλογος
    - [ ] before/after φωτογραφίες όπου ταιριάζει
    - [ ] social links και υπάρχον υλικό
    - [ ] επιβεβαίωση δικαιωμάτων χρήσης για κάθε asset
  - [ ] Φτιάξε site (3 επιλογές → επιλογή → αλλαγές → deploy).
  - [ ] Ρώτα αν έχει ήδη:
    - [ ] Facebook Page
    - [ ] Instagram Business/Creator συνδεδεμένο με τη Facebook Page
    - [ ] Meta Business/Ad Account
    - [ ] payment method για ads
  - [ ] Αν δεν έχει, δώσε guided setup checklist. ΜΗΝ δημιουργείς pages/ad accounts χωρίς
        ρητή έγκριση και login/ιδιοκτησία του πελάτη.
  - [ ] Σύνδεσε social με Facebook Login/OAuth → αποθήκευσε Page/IG credentials.
  - [ ] Ενεργοποίησε καθημερινά posts.
  - [ ] Προαιρετικά: business email/domain setup (`hello@...`) μέσω Cloudflare Email Routing
        ή Google Workspace, ανάλογα με το budget του πελάτη.
  - [ ] Ξεκίνα **πρώτο μήνα δωρεάν**, μετά Stripe.
- [ ] Ζήτα **testimonial / σύσταση** (το #1 κανάλι ανάπτυξης στην Ελλάδα).

**Gate:** 3 ευχαριστημένοι πελάτες που πληρώνουν = έχεις επιχείρηση. ✅

### Τι αναλαμβάνει η Vitrina στο onboarding

| Κομμάτι | Τι κάνουμε | Αυτόματο; |
|---|---|---|
| Site | 3 επιλογές, επιλογή, αλλαγές, deploy | Ναι, με approval πελάτη |
| Assets | Φωτογραφίες, logo, bio, μενού/υπηρεσίες, τιμοκατάλογος | Ο πελάτης τα δίνει |
| Business email | Πρόταση/ρύθμιση `hello@domain` αν θέλει | Μερικώς |
| Facebook Page | Σύνδεση υπάρχουσας Page ή οδηγίες δημιουργίας | Θέλει πελάτη/admin |
| Instagram | Σύνδεση IG Business με Page | Θέλει πελάτη/admin |
| Posts | Καθημερινά captions/images + publish | Ναι μετά OAuth |
| Ads | Draft campaigns + approval + budget limits | Μελλοντικό Growth |

Κανόνας: **ο πελάτης πρέπει να κατέχει τους λογαριασμούς του.** Εμείς μπορούμε να
καθοδηγήσουμε/αυτοματοποιήσουμε μετά από άδεια, αλλά δεν “παίρνουμε” ιδιοκτησία Page,
Instagram ή ad account.

---

## ΒΗΜΑ 10 — Κλίμακα & βελτίωση (συνεχές)

- [ ] **Coordinator Agent** (Opus) με `multiagent: coordinator` (όταν μεγαλώσεις).
- [ ] **Dashboard πελάτη**: calendar posts, έγκριση 1-tap, ανέβασμα φωτό.
- [ ] **Διανομή:**
  - [ ] Ζήτα συστάσεις από τους 3 πρώτους.
  - [ ] FB groups τοπικά, λογιστές/συλλόγους επαγγελματιών.
  - [ ] Demo videos (TikTok/Reels: «κοίτα, ποστάρει μόνο του»).
- [ ] **Monitoring κόστους** ανά πελάτη (Claude usage + εικόνες).
- [ ] **Upsell** €9.90 → €49 (το πραγματικό κέρδος).
- [ ] Πρόσθεσε επαγγέλματα/presets κατ' απαίτηση.
- [ ] Premium features: stories, απαντήσεις σε σχόλια.

---

## ΒΗΜΑ 11 — Growth add-on: Facebook Ads (μετά το MVP)

> Μην το ξεκινήσεις πριν δουλέψει το auto-posting με 1-3 πραγματικά μαγαζιά.
> Ads = πραγματικά χρήματα, άρα θέλει approval και budget limits.

- [ ] **Πακέτο Growth**: €99–149/μήνα + ad spend.
- [x] **Ads Agent skill**: `facebook-ads-gr` με local Facebook ads ανά vertical.
- [ ] **Approval flow**: ο agent φτιάχνει draft, άνθρωπος εγκρίνει πριν ξοδευτεί budget.
- [ ] **Meta Marketing API**:
  - [ ] `ads_read`
  - [ ] `ads_management`
  - [ ] ad account σύνδεση
- [ ] **Budget guardrails**:
  - [ ] max daily budget
  - [ ] max monthly budget
  - [ ] pause button
  - [ ] audit log
- [ ] **Monthly report**: reach, clicks, messages/calls, spend.

**Καλύτερο πρώτο use case:** Facebook local ad για ταβέρνα/καφέ/κομμωτήριο σε ακτίνα 3-5km,
με στόχο messages, calls ή local reach.

---

## 🎯 ΚΡΙΣΙΜΗ ΣΕΙΡΑ (μην την παρακάμψεις)

```
Λογαριασμοί → Meta Review (παράλληλα) → Skills → Agents →
Auto-posting (1 μαγαζί) → Test → Website → Stripe →
Onboard 3 πελάτες → Κλίμακα → Growth/Facebook Ads
```

## ⚡ ΤΙ ΝΑ ΚΑΝΕΙΣ ΑΥΤΗ ΤΗΝ ΕΒΔΟΜΑΔΑ
1. **ΒΗΜΑ 2 (Meta App Review)** — ξεκίνα ΣΗΜΕΡΑ (αργεί).
2. **ΒΗΜΑ 1 (λογαριασμοί)** — Anthropic + Managed Agents access.
3. **ΒΗΜΑ 3** — βάλε τα 10-15 posts στο `social-post-gr` από το concierge.

## 📌 Χρυσοί κανόνες
- **Agent μία φορά, Session κάθε run.** Μην φτιάχνεις agent σε κάθε κλήση.
- **Σωστό μοντέλο ανά δουλειά** (Opus/Sonnet/Haiku) — μην τρέχεις τα πάντα σε Opus.
- **Το moat = ελληνικά skills + διανομή + managed**, όχι ο κώδικας.
- **€9.90 = δόλωμα, €49 = ταμείο.** Site-only στο φθηνό, AI posts στο ακριβό.
- **Ads μόνο με approval.** Ο agent ετοιμάζει, άνθρωπος εγκρίνει, backend βάζει budget limits.
- **Βελτιώνεις skills, όχι κώδικα.** Η ποιότητα ζει στα SKILL.md.
