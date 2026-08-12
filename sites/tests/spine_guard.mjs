/**
 * Vitrina Spine — ο φύλακας του συμβολαίου χρώματος.
 *
 *   node tests/spine_guard.mjs
 *
 * Γιατί υπάρχει: μετρήθηκε ότι 108 από τα 175 design tokens (62%) ήταν εκτός
 * εμβέλειας του palette layer — και τα ΝΕΟΤΕΡΑ themes ήταν οι χειρότεροι
 * παραβάτες. Δηλαδή η ασυνέπεια δεν ήταν παλιό χρέος· παραγόταν με κάθε νέο
 * theme. Χωρίς αυτόν τον έλεγχο, το επόμενο theme θα την ξαναπαρήγαγε.
 *
 * Ελέγχει τρία πράγματα:
 *   1. ΣΥΜΒΟΛΑΙΟ  — κάθε μεταφερμένο theme δηλώνει και τους έντεκα ρόλους
 *   2. ΚΑΘΑΡΟΤΗΤΑ — χρώμα κυριολεκτικά μόνο μέσα στο `.root` (η ταυτότητα)
 *   3. ΑΝΤΙΘΕΣΗ   — τα ζεύγη `on-` περνούν WCAG AA σε ΚΑΘΕ παλέτα, όχι μόνο
 *                   στην προεπιλεγμένη
 *
 * Ο (3) είναι ο λόγος που το συμβόλαιο αξίζει: το ίδιο accent μπορεί να είναι
 * μια χαρά ως φόντο κουμπιού και αδιάβαστο ως κείμενο. Μετρήθηκε: 6 στις 7
 * παλέτες απέτυχαν στο «accent πάνω σε σκούρα ζώνη» πριν μπει ο ρόλος.
 */
import { readFileSync, readdirSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const SPINE_CSS = join(ROOT, 'app/site/[client]/theme.module.css')
const TEMPLATES = join(ROOT, 'lib/templates')

export const ROLES = [
  'surface', 'surface-2', 'surface-deep',
  'ink', 'ink-soft', 'on-deep',
  'accent', 'on-accent', 'accent-ink', 'accent-on-deep',
  'line',
]

/** Ζεύγη που ΠΡΕΠΕΙ να διαβάζονται. [κείμενο, φόντο, ελάχιστο] */
const PAIRS = [
  ['ink', 'surface', 4.5],
  ['ink-soft', 'surface', 4.5],
  ['ink', 'surface-2', 4.5],
  ['ink-soft', 'surface-2', 4.5],
  ['on-accent', 'accent', 4.5],
  ['accent-ink', 'surface', 4.5],
  ['accent-ink', 'surface-2', 4.5],
  ['on-deep', 'surface-deep', 4.5],
  ['accent-on-deep', 'surface-deep', 4.5],
  // Οι γραμμές δεν είναι κείμενο. Το WCAG ζητά 3:1 μόνο για όρια στοιχείων
  // ελέγχου· οι διαχωριστικές γραμμές είναι διακριτικές εξ ορισμού. Το όριο
  // εδώ εγγυάται μόνο ότι η γραμμή ΦΑΙΝΕΤΑΙ. Όπου μια γραμμή οριοθετεί input
  // ή κουμπί, χρησιμοποίησε --vt-ink-soft, όχι --vt-line.
  ['line', 'surface', 1.2],
]

/** Ό,τι ΔΕΝ έχει μεταφερθεί ακόμη — ρητά, ώστε να μη γίνει αόρατο.
 *  Κάθε αρχείο πρέπει να είναι είτε εδώ είτε στο MIGRATED είτε κοινό component.
 *  Μεταφέρεις theme; Μετακίνησε το όνομα από εδώ εκεί — αλλιώς ο guard κόβει. */
export const PENDING = ['CafeCollection', 'Pulse', 'Quiet', 'Warmth']

// Themes που έχουν μεταφερθεί. Προσθήκη = υπόσχεση ότι περνά όλα τα παραπάνω.
export const MIGRATED = ['ClinicTriage','Callout','Ember','Motor','Terra','Forge','Volt','Aegean','Bloom','Marble','Runway','Dispatch','BeautyAtelier','Cinematic','Editorial','Infinite','Living', 'Coast','Canvas','Kinetic','Longform','Magazine','TypeGallery', 'Bento','Corporate','Grid','Poster','Showcase','Sidebar','Split']

const toRgb = (h) => {
  h = h.replace('#', '')
  if (h.length === 3) h = [...h].map((c) => c + c).join('')
  return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16))
}
const luminance = (rgb) => {
  const s = rgb.map((v) => {
    v /= 255
    return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4
  })
  return 0.2126 * s[0] + 0.7152 * s[1] + 0.0722 * s[2]
}
const contrast = (a, b) => {
  const [l1, l2] = [luminance(toRgb(a)), luminance(toRgb(b))]
  const [hi, lo] = l1 > l2 ? [l1, l2] : [l2, l1]
  return (hi + 0.05) / (lo + 0.05)
}

