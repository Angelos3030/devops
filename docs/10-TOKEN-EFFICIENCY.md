# 10 — Token Efficiency: Τέλεια ιεραρχία για λιγότερα tokens

> Στόχος: ίδιο αποτέλεσμα, **πολύ λιγότερο κόστος**. Κάθε token μετράει στην κλίμακα.

## Η #1 αλλαγή: ΟΧΙ runtime coordinator για ρουτίνα

Το multiagent coordinator (Opus) είναι **ακριβό** — κάνει reasoning + delegation σε κάθε
κλήση. Για ρουτίνα (καθημερινό post) **δεν το χρειάζεσαι**.

❌ Ακριβό: `Coordinator (Opus) → αποφασίζει → καλεί Social Agent`
✅ Φθηνό: `Backend (κώδικας, €0 tokens) → καλεί ΑΠΕΥΘΕΙΑΣ Social Agent`

**Ο orchestrator είναι ο κώδικάς σου** (δωρεάν), όχι ένας Opus agent. Το backend ξέρει
ήδη ποιον agent θέλει — δεν χρειάζεται LLM για να το αποφασίσει.

> Coordinator (Opus + multiagent) **μόνο** για γνήσια σύνθετα, ανοιχτά tasks.
> Για το 99% (daily post, onboarding) → απευθείας κλήση του σωστού agent.

## Η σωστή ιεραρχία (token-optimized)

```
Backend (Python, ΔΩΡΕΑΝ orchestration)
   ├── daily_post()     → Social Agent   (Sonnet, effort: low)
   ├── onboard()        → Onboarding     (Haiku)  → Website Agent (Sonnet)
   └── [σπάνια] σύνθετο → Coordinator    (Opus)  ← μόνο αν χρειαστεί
```

## Μοντέλο ανά δουλειά (φθηνότερο → ακριβότερο)

| Δουλειά | Μοντέλο | Effort | Γιατί |
|---------|---------|--------|-------|
| Brand profile | **Haiku 4.5** | low | Απλό, δομημένο output |
| Caption (daily post) | **Haiku 4.5** ή Sonnet | low | Μικρό κείμενο — Haiku φτάνει |
| Website generation | **Sonnet 4.6** | medium | Θέλει ποιότητα design |
| Σύνθετο reasoning | Opus 4.8 | high | Σπάνια, μόνο αν χρειαστεί |

> Δοκίμασε **Haiku** για τα captions πρώτα. Αν η ποιότητα δεν φτάνει → Sonnet με `low`.
> ΜΗΝ ξεκινάς από Opus «για σιγουριά» — είναι 5x το κόστος του Sonnet.

## Οι 6 τεχνικές εξοικονόμησης tokens

### 1. Prompt caching (το μεγαλύτερο κέρδος)
Το **system prompt + brand profile** είναι σταθερά → cache τα (~90% έκπτωση στο
επαναλαμβανόμενο input). Βάλε το μεταβλητό (θέμα ημέρας, ημερομηνία) στο ΤΕΛΟΣ.

### 2. Skills = lazy loading (progressive disclosure)
Τα skills φορτώνουν το πλήρες κείμενο **μόνο όταν χρειάζονται**. Μόνο το `description`
κάθεται στο context. → Βάζεις πολλή εξειδίκευση χωρίς να γεμίζεις το context.
**Γι' αυτό βάζουμε το know-how σε skills, όχι σε τεράστιο system prompt.**

### 3. effort: low όπου γίνεται
`output_config: {effort: "low"}` → λιγότερο thinking, λιγότερα tokens. Ιδανικό για
απλά captions. Ανέβασε σε `medium` μόνο για website.

### 4. Μικρά, εστιασμένα system prompts
Το system prompt να είναι σύντομο. Η λεπτομέρεια ζει στα skills (που φορτώνουν on-demand).

### 5. Σταθερά μηνύματα = σταθερό cache
Μην βάζεις timestamps/random IDs στην αρχή του prompt (σπάνε το cache). Μεταβλητά στο τέλος.

### 6. Επαναχρησιμοποίηση agent (όχι re-create)
Agent μία φορά → reuse. Κάθε `agents.create()` = latency + setup tokens τζάμπα.

## Χρήση των ΕΤΟΙΜΩΝ skills (για ωραίο αποτέλεσμα + λιγότερη δουλειά)

Μην ξαναγράφεις ό,τι υπάρχει. Σύνδεσε:
- **`frontend-design` (official Anthropic)** → όμορφα sites, design tokens, χωρίς "AI slop".
  Το δικό σου `greek-website` βάζει ΜΟΝΟ το ελληνικό κομμάτι (presets, γλώσσα).
- **Anthropic doc skills** (`pdf`, `xlsx`) → αν χρειαστούν reports/τιμοκατάλογοι.
- **`image-gen`** → εικόνες.

> Έτσι: μικρά δικά σου skills (μόνο το ελληνικό moat) + μεγάλα έτοιμα skills (δωρεάν
> ποιότητα). Λιγότερος κώδικας, λιγότερα tokens, καλύτερο αποτέλεσμα.

## Πρακτικός αντίκτυπος κόστους
```
ΠΡΙΝ  (Opus coordinator σε κάθε post):  ~€0.15-0.30 / post
ΜΕΤΑ  (Haiku/Sonnet απευθείας + cache):  ~€0.02-0.05 / post
                                         → 5-10x φθηνότερα
```
Στους 100 πελάτες × 30 posts/μήνα = 3.000 posts:
- Πριν: ~€450-900/μήνα. Μετά: ~€60-150/μήνα. **Διαφορά: εκατοντάδες €/μήνα.**

## Κανόνας-κλειδί
**Το LLM κάνει ΜΟΝΟ ό,τι χρειάζεται ευφυΐα.** Routing, scheduling, αποθήκευση,
αποφάσεις «ποιος agent» → κώδικας (δωρεάν). Caption/design → LLM (το φθηνότερο που φτάνει).
