---
name: facebook-ads-gr
description: >
  Φτιάχνει draft Facebook/Instagram ads στα ελληνικά για μικρές ελληνικές
  επιχειρήσεις, με local targeting, budget πρόταση, copy variants, creative brief
  και approval-first κανόνες. Χρησιμοποίησέ το για Vitrina Growth, paid social
  ιδέες, Meta ads drafts, τοπικές διαφημίσεις, boost-worthy posts και μηνιαία
  ad reports για ταβέρνες, καφέ, κομμωτήρια, οδοντιατρεία, μάστορες και άλλα SMBs.
---

# Facebook Ads GR

## Χρυσός κανόνας
Ο agent ετοιμάζει διαφήμιση. Άνθρωπος εγκρίνει. Το backend βάζει budget limits.
Ποτέ μην προτείνεις αυτόματο spend χωρίς approval.

## Output format
Πάντα δώσε:

```json
{
  "objective": "messages | calls | website_clicks | local_reach",
  "audience": {
    "location": "πόλη/περιοχή",
    "radius_km": 3,
    "age": "25-65",
    "notes": "τοπικό κοινό, όχι υπερβολικά στενή στόχευση"
  },
  "budget": {
    "daily_eur": 3,
    "duration_days": 5,
    "needs_approval": true
  },
  "copy_variants": [
    {"primary_text": "...", "headline": "...", "cta": "Send Message"}
  ],
  "creative_brief": "...",
  "approval_summary": "Τι θα εγκρίνει ο άνθρωπος πριν τρέξει"
}
```

## Κανόνες copy
- Μίλα απλά, σαν τοπικό μαγαζί. Όχι agency jargon.
- Πούλα αφορμή: μενού ημέρας, ραντεβού, επείγον, εποχικό, προσφορά, νέα υπηρεσία.
- Μην υπόσχεσαι εγγυημένα αποτελέσματα.
- Να υπάρχει ένα CTA: μήνυμα, τηλέφωνο, κράτηση, οδηγίες.
- Να είναι έτοιμο για μικρό budget local campaign.

## Objective ανά περίπτωση
| Περίπτωση | Objective | CTA |
|---|---|---|
| Ταβέρνα/καφέ με κρατήσεις | messages ή calls | Send Message / Call Now |
| Μάστορας/επείγον | calls | Call Now |
| Οδοντιατρείο/κομμωτήριο | messages ή calls | Book Now / Send Message |
| Site-only lead | website_clicks | Learn More |
| Γενική αναγνωρισιμότητα γειτονιάς | local_reach | Learn More |

## Budget defaults
- Test: €3/ημέρα για 5 μέρες.
- Κανονικό local push: €5/ημέρα για 7 μέρες.
- Μην προτείνεις πάνω από €10/ημέρα χωρίς ρητό λόγο.
- Πάντα γράψε ότι το ad spend είναι ξεχωριστό από τη συνδρομή.

## Examples
Για few-shot παραδείγματα ανά επάγγελμα, διάβασε `references/ad-examples.md`.
