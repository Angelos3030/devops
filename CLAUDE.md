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

## Συντονισμός agents

Πριν ξεκινήσεις, διάβασε `STATUS.md` και `git status`. Μην επαναλαμβάνεις εργασία άλλου agent,
μην επαναφέρεις αλλαγές που δεν έκανες και ενημέρωσε το `STATUS.md` όταν αλλάζει ουσιαστικά η
κατάσταση του project. Τα secrets μπαίνουν μόνο σε `.env`/platform variables, ποτέ σε docs,
chat, screenshots ή commits.
