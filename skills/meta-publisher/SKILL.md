---
name: meta-publisher
description: >
  Δημοσιεύει posts (caption + εικόνα) σε Facebook Page & Instagram Business
  μέσω του Meta Graph API / Meta MCP. Χρησιμοποίησέ το όταν ένα έτοιμο post
  πρέπει να αναρτηθεί στα social ενός πελάτη.
---

# Πώς ποστάρω σε Facebook & Instagram

## Προϋποθέσεις (κρίσιμα)
- Ο πελάτης ΠΡΕΠΕΙ να έχει **Facebook Page** + **Instagram Business/Creator** account
  συνδεδεμένα. Personal accounts ΔΕΝ υποστηρίζονται για auto-posting.
- Η εφαρμογή μας πρέπει να έχει περάσει **Meta App Review**.
- Τα credentials (tokens) ζουν σε **vault** (auto-refresh) — ΠΟΤΕ σε prompt/log/κώδικα.

## Χρησιμοποίησε το Meta MCP (προτιμότερο)
Από 29/4/2026 υπάρχει επίσημο Meta MCP που χειρίζεται posting/reporting.
Κάλεσε τα διαθέσιμα tools του MCP — μην χτίζεις raw HTTP εκτός αν χρειαστεί.

## Ροή δημοσίευσης
1. Πάρε το έτοιμο post: `{ caption, image_url|image_file, hashtags }`.
2. Συνδύασε caption + hashtags (hashtags στο τέλος ή σε πρώτο σχόλιο για IG).
3. Δημοσίευσε:
   - **Instagram:** εικόνα + caption (το IG ΑΠΑΙΤΕΙ εικόνα — όχι text-only).
   - **Facebook:** εικόνα + caption (ή text-only αν δεν υπάρχει εικόνα).
4. Επιβεβαίωσε επιτυχία· αποθήκευσε το post_id + timestamp.

## Κανόνες μορφής
- **Instagram:** πάντα εικόνα. Caption ≤ ~2.200 χαρακτήρες. Hashtags 3-10.
- **Facebook:** εικόνα προαιρετική αλλά συνιστάται. Χωρίς όριο hashtag αλλά κράτα 2-3.
- Καλύτερες ώρες (Ελλάδα): πρωί ~9-11 ή απόγευμα ~18-20. Πρόγραμμα αναλόγως.

## Χειρισμός σφαλμάτων
- Token expired → trigger refresh (μέσω vault) και retry.
- Rate limit → backoff & retry αργότερα.
- Αποτυχία IG αλλά επιτυχία FB → κατέγραψε μερική επιτυχία, μην ξαναποστάρεις FB.

## Δες και
`publish.py` — βοηθητικός κώδικας (σκελετός) για το ντετερμινιστικό κομμάτι.
Το «τι» (caption) το γράφει το `social-post-gr`· αυτό το skill είναι το «πώς δημοσιεύω».