/** Όλοι οι ρόλοι ενός μπλοκ CSS, ως {role: hex}. */
function rolesIn(block) {
  const out = {}
  for (const m of block.matchAll(/--vt-([a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,8})/g)) out[m[1]] = m[2]
  return out
}

let failures = 0
const fail = (m) => { failures++; console.log(`  ✗ ${m}`) }
const pass = (m) => console.log(`  ✓ ${m}`)

// ── 1. Οι παλέτες ─────────────────────────────────────────────────────────
const spine = readFileSync(SPINE_CSS, 'utf8')
const palettes = {}
for (const m of spine.matchAll(/\.scope\[data-palette='([a-z]+)'\]\s*>\s*:first-child\s*\{([^}]*)\}/g)) {
  const found = rolesIn(m[2])
  if (Object.keys(found).length) palettes[m[1]] = { ...(palettes[m[1]] || {}), ...found }
}

console.log('\n[1] Παλέτες του spine')
if (!Object.keys(palettes).length) fail('δεν βρέθηκε καμία παλέτα')
for (const [name, roles] of Object.entries(palettes)) {
  const missing = ROLES.filter((r) => !roles[r])
  missing.length
    ? fail(`${name}: λείπουν ρόλοι — ${missing.join(', ')}`)
    : pass(`${name}: και οι ${ROLES.length} ρόλοι`)
}

