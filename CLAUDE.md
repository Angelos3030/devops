# CLAUDE.md - Vitrina Site Production Contract

Αυτό είναι το κεντρικό συμβόλαιο για κάθε AI agent που δημιουργεί ή αλλάζει site στο Vitrina.
Διάβασέ το πριν πειράξεις templates, client data, previews ή production sites.

## Στόχος

Κάθε πρώτη παρουσίαση πρέπει να μοιάζει με custom δουλειά σύγχρονου studio, όχι με generic template.
Ο πελάτης πρέπει να βλέπει αμέσως:

- ποιος είναι,
- τι προσφέρει,
- πού εξυπηρετεί,
- πραγματική ή κατάλληλη οπτική απόδειξη,
- μία καθαρή ενέργεια: κλήση, κράτηση, ραντεβού ή προσφορά.

Το production engine παραμένει το multi-tenant Next.js app στο `sites/`. Τα standalone prototypes
χρησιμοποιούνται για εξερεύνηση και έγκριση· δεν αποτελούν δεύτερη production αρχιτεκτονική.

## Υποχρεωτικά Skills

Πριν από design ή υλοποίηση διάβασε, με αυτή τη σειρά:

1. `skills/vitrina-design-system/SKILL.md`
2. `docs/18-VERTICAL-DESIGN-INTELLIGENCE.md`
3. `skills/vitrina-design-system/references/design-spec.md`
4. `skills/vitrina-design-system/references/design-routes.md`
5. `skills/greek-website/SKILL.md`
6. `skills/local-seo-gr/SKILL.md`
7. `skills/brand-builder-gr/SKILL.md` και `skills/vitrina-logo-system/SKILL.md` όταν χρειάζεται brand/logo.
8. `skills/vitrina-theme-builder/SKILL.md` **υποχρεωτικά** όταν δημιουργείται νέο theme/template.

### Νέα themes: μόνο μέσω reference

Trigger: `New theme | Vertical: dentist | Reference: https://…` → ακολούθησε
`skills/vitrina-theme-builder/SKILL.md`. Μηχανική συλλογή πρώτα, compact ανάλυση
(Keep/Adapt/Discard/Sections/Tokens/Customizable/Locked/Risks), **ρητή έγκριση**, μετά κώδικας.
Απαγορεύεται theme «από έμπνευση» ή implementation πριν την έγκριση. Ποτέ proprietary κώδικας,
λογότυπα, κείμενα ή φωτογραφίες — μόνο σχεδιαστική λογική.

## End-to-End Workflow

### 1. Intake και facts

Συγκέντρωσε όσα υπάρχουν: επωνυμία, επάγγελμα, πόλη/περιοχές, τηλέφωνο, email, υπηρεσίες,
ωράριο, ύφος, διακριτικά πλεονεκτήματα, social links και φωτογραφίες. Μην επινοείς χρόνια
εμπειρίας, πιστοποιήσεις, κριτικές, τιμές ή έργα.

Τα κενά που δεν εμποδίζουν το preview συμπληρώνονται με ασφαλή προσωρινά defaults και
καταγράφονται. Ρώτησε τον πελάτη μόνο για στοιχεία που αλλάζουν ουσιαστικά το αποτέλεσμα.

### 2. Photo mode

Κατάταξε το project σε έναν από τους παρακάτω τρόπους:

- `real`: υπάρχουν αρκετές καλές φωτογραφίες πελάτη. Αυτές έχουν προτεραιότητα.
- `mixed`: υπάρχουν λίγες ή μέτριες φωτογραφίες. Βελτίωσέ τες και συμπλήρωσε με νόμιμα
  stock ή AI visuals που δεν παρουσιάζονται ως πραγματικά έργα.
- `no-photo`: δεν υπάρχουν φωτογραφίες. Το site πρέπει πάλι να είναι πλήρες και εντυπωσιακό.
  Χρησιμοποίησε profession-specific licensed/AI imagery, υλικά, λεπτομέρειες, typography και
  layout. Σήμανε τις ενδεικτικές εικόνες όπου μπορεί να δημιουργηθεί παρανόηση.

