---
name: local-seo-gr
description: >
  Εφαρμόζει SEO best practices (ειδικά LOCAL SEO) σε ελληνικά websites μικρών
  επιχειρήσεων, ανά επάγγελμα. Χρησιμοποίησέ το σε ΚΑΘΕ site που φτιάχνεται —
  τίτλοι, meta, schema.org, λέξεις-κλειδιά «επάγγελμα + πόλη», Google Business.
---

# Local SEO για ελληνικά μικρομάγαζα

> Ο στόχος: όταν κάποιος ψάχνει «υδραυλικός Θεσσαλονίκη», να εμφανίζεται ο πελάτης μας.
> Αυτό εφαρμόζεται σε **κάθε** site, για **κάθε** επάγγελμα.

## 1. On-page SEO (σε κάθε σελίδα)
- **`<title>`:** `{Επάγγελμα/Όνομα} {Πόλη} | {υπηρεσία-κλειδί}`
  π.χ. «Υδραυλικός Θεσσαλονίκη | Άμεση Εξυπηρέτηση 24/7 — Παπαδόπουλος»
- **`<meta description>`:** 1 πρόταση με επάγγελμα + πόλη + USP + τηλέφωνο.
- **`<h1>` ένα ανά σελίδα**, με επάγγελμα + πόλη.
- **URL slugs** στα ελληνικά ή greeklish καθαρά (π.χ. `/ydravlikos-thessaloniki`).
- **Alt text** σε όλες τις εικόνες (περιγραφή + λέξη-κλειδί).
- **Lang:** `<html lang="el">`. Mobile-first (τα περισσότερα searches από κινητό).

## 2. Local SEO (το πιο σημαντικό για μικρομάγαζο)
- **Λέξεις-κλειδιά «επάγγελμα + περιοχή»** σε title, h1, κείμενα.
- **NAP συνέπεια:** Name, Address, Phone ίδια ΠΑΝΤΟΥ (site, Google, FB).
- **Google Business Profile** (πρώην Google My Business): φτιάξ' το/βελτιστοποίησέ το —
  είναι ό,τι πιο σημαντικό για τοπική αναζήτηση & Google Maps.
- **Περιοχές που καλύπτει** ως section (ιδίως μάστορες): «Εξυπηρετούμε: Καλαμαριά, Τούμπα…».
- **Χάρτης** (Google Maps embed) — σήμα τοποθεσίας.

## 3. Structured data (schema.org JSON-LD)
Βάλε JSON-LD ανάλογα με τον τύπο. Παραδείγματα τύπων:
- Γενικό: `LocalBusiness`
- Εστιατόριο/ταβέρνα: `Restaurant`
- Ιατρός/οδοντίατρος: `Dentist` / `MedicalBusiness`
- Δικηγόρος: `LegalService` / `Attorney`
- Λογιστής: `AccountingService`
- Μάστορας (υδραυλικός/ηλεκτρολόγος): `Plumber` / `Electrician` / `HomeAndConstructionBusiness`

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "{{SCHEMA_TYPE}}",
  "name": "{{NAME}}",
  "telephone": "{{PHONE}}",
  "address": { "@type": "PostalAddress", "streetAddress": "{{ADDRESS}}",
               "addressLocality": "{{CITY}}", "addressCountry": "GR" },
  "areaServed": "{{CITY}}",
  "openingHours": "{{HOURS}}",
  "url": "{{URL}}"
}
</script>
```

## 4. Τεχνικό SEO
- Γρήγορο site (static = ήδη γρήγορο ✅).
- HTTPS (Cloudflare/Netlify το δίνουν δωρεάν).
- `sitemap.xml` + `robots.txt`.
- Mobile responsive (υποχρεωτικό).
- Open Graph tags (για ωραίο preview όταν μοιράζεται σε FB/Viber).

## 5. Off-page (πες το στον πελάτη)
- Google Business Profile reviews (ζήτα από πελάτες αξιολογήσεις).
- Καταχώρηση σε ελληνικούς καταλόγους (vrisko.gr, χρυσός οδηγός κ.λπ.).
- Σύνδεση social με το site.

## Κανόνας
Κάθε site που βγαίνει ΠΡΕΠΕΙ να περνά αυτό το checklist. Το SEO δεν είναι extra —
είναι ο λόγος που το site έχει αξία (να σε βρίσκουν).

Δες `PRESETS.md` (στο greek-website) για τις λέξεις-κλειδιά & schema type ανά επάγγελμα.