// ── 2. Τα μεταφερμένα themes ──────────────────────────────────────────────
console.log('\n[2] Ταυτότητα και καθαρότητα ανά theme')
const identities = {}
for (const name of MIGRATED) {
  const file = join(TEMPLATES, `${name}.module.css`)
  let css
  try { css = readFileSync(file, 'utf8') } catch { fail(`${name}: δεν βρέθηκε το CSS`); continue }

  // Τρία templates είναι minified σε μία γραμμή: εκεί δεν υπάρχει «.root {» με
  // κενό. Ο guard πρέπει να διαβάζει ΚΑΙ τα minified, αλλιώς τα άφηνε έξω σιωπηλά
  // — και ένα theme εκτός συμβολαίου που «περνάει» είναι χειρότερο από ένα που κόβει.
  // Το `Split` χρησιμοποιεί `.shell` αντί για `.root`: δεχόμαστε και τα δύο, αλλά
  // αν δεν βρεθεί κανένα, ΚΟΒΟΥΜΕ αντί να συνεχίσουμε με άδειο μπλοκ.
  const start = css.search(/\.(root|shell)\s*\{/)
  if (start < 0) {
    fail(`${name}: δεν βρέθηκε μπλοκ ταυτότητας (.root/.shell) — δεν ελέγχθηκε`)
    continue
  }
  const end = css.indexOf('}', css.indexOf('{', start))
  const identity = rolesIn(css.slice(start, end))
  identities[name] = identity

  const missing = ROLES.filter((r) => !identity[r])
  missing.length
    ? fail(`${name}: δεν δηλώνει — ${missing.join(', ')}`)
    : pass(`${name}: δηλώνει και τους ${ROLES.length} ρόλους`)

  // Χρώμα κυριολεκτικά επιτρέπεται ΜΟΝΟ στην ταυτότητα. Οπουδήποτε αλλού
  // σημαίνει σημείο που δεν θα ακολουθήσει την παλέτα του πελάτη.
  const outside = css.slice(end)
  const literals = (outside.match(/(?<!-)#[0-9a-fA-F]{3,6}\b/g) || [])
    .filter((h) => !/^#(fff|ffffff|000|000000)$/i.test(h))
  literals.length
    ? fail(`${name}: χρώμα εκτός .root — ${[...new Set(literals)].join(' ')}`)
    : pass(`${name}: κανένα χρώμα εκτός ταυτότητας`)

  // Παλιά ονόματα σημαίνουν ότι το theme εξαρτάται ακόμη από τη legacy γέφυρα.
  const legacy = outside.match(/var\(--(accent|ink|ink-soft|paper|tint|bone|bg|night|coral|leaf|sea|gold|rust)\)/g)
  legacy
    ? fail(`${name}: κρέμεται από legacy tokens — ${[...new Set(legacy)].join(' ')}`)
    : pass(`${name}: μηδέν legacy tokens`)
}

// ── 3. Αντίθεση σε κάθε παλέτα × κάθε theme ───────────────────────────────
console.log('\n[3] Αντίθεση — κάθε ζεύγος, κάθε παλέτα')
const sets = { ...palettes }
for (const [name, identity] of Object.entries(identities)) sets[`${name} (original)`] = identity

let worst = { ratio: Infinity, where: '' }
for (const [setName, roles] of Object.entries(sets)) {
  const broken = []
  for (const [fg, bg, min] of PAIRS) {
    if (!roles[fg] || !roles[bg]) continue
    const r = contrast(roles[fg], roles[bg])
    if (r < min) broken.push(`${fg}/${bg} ${r.toFixed(2)}<${min}`)
    if (r < worst.ratio && min >= 4.5) worst = { ratio: r, where: `${setName} ${fg}/${bg}` }
  }
  broken.length ? fail(`${setName}: ${broken.join(' · ')}`) : pass(`${setName}: όλα τα ζεύγη περνούν`)
}
console.log(`\n  χαμηλότερη αντίθεση κειμένου: ${worst.ratio.toFixed(2)}:1 — ${worst.where}`)

// ── 4. COVERAGE — «πράσινο επειδή δεν κοίταξε» δεν επιτρέπεται ────────────
// Ο guard ήταν πράσινος ενώ τρία minified themes δεν είχαν ελεγχθεί ποτέ: δεν
// ήταν στη λίστα, άρα δεν υπήρχαν γι' αυτόν. Αυτό ήταν σοβαρότερο από τα ίδια
// τα σφάλματα αντίθεσης. Τώρα κάθε αρχείο πρέπει να είναι ΡΗΤΑ κάπου.
console.log('\n[4] Κάλυψη')
const SHARED = ['CallBar', 'FindUs', 'SocialLinks']   // κοινά components, όχι themes
const all = readdirSync(TEMPLATES).filter((f) => f.endsWith('.module.css'))
  .map((f) => f.replace('.module.css', ''))
const accounted = new Set([...MIGRATED, ...PENDING, ...SHARED])
const orphans = all.filter((n) => !accounted.has(n))
const ghosts = [...accounted].filter((n) => !all.includes(n))

orphans.length
  ? fail(`αρχεία που δεν είναι ούτε migrated ούτε pending: ${orphans.join(' ')}`)
  : pass(`και τα ${all.length} αρχεία λογοδοτούν`)
ghosts.length
  ? fail(`ονόματα σε λίστα χωρίς αρχείο: ${ghosts.join(' ')}`)
  : pass('καμία λίστα δεν δείχνει σε ανύπαρκτο αρχείο')

const inspected = Object.keys(identities).length
inspected === MIGRATED.length
  ? pass(`ελέγχθηκαν ${inspected} από ${MIGRATED.length} δηλωμένα`)
  : fail(`ελέγχθηκαν ${inspected} ενώ δηλώθηκαν ${MIGRATED.length} — κάποιο ξέφυγε`)

const bangs = (spine.match(/!important/g) || []).length
console.log(`\n  μεταφερμένα: ${MIGRATED.length}/${all.length - SHARED.length}   ·   εκκρεμούν: ${PENDING.length}   ·   !important: ${bangs}`)

console.log('\n' + '─'.repeat(64))
if (failures) {
  console.log(`❌ ${failures} παραβάσεις του συμβολαίου`)
  process.exit(1)
}
console.log('✅ Το συμβόλαιο τηρείται σε κάθε παλέτα.')
