# WORKSTREAMS

> Ποιος κρατά τι **αυτή τη στιγμή**. Ο κανόνας είναι ένας: **μην αγγίζεις
> uncommitted αρχεία άλλου workstream** — ούτε για «μικρή διόρθωση».
> Ενημέρωση: 2026-08-13.

## 1. Design / Themes — **καθαρό, σταματημένο**

| | |
|---|---|
| Κατάσταση | Clean· καμία ενεργή εργασία theme ή refactor |
| Baseline | `e2aca85` |
| Uncommitted | **κανένα** |

**Περιοχή:** `sites/lib/templates/`, `sites/lib/verticalProfiles.js`,
`sites/lib/mediaFallback.js`, `sites/app/`, `sites/tests/*.mjs`,
`skills/vitrina-design-system/`, `skills/vitrina-theme-builder/`,
`src/premium_generator.py`.

**Τελευταία δουλειά:** `f1a7fdd` (theme `signature`, 40 → 41 ταυτότητες),
`e2aca85` (το `qa:editor` κλειδώνει τη ροή site-first).

**Δεν ξεκινά** νέο theme ή refactor χωρίς ρητή εντολή. Νέο theme μόνο κατά
[DECISIONS.md §D2](DECISIONS.md).

## 2. Lead Scoring / Agent Runtime — **ενεργό**

| | |
|---|---|
| Κατάσταση | Active· ADR-0004 code complete, αναμένει εκτέλεση σε staging |
| Uncommitted | Ναι — δικά του, **μην τα αγγίξεις** |

**Κατέχει αυτή τη στιγμή (uncommitted):**

```
 M src/lead_scoring/graph.py
 M src/lead_scoring/kernel_registry.py
 M src/lead_scoring/providers.py
 M src/lead_scoring/run_staging_pilot.py
?? src/lead_scoring/disable_staging.py
?? src/lead_scoring/enable_staging.py
?? src/lead_scoring/staging_e2e_report.py
?? docs/adr/0004-lead-scoring-staging-enablement.md
```

**Περιοχή:** `src/lead_scoring/`, `docs/adr/`, `scripts/seed_staging.py`,
`docs/25-AGENCY-KERNEL.md`.

## 3. Κοινά αρχεία — προσοχή

| Αρχείο | Κάτοχος τώρα | Κανόνας |
|---|---|---|
| `STATUS.md` | **Lead Scoring** (uncommitted) | Μην το τροποποιείς μέχρι να ελευθερωθεί· βλ. [HANDOFF.md](HANDOFF.md) |
| `CLAUDE.md` | κανένας | Αλλάζει μόνο με ρητή απόφαση του ιδιοκτήτη |
| `docs/ai/*` | κοινό | Σύντομες εγγραφές· καμία αντιγραφή μεγάλων κειμένων |

## Παράλληλα Next.js builds

Δύο agents δεν μοιράζονται `sites/.next`. Κάθε παράλληλος worker ορίζει δικό του
dist dir και port:

```powershell
$env:NEXT_DIST_DIR='.next-<agent>'; npx next dev -p 38xx
```

Καμία διαγραφή σε `.next*` όσο υπάρχει άλλος ενεργός agent. Τα screenshots πάνε
στο αγνοημένο `sites/artifacts/`.

## Πριν ξεκινήσεις οτιδήποτε

1. `git status` — δες ποια αρχεία κρατά ήδη κάποιος.
2. [CURRENT_STATE.md](CURRENT_STATE.md) — τι ισχύει.
3. [DECISIONS.md](DECISIONS.md) — τι δεν ξανασυζητιέται.
4. [HANDOFF.md](HANDOFF.md) — τι μπλοκάρει.
