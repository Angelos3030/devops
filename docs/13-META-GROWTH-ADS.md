# 13 — Meta Growth Strategy: Από Organic Posts σε Facebook Ads

> Πλήρης οδηγός ανάπτυξης μέσω Meta. Ξεκινάμε με organic, ανεβαίνουμε σε paid.
> Μη ξεκινήσεις το Ads tier πριν δουλέψει το auto-posting με 3+ ικανοποιημένους πελάτες.

---

## 📊 Το τρίπτυχο Meta (τρία επίπεδα, τρεις τιμές)

```
Επίπεδο 1 — Organic Posts        €49/μήνα    ← ΤΩΡΑ (MVP)
   ↓  upsell μετά από 2-3 μήνες
Επίπεδο 2 — Promoted Posts       €79/μήνα    ← Απλό boost, ίδιος API
   ↓  upsell σε όσους βλέπουν αποτέλεσμα
Επίπεδο 3 — Full Facebook Ads    €99–149/μήνα + ad spend  ← Marketing API
```

**Γιατί αυτή η σειρά:**
- Επίπεδο 1 αποδεικνύει αξία (ο πελάτης βλέπει posts χωρίς δουλειά).
- Επίπεδο 2 είναι η πιο εύκολη πώληση: «θέλεις να σε δει περισσότερος κόσμος;»
- Επίπεδο 3 για τους σοβαρούς: λογιστές, οδοντίατροι, ενεργεία που θέλουν leads.

---

## ΕΠΙΠΕΔΟ 1 — Organic Posts (τρέχον MVP)

**Τι κάνει:** Social Agent γράφει caption → `publish.py` ποστάρει σε FB Page + IG.

**APIs που χρησιμοποιεί:**
- `POST /{page-id}/feed` (Facebook text/photo post)
- `POST /{ig-user-id}/media` + `/media_publish` (Instagram)

**Permissions που έχουμε ήδη:**
```
pages_show_list
pages_read_engagement
pages_manage_posts
instagram_basic
instagram_content_publish
```

**Κόστος:** ~€1–3/πελάτη/μήνα (Claude tokens). Margin ~85%.

---

## ΕΠΙΠΕΔΟ 2 — Promoted Posts (βήμα 1 στα paid)

**Τι είναι:** Παίρνεις ένα organic post που πήγε καλά και το «ανεβάζεις» με €3–5/μέρα.
Απλούστερο από full campaign: ένα API call, ίδιο creative, τοπικό targeting.

**Πώς λειτουργεί (API):**
```python
# Boost existing post → δημιουργεί απλή ad campaign
POST /{page-id}/promotions
  params: post_id, daily_budget (σε cents), duration_days,
          targeting: {geo_locations: {cities: [...]}, age_min: 25}
```

**Permissions επιπλέον:**
```
ads_management          # δημιουργία/έλεγχος ads
ads_read                # ανάγνωση metrics
```

**Approval flow (κρίσιμο):**
1. Agent επιλέγει ποιο post αξίζει boost (engagement > μέσος όρος × 1.5).
2. Ετοιμάζει πρόταση: post, targeting, budget, διάρκεια.
3. Αποστολή στον πελάτη/operator για approval (push notification ή email).
4. Μόνο μετά approval → `POST /promotions`.
5. Log: ποιος έκανε approve, πότε, ποσό.

**Τιμολόγηση:**
- Εσύ χρεώνεις €20–30/μήνα επιπλέον για τη διαχείριση.
- Ad spend: πληρώνει ο πελάτης απευθείας από τον ad account του.

---

## ΕΠΙΠΕΔΟ 3 — Full Facebook Ads (Marketing API)

**Τι προσθέτει vs Επίπεδο 2:**
- Πλήρεις campaigns (awareness, messages, leads, calls).
- Αδιάνοητο targeting: ηλικία + ακτίνα + interests.
- A/B testing 2-3 creatives.
- Μηνιαία αναφορά: reach, impressions, clicks, cost per result.

### Αρχιτεκτονική Ads Agent

```
Ads Agent (Haiku)
├── Διαβάζει: brand profile + τελευταία 30 posts + metrics
├── Επιλέγει: ποιο post γίνεται ad (engagement score)
├── Γράφει: 2 παραλλαγές headline + primary text
├── Προτείνει: campaign objective, targeting, budget, διάρκεια
├── Δημιουργεί: Draft (ΔΕΝ δημοσιεύει)
└── Στέλνει: notification στον operator για approval
         ↓ Approve → backend δημιουργεί campaign
         ↓ Reject → log + end
```

### Meta Marketing API calls (σε σειρά)

```python
# 1. Ad Account (πρέπει να έχεις πρόσβαση στον ad account του πελάτη)
GET /me/adaccounts

# 2. Campaign
POST /act_{ad_account_id}/campaigns
  name, objective (MESSAGES | LOCAL_AWARENESS | LINK_CLICKS),
  status=PAUSED  # ← ΠΑΝΤΑ paused αρχικά, ενεργοποιείς μετά approval

# 3. Ad Set (targeting + budget)
POST /act_{ad_account_id}/adsets
  campaign_id, daily_budget (cents), targeting {
    geo_locations: {cities: [{key, name, country}], custom_locations: [{radius: 5km}]},
    age_min: 25, age_max: 65,
  }, optimization_goal, billing_event

# 4. Ad Creative
POST /act_{ad_account_id}/adcreatives
  object_story_spec: {page_id, link_data: {message, link, picture}}

# 5. Ad (συνδέει creative + adset)
POST /act_{ad_account_id}/ads
  adset_id, creative, status=PAUSED

# 6. Μόνο μετά approval → ACTIVE
POST /act_{ad_account_id}/ads/{id}
  status=ACTIVE
```

