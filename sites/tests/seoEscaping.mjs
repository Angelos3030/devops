// Regression: το JSON-LD δεν επιτρέπεται να γίνει εκτελέσιμος κώδικας.
//
//   node tests/seoEscaping.mjs
//
// ΤΟ ΣΦΑΛΜΑ. Η σελίδα έγραφε `JSON.stringify(jsonLd)` μέσα σε <script>. Το
// `JSON.stringify` δεν διαφεύγει `<` — σωστά, δεν είναι δουλειά του. Αλλά ο
// HTML parser κόβει στο πρώτο `</script>` ΠΡΙΝ δει το JSON. Πελάτης που
// αποθήκευσε όνομα επιχείρησης «Καφέ</script><script>…</script>» πετύχαινε
// εκτέλεση κώδικα στο ΔΗΜΟΣΙΟ site του, σε κάθε επισκέπτη — αποδείχθηκε
// ζωντανά με πραγματικό PUT στο staging και render στον browser.
//
// Δύο πράγματα πρέπει να ισχύουν ΜΑΖΙ, γι' αυτό ελέγχονται μαζί: κανένα
// `</script>` στην έξοδο, ΚΑΙ το JSON να παραμένει έγκυρο — μια «διόρθωση»
// που σπάει το structured data κοστίζει local SEO σιωπηλά.
import { jsonLdScript } from '../lib/seo.js'

let failed = 0
const check = (name, cond, detail = '') => {
  if (!cond) { failed++; console.log(`  ✗ ${name}${detail ? '  ' + detail : ''}`) }
  else console.log(`  ✓ ${name}`)
}

const NASTY = [
  ['κλείσιμο script', 'Καφέ</script><script>window.x=1</script>'],
  ['πεζά-κεφαλαία', 'Α</ScRiPt><img src=x onerror=alert(1)>'],
  ['σχόλιο HTML', 'Β<!--<script>--><script>x</script>'],
  ['εισαγωγικά', 'Ο «Γιώργος» \'ο\' "καφές"'],
  ['ampersand', 'Ψητοπωλείο & Σία'],
  ['διαχωριστές γραμμής', `Καφέ  τέλος`],
  ['emoji + ελληνικά', '☕ Καφεκοπτείο Παπαδόπουλος 🇬🇷'],
  ['πολύ μεγάλο', 'Α'.repeat(5000)],
]

for (const [label, name] of NASTY) {
  const out = jsonLdScript({ '@type': 'LocalBusiness', name })
  check(`${label} — χωρίς </script>`, !/<\/script/i.test(out))
  check(`${label} — χωρίς ωμό <`, !out.includes('<'))
  let round
  try { round = JSON.parse(out) } catch (e) { round = null }
  check(`${label} — έγκυρο JSON`, round !== null)
  check(`${label} — ίδιο κείμενο πίσω`, round?.name === name,
    round ? '' : '(δεν έγινε parse)')
}

// U+2028/U+2029 είναι έγκυρα σε JSON αλλά τερματίζουν γραμμή στη JavaScript.
const sep = jsonLdScript({ name: ' ' })
check('U+2028 διαφεύγει', !sep.includes(' '))

console.log(failed ? `\n  ΑΠΟΤΥΧΙΕΣ: ${failed}` : '\n  όλα πέρασαν')
process.exit(failed ? 1 : 0)
