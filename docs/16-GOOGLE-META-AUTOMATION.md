# Google Business Profile + Meta Automation

Τελευταίος έλεγχος απαιτήσεων: 2026-08-06.

## Τι προσφέρει το Vitrina

Για κάθε πελάτη στοχεύουμε σε μία ενιαία ροή:

1. site και domain,
2. Google Business Profile σε Search/Maps,
3. Facebook Page και επαγγελματικό Instagram,
4. προγραμματισμένα οργανικά posts,
5. προαιρετικές πληρωμένες διαφημίσεις με ρητή έγκριση και budget πελάτη.

## Τι δεν γίνεται 100% αυτόματα

- Η αρχική δημιουργία/διεκδίκηση και επαλήθευση Google Business Profile απαιτεί συμμετοχή του ιδιοκτήτη.
- Ο πελάτης πρέπει να εξουσιοδοτήσει το Vitrina μέσω Google OAuth.
- Facebook Page, Instagram Professional account, Business Portfolio και ad account πρέπει να ανήκουν
  στον πελάτη ή να μας δοθεί νόμιμη πρόσβαση.
- Καμία διαφήμιση δεν δημοσιεύεται και κανένα budget δεν ξοδεύεται χωρίς σαφή έγκριση.

Μετά την επαλήθευση και το OAuth, η καθημερινή διαχείριση μπορεί να αυτοματοποιηθεί σε μεγάλο βαθμό.

## Google Business Profile - σειρά έγκρισης

1. Δημιουργούμε/ολοκληρώνουμε το επίσημο Vitrina Business Profile και το συνδέουμε με το live site.
2. Το profile πρέπει να είναι verified και ενεργό για τουλάχιστον 60 ημέρες πριν από αίτηση GBP API access.
3. Δημιουργούμε Google Cloud project και GBP Organization account.
4. Ρυθμίζουμε OAuth consent screen, privacy policy, terms, support email και verified domains.
5. Υποβάλλουμε αίτηση Basic API Access από email που είναι owner/manager του profile.
6. Μετά την έγκριση ενεργοποιούμε τα Business Profile APIs και ελέγχουμε ότι το quota δεν είναι 0.
7. Υλοποιούμε OAuth με scope `https://www.googleapis.com/auth/business.manage` και ασφαλή refresh tokens.

Η Google αναφέρει ότι οι αιτήσεις συνήθως εξετάζονται εντός 14 ημερών, αλλά αυτό δεν είναι εγγύηση.

### Αυτοματισμοί μετά την έγκριση

- ενημέρωση επωνυμίας, κατηγορίας, ωραρίου και υπηρεσιών,
- προσθήκη website, τηλεφώνου και φωτογραφιών,
- Google Business posts,
- ανάγνωση και υποβοηθούμενες απαντήσεις σε reviews,
- performance insights όπου διατίθενται.

## Meta - οργανικά Facebook/Instagram posts

### Προαπαιτούμενα

- Meta Business verification και ολοκληρωμένα app settings,
- live privacy policy, terms και data-deletion URL,
- Facebook Login flow και reviewer test account/assets,
- Facebook Page συνδεδεμένη με Instagram Professional account για Instagram publishing.

### Ελάχιστες λειτουργικές άδειες

- `pages_show_list`
- `pages_read_engagement`
- `pages_manage_posts`
- `instagram_basic`
- `instagram_content_publish`

Ζητάμε μόνο τις άδειες που χρησιμοποιεί πραγματικά το demo. Κάθε permission πρέπει να φαίνεται
σε καθαρό screencast: login, consent, επιλογή Page/account, δημιουργία post, δημοσίευση και αποτέλεσμα.

## Meta - πληρωμένες διαφημίσεις

Οι διαφημίσεις είναι δεύτερη, ανεξάρτητη φάση μετά τα οργανικά posts.

Χρειάζονται:

- Marketing API product,
- `ads_management` για δημιουργία/αλλαγή campaigns,
- `ads_read` όπου απαιτείται reporting,
- ενδεχομένως `business_management` μόνο αν το πραγματικό flow το απαιτεί,
- App Review/Advanced Access και το τρέχον Marketing API access tier,
- πραγματικό test ad account και πλήρης reviewer walkthrough.

Το Vitrina πρέπει να κρατά draft → customer approval → publish. Daily και monthly spend caps,
audit log, pause switch και campaign status είναι υποχρεωτικά πριν από production ad spend.

## Σειρά υλοποίησης

1. Ολοκλήρωση live Vitrina domain, privacy, terms και data deletion.
2. Meta οργανικό posting end-to-end σε δικά μας test assets.
3. Meta App Review για Page + Instagram publishing permissions.
4. Google Business Profile του Vitrina: verified, πλήρες και 60+ ημερών.
5. Google Cloud/Organization/OAuth και αίτηση GBP API access.
6. Production onboarding ώστε κάθε πελάτης να συνδέει Google και Meta με OAuth.
7. Ads drafts και approval workflow.
8. Meta Marketing API review μόνο όταν το ad flow είναι πλήρως δοκιμασμένο.

## Σημερινό επόμενο βήμα

Προτεραιότητα είναι η Meta οργανική ροή και το review package, επειδή το Google API access έχει
υποχρεωτική προϋπόθεση verified/active GBP 60+ ημερών. Παράλληλα δημιουργούμε τώρα το Vitrina GBP,
ώστε να αρχίσει να μετρά αυτή η περίοδος.

## Επίσημες πηγές

- Google GBP prerequisites: https://developers.google.com/my-business/content/prereqs
- Google GBP OAuth: https://developers.google.com/my-business/content/implement-oauth
- Google GBP API overview: https://developers.google.com/my-business/ref_overview
- Meta Instagram API official Postman workspace: https://www.postman.com/meta/workspace/instagram/
- Meta Business SDK: https://github.com/facebook/facebook-python-business-sdk
