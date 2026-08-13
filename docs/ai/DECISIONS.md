# DECISIONS

> Αποφάσεις που **δεν ξανασυζητιούνται**, με απόδειξη σε κώδικα ή test — όχι σε
> ανάμνηση. Αν μια απόφαση εδώ διαφωνεί με ένα doc, **κερδίζει ο κώδικας** και το
> doc διορθώνεται. Κάθε εγγραφή: απόφαση → απόδειξη → τι απαγορεύεται.

## D1. Canonical onboarding funnel = **site first**

```
web/index.html → start.html?text= → POST /start → progress
               → /choose/{client_id}#claim= → sessionStorage → dashboard
```

Το `connect.html` **δεν είναι** το primary funnel. Παραμένει για **OAuth callback**
και **pilot intake**, και δεν διαγράφεται.

**Απόδειξη:**
- commit `ccbfdb8` (11/8/2026 07:02) — «ο ιδιοκτήτης όρισε ξανά την κανονική ροή»
- docstring του `POST /start` στο [`src/meta_oauth.py`](../../src/meta_oauth.py) —
  «Site first, questions later… κάθε βήμα πριν την πρώτη ουάου στιγμή είναι σημείο διαρροής»
- [`sites/tests/editorFlow.mjs`](../../sites/tests/editorFlow.mjs) από το `e2aca85` —
  κλειδώνει και τα τέσσερα σκαλοπάτια και **απαγορεύει ρητά** το `connect.html?desc=`

**Απαγορεύεται:** επαναφορά φόρμας πριν ο πελάτης δει αποτέλεσμα. Το test θα σκάσει,
και σωστά.

> Ιστορικό που εξηγεί γιατί υπάρχει αυτό το αρχείο: η ροή άλλαξε στις 07:02 και το
> `STATUS.md` είχε γραφτεί στις 05:13. Δύο agents διάβασαν δύο διαφορετικές
> πραγματικότητες από το ίδιο repo, και το QA test έμεινε κόκκινο δύο μέρες.

## D2. Νέο theme μόνο από reference, με ρητή έγκριση

Μέτρηση → compact ανάλυση (Keep/Adapt/Discard/Sections/Tokens/Risks) → **έγκριση** →
κώδικας. Ποτέ theme «από έμπνευση», ποτέ implementation πριν την έγκριση.
Αντιγράφεται **μόνο σχεδιαστική λογική** — ποτέ κώδικας, markup, κείμενο, εικόνες ή
γραμματοσειρές. Άδειες επαληθεύονται από το ίδιο το LICENSE του repo.

**Απόδειξη:** [`skills/vitrina-theme-builder/SKILL.md`](../../skills/vitrina-theme-builder/SKILL.md),
[reference-library.md](../../skills/vitrina-theme-builder/references/reference-library.md).
**«Zero themes σε έναν κύκλο» είναι αποδεκτό αποτέλεσμα** — έχει ήδη συμβεί.

## D3. Χρώμα μόνο μέσω Color Spine

11 σημασιολογικοί ρόλοι, 5 παλέτες, η παλέτα κερδίζει με specificity.

**Απαγορεύεται:** επαναφορά της legacy γέφυρας, νέο global χρωματικό token, δεύτερο
accent, και λύση αντίθεσης με `!important`. Τοπικό πρόβλημα λύνεται τοπικά
(π.χ. `color-mix` για κείμενο σε σκούρη ζώνη), όχι με νέο καθολικό ρόλο.

**Απόδειξη:** [`sites/tests/spine_guard.mjs`](../../sites/tests/spine_guard.mjs) —
41 ταυτότητες, κάθε ζεύγος σε κάθε παλέτα.

## D4. Καμία εφεύρεση περιεχομένου

Χρόνια εμπειρίας, πιστοποιήσεις, κριτικές, τιμές, έργα, before/after: **μόνο αν
υπάρχουν**. Το stock είναι σημασμένο ενδεικτικό υλικό, ποτέ «η δουλειά μου».

**Απόδειξη:** `HERO_IS_REAL` στο [`sites/lib/mediaFallback.js`](../../sites/lib/mediaFallback.js)
— το `MEDIA_MODE` δεν απαντούσε «είναι δικιά του η φωτογραφία;», οπότε ένα stock
πρόσωπο μπορούσε να μπει σε πλαίσιο πορτρέτου με `alt="{ΟΝΟΜΑ} — {ΕΙΔΙΚΟΤΗΤΑ}"`.
Επίσης [`tests/test_intake_quality.py`](../../tests/test_intake_quality.py).

## D5. Approval-first σε ό,τι βγαίνει προς τα έξω

- **Chat-to-edit:** ο provider επιστρέφει allowlisted JSON patch → preview →
  ρητό «Έγκριση αλλαγών». Η απόρριψη δεν γράφει τίποτα.
- **Social:** το `src/daily_post.py` φτιάχνει **μόνο drafts**· δημοσίευση μόνο
  μέσω `src/social_engine.py` με έγκριση και audit log.
- **Domain:** μόνο με τη διαδικασία του [14-DOMAIN-AUTOMATION.md](../14-DOMAIN-AUTOMATION.md).

## D6. Κανένα test δεν γράφει στη βάση παραγωγής

Το production QA είναι read-only. Καταστροφικά scripts απαιτούν
`VITRINA_ENV == staging` **και** ρητό flag. Τα secrets ζουν μόνο σε
`.env`/platform variables — ποτέ σε docs, chat, screenshots ή commits.

## D7. «Αχρησιμοποίητο» δεν το αποφασίζει το text search

Πριν από διαγραφή/μετακίνηση ελέγχονται σταθερές, σύνθεση διαδρομής, imports,
δυναμική φόρτωση και runtime call chain — και μένει test που το αποδεικνύει.
Το `skills/vitrina-design-system/templates/` είναι runtime-critical.

**Απόδειξη:** `CLAUDE.md` §Refactor, [`tests/test_runtime_assets.py`](../../tests/test_runtime_assets.py).

## D8. Μαζική read-only έρευνα → DeepSeek· κρίση και production → Claude

Ο DeepSeek worker (`scripts/research.py`) κάνει discovery, πρώτη ταξινόμηση,
metadata και license evidence. Το Claude επικυρώνει, αποφασίζει και υλοποιεί.
Ο DeepSeek **δεν** τροποποιεί production κώδικα.