Ποτέ placeholder κουτιά, broken images, άσχετο stock ή ψεύτικο before/after. Κάθε asset πρέπει
να έχει σαφή προέλευση και κατάλληλο `alt`. Οι εικόνες βελτιστοποιούνται σε WebP/AVIF όπου
υποστηρίζεται, με responsive sizes και σταθερό aspect ratio για να αποφεύγεται layout shift.

### 3. Spec πριν τον κώδικα

Γράψε σύντομο design spec με τα 9 πεδία του `design-spec.md`: στόχος, κοινό, conversion,
οπτική κατεύθυνση, typography, palette, sections, responsive συμπεριφορά και accessibility.

Το production chooser επιστρέφει έως εννέα ranked επιλογές από το vertical profile.
Οι επιλογές πρέπει να διαφέρουν σε layout, hero, content rhythm, typography και motion,
όχι μόνο σε χρώμα. Μια ακατάλληλη επιλογή αποκλείεται αντί να γεμίζει τεχνητά το grid.

Μην προσθέτεις νέο template επειδή αλλάζει μόνο palette ή γραμματοσειρά. Νέο template
δικαιολογείται μόνο όταν προσθέτει επαναχρησιμοποιήσιμη δομή που λείπει από τη συλλογή.

### 4. Build

- Πρώτο viewport: επωνυμία, αντικείμενο, περιοχή και primary CTA.
- Χρησιμοποίησε semantic HTML και αληθινά headings (`h1` μία φορά).
- Βάλε πραγματικές ενότητες υπηρεσιών, proof/gallery, about, περιοχές εξυπηρέτησης και contact.
- Πρόσθεσε sticky ή σαφή navigation και fixed mobile CTA όταν ταιριάζει.
- Όλα τα links, anchors, menu controls, modal/forms και `tel:` πρέπει να λειτουργούν.
- Χρησιμοποίησε self-hosted fonts με ελληνικό subset. Όχι runtime Google Fonts request.
- Μην χρησιμοποιείς εξωτερικό tracking χωρίς consent strategy.
- Μην βάζεις τεράστιο hero που κρύβει όλη την επόμενη ενότητα σε κάθε viewport.
- Μην χρησιμοποιείς template filler, lorem ipsum ή γενικόλογο AI copy.

### 5. Responsive contract

Έλεγξε τουλάχιστον:

- mobile: 390 x 844,
- tablet: 768 x 1024,
- desktop: 1440 x 1024.

Σε κάθε viewport:

- δεν υπάρχει horizontal overflow,
- κείμενο και κουμπιά δεν κόβονται ή επικαλύπτονται,
- navigation και modal λειτουργούν με touch και keyboard,
- tap targets είναι τουλάχιστον περίπου 44 px,
- εικόνες έχουν σωστό crop και δεν κρύβουν το προϊόν/έργο,
- το primary CTA είναι ορατό και κατανοητό,
- fixed στοιχεία δεν καλύπτουν περιεχόμενο.

### 6. SEO και εμπιστοσύνη

Κάθε production site χρειάζεται:

- μοναδικό Greek title και meta description,
- canonical URL όταν υπάρχει domain,
- LocalBusiness JSON-LD με αληθινά NAP στοιχεία,
- σωστό Open Graph image,
- επάγγελμα + περιοχή γραμμένα φυσικά σε headings/copy,
- indexable semantic content, sitemap και robots σύμφωνα με το production routing,
- ίδιες πληροφορίες επωνυμίας/διεύθυνσης/τηλεφώνου παντού.

Δεν γίνεται keyword stuffing και δεν δημιουργούνται ψεύτικες τοποθεσίες ή reviews.

### 7. QA πριν την παρουσίαση

