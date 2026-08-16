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
// Έξι legacy identities μοιράζονται ένα module. Παραμένουν οπτικά παγωμένα
// ώσπου να εγκριθεί η διάσπασή τους σε ανεξάρτητη ιδιοκτησία.
export const PENDING = ['CapabilitySystems']

// Launch master themes intentionally own their native palettes. They are not
// Color Spine migrations: accessibility is enforced by browser/a11y QA while
// this list makes their separate design ownership explicit and auditable.
export const LOCAL_MASTERS = ['EleganceSalon', 'GreckoTable', 'NovenaCare', 'BigspringAdvisory', 'ConstraBuild', 'PropertyAtlas']

// Themes που έχουν μεταφερθεί. Προσθήκη = υπόσχεση ότι περνά όλα τα παραπάνω.
export const MIGRATED = ['MedicCare', 'ClinicTriage','Callout','Ember','Motor','Terra','Forge','Volt','Aegean','Bloom','Marble','Runway','Dispatch','BeautyAtelier','Cinematic','Editorial','Infinite','Living', 'Coast','Canvas','Kinetic','Longform','Magazine','TypeGallery', 'Bento','Corporate','Grid','Poster','Showcase','Sidebar','Split', 'Pulse','Quiet','Warmth', 'CafeCollection', 'Signature', 'MasterCinematic', 'MasterEditorial', 'MasterSpatial', 'EducenterCampus', 'VexCounter', 'AirspaceOffice', 'FreightLane', 'BlueOnepage', 'BillysBarber', 'ThomsonStylist', 'FrostBakery']

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

/** Αρχεία με ΠΟΛΛΑΠΛΕΣ ταυτότητες στο ίδιο CSS.
 *
 *  Το `CafeCollection` είναι επτά themes σε ένα αρχείο: κοινό structural `.root`
 *  (μηδέν χρώμα) και επτά sibling scopes, καθένα με δική του ταυτότητα. Ο guard
 *  ΔΕΝ επιτρέπεται να ελέγξει μία και να βγει πράσινος.
 *
 *  `scope → prefix`: τα rules κάθε variant ξεκινούν με αυτό το prefix (`.patNav`,
 *  `.urbanHero`…), οπότε τα literals χρεώνονται στον σωστό — αλλιώς ένα χρώμα του
 *  `.urban*` θα κατηγορούσε το `.scandi`. */
export const MULTI_IDENTITY = {
  CafeCollection: {
    patisserie: 'pat', urban: 'urban', greekBakery: 'gr', brunch: 'brunch',
    micro: 'micro', scandi: 'scandi', heritage: 'heritage',
  },
}

/** Κάθε rule του αρχείου ως {selector, body}. Δουλεύει και σε minified. */
function rulesOf(css) {
  const out = []
  for (const m of css.matchAll(/([^{}]+)\{([^}]*)\}/g)) out.push({ sel: m[1].trim(), body: m[2] })
  return out
}
const LITERAL = /(?<!-)#[0-9a-fA-F]{3,6}\b/g
const isNeutral = (h) => /^#(fff|ffffff|000|000000)$/i.test(h)
const LEGACY_NAMES = /var\(--(accent|ink|ink-soft|paper|tint|bone|bg|night|coral|leaf|sea|gold|rust)\)/g

