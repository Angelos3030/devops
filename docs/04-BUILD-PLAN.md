# 04 — Build Plan (βήμα-βήμα)

> Χρυσός κανόνας: **Μη χτίσεις όλα μαζί.** 2 agents πρώτα, validation πριν από κώδικα.

---

## 🔴 Εβδομάδα 0 — VALIDATION (ΠΡΙΝ από κάθε γραμμή κώδικα)

**Στόχος:** να βρεις 3 μαγαζιά που λένε «ναι, θα πλήρωνα €49/μήνα».

1. Φτιάξε ένα 1-σέλιδο pitch (στα ελληνικά): «Σου φτιάχνω site + ποστάρω κάθε μέρα
   στο Insta/FB, €49/μήνα, πρώτος μήνας δωρεάν».
2. Μίλα σε **5-10 μαγαζιά** (γνωστοί, οικογένεια, γειτονιά).
3. Πρόσφερε: «πρώτος μήνας τζάμπα, το κάνω **χειροκίνητα**» (concierge MVP).
4. **Κριτήριο:** αν 3 πουν ναι → χτίζεις. Αν όχι → άλλαξε ιδέα/κοινό **πριν** γράψεις κώδικα.

> Το concierge MVP (χειροκίνητα posts για 3 μαγαζιά) σου δίνει: απόδειξη ζήτησης +
> πραγματικά παραδείγματα posts → γίνονται το `social-post-gr` skill σου.

---

## 🟡 Φάση 1 — Το ταμείο πρώτα (2 agents μόνο)

**Στόχος:** ένα μαγαζί ποστάρει αυτόματα κάθε μέρα στο Instagram. ΤΙΠΟΤΑ άλλο.

- [ ] Setup Anthropic account + Managed Agents access
- [ ] `setup_agents.py`: φτιάξε **Social Agent** (Sonnet 4.6)
- [ ] Γράψε `social-post-gr` skill (με τα posts από το concierge MVP) + ανέβασέ το
- [ ] **Meta App + App Review** (ξεκίνα ΤΩΡΑ — παίρνει χρόνο, δες [06](06-RISKS-LEGAL.md))
- [ ] Σύνδεσε Meta MCP + vault με credentials
- [ ] `daily_post.py`: cron → session → caption → post σε IG/FB
- [ ] Δοκίμασε με **1 πραγματικό μαγαζί** (τα Week-0 volunteers)

✅ **Gate:** Αν αυτό δουλεύει και κάποιος πληρώνει → έχεις επιχείρηση. Προχώρα.

---

## 🟢 Φάση 2 — Website + Brand (πρόσθεσε 2 agents)

- [ ] `brand-builder-gr` skill + **Onboarding Agent** (Haiku 4.5)
- [ ] `greek-website` skill + templates (ταβέρνα/καφέ/μάστορας)
- [ ] **Website Agent** (Sonnet) με `frontend-design` (official) + `greek-website` + `image-gen`
- [ ] Custom tool / MCP για deploy σε Cloudflare Pages
- [ ] `onboard_client.py`: φόρμα → brand → site → live URL
- [ ] (Προαιρετικά) αγορά `.gr` domain μέσω Papaki API

---

## 🔵 Φάση 3 — Προϊόν & κλίμακα

- [ ] **Coordinator Agent** (Opus) με `multiagent: coordinator`
- [ ] Ωραίο UI (dashboard πελάτη): calendar posts, έγκριση 1-tap, ανέβασμα φωτό
- [ ] **Stripe** συνδρομές (free 3 scans → premium)
- [ ] Έγκριση posts από πελάτη πριν δημοσίευση (1-tap)
- [ ] Πολλαπλοί πελάτες, monitoring, token-cost tracking ανά πελάτη
- [ ] Stories, απαντήσεις σε σχόλια (premium tier)

---

## Σειρά προτεραιότητας (μην την παρακάμψεις)

```
Validation → Social auto-post (1 πελάτης) → Πληρώνει; →
Website → Coordinator/UI/Stripe → Κλίμακα
```

**Κάθε φάση πρέπει να «κλειδώνει» πριν την επόμενη.** Αν η Φάση 1 δεν πληρώνεται,
δεν χτίζεις Φάση 2.

Δες [05-COSTS-PRICING.md](05-COSTS-PRICING.md) για το αν στέκει οικονομικά.