Ο agent πρέπει να ανοίξει το site σε πραγματικό browser και να ελέγξει οπτικά desktop/mobile.
Δεν αρκεί να περάσει το build.

Υποχρεωτικά:

1. production build,
2. υπάρχοντα frontend/e2e tests,
3. browser screenshots desktop και mobile,
4. έλεγχος console errors και broken network assets,
5. δοκιμή navigation, CTA, phone link και form flow,
6. σύγκριση με το εγκεκριμένο concept/reference,
7. καταγραφή QA με τελικό αποτέλεσμα `passed` πριν δοθεί link.

Για τις **δικές μας** σελίδες (`web/`), μετά από κάθε deploy τρέχει υποχρεωτικά
`node sites/tests/production_qa.mjs` — Playwright + Lighthouse μαζί. Τα thresholds και το
γιατί υπάρχει κάθε έλεγχος: `docs/23-PRODUCTION-QA.md`. Τρεις κανόνες από εκεί ισχύουν
παντού: lazy εικόνες επαληθεύονται **μετά από `img.decode()`**, ξένο περιεχόμενο μπαίνει
ως **στιγμιότυπο + σύνδεσμος και ποτέ ως iframe** (`X-Frame-Options` αφήνει κενό πλαίσιο),
και **κανένα test δεν γράφει στη βάση παραγωγής** — κόψε το αίτημα και επαλήθευσε το σώμα.

### 8. Έγκριση, αποθήκευση και live

Η επιλογή template, το κείμενο και τα assets αποθηκεύονται ως structured client/site data στη
Supabase. Μην κρατάς κρίσιμες αλλαγές μόνο σε ένα standalone HTML. Το production render γίνεται
από το `sites/` και πρέπει να παραμένει επεξεργάσιμο από dashboard/chat editor.

Το chat-to-edit είναι πάντα **draft first**: ο AI provider επιστρέφει allowlisted JSON patch,
το dashboard το δείχνει μόνο στο preview και απαιτεί ρητό **Έγκριση αλλαγών**. Η απόρριψη δεν
γράφει τίποτα στη βάση. Ποτέ μην επαναφέρεις αυτόματη αποθήκευση απευθείας από AI απάντηση.

Μετά την έγκριση:

1. αποθήκευσε layout και client data,
2. τρέξε `python scripts/e2e.py --quick`,
3. τρέξε `cd sites && npm run build`,
4. σύνδεσε domain μόνο με τη διαδικασία του `docs/14-DOMAIN-AUTOMATION.md`,
5. επαλήθευσε HTTPS, canonical, sitemap, robots και production CTA,
6. δώσε το live URL στον πελάτη.

Μην αλλάζεις DNS live domain για δοκιμή και μην δημοσιεύεις χωρίς έγκριση.

## Social publishing contract

Το social scope είναι ξανά ενεργό από 2026-08-06. Διάβασε `docs/18-SOCIAL-ENGINE.md` πριν
αλλάξεις posts, OAuth ή publishing. Το `src/daily_post.py` δημιουργεί μόνο drafts. Πραγματική
δημοσίευση επιτρέπεται αποκλειστικά μέσω `src/social_engine.py`, μετά από ρητή έγκριση και
με audit log. Μην επαναφέρεις direct generate-and-publish flow και μην ενεργοποιήσεις ads spend.

## Definition of Done

Ένα site είναι έτοιμο μόνο όταν:

- είναι συγκεκριμένο για τον πελάτη και το επάγγελμα,
- έχει ολοκληρωμένη λύση και στο `no-photo` mode,
- είναι όμορφο και λειτουργικό σε mobile, tablet και desktop,
- δεν περιέχει invented facts ή placeholders,
- περνά build, tests και browser QA,
- έχει βασικό local SEO και σωστά NAP στοιχεία,
- όλες οι ενέργειες λειτουργούν,
- είναι αποθηκευμένο στο production data model και όχι μόνο τοπικά,
- έχει εγκριθεί πριν συνδεθεί με domain.

