# 12 — Meta App Review: Πλήρης Οδηγός Βήμα-Βήμα

> Στόχος: άδεια να ποστάρεις αυτόματα σε Facebook Pages & Instagram Business εκ μέρους
> των πελατών σου. Είναι το πιο αργό κομμάτι — **ξεκίνα ΣΗΜΕΡΑ**, τρέχει παράλληλα.

> ⚠️ Η Meta αλλάζει συχνά UI/ονόματα. Τα βήματα είναι ο σκελετός· επιβεβαίωσε ζωντανά
> στο [developers.facebook.com](https://developers.facebook.com) και
> [Instagram Platform docs](https://developers.facebook.com/docs/instagram-platform).

---

## Τι θα χρειαστείς (προαπαιτούμενα)
- [ ] Προσωπικός λογαριασμός Facebook (developer).
- [ ] **Meta Business Account** ([business.facebook.com](https://business.facebook.com)).
- [ ] Μία **test** Facebook Page + **Instagram Business/Creator** account (δικά σου, για δοκιμές).
- [ ] **Privacy Policy URL** (στα ελληνικά, δημόσια προσβάσιμη).
- [ ] **Terms of Service URL**.
- [ ] **User Data Deletion URL**.
- [ ] Domain για την εφαρμογή (μπορεί να είναι το landing του προϊόντος).

---

## ΦΑΣΗ Α — Δημιουργία App (1 ώρα)

- [ ] Πήγαινε [developers.facebook.com](https://developers.facebook.com) → **My Apps** → **Create App**.
- [ ] Τύπος: **Business**.
- [ ] Σύνδεσε το **Meta Business Account**.
- [ ] Στο App Dashboard → **Add Products**:
  - [ ] **Instagram** (Instagram Graph API / Instagram Platform)
  - [ ] **Facebook Login for Business**
- [ ] App Settings → **Basic**: συμπλήρωσε
  - [ ] App name, contact email
  - [ ] Website URL: `https://getvitrina.gr`
  - [ ] **Privacy Policy URL**: `https://getvitrina.gr/privacy.html`
  - [ ] **Terms URL**: `https://getvitrina.gr/terms.html`
  - [ ] **User Data Deletion URL**: `https://getvitrina.gr/data-deletion.html`
  - [ ] App icon: `web/icon-1024.png`
  - [ ] App Domain + Category

---

## ΦΑΣΗ Β — Permissions που θα ζητήσεις

Για auto-posting σε FB Page + IG Business χρειάζεσαι:

| Permission | Γιατί |
|------------|-------|
| `instagram_basic` | Βασική πρόσβαση IG |
| `instagram_content_publish` | **Δημοσίευση posts στο IG** (το κρίσιμο) |
| `pages_show_list` | Λίστα των Pages του χρήστη |
| `pages_read_engagement` | Ανάγνωση δεδομένων Page |
| `pages_manage_posts` | **Δημοσίευση posts στο FB Page** |
| `business_management` | ΜΗΝ το ζητήσεις στο MVP, εκτός αν υπάρχει συγκεκριμένη απαίτηση στο review |

> Για το πρώτο review ζήτα μόνο organic posting permissions. Όχι `ads_read`,
> `ads_management` ή άλλα Marketing API permissions πριν δουλέψει το core MVP.

> Χωρίς App Review, αυτά δουλεύουν **μόνο** σε ρόλους της δικής σου app (admin/developer/
> tester). Γι' αυτό μπορείς να αναπτύσσεις/δοκιμάζεις **πριν** την έγκριση.

---

## ΦΑΣΗ Γ — Ανάπτυξη σε Development Mode (παράλληλα με το review)

> Δεν περιμένεις το review για να δουλέψεις! Σε dev mode όλα δουλεύουν σε δικούς σου λογ/σμούς.

- [ ] Πρόσθεσε τον εαυτό σου + το test μαγαζί ως **Roles → Testers**.
- [ ] Υλοποίησε το **OAuth flow**: ο πελάτης συνδέει τη FB Page + IG Business του.
- [ ] Πάρε **Page Access Token** (long-lived) → αποθήκευσέ το σε **vault** (auto-refresh).
- [ ] Δοκίμασε **πραγματικό post** στο test IG/FB (το ΒΗΜΑ 5-6 του master plan).
- [ ] Αυτό σου δίνει και το **demo** που χρειάζεται το review (βλ. Φάση Δ).

### Το IG publishing flow (2 βήματα — βάλ' το στο `meta-publisher`)
```
1) POST /{ig-user-id}/media          → creation_id  (εικόνα + caption)
2) POST /{ig-user-id}/media_publish  → publish (creation_id)
```
FB Page: `POST /{page-id}/photos` (με εικόνα) ή `/{page-id}/feed` (κείμενο).

---

## ΦΑΣΗ Δ — Προετοιμασία υλικού για το Review

Η Meta θέλει να **δει** ότι χρησιμοποιείς σωστά το κάθε permission:

- [ ] **Screencast video** (υποχρεωτικό): δείξε ΟΛΟ το flow —
  1. Φαίνεται το `https://getvitrina.gr` και το brand Vitrina.
  2. Φαίνονται σύντομα τα `privacy.html` και `data-deletion.html`.
  3. Ο χρήστης κάνει login με Facebook.
  4. Φαίνεται καθαρά το OAuth consent dialog και τα permissions.
  5. Διαλέγει/συνδέει τη Page + IG account του.
  6. Η app δημοσιεύει ένα post στο IG + FB.
  7. Φαίνεται το post live.
- [ ] **Step-by-step οδηγίες** (κείμενο) πώς να αναπαράγει ο reviewer το flow.
- [ ] **Use-case description** ανά permission (γιατί το χρειάζεσαι). Παράδειγμα:
  > «Η εφαρμογή δημοσιεύει marketing posts στις σελίδες/IG λογαριασμούς μικρών
  >  επιχειρήσεων, **με τη ρητή συγκατάθεσή τους**, στο πλαίσιο συνδρομητικής
  >  υπηρεσίας διαχείρισης social media.»
- [ ] **Test credentials** για τον reviewer (test user/μαγαζί).

---

## ΦΑΣΗ Ε — Business Verification (συχνά απαιτείται)

- [ ] Στο **Business Settings → Security Center** → ξεκίνα **Business Verification**.
- [ ] Χρειάζεται: νόμιμη επιχείρηση (ΑΦΜ/έγγραφα), διεύθυνση, τηλέφωνο που επιβεβαιώνεται.
- [ ] ⚠️ Εδώ μπλέκει το **νομικό**: για να βγάλεις έσοδα + business verification, μάλλον
  χρειάζεσαι **μπλοκάκι/εταιρεία**. Ρώτα λογιστή (δες [06-RISKS-LEGAL.md](06-RISKS-LEGAL.md)).

---

## ΦΑΣΗ ΣΤ — Submit for Review

- [ ] App Dashboard → **App Review → Permissions and Features**.
- [ ] Για κάθε permission (λίστα Φάσης Β) → **Request** → συμπλήρωσε use-case + screencast.
- [ ] **Submit**.
- [ ] Περίμενε: συνήθως **μερικές μέρες έως 2-3 βδομάδες** (μερικές φορές πάνε πίσω-μπρος).
- [ ] Αν απορριφθεί: διάβασε τον λόγο, διόρθωσε το screencast/περιγραφή, ξανα-submit.

---

## ΦΑΣΗ Ζ — Μετά την έγκριση

- [ ] **Switch app σε Live mode**.
- [ ] Τώρα ΟΠΟΙΟΣΔΗΠΟΤΕ πελάτης μπορεί να συνδέσει τη Page/IG του (όχι μόνο testers).
- [ ] Onboard τους 3 πραγματικούς πελάτες (ΒΗΜΑ 9 master plan).

---

## ⏱️ Χρονοδιάγραμμα (ρεαλιστικό)
```
Μέρα 1:      Create app + products + privacy policy
Μέρα 1-3:    OAuth flow + test post (dev mode) → φτιάχνεις το demo
Μέρα 3-5:    Business verification (αν χρειάζεται) — μπορεί να αργήσει
Μέρα 5:      Submit for review
Μέρα 5-25:   Αναμονή έγκρισης (δούλεψε τα υπόλοιπα στο μεταξύ)
```

## ✅ Checklist «έτοιμος για submit»
- [ ] App + Instagram + FB Login products
- [ ] Privacy Policy + Terms URLs
- [ ] OAuth flow δουλεύει (test)
- [ ] Πραγματικό post σε test IG + FB (αποδεικτικό)
- [ ] Screencast video όλου του flow
- [ ] Use-case κείμενο ανά permission
- [ ] Test credentials για reviewer
- [ ] Business verification (αν ζητηθεί)

## 💡 Συμβουλές που γλιτώνουν απορρίψεις
1. **Δείξε ξεκάθαρα τη συγκατάθεση** του χρήστη στο video (το πιο συχνό σημείο απόρριψης).
2. Το screencast να είναι **πλήρες & καθαρό** — κάθε permission να φαίνεται σε χρήση.
3. Privacy policy να **αναφέρει ρητά** τι δεδομένα παίρνεις και πώς τα χρησιμοποιείς.
4. Βάλε ξεχωριστό **Data Deletion URL** και όχι μόνο μια θαμμένη παράγραφο στο privacy.
5. Μην ζητάς permissions που δεν χρησιμοποιείς — απορρίπτεται.
6. Κράτα app σε dev mode όσο αναπτύσσεις — δεν χρειάζεσαι review για testers.
7. Δοκίμασε test credentials, test Page και IG Business ακριβώς πριν το submit.
8. Παντού ίδιο brand: **Vitrina**.

> ⚠️ Νομικό: η Business Verification + τα έσοδα = πιθανώς χρειάζεσαι μπλοκάκι/εταιρεία.
> Δεν είναι νομική συμβουλή — ρώτα λογιστή. Δες [06-RISKS-LEGAL.md](06-RISKS-LEGAL.md).
