# Vitrina — Compliance & Approval Gate

Τελευταίος έλεγχος: 6 Αυγούστου 2026. Το αρχείο είναι operational checklist,
όχι υποκατάστατο γνωμοδότησης δικηγόρου ή λογιστή.

## Κανόνας κυκλοφορίας

Δεν ανοίγουμε onboarding σε τρίτους ούτε ξεκινάμε πληρωμένες συνδρομές πριν
κλείσουν όλα τα στοιχεία με ένδειξη **BLOCKER**.

## 1. Νόμιμη επιχείρηση — BLOCKER

- [ ] Έναρξη επιχείρησης και κατάλληλοι ΚΑΔ.
- [ ] Πραγματική νομική επωνυμία, ΑΦΜ, έδρα και email στο site, Stripe και Meta.
- [ ] Τα στοιχεία γράφονται παντού ακριβώς ίδια, χωρίς συντομογραφίες/παραλλαγές.
- [ ] Λογιστής επιβεβαιώνει ΦΠΑ, παραστατικά, myDATA και χειρισμό συνδρομών.
- [ ] Νομικός ελέγχει Terms, Privacy, DPA και πολιτική επιστροφών πριν το launch.

## 2. Meta — BLOCKER για λογαριασμούς πελατών

- [ ] Business Verification με πραγματικά εταιρικά έγγραφα.
- [ ] Access Verification ως Tech Provider, αν εμφανιστεί/απαιτηθεί.
- [ ] Domain verification για `getvitrina.gr` στο Business Manager.
- [ ] App Settings: App name, icon, domain, contact email, category.
- [ ] Public URLs: privacy, terms και data deletion, όλα HTTPS και χωρίς login.
- [ ] OAuth redirect ακριβώς `https://api.getvitrina.gr/connect/callback`.
- [ ] Ζητάμε μόνο `instagram_basic`, `instagram_content_publish`,
  `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`.
- [ ] Πραγματικό end-to-end test σε Page/IG Business που ανήκει σε app role.
- [ ] Συνεχές screencast: login, permissions, επιλογή asset, publish, live post.
- [ ] Οδηγίες reviewer + ενεργά test credentials.
- [ ] App Review/Advanced Access για κάθε permission.
- [ ] Live mode μόνο αφού εγκριθούν τα παραπάνω.
- [ ] Ετήσιο Data Use Checkup και ανάκληση/deauthorization ελέγχονται περιοδικά.

## 3. GDPR / ePrivacy — BLOCKER

- [x] Privacy notice: σκοποί, δεδομένα, νομικές βάσεις, αποδέκτες, transfers,
  retention, δικαιώματα, ΑΠΔΠΧ, deletion.
- [x] Τα customer sites δεν έχουν optional trackers/cookies και δεν εμφανίζουν banner.
- [ ] Αν προστεθεί analytics/advertising στη Vitrina, consent πριν από οποιοδήποτε
  optional request, ισότιμη απόρριψη και εύκολη ανάκληση.
- [x] Δημόσιες οδηγίες διαγραφής δεδομένων.
- [ ] Συμπλήρωση πραγματικού controller (επωνυμία, διεύθυνση, ΑΦΜ) μετά την έναρξη.
- [ ] Υπογεγραμμένο DPA άρθρου 28 με κάθε πελάτη.
- [ ] DPA/SCC και ρυθμίσεις privacy με κάθε subprocessor.
- [ ] Record of Processing Activities (ROPA) με owner και ημερομηνίες retention.
- [ ] Διαδικασία αιτημάτων δικαιωμάτων με identity check και ticket log.
- [ ] Τεχνική αυτόματη διαγραφή tokens/δεδομένων, όχι μόνο email οδηγίες.
- [ ] DPIA screening πριν από profiling, ευαίσθητα δεδομένα ή μεγάλη κλίμακα.

## 4. Ασφάλεια — BLOCKER

- [ ] Όλα τα κλειδιά ανανεώνονται, επειδή παλιά secrets εμφανίστηκαν σε chat.
- [ ] Meta tokens και service-role keys δεν αποθηκεύονται σε plaintext logs/client.
- [ ] Least privilege, MFA σε Meta/Stripe/Supabase/Cloudflare/Railway/GitHub.
- [ ] RLS και tenant-isolation tests στο Supabase.
- [ ] Backup/restore test και τεκμηριωμένος χρόνος διατήρησης backup.
- [ ] Incident register και διαδικασία ειδοποίησης εντός 72 ωρών όπου απαιτείται.
- [ ] Dependency/security scan πριν από κάθε production release.

## 5. Stripe / καταναλωτής — BLOCKER πριν την πρώτη χρέωση

- [x] Δημόσιο site με σαφή υπηρεσία, τιμές και στοιχεία υποστήριξης.
- [x] Terms, Privacy, cancellation/refund/dispute policy.
- [ ] Business name και website στο Stripe ταιριάζουν με τη νόμιμη επιχείρηση.
- [ ] Checkout δείχνει ποσό, νόμισμα, συχνότητα, trial και ημερομηνία χρέωσης.
- [ ] Ρητή επιβεβαίωση recurring subscription πριν την πληρωμή.
- [ ] Customer Portal ή ισοδύναμος απλός τρόπος ακύρωσης.
- [ ] Webhook signature verification και idempotency tests.
- [ ] Παραστατικό/τιμολόγιο και φορολογική ροή επιβεβαιωμένα από λογιστή.

## 6. Περιεχόμενο και διαφημίσεις

- [ ] Ο πελάτης δηλώνει ότι έχει δικαιώματα σε εικόνες, λογότυπα και claims.
- [ ] Approval log για posts/ads πριν τη δημοσίευση, με timestamp και έκδοση.
- [ ] Ειδικοί κανόνες για υγεία, νομικές/οικονομικές υπηρεσίες και regulated ads.
- [ ] Δεν δημιουργούμε ψεύτικες κριτικές, αποτελέσματα, προσφορές ή πιστοποιήσεις.
- [ ] AI output περνά ανθρώπινο έλεγχο για claims, τιμές και στοιχεία επικοινωνίας.

## Αποδεικτικά που κρατάμε

Κρατάμε screenshots/exports των approvals, εκδόσεις νομικών κειμένων, consent
records, reviewer screencast, test results, processor agreements, security tests
και incident/rights-request logs. Η συμμόρφωση πρέπει να αποδεικνύεται, όχι μόνο
να δηλώνεται.
