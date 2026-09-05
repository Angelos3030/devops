# Production deployment — βιβλιοθήκη 58 themes

Ημερομηνία: 2026-08-22

## Εκδόσεις

| | |
|---|---|
| **Σημείο επαναφοράς** | `71e6020` — *fix(templates): τα έξι capability keys εισάγονταν από λάθος module* |
| Deploy 1 | `aa6a7f1` — 58 εμπορικά themes, backend registration, selector |
| Deploy 2 | `9a369ea` — διόρθωση του `library.json` |
| **Deploy 3 (τρέχον)** | `c7cb06d` — διόρθωση υπερχείλισης `horizontal-story` |

Επαναφορά: `git revert c7cb06d 9a369ea aa6a7f1` ή `git reset --hard 71e6020 && git push --force-with-lease`.

Μηχανισμός: Railway auto-deploy από `origin/main` (GitHub `Angelos3030/devops`).
Δύο υπηρεσίες: `railway.toml` (FastAPI, `api.getvitrina.gr`) και
`sites/railway.toml` (Next.js, `sites-production-da56.up.railway.app`).

## Πύλες πριν το deploy

| έλεγχος | αποτέλεσμα |
|---|---|
| `qa:registry` | 64 themes × 4 σημεία εγγραφής · 49 design ids · 56 components ✓ |
| `qa:trust` | κανένα theme δεν ισχυρίζεται κάτι εκ μέρους του πελάτη ✓ |
| `qa:profiles` | 17 demo verticals + generic fallback ✓ |
| `qa:capabilities` | contracts + demo providers ✓ |
| `qa:verticals` | 15 semantic media cases ✓ |
| `next build` | Compiled successfully · 22/22 static pages ✓ |

> Το `npm run qa:release` δεν εκτελείται ως έχει: καλεί `qa:spine`, script που
> δεν υπάρχει πια (το `spine_guard.mjs` διαγράφηκε στο `d530d23`). Εκτελέστηκαν
> ένα προς ένα όλα τα υπόλοιπα βήματα της αλυσίδας.

## Τι ΔΕΝ αναπτύχθηκε, και γιατί

**Homepage.** Ο ανασχεδιασμός δεν ενσωματώθηκε ποτέ στο `web/`· η τελευταία
οδηγία ήταν «Do not integrate into production yet». Επιπλέον το
`web/index.html` έχει **1158 προσθήκες / 783 διαγραφές μη δεσμευμένες, από
παράλληλο agent** — ήταν ήδη τροποποιημένο στην αρχή της συνεδρίας. Το
CLAUDE.md απαγορεύει να γραφτεί από πάνω. Έμεινε εκτός commit.

Τρεις διαφορετικές αρχικές υπάρχουν αυτή τη στιγμή:

| πού | h1 | γραμματοσειρά |
|---|---|---|
| ζωντανή `getvitrina.gr` | «Η ψηφιακή σου παρουσία. Σε ένα λεπτό.» | Plus Jakarta Sans |
| working tree `web/index.html` | «Η επιχείρησή σου. Σχεδιασμένη.» | — |
| `research/homepage-redesign/` | «Φτιάχνουμε το site.» | Manrope |

**Logo/wordmark.** Δεν υπάρχει τελικό asset. Μετρήθηκε ότι το σήμα δεν στέκει
στα 14px ούτε στο favicon-16 όπως σχεδιάστηκε· η διορθωμένη παραλλαγή (12px
τετράγωνο, 2px μοντάζ) παρουσιάστηκε και εκκρεμεί απόφαση.

## Regression που αποκάλυψε το deploy

`horizontal-story` — οριζόντια υπερχείλιση στα 390 (scrollWidth 418).

Δεν το είχε πιάσει το προηγούμενο QA επειδή μέχρι το `71e6020` το id απέδιδε
**άλλο component**· ο πρώτος σωστός έλεγχος έγινε αφού ζωντάνεψε η διόρθωση.

Δύο αιτίες:

1. `.horizontal{overflow:visible}` στο mobile block ακύρωνε το
   `.root{overflow-x:hidden}` — το shorthand επαναφέρει και τον οριζόντιο
   άξονα. → `overflow-x:clip; overflow-y:visible`
2. Το `<h1>` «ΕΠΙΣΚΕΥΕΣ & ΛΟΥΣΤΡΑΡΙΣΜΑΤΑ» στα `clamp(52px,8vw,112px)` είχε
   πλάτος 400px μέσα σε κουτί 289px (`max-width:10ch`). → `overflow-wrap:anywhere`

Διορθώθηκε, ξανα-αναπτύχθηκε, επαληθεύτηκε στην παραγωγή: 418 → **390**.
Desktop αμετάβλητο.

## Production smoke

| έλεγχος | αποτέλεσμα |
|---|---|
| `getvitrina.gr` | 200 · 13 εικόνες, καμία σπασμένη · 1440 και 390 χωρίς υπερχείλιση · 0 console errors |
| `api.getvitrina.gr/healthz` | 200 |
| Selector `/choose/…` | 58 κάρτες · 9 κατηγορίες · φίλτρο «Εστίαση» → 17 · **0 ωμά ids** · 0 console errors |
| Tabs | «Προτεινόμενα για σένα (4)» / «Δες όλα τα σχέδια (58)» |
| Ζωντανά themes | **58/58** desktop + mobile, 200, χωρίς σπασμένα assets, χωρίς localhost/staging, χωρίς console errors |
| Δεν εκτίθενται | αρχέτυπα 0 · `split` όχι · Master όχι |
| `/select-design` | `nonexistent-theme` → **400**· 5 δείγματα από 5 κατηγορίες περνούν την επικύρωση |

## Ανοιχτό: το τελευταίο σκέλος του flow

Το *select → persist → next step* χρειάζεται πραγματικό client. Δεν υπάρχει
QA client (`/clients/lookup` κενό) ούτε ζωντανό staging
(`api-staging.getvitrina.gr` δεν απαντά). Η δημιουργία client θα έγραφε στη
**βάση παραγωγής**, που το CLAUDE.md απαγορεύει σε test.

Η επικύρωση ελέγχθηκε χωρίς εγγραφή: με ψεύτικο client id, τα έγκυρα themes
περνούν τον έλεγχο layout και αποτυγχάνουν αργότερα (ανύπαρκτος client), ενώ
ένα άγνωστο id κόβεται στα 400. Ακριβώς η συμπεριφορά που ήταν σπασμένη.

Για να κλείσει: μόνιμος QA client ή staging deployment.
