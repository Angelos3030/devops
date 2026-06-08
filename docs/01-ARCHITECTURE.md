# 01 — Αρχιτεκτονική

## Η μεγάλη απόφαση: Claude Managed Agents (CMA)

Δεν χτίζουμε δικό μας agent loop από το μηδέν. Χρησιμοποιούμε **Claude Managed Agents**:
η Anthropic τρέχει τον agent loop + ένα container ανά session όπου εκτελούνται τα tools.
Εμείς δίνουμε **config** (μοντέλο, system prompt, tools, skills) και χειριζόμαστε τα events.

**Γιατί CMA και όχι σκέτο API:**
- Έτοιμο loop, sandbox, context compaction, prompt caching, streaming → λιγότερος κώδικας.
- **Native υποστήριξη Skills** (`skills` array στο agent).
- **Multiagent coordinator** για τη συνεργασία agents.
- **MCP servers + vaults** για ασφαλή σύνδεση με Meta/τρίτους.

> Ο χρυσός κανόνας: **Agent (μία φορά) → Session (κάθε run).**
> Φτιάχνεις το agent config μία φορά, αποθηκεύεις το `agent_id`, και ανοίγεις session ανά εργασία.

---

## Το διάγραμμα

```
                       ┌─────────────────────────────────┐
                       │   COORDINATOR AGENT             │  ← ο "αρχηγός"
                       │   (Claude Opus 4.8)             │     μοιράζει δουλειές
                       │   multiagent: coordinator       │
                       └───────────────┬─────────────────┘
            ┌──────────────────────────┼──────────────────────────┐
            ▼                          ▼                          ▼
   ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
   │  ONBOARDING     │        │  WEBSITE        │        │  SOCIAL         │
   │  AGENT          │        │  AGENT          │        │  AGENT          │
   │  (Haiku 4.5)    │        │  (Sonnet 4.6)   │        │  (Sonnet 4.6)   │
   └─────────────────┘        └─────────────────┘        └─────────────────┘
   skills:                    skills:                    skills:
   - brand-builder-gr         - greek-website            - social-post-gr
                              - local-seo-gr             - meta-publisher
                              - conversion-copy-gr
```

Κάθε agent είναι context-isolated thread με δικό του μοντέλο, system prompt, tools, skills.

---

## Οι agents & τι κάνει ο καθένας

### 1. 🧠 Coordinator Agent — `claude-opus-4-8`
- Ο "αρχηγός". Μιλάει με το backend μας, αποφασίζει ποιος υπο-agent τρέχει.
- `multiagent: { type: "coordinator", agents: [onboarding, website, social] }`
- Opus γιατί παίρνει τις δύσκολες αποφάσεις. Τρέχει σπάνια → το κόστος μένει χαμηλό.

### 2. 👋 Onboarding Agent — `claude-haiku-4-5`
- Τρέχει **μία φορά** ανά νέο πελάτη.
- Input: «ταβέρνα, Θεσσαλονίκη, παραδοσιακή, φιλικός τόνος».
- Output: **brand profile** (τόνος, χρώματα, hashtags, θέματα) → το χρησιμοποιούν όλοι.
- Skill: `brand-builder-gr`. Haiku γιατί είναι απλό/φθηνό.

### 3. 🌐 Website Agent — `claude-sonnet-4-6`
- Φτιάχνει **static site** στα ελληνικά από το brand profile.
- Skills: `greek-website` + `local-seo-gr` + `conversion-copy-gr`.
- Output → deploy σε Cloudflare Pages/Netlify (μέσω custom tool ή MCP).

### 4. ✍️ Social Agent — `claude-sonnet-4-6` (ΤΟ ΤΑΜΕΙΟ)
- Τρέχει **κάθε μέρα** (cron). Γράφει caption + διαλέγει/φτιάχνει εικόνα + hashtags.
- Skills: `social-post-gr` + `meta-publisher` + `image-gen`.
- Ποστάρει μέσω **Meta MCP** (επίσημο, από 29/4/2026) σε FB + Instagram.

> ⚠️ Το «posting» καθαυτό είναι **απλός κώδικας/MCP**, όχι AI. Μην βάζεις AI εκεί που δεν χρειάζεται.

