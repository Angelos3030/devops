# 02 — Skills

## Τι είναι ένα Skill

Ένας **φάκελος** με ένα `SKILL.md` (οδηγίες + metadata) και προαιρετικά scripts/templates.
Ο Claude φορτώνει το πλήρες περιεχόμενο **μόνο όταν το χρειάζεται** (progressive disclosure):
η περιγραφή κάθεται στο context, το σώμα διαβάζεται on-demand. → Αποδοτικό σε tokens.

## Δομή `SKILL.md`

```markdown
---
name: social-post-gr
description: Γράφει captions για FB/Instagram στα ελληνικά, στο σωστό τόνο
             ανά τύπο μαγαζιού (ταβέρνα, καφέ, μάστορας). Χρησιμοποίησέ το όταν
             πρέπει να φτιαχτεί καθημερινό post για ελληνικό μικρομάγαζο.
---

# Πώς γράφω ελληνικό caption για social

## Αρχές
- Φιλικός, ζεστός τόνος — όχι εταιρικός.
- 1-2 emoji max. Καθαρά ελληνικά.
- Πάντα call-to-action (τηλέφωνο, ωράριο, "πέρνα να δοκιμάσεις").

## Ανά τύπο μαγαζιού
- Ταβέρνα: έμφαση στο φαγητό, παράδοση, οικογένεια.
- Καφέ: ατμόσφαιρα, πρωινό, "η μέρα σου ξεκινά εδώ".
- Μάστορας: αξιοπιστία, "γρήγορη εξυπηρέτηση", περιοχές που καλύπτει.

## Hashtags
3-5, τοπικά + κλάδος: #θεσσαλονικη #ταβερνα #ελληνικηκουζινα

## Παραδείγματα (καλά)
(βάλε εδώ 5-10 πραγματικά καλά posts ως few-shot)
```

**Δύο πεδία υποχρεωτικά στο frontmatter:** `name` και `description`.
Το `description` είναι κρίσιμο — από αυτό αποφασίζει ο agent αν θα φορτώσει το skill.

---

## Τα skills του project

### Δικά μας (custom) — εδώ είναι το moat σου
| Skill | Τι κάνει | Μοντέλο που το χρησιμοποιεί |
|-------|----------|------------------------------|
| `brand-builder-gr` | Φτιάχνει brand profile για ελληνικό μαγαζί | Onboarding |
| `greek-website` | Static site στα ελληνικά + templates (ταβέρνα/καφέ/μάστορας) | Website |
| `social-post-gr` | Captions FB/IG στα ελληνικά, σωστός τόνος | Social |
| `meta-publisher` | Πώς ποστάρω σωστά μέσω Meta API (μορφή, χρόνοι) | Social |
| `local-seo-gr` | Local SEO/schema.org για ελληνικά sites | Website |
| `conversion-copy-gr` | Ελληνικά headlines, CTAs, offers, pricing/landing copy | Website |
| `facebook-ads-gr` | Draft Facebook ads, local targeting, budget/approval/reporting | Μελλοντικός Ads/Growth |

### Έτοιμα (δωρεάν) — δεν τα γράφεις εσύ
| Skill | Πηγή |
|-------|------|
| `frontend-design` | Επίσημο Anthropic (όμορφο, design tokens, best practices) |
| `image-gen` | Image generation (AI εικόνες) |
| Anthropic doc skills (`xlsx`, `pdf`, `docx`) | Built-in (αν χρειαστούν reports) |

---

## Πώς φορτώνονται στο Managed Agents

Τα skills μπαίνουν στο **agent** (όχι στο session), μέγιστο 20 ανά agent:

```python
agent = client.beta.agents.create(
    name="Social Agent",
    model="claude-sonnet-4-6",
    system="Είσαι ο social media manager για ελληνικά μικρομάγαζα.",
    skills=[
        {"type": "anthropic", "skill_id": "image-gen"},          # έτοιμο
        {"type": "custom", "skill_id": "skill_xxx", "version": "latest"},  # social-post-gr
        {"type": "custom", "skill_id": "skill_yyy", "version": "latest"},  # meta-publisher
    ],
    tools=[{"type": "agent_toolset_20260401"}],   # bash, read, write, web κ.λπ.
    mcp_servers=[{"type": "url", "name": "meta", "url": "https://..."}],
)
```

### Πώς ανεβάζεις custom skill (Skills API, beta `skills-2025-10-02`)

```
POST /v1/skills                       → δημιουργεί skill, επιστρέφει skill_id
POST /v1/skills/{skill_id}/versions   → ανεβάζει version (το SKILL.md + αρχεία)
```

Μετά αναφέρεις το `skill_id` στο agent config (όπως πάνω).

---

## Best practices για skills

1. **Ένα skill = μία δουλειά.** Μην φτιάξεις «mega-skill».
2. **Το `description` πουλάει το skill στον agent** — γράψε πότε να χρησιμοποιηθεί,
   όχι μόνο τι κάνει. («Χρησιμοποίησέ το όταν...»).
3. **Few-shot μέσα στο skill ή σε `references/`.** Για μικρά skills βάλε 5-10 παραδείγματα
   στο `SKILL.md`. Για μεγάλες βιβλιοθήκες, όπως ads/copy, βάλε τα σε `references/`
   ώστε να φορτώνονται μόνο όταν χρειάζονται.
4. **Scripts για το ντετερμινιστικό.** Το «ποστάρισμα» είναι κώδικας (`publish.py`),
   όχι κείμενο — βάλ' το ως script μέσα στο skill ή ως custom tool.
5. **Versioning.** Κάθε βελτίωση = νέο version. Μπορείς να κάνεις rollback.

Δες [03-TECH-STACK.md](03-TECH-STACK.md) για μοντέλα, APIs, υποδομή.
