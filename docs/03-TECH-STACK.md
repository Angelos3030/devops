# 03 — Tech Stack

## Μοντέλα Claude (ακριβή IDs & τιμές)

| Μοντέλο | ID | Input $/1M | Output $/1M | Πού το χρησιμοποιούμε |
|---------|-----|-----------|-------------|------------------------|
| Opus 4.8 | `claude-opus-4-8` | $5.00 | $25.00 | Coordinator (δύσκολες αποφάσεις) |
| Sonnet 4.6 | `claude-sonnet-4-6` | $3.00 | $15.00 | Website + Social (παραγωγή) |
| Haiku 4.5 | `claude-haiku-4-5` | $1.00 | $5.00 | Onboarding (απλά/φθηνά) |

> Κανόνας: το 90% των tokens να τρέχει σε Sonnet/Haiku. Opus μόνο όπου μετράει η ευφυΐα.

## Layers

| Κομμάτι | Τεχνολογία | Γιατί |
|---------|-----------|-------|
| Agents/loop | **Claude Managed Agents** (Python SDK `anthropic`) | Έτοιμο loop + skills + MCP |
| Brain | Claude API (Opus/Sonnet/Haiku) | Καλά ελληνικά, reasoning |
| Backend/orchestration | **Python** (FastAPI) ή **TypeScript** (Node) | Κρατά agent_ids, τρέχει cron, χειρίζεται events |
| DB / Auth / Storage | **Supabase** (Postgres) | Γρήγορο, λίγη συντήρηση, EU hosting |
| Scheduling | **Supabase cron** ή **Vercel cron** | Καθημερινά posts |
| Site hosting | **Cloudflare Pages** / **Netlify** (API) | Static, φθηνό, auto-deploy |
| Εικόνες | Image generation API (via `image-gen` skill) | AI εικόνες |
| Social posting | **Meta Graph API** μέσω **Meta MCP** (επίσημο) | FB + Instagram |
| Domain `.gr` | **Papaki / GR-EL** API | Τα `.gr` ΔΕΝ είναι απλό registrar API |
| Πληρωμές | **Stripe** (συνδρομές) | Recurring billing |

## Γιατί Python για το backend
Το Managed Agents έχει πλήρες Python SDK (`anthropic`), το ίδιο και TypeScript.
Διάλεξε ό,τι ξέρεις καλύτερα. Τα παραδείγματα εδώ είναι Python.

## Δομή φακέλων (πρόταση)

```
greek-smb-agent/
├── README.md
├── docs/                      # αυτή η τεκμηρίωση
├── skills/                    # τα custom SKILL.md
│   ├── brand-builder-gr/
│   │   └── SKILL.md
│   ├── greek-website/
│   │   ├── SKILL.md
│   │   └── templates/         # taverna.html, cafe.html, mastoras.html
│   ├── social-post-gr/
│   │   ├── SKILL.md
│   │   └── examples/          # καλά παραδείγματα posts
│   └── meta-publisher/
│       ├── SKILL.md
│       └── publish.py
├── src/
│   ├── setup_agents.py        # ONE-TIME: δημιουργία agents, αποθήκευση IDs
│   ├── upload_skills.py       # ανεβάζει τα custom skills (Skills API)
│   ├── onboard_client.py      # νέος πελάτης → brand + site
│   ├── daily_post.py          # cron: καθημερινό post ανά πελάτη
│   └── config.py              # agent_ids, env_id από env/DB
└── .env.example               # ANTHROPIC_API_KEY, SUPABASE_*, STRIPE_*, META_*
```

## Setup vs Runtime (κρίσιμη διάκριση)

- **Setup (μία φορά):** `setup_agents.py` + `upload_skills.py` → φτιάχνουν agents/skills,
  αποθηκεύουν τα IDs. ΔΕΝ τρέχουν σε κάθε request.
- **Runtime (κάθε φορά):** `onboard_client.py`, `daily_post.py` → φορτώνουν τα IDs,
  ανοίγουν session, στέλνουν events, κάνουν stream.

> ⚠️ Anti-pattern: να καλείς `agents.create()` σε κάθε run. Δημιουργεί ορφανά agents
> και πληρώνεις latency τζάμπα. Φτιάξε μία φορά → αποθήκευσε ID → reuse.

## Περιβάλλον (Environment)
Ένα cloud environment με `networking: limited` και `allow_mcp_servers: true` (για Meta),
ή `unrestricted` στην αρχή για ευκολία. Δες κόστος/ασφάλεια στο [06-RISKS-LEGAL.md](06-RISKS-LEGAL.md).

Δες [04-BUILD-PLAN.md](04-BUILD-PLAN.md) για το βήμα-βήμα πλάνο.
