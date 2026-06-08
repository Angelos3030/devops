# ⚡ QUICKSTART — Τρέξε το end-to-end

> Ακριβείς εντολές, με σειρά. Προϋπόθεση: Python 3.11+, Anthropic + Managed Agents access.

## 0. Setup περιβάλλοντος
```bash
cd greek-smb-agent
python -m venv .venv && . .venv/Scripts/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # μετά συμπλήρωσε τα κλειδιά
```

## 1. Βάλε κλειδιά στο .env (όσα έχεις)
```
ANTHROPIC_API_KEY=...
SUPABASE_URL=...        SUPABASE_KEY=...
META_APP_ID=...         META_APP_SECRET=...
STRIPE_SECRET_KEY=...   STRIPE_WEBHOOK_SECRET=...
CF_API_TOKEN=...        CF_ACCOUNT_ID=...
```

## 2. Βάση δεδομένων
- Άνοιξε Supabase → SQL Editor → τρέξε όλο το `db/schema.sql`.

## 3. Ανέβασε τα skills (μία φορά)
```bash
python -m src.upload_skills
# → αντέγραψε τα SKILL_* IDs στο .env
```

## 4. Φτιάξε τους agents (μία φορά)
```bash
python -m src.setup_agents
# → αντέγραψε ENV_ID + *_AGENT_ID στο .env
# (direct Graph API posting — δεν χρειάζεται Meta MCP)
```

## 5. Deploy backend (Railway — μία φορά)
```bash
# 1. Πήγαινε στο railway.app → New Project → Deploy from GitHub repo
# 2. Railway βρίσκει αυτόματα το Procfile: uvicorn src.main:app --host 0.0.0.0 --port $PORT
# 3. Variables → βάλε όλα τα .env keys (SUPABASE_URL, META_*, STRIPE_*, ANTHROPIC_*)
# 4. Settings → Domains → Custom Domain → api.getvitrina.gr
# 5. Στον registrar (Papaki): CNAME api → <railway-app>.up.railway.app
```
Μετά ενημέρωσε στο Meta App → Valid OAuth Redirect URIs:
  https://api.getvitrina.gr/connect/callback

## 5β. Σύνδεση Facebook (OAuth) — για test
```bash
# βάλε το redirect_uri στο src/meta_oauth.py + δήλωσέ το στο Meta App settings
uvicorn src.meta_oauth:app --port 8001
# άνοιξε: http://localhost:8001/connect/start?client_id=TEST
# (σε production: HTTPS domain που ταιριάζει με το redirect_uri)
```

## 6. Test post (Φάση 1 — το ταμείο)
```bash
# αφού υπάρχει 1 πελάτης με brand_profile + social_account στη βάση:
python -m src.daily_post
```

## 7. Onboarding πελάτη (Φάση 2 — website)
```python
# python -c interactive ή από backend:
from src.onboard_client import onboard, refine, finalize_and_deploy
r = onboard({"type":"ταβέρνα","city":"Θεσσαλονίκη","style":"παραδοσιακό","name":"Ο Μήτσος"}, client_id="...")
print(r["options"])                       # δείξε 3 επιλογές στον πελάτη
html = refine(r["session_id"], "διάλεξα τη 2η, βάλε το μενού πάνω")   # αλλαγές
finalize_and_deploy(client_id="...", html=html, preset="taverna", variant=2, slug="o-mitsos")
```

## 8. Πληρωμές
```bash
# Σε production: τρέχει μέσω Railway (src.main:app) — περιλαμβάνει Stripe + Meta OAuth.
# Για τοπικό test:
uvicorn src.main:app --port 8000
```
Stripe Dashboard → Developers → Webhooks → βάλε `https://api.getvitrina.gr/stripe/webhook`
Events: `checkout.session.completed`, `customer.subscription.deleted`

## 9. Cron (καθημερινά posts)
- Supabase cron ή Vercel cron → καλεί `python -m src.daily_post` κάθε πρωί.
- Ή τοπικά (test): Windows Task Scheduler / cron → `python -m src.daily_post`.

---

## 🔑 Ελάχιστο μονοπάτι για ΠΡΩΤΟ test post
```
.env (ANTHROPIC + META) → upload_skills → setup_agents →
meta_oauth (σύνδεσε test page) → βάλε brand_profile στη βάση → daily_post
```

## ⚠️ Αν κάτι σκάσει
- `upload_skills` 400 → τύπωσε το response, προσάρμοσε field names (δες σχόλιο στο αρχείο).
- OAuth error → το `redirect_uri` πρέπει να ταιριάζει ΑΚΡΙΒΩΣ με το Meta App settings.
- IG post fail → το `image_url` πρέπει να είναι ΔΗΜΟΣΙΟ URL· ο λογ/σμός IG Business.
- Δες πάντα το **STATUS.md** για το τι είναι έτοιμο και τι ανοιχτό.