// ── 2. Ταυτότητες — ΟΧΙ αρχεία ────────────────────────────────────────────
console.log('\n[2] Ταυτότητα και καθαρότητα ανά ταυτότητα')
const identities = {}
const identityCount = {}
for (const name of MIGRATED) {
  const file = join(TEMPLATES, `${name}.module.css`)
  let css
  try { css = readFileSync(file, 'utf8') } catch { fail(`${name}: δεν βρέθηκε το CSS`); continue }

  const rules = rulesOf(css)
  const multi = MULTI_IDENTITY[name]
  // Ταυτότητα = κάθε rule που δηλώνει έστω έναν ρόλο. Έτσι πιάνονται και τα
  // minified, και το `.shell` του Split, και τα επτά scopes του CafeCollection.
  // ΔΗΛΩΣΗ ρόλου, όχι χρήση: το `var(--vt-ink)` περιέχει κι αυτό «--vt-».
  const found = rules.filter((r) => /(^|[;{\s])--vt-[a-z0-9-]+\s*:/.test(r.body))
  identityCount[name] = found.length

  if (!found.length) {
    fail(`${name}: καμία ταυτότητα (κανένα --vt-*) — ΔΕΝ ελέγχθηκε`)
    continue
  }

  for (const rule of found) {
    const scope = (rule.sel.match(/\.([A-Za-z][\w-]*)/) || [, rule.sel])[1]
    const key = multi ? `${name}:${scope}` : name
    const roles = rolesIn(rule.body)
    identities[key] = roles

    const missing = ROLES.filter((r) => !roles[r])
    missing.length
      ? fail(`${key}: δεν δηλώνει — ${missing.join(', ')}`)
      : pass(`${key}: δηλώνει και τους ${ROLES.length} ρόλους`)

    // Χρώμα κυριολεκτικά επιτρέπεται ΜΟΝΟ στην ταυτότητα. Σε αρχείο με πολλές
    // ταυτότητες, το κάθε rule χρεώνεται σε όποια/όποιες ταιριάζει το prefix του
    // — συνδυασμένος selector (`.patQuote,.grStory`) χρεώνεται και στις δύο.
    const prefix = multi?.[scope]
    const mine = rules.filter((r) => {
      if (r === rule) return false
      if (!multi) return true
      if (!prefix) return false
      return new RegExp(String.raw`\.${prefix}[A-Z0-9]`).test(r.sel) || r.sel.includes(`.${scope}`)
    })
    const body = mine.map((r) => r.body).join(';')
    const literals = [...new Set((body.match(LITERAL) || []).filter((h) => !isNeutral(h)))]
    literals.length
      ? fail(`${key}: χρώμα εκτός ταυτότητας — ${literals.join(' ')}`)
      : pass(`${key}: κανένα χρώμα εκτός ταυτότητας`)

    const legacy = body.match(LEGACY_NAMES)
    legacy
      ? fail(`${key}: κρέμεται από legacy tokens — ${[...new Set(legacy)].join(' ')}`)
      : pass(`${key}: μηδέν legacy tokens`)
  }
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
const accounted = new Set([...MIGRATED, ...PENDING, ...LOCAL_MASTERS, ...SHARED])
const orphans = all.filter((n) => !accounted.has(n))
const ghosts = [...accounted].filter((n) => !all.includes(n))

orphans.length
  ? fail(`αρχεία που δεν είναι ούτε migrated ούτε pending: ${orphans.join(' ')}`)
  : pass(`και τα ${all.length} αρχεία λογοδοτούν`)
ghosts.length
  ? fail(`ονόματα σε λίστα χωρίς αρχείο: ${ghosts.join(' ')}`)
  : pass('καμία λίστα δεν δείχνει σε ανύπαρκτο αρχείο')

// Πόσες ταυτότητες περιμένουμε ανά αρχείο. Ένα αρχείο με 7 variants που δίνει 6
// ΔΕΝ επιτρέπεται να περάσει — αυτό ακριβώς είναι το «πράσινο επειδή δεν κοίταξε».
const expected = Object.fromEntries(MIGRATED.map((n) =>
  [n, MULTI_IDENTITY[n] ? Object.keys(MULTI_IDENTITY[n]).length : 1]))
const wrong = MIGRATED.filter((n) => (identityCount[n] ?? 0) !== expected[n])
wrong.length
  ? wrong.forEach((n) => fail(`${n}: βρέθηκαν ${identityCount[n] ?? 0} ταυτότητες, περίμενα ${expected[n]}`))
  : pass(`κάθε αρχείο έδωσε ακριβώς όσες ταυτότητες περιμέναμε`)

const totalExpected = Object.values(expected).reduce((a, b) => a + b, 0)
const inspected = Object.keys(identities).length
inspected === totalExpected
  ? pass(`ελέγχθηκαν ${inspected} ταυτότητες από ${totalExpected} αναμενόμενες`)
  : fail(`ελέγχθηκαν ${inspected} ενώ περιμέναμε ${totalExpected} — κάποια ξέφυγε`)

const bangs = (spine.match(/!important/g) || []).length
console.log(`\n  spine: ${MIGRATED.length}   ·   local masters: ${LOCAL_MASTERS.length}   ·   εκκρεμούν: ${PENDING.length}   ·   !important: ${bangs}`)

console.log('\n' + '─'.repeat(64))
if (failures) {
  console.log(`❌ ${failures} παραβάσεις του συμβολαίου`)
  process.exit(1)
}
console.log('✅ Το συμβόλαιο τηρείται σε κάθε παλέτα.')