### 5. 📣 Ads Agent — μελλοντικό Growth add-on
- Μπαίνει **μετά** το MVP των posts. Δεν είναι μέρος του πρώτου test.
- Input: brand profile, πρόσφατα posts, εποχικότητα, στόχος πελάτη, περιοχή, budget.
- Output: πρόταση Facebook ad (copy, creative, targeting, budget, objective).
- Κανόνας: **draft + approval πρώτα, ποτέ αυτόματο spend χωρίς άνθρωπο**.
- Integration: Meta Marketing API αργότερα (`ads_read`, `ads_management`), budget limits στο backend.

Το Ads Agent δεν πρέπει να είναι “agent που ξοδεύει λεφτά”. Πρέπει να είναι agent που
ετοιμάζει διαφήμιση και ο πελάτης/χειριστής την εγκρίνει.

---

## Ροή: Νέος πελάτης (μία φορά)

```
Πελάτης συμπληρώνει φόρμα onboarding (τύπος μαγαζιού + λίγα στοιχεία)
   → Coordinator → Onboarding Agent (brand profile)
   → Coordinator → Website Agent:
        1. φορτώνει preset ανά επάγγελμα (δες 07-VERTICALS.md)
        2. φτιάχνει 3 ΕΠΙΛΟΓΕΣ site (διαφορετική αισθητική)
        3. ο πελάτης διαλέγει: "μ' αρέσει η 2η"
        4. interactive refinement: "θες να αλλάξω κάτι; να βάλω το μενού εδώ;"
        5. συνομιλιακές αλλαγές μέχρι "τέλειο"
        6. deploy
   → Επιστροφή: live URL
```

> Κλειδί UX: **3 επιλογές + συνομιλιακές αλλαγές**, όχι «πάρε ό,τι σου έδωσα».
> Έτσι ο μη-τεχνικός μαγαζάτορας νιώθει ότι ελέγχει το αποτέλεσμα.

## Ροή: Καθημερινό post (cron, κάθε πρωί)

```
Cron job (Supabase/Vercel cron) ξυπνά για κάθε ενεργό πελάτη
   → Session με Social Agent + brand profile (από DB)
   → Claude: caption (σωστός τόνος) + εικόνα (AI ή φωτό πελάτη)
   → Meta MCP: post σε IG + FB
   → Αποθήκευση στο calendar/DB + (προαιρετικά) έγκριση 1-tap από πελάτη
```

---

## Ροή: Facebook ad (Growth add-on, όχι MVP)

```
Κάθε εβδομάδα ή όταν ένα post πάει καλά
   → Backend φορτώνει brand profile + recent posts + στόχο
   → Ads Agent προτείνει:
        - objective (messages/calls/clicks/local reach)
        - copy 2-3 εκδοχές
        - creative
        - περιοχή/ακτίνα
        - budget και διάρκεια
   → Approval screen ή managed approval από εμάς
   → Μόνο μετά την έγκριση: Meta Marketing API δημιουργεί/τρέχει campaign
   → DB log + monthly report
```

Hard limits:
- max daily budget ανά πελάτη
- max monthly budget
- approval id για κάθε campaign
- audit log για ποιος ενέκρινε τι
- pause button πάντα διαθέσιμο

## Best practices (Claude-specific)

1. **Σωστό μοντέλο ανά δουλειά:** Opus για coordinator/δύσκολα, Sonnet για παραγωγή,
   Haiku για απλά/φθηνά. Μην τρέχεις τα πάντα σε Opus.
2. **Effort tuning:** `effort: "low"` για Haiku tasks, `medium/high` για Sonnet δημιουργικά.
3. **Adaptive thinking:** `thinking: {type: "adaptive"}` στο coordinator.
4. **Prompt caching:** το brand profile + system prompt είναι σταθερά → κρατάς cache,
   βάζεις το μεταβλητό (ημερομηνία, θέμα ημέρας) στο τέλος.
5. **Skills για το know-how:** η ελληνική εξειδίκευση μπαίνει σε `SKILL.md`, όχι σε κώδικα.
6. **MCP auth μέσω vaults:** ποτέ tokens μέσα στο agent config ή σε prompts.
7. **Custom tool για secrets:** ό,τι θέλει δικό σου κλειδί (π.χ. domain API) → custom tool
   που το χειρίζεται το backend σου, όχι το container.

Δες [02-SKILLS.md](02-SKILLS.md) για το πώς γράφονται τα skills.