## Refactor: «αχρησιμοποίητο» δεν το αποφασίζει το text search

**Ποτέ μη χαρακτηρίσεις διαδρομή, φάκελο ή module αχρησιμοποίητο μόνο από
αναζήτηση κειμένου.** Μετρήθηκε: το `grep "vitrina-design-system/templates"`
επιστρέφει **μηδέν αποτελέσματα** ενώ ο φάκελος διαβάζεται σε κάθε δημιουργία
site — γιατί η διαδρομή χτίζεται με `Path` segments και δεν υπάρχει πουθενά ως
συμβολοσειρά.

Πριν από κάθε διαγραφή ή μετακίνηση, έλεγξε **και τα πέντε**:

1. **σταθερές** που κρατούν τη διαδρομή (`TEMPLATE_DIR`, `ASSET_ROOT`, …)
2. **σύνθεση διαδρομής** — `Path(a)/b/c`, `os.path.join`, f-strings
3. **imports**, συμπεριλαμβανομένων των re-export από `__init__`/`index`
4. **δυναμική φόρτωση** — `importlib`, `require()`, glob, όνομα από μεταβλητή
5. **αλυσίδα κλήσης σε runtime** — ποιος endpoint ή background job το φτάνει

Και όπου γίνεται, **άφησε test που αποδεικνύει ότι η εξάρτηση χρησιμοποιείται**.
Ένα test είναι η μόνη μορφή τεκμηρίωσης που δεν παλιώνει σιωπηλά.

Το `skills/vitrina-design-system/templates/` είναι **runtime-critical**: δεν
μετακινείται και δεν διαγράφεται χωρίς migration plan και regression test.
Φυλάσσεται από το `tests/test_runtime_assets.py`.

## Μαζική έρευνα → DeepSeek worker

Μεγάλες, read-only εργασίες ανακάλυψης (GitHub repos, theme references, ανταγωνιστές,
αρχιτεκτονικά patterns, license research) περνάνε πρώτα από τον DeepSeek worker
(`scripts/research.py`, υλοποίηση στο `src/research_worker.py`) — όχι απευθείας από
το Claude. Το Claude διαβάζει το `research/<task-id>/summary.md`, επικυρώνει τα
σημαντικά συμπεράσματα και αποφασίζει/υλοποιεί· δεν ξαναρχίζει την ίδια έρευνα από
την αρχή. Production αλλαγές, migrations, security review και ενεργά refactors
(π.χ. το τρέχον Spine migration) μένουν πάντα στο Claude.

## Συντονισμός agents

Πριν ξεκινήσεις, διάβασε `STATUS.md` και `git status`. Μην επαναλαμβάνεις εργασία άλλου agent,
μην επαναφέρεις αλλαγές που δεν έκανες και ενημέρωσε το `STATUS.md` όταν αλλάζει ουσιαστικά η
κατάσταση του project. Τα secrets μπαίνουν μόνο σε `.env`/platform variables, ποτέ σε docs,
chat, screenshots ή commits.

### Παράλληλα Next.js builds

Δύο agents δεν επιτρέπεται να χρησιμοποιούν ταυτόχρονα το ίδιο `sites/.next`. Κάθε παράλληλος
dev/QA worker ορίζει μοναδικό directory, π.χ. PowerShell:

```powershell
$env:NEXT_DIST_DIR='.next-visual'; npx next dev -p 3800
```

Χρησιμοποίησε άλλο suffix/port ανά agent (`.next-agent2`, `.next-callout`, κ.λπ.). Το production
build χωρίς `NEXT_DIST_DIR` συνεχίζει να χρησιμοποιεί `.next`. Μην εκτελείς clean/delete σε
`.next*` όταν υπάρχει άλλος ενεργός agent. Τα browser screenshots γράφονται στο αγνοημένο
`sites/artifacts/`, ποτέ μέσα σε source directories.