### Permissions για Επίπεδο 3

```
ads_management          # δημιουργία campaigns
ads_read                # ανάγνωση stats
business_management     # ad account access (αν χρειαστεί)
```

**⚠️ Σημαντικό:** Χρειάζεται ο πελάτης να δώσει πρόσβαση στον **ad account** του
(από Meta Business Suite → Settings → Ad Accounts → Add People).
ΔΕΝ αρκεί η page permission.

### Budget Guardrails (υποχρεωτικά)

```python
# src/ads_guardrails.py (να φτιαχτεί στο Επίπεδο 3)
MAX_DAILY_BUDGET_EUR = 20      # hard limit ανά πελάτη
MAX_MONTHLY_BUDGET_EUR = 200   # hard limit ανά πελάτη
REQUIRE_APPROVAL_ABOVE_EUR = 5 # approval για οτιδήποτε > €5/μέρα

def validate_budget(daily_eur: float, client_id: str) -> bool:
    if daily_eur > MAX_DAILY_BUDGET_EUR:
        raise ValueError(f"Budget {daily_eur}€ > max {MAX_DAILY_BUDGET_EUR}€")
    monthly = get_month_spend(client_id)  # από DB
    if monthly + daily_eur * 30 > MAX_MONTHLY_BUDGET_EUR:
        raise ValueError("Υπέρβαση μηνιαίου budget")
    return True
```

### Μηνιαίο Report

```python
# Metrics από Marketing API
GET /act_{ad_account_id}/insights
  fields: impressions, reach, clicks, spend, actions (messages, calls)
  date_preset: last_month
```

**Format report:**
```
Μήνας Μαΐου — Ταβέρνα Ο Μήτσος
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reach:        4.200 άτομα
Εμφανίσεις:   8.900
Κλικ:           320
Μηνύματα:        18  ← το σημαντικό
Κόστος:        €87  (σου)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Κόστος/μήνυμα: €4.83
```

---

## Τι να προσθέσεις στο Meta OAuth flow (για ads)

Όταν φτάσεις Επίπεδο 2/3, πρόσθεσε στα scopes:

```python
# src/meta_oauth.py — ενημέρωσε το SCOPES
SCOPES_ORGANIC = ",".join([
    "pages_show_list", "pages_read_engagement", "pages_manage_posts",
    "instagram_basic", "instagram_content_publish",
])

SCOPES_WITH_ADS = SCOPES_ORGANIC + "," + ",".join([
    "ads_management",
    "ads_read",
])

# Χρησιμοποίησε SCOPES_WITH_ADS μόνο για πελάτες Growth plan
SCOPES = SCOPES_WITH_ADS if plan == "growth" else SCOPES_ORGANIC
```

**⚠️ Meta App Review:** τα `ads_management` + `ads_read` χρειάζονται **ξεχωριστό review**
από τα organic permissions. Κάνε τα reviews παράλληλα, αλλά σε χωριστά submissions
(το organic πρέπει να εγκριθεί πρώτο).

---

## Timeline: πότε να ξεκινήσεις κάθε επίπεδο

```
Τώρα (MVP):          Επίπεδο 1 — organic posts
                     3+ ικανοποιημένοι πελάτες × 2 μήνες
                     ↓
Μήνας 3-4:           Επίπεδο 2 — promoted posts (εύκολο upsell)
                     5+ πελάτες Growth plan × 1 μήνας
                     ↓
Μήνας 6+:            Επίπεδο 3 — full ads campaigns
```

**Gate πριν ads:** ο πελάτης πρέπει να λέει «τα organic posts μου φέρνουν κόσμο,
θέλω περισσότερα». Αν δεν το λέει, δεν είναι έτοιμος για ads.

---

## Πρώτα use cases (ποιοι αγοράζουν Growth)

| Επιχείρηση | Στόχος | Bid strategy |
|---|---|---|
| Ταβέρνα / καφέ | Local reach, messages για κρατήσεις | MESSAGES, ακτίνα 3km |
| Κομμωτήριο | Ραντεβού, νέοι πελάτες | MESSAGES, γυναίκες 20-50 |
| Οδοντίατρος | Leads (νέοι ασθενείς) | LINK_CLICKS → booking page |
| Γυμναστήριο | Εγγραφές (Σεπτέμβριος) | LOCAL_AWARENESS εποχιακά |
| Φροντιστήριο | Γονείς 30-50, Αύγουστος | LINK_CLICKS, interests: education |

---

## Checklist για Επίπεδο 2 (να γίνει στο μέλλον)

- [ ] Ζήτα `ads_management` + `ads_read` permissions από Meta (ξεχωριστό review).
- [ ] Πρόσθεσε `ads_accounts` table στη Supabase (client_id, ad_account_id, monthly_limit).
- [ ] Φτιάξε `src/ads_guardrails.py` (budget validation, approval check).
- [ ] Φτιάξε `src/promote_post.py` (boost existing post, PAUSED έως approval).
- [ ] Approval flow: email/push → ο operator approves → ACTIVE.
- [ ] Monthly report generator (`src/ads_report.py`).
- [ ] Ανέβασε τιμή connect.html: Growth plan = €99/μήνα.
- [ ] Stripe: νέο price ID για Growth.
