// Κανένα theme δεν επιτρέπεται να τυπώνει πραγματολογικό ισχυρισμό ως σταθερό
// κείμενο. Ό,τι μπορεί να είναι ψέμα για κάποιον πελάτη πρέπει να έρχεται από
// τα δεδομένα του — αλλιώς το λέει σε ΟΛΟΥΣ.
//
// Γιατί υπάρχει: benchmark 13/8/2026. Το `Motor` έγραφε «✓ Γραπτή εγγύηση», το
// `Forge` «Εγγύηση σε κάθε εργασία», το `CafeCollection` «Depuis 2026» — σε κάθε
// πελάτη τους, ανεξάρτητα από το τι είχε δηλώσει. Κανένα test δεν τα έβλεπε.
//
// Ο έλεγχος κοιτάζει ΜΟΝΟ σταθερό κείμενο. Ένας ισχυρισμός μέσα σε `{d.X}` είναι
// δεδομένο του πελάτη και επιτρέπεται (π.χ. το `Callout` δείχνει «24/7» μόνο όταν
// το λένε οι ώρες που έδωσε ο ίδιος).
import { readdir, readFile } from 'node:fs/promises'

const DIR = new URL('../lib/templates/', import.meta.url)

// Κατηγορίες ισχυρισμού που απαιτούν απόδειξη (ίδιες με το src/truth_guard.py).
const CLAIMS = [
  ['εγγύηση', /εγγύησ\w*|εγγυημέν\w*|εγγυόμαστε/i],
  ['έτος ίδρυσης', /\b(?:depuis|since|est\.)\s*\d{2,4}\b|από\s+το\s+['’΄]?\s*\d{2,4}\b/i],
  ['χρόνια', /\b\d{1,3}\s*\+?\s*(?:χρόνι|χρόνων|ετών)\w*|δεκαετ(?:ία|ίες|ιών)/i],
  ['τιμή', /\b\d+[.,]?\d*\s*(?:€|ευρώ)\b/i],
  ['πιστοποίηση', /πιστοποι\w+|διαπιστευ\w+|certified/i],
  ['βραβείο', /βραβε(?:ίο|ία|υμέν)\w*/i],
  ['βαθμολογία', /\b\d(?:[.,]\d)?\s*\/\s*5\b|\bαστέρι\w*/i],
  ['κριτικές', /κριτικ(?:ή|ές|ών)\b|αξιολογήσ\w+/i],
  ['πλήθος', /\b\d{2,}\s*\+?\s*(?:πελάτ|έργα|ασθεν|projects)\w*/i],
  ['διαθεσιμότητα', /\b24\s*\/\s*7\b|\b24\s*ώρες\b/i],
  ['υπερθετικό', /\b(?:ο|η|το)\s+(?:καλύτερ|κορυφαί)\w*|\bΝο\.?\s*1\b|#1\b/i],
  ['ισχυρισμός προϊόντος', /επαγγελματικά\s+προϊόντα|premium\s+προϊόντα/i],
]

// Σταθερό κείμενο = ό,τι βλέπει ο επισκέπτης χωρίς να περάσει από `d.`:
//   >κείμενο<        JSX text node
//   'κείμενο'        literal σε πίνακα/μεταβλητή
// Τα σχόλια εξαιρούνται: εκεί ΠΡΕΠΕΙ να μπορούμε να γράψουμε γιατί κόπηκε κάτι.
function literals(src) {
  const noComments = src
    .replace(/\/\*[\s\S]*?\*\//g, ' ')
    .replace(/^[ \t]*\/\/.*$/gm, ' ')
    .replace(/\{\/\*[\s\S]*?\*\/\}/g, ' ')
  const out = []
  for (const m of noComments.matchAll(/>([^<>{}\n]{3,})</g)) out.push(m[1])
  for (const m of noComments.matchAll(/'([^'\n]{3,})'/g)) out.push(m[1])
  for (const m of noComments.matchAll(/`([^`$\n]{3,})`/g)) out.push(m[1])
  return out
}

// Εξαιρέσεις που ΑΠΟΔΕΙΚΝΥΟΝΤΑΙ, δεν δηλώνονται. Κάθε εγγραφή λέει ποια
// μεταβλητή φυλάει τον ισχυρισμό, και ο guard επαληθεύει ότι αυτή η μεταβλητή
// παράγεται όντως από δεδομένα του πελάτη (`d.`). Χωρίς την απόδειξη, αποτυγχάνει.
const DATA_BOUND = [{
  file: 'Callout.jsx',
  text: 'Τηλέφωνο βλάβης · 24/7',
  guard: 'always',
  why: 'Εμφανίζεται μόνο όταν οι ΔΗΛΩΜΕΝΕΣ ώρες του πελάτη λένε 24ωρη λειτουργία.',
}]

function isProvenDataBound(file, text, src) {
  const entry = DATA_BOUND.find((e) => e.file === file && text.includes(e.text))
  if (!entry) return false
  // Η μεταβλητή-φύλακας πρέπει να ορίζεται από `d.` στο ίδιο αρχείο…
  const def = new RegExp(`const\\s+${entry.guard}\\s*=[^\\n]*\\bd\\.`).test(src)
  // …και ο ισχυρισμός να είναι πράγματι υπό συνθήκη αυτής.
  const used = new RegExp(`${entry.guard}\\s*\\?`).test(src)
  return def && used
}

const files = (await readdir(DIR)).filter((f) => f.endsWith('.jsx'))
let failures = 0
let scanned = 0
let proven = 0

for (const file of files.sort()) {
  const src = await readFile(new URL(file, DIR), 'utf8')
  scanned++
  for (const text of literals(src)) {
    for (const [kind, pattern] of CLAIMS) {
      const hit = text.match(pattern)
      if (!hit) continue
      if (isProvenDataBound(file, text, src)) { proven++; continue }
      failures++
      console.log(`  ✗ ${file}: σταθερός ισχυρισμός «${kind}» → ${JSON.stringify(text.trim().slice(0, 70))}`)
    }
  }
}

// Coverage: αν δεν κοίταξε όσα αρχεία υπάρχουν, το πράσινο δεν σημαίνει τίποτα.
if (scanned !== files.length) {
  console.log(`  ✗ ελέγχθηκαν ${scanned} από ${files.length} αρχεία`)
  failures++
} else {
  console.log(`  ✓ ελέγχθηκαν ${scanned} templates × ${CLAIMS.length} κατηγορίες ισχυρισμού`)
  if (proven !== DATA_BOUND.length) {
    console.log(`  ✗ ${DATA_BOUND.length} δηλωμένες εξαιρέσεις αλλά ${proven} αποδείχθηκαν — μια εγγραφή είναι ξεπερασμένη`)
    failures++
  } else if (proven) console.log(`  ✓ ${proven} εξαίρεση αποδεδειγμένα data-bound`)
}

console.log('─'.repeat(60))
if (failures) {
  console.log(`❌ ${failures} σταθεροί ισχυρισμοί — δέσε τους σε δεδομένα πελάτη ή αφαίρεσέ τους`)
  process.exit(1)
}
console.log('✅ Κανένα theme δεν ισχυρίζεται κάτι εκ μέρους του πελάτη.')
