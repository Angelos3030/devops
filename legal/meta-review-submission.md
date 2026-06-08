# Meta App Review — Έτοιμα κείμενα για το submission

> Αντίγραψε-επικόλλησε αυτά στη φόρμα του App Review. Συμπλήρωσε τα [ΑΓΚΥΛΕΣ].

## App description (γενική περιγραφή της εφαρμογής)
> Η «Vitrina» είναι μια συνδρομητική υπηρεσία δημιουργίας website και διαχείρισης social media για μικρές
> ελληνικές επιχειρήσεις. Οι επιχειρήσεις συνδέουν τη δική τους Σελίδα Facebook και
> τον λογαριασμό τους Instagram Business, και η εφαρμογή δημοσιεύει για λογαριασμό τους
> προγραμματισμένο περιεχόμενο (κείμενα και εικόνες), με τη ρητή συγκατάθεσή τους.

## URLs για App Settings

- Website URL: `https://getvitrina.gr`
- Privacy Policy URL: `https://getvitrina.gr/privacy.html`
- Terms of Service URL: `https://getvitrina.gr/terms.html`
- User Data Deletion URL: `https://getvitrina.gr/data-deletion.html`
- OAuth Redirect URI: `https://api.getvitrina.gr/connect/callback`

## Use-case ανά permission (αντίγραψε στο αντίστοιχο πεδίο)

**`instagram_basic`**
> Χρειάζεται για να αναγνωρίσουμε τον λογαριασμό Instagram Business που ο χρήστης
> συνδέει, ώστε να δημοσιεύουμε στο σωστό προφίλ.

**`instagram_content_publish`**
> Χρειάζεται για να δημοσιεύουμε εικόνες με λεζάντες στον λογαριασμό Instagram Business
> του χρήστη, ως μέρος της υπηρεσίας προγραμματισμένων αναρτήσεων που έχει αγοράσει.

**`pages_show_list`**
> Χρειάζεται για να ανακτήσουμε τη λίστα των Σελίδων Facebook που ο χρήστης διαχειρίζεται
> (μέσω `/me/accounts`) και να την εμφανίσουμε στην εφαρμογή ώστε ο χρήστης να επιλέξει
> ποια Σελίδα θα συνδεθεί — εμφανίζονται κάρτες ανά Σελίδα, ο χρήστης κλικάρει μία.

**`pages_read_engagement`**
> Χρειάζεται για να διαβάζουμε βασικές πληροφορίες της Σελίδας που επέλεξε ο χρήστης,
> ώστε να λειτουργεί σωστά η δημοσίευση.

**`pages_manage_posts`**
> Χρειάζεται για να δημοσιεύουμε αναρτήσεις στη Σελίδα Facebook του χρήστη, ως μέρος
> της υπηρεσίας προγραμματισμένων αναρτήσεων.

> Σημείωση: Μην ζητήσεις `business_management`, `ads_read` ή `ads_management` στο MVP.
> Το πρώτο review πρέπει να δείχνει μόνο organic Facebook Page + Instagram Business publishing.

## Screencast script (τι να δείξεις στο video — ΚΡΙΣΙΜΟ)
Γύρισε ένα καθαρό video (2-4 λεπτά) που δείχνει ΟΛΟ το flow:

1. **Αρχική/landing:** Φαίνεται το `https://getvitrina.gr` και το brand Vitrina.
2. **Privacy/Data deletion:** Άνοιξε σύντομα `privacy.html` και `data-deletion.html` για να φανούν δημόσια.
3. **Login:** Ο χρήστης πατά «Σύνδεση με Facebook» → εμφανίζεται το Facebook OAuth dialog.
4. **Συγκατάθεση:** Φαίνεται καθαρά ότι ο χρήστης δίνει άδεια (τα permissions στο dialog).
   👉 **Αυτό είναι το #1 σημείο που ελέγχει η Meta — δείξ' το ξεκάθαρα.**
5. **Επιλογή Σελίδας:** Μετά το OAuth, η εφαρμογή εμφανίζει λίστα με τις Σελίδες Facebook του χρήστη.
   Ο χρήστης κλικάρει **«Επέλεξε»** στη Σελίδα που θέλει — η εφαρμογή αποθηκεύει token μόνο για αυτή.
6. **Δημιουργία post:** Φαίνεται η εφαρμογή να ετοιμάζει caption + εικόνα.
7. **Δημοσίευση:** Πατάει «Δημοσίευση» ή τρέχει το demo publish flow → το post ανεβαίνει.
8. **Επιβεβαίωση:** Δείξε το post **live** στο Facebook ΚΑΙ στο Instagram.

## Reviewer instructions (βήματα αναπαραγωγής)
> 1. Πήγαινε στο https://getvitrina.gr/connect.html
> 2. Πάτησε «Σύνδεση με Facebook» και κάνε login με τα test credentials παρακάτω.
> 3. Επίλεξε τη test Σελίδα και τον test λογαριασμό Instagram.
> 4. Πάτησε «Δημιουργία post» και μετά «Δημοσίευση».
> 5. Δες το δημοσιευμένο post στη Σελίδα/IG.
>
> **Test credentials:** [TEST_EMAIL] / [TEST_PASSWORD]
> **Test Page:** [όνομα] · **Test IG:** [@handle]

## Συχνοί λόγοι απόρριψης (απόφυγέ τους)
- ❌ Δεν φαίνεται η συγκατάθεση του χρήστη → δείξε το OAuth dialog καθαρά.
- ❌ Ζητάς permission που δεν χρησιμοποιείς στο video → ζήτα μόνο όσα δείχνεις.
- ❌ Privacy policy ελλιπής/μη προσβάσιμη → δημόσιο URL, αναφέρει Meta data.
- ❌ Δεν υπάρχει ξεχωριστό data deletion URL → βάλε `https://getvitrina.gr/data-deletion.html`.
- ❌ Άλλο brand στο site και άλλο στη φόρμα review → παντού γράφουμε Vitrina.
- ❌ Screencast θολό/ασαφές → καθαρή ανάλυση, αργά, με κάθε βήμα ορατό.
- ❌ Test account/test Page δεν δουλεύουν → δοκίμασε τα credentials ακριβώς πριν το submit.
