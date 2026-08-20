// Coverage assertion για την ΕΓΓΡΑΦΗ ενός theme, όχι για το χρώμα του.
//
// Γιατί υπάρχει: στις 13/8/2026 το `signature` μπήκε σε TEMPLATES και
// TEMPLATE_KEYS αλλά ΟΧΙ σε TEMPLATE_META. Κανένα test δεν το είδε — έσπασε το
// prerender της αρχικής με `Cannot read properties of undefined (reading
// 'label')`, δηλαδή το έπιασε το `next build` κατά τύχη. Λίγο νωρίτερα, τρία
// themes (`callout`, `dispatch`, `longform`) υπήρχαν παντού αλλά έλειπαν από τα
// vertical profiles, οπότε ΔΕΝ προτείνονταν ποτέ σε πελάτη και κανείς δεν το
// κατάλαβε για εβδομάδες.
//
// Κοινό μοτίβο: η εγγραφή είναι διάσπαρτη σε τέσσερα σημεία και η παράλειψη
// ενός είναι σιωπηλή. Εδώ γίνεται θορυβώδης.
//
// Ο έλεγχος ξεκινά από τα ΑΡΧΕΙΑ, όχι από τις λίστες: κάθε component στο
// lib/templates/ πρέπει είτε να είναι εγγεγραμμένο theme είτε να δηλωθεί ρητά
// ως βοηθητικό. Έτσι ένα καινούριο theme δεν μπορεί να «ξεχαστεί» — θα σκάσει.
import assert from 'node:assert/strict'
import { readFile, readdir } from 'node:fs/promises'

const url = (p) => new URL(p, import.meta.url)
const index = await readFile(url('../lib/templates/index.js'), 'utf8')

// Κοινά components που ΔΕΝ είναι themes. Κάθε προσθήκη εδώ είναι συνειδητή.
const SHARED = new Set([
  // Proof-only: renderable αλλά εκτός chooser μέχρι ανθρώπινη οπτική έγκριση.
  'MasterCinematic', 'MasterEditorial', 'MasterSpatial', 'CapabilitySystems','Brand', 'CallBar', 'FindUs', 'MapEmbed', 'MediaDisclosure', 'SocialLinks'])
// Themes που προσφέρονται αλλά δεν προτείνονται σε κανένα vertical, με λόγο.
const UNPROFILED = {
  'clean-work': 'Port worker proof — εκκρεμεί οπτική έγκριση πριν προταθεί σε πελάτη.',
  'klassy-cafe': 'Port worker proof — εκκρεμεί οπτική έγκριση πριν προταθεί σε πελάτη.',
  'barber-shop': 'Port worker proof — εκκρεμεί οπτική έγκριση πριν προταθεί σε πελάτη.',
  'villa-agency': 'Port worker proof — εκκρεμεί οπτική έγκριση πριν προταθεί σε πελάτη.',
  'gymso-fitness': 'Port worker proof — εκκρεμεί οπτική έγκριση πριν προταθεί σε πελάτη.',
  'medic-care': 'Port worker proof — εκκρεμεί οπτική έγκριση πριν προταθεί σε πελάτη.',
  'educenter-campus': 'Batch B — εκκρεμεί απόφαση chooser/ranking.',
  'vex-counter': 'Batch B — εκκρεμεί απόφαση chooser/ranking.',
  'airspace-office': 'Batch B — εκκρεμεί απόφαση chooser/ranking.',
  'freight-lane': 'Batch B — εκκρεμεί απόφαση chooser/ranking.',
  'blue-onepage': 'Salon batch — εκκρεμεί απόφαση chooser/ranking.',
  'billys-barber': 'Salon batch — εκκρεμεί απόφαση chooser/ranking.',
  'thomson-stylist': 'Salon batch — εκκρεμεί απόφαση chooser/ranking.',
  'frost-bakery': 'Port worker proof — εκκρεμεί οπτική έγκριση πριν προταθεί σε πελάτη.',

  dispatch: 'Πολύ ειδικό (courier/μεταφορές). Αφήνεται ρητά εκτός profiles αντί να '
    + 'μπει «κάπου» μόνο και μόνο για να μηδενίσει έναν μετρητή.',
}
// Renderable αλλά εκτός καταλόγου: υπάρχοντα sites τα χρησιμοποιούν ακόμη.
const RETIRED = new Set(['showcase', 'corporate', 'coast', 'pulse'])

const slice = (start) => {
  const i = index.indexOf(start)
  assert.notEqual(i, -1, `δεν βρέθηκε το ${start}`)
  return index.slice(i, index.indexOf('\nexport const', i + 1) + 1 || undefined)
}
const keysOf = (text) => [...text.matchAll(/(?:[{,]\s*)'?([a-z][a-z0-9-]*)'?\s*:/g)].map((m) => m[1])

const templates = new Set(keysOf(slice('export const TEMPLATES = {').split('\n')[0]))
const templateKeys = [...slice('export const TEMPLATE_KEYS = [').split('\n')[0].matchAll(/'([^']+)'/g)].map((m) => m[1])
const metaBlock = slice('export const TEMPLATE_META = {')
const meta = new Set([...metaBlock.matchAll(/^ {2}'?([a-z][a-z0-9-]*)'?\s*:\s*\{?/gm)].map((m) => m[1]))

const profileSource = await readFile(url('../lib/verticalProfiles.js'), 'utf8')
const profileUrl = `data:text/javascript;base64,${Buffer.from(profileSource).toString('base64')}`
const { DESIGN_SYSTEM_IDS, VERTICAL_PROFILES } = await import(profileUrl)

let checked = 0
const check = (name, fn) => { checked++; fn() }

// 1. Κάθε αρχείο component λογοδοτεί: ή theme ή δηλωμένο shared.
const files = (await readdir(url('../lib/templates')))
  .filter((f) => f.endsWith('.jsx')).map((f) => f.replace('.jsx', ''))
// Με ΔΙΑΔΡΟΜΗ, όχι με όνομα binding: το Grid εισάγεται ως `GridT` και το
// CafeCollection με named imports για τα 7 variants του.
const imported = new Set([...index.matchAll(/from '\.\/([A-Za-z]+)'/g)].map((m) => m[1]))
const orphans = files.filter((f) => !SHARED.has(f) && !imported.has(f))
check('files', () => assert.deepEqual(orphans, [],
  `components που δεν είναι ούτε theme ούτε δηλωμένα shared: ${orphans.join(' ')}`))

// 2. Κάθε key σε TEMPLATE_KEYS έχει component ΚΑΙ meta με label + desc.
for (const k of templateKeys) {
  check(k, () => {
    assert.ok(templates.has(k), `${k}: λείπει από TEMPLATES`)
    assert.ok(meta.has(k), `${k}: λείπει από TEMPLATE_META — η αρχική θα σπάσει στο prerender`)
    const body = metaBlock.slice(metaBlock.indexOf(`${k.includes('-') ? `'${k}'` : k}:`))
    assert.match(body.slice(0, 400), /label:\s*'[^']+'/, `${k}: meta χωρίς label`)
    assert.match(body.slice(0, 600), /desc:\s*'[^']+'/, `${k}: meta χωρίς desc`)
  })
}

// 3. Κάθε design system id δείχνει σε υπαρκτό theme (τυπογραφικό λάθος = σιωπή).
for (const id of DESIGN_SYSTEM_IDS) {
  check(id, () => assert.ok(templates.has(id), `DESIGN_SYSTEM_IDS: το '${id}' δεν αντιστοιχεί σε template`))
}

// 4. Κάθε theme ή προτείνεται κάπου ή έχει γραπτό λόγο που δεν προτείνεται.
const used = new Set(Object.values(VERTICAL_PROFILES).flatMap((p) => p.compatibleDesignSystemIds))
const silent = templateKeys.filter((k) => !used.has(k) && !UNPROFILED[k])
check('profiles', () => assert.deepEqual(silent, [],
  `themes που δεν προτείνονται πουθενά χωρίς δηλωμένο λόγο: ${silent.join(' ')}`))
const stale = Object.keys(UNPROFILED).filter((k) => used.has(k))
check('stale', () => assert.deepEqual(stale, [],
  `δηλώθηκαν ως μη-προτεινόμενα αλλά προτείνονται: ${stale.join(' ')}`))

// 5. Ό,τι είναι renderable αλλά εκτός καταλόγου, είναι δηλωμένα αποσυρμένο.
const offCatalog = [...templates].filter((k) => !templateKeys.includes(k))
check('retired', () => assert.deepEqual(offCatalog.filter((k) => !RETIRED.has(k)), [],
  `themes εκτός TEMPLATE_KEYS χωρίς δήλωση απόσυρσης: ${offCatalog.join(' ')}`))

// 6. Το ίδιο το coverage: αν ο έλεγχος δεν άγγιξε όσα περίμενε, αποτυγχάνει.
const expected = 4 + templateKeys.length + DESIGN_SYSTEM_IDS.length
assert.equal(checked, expected, `ελέγχθηκαν ${checked} ενώ περίμενα ${expected}`)

console.log(`templateRegistry: ${templateKeys.length} themes × 4 σημεία εγγραφής · ` +
  `${DESIGN_SYSTEM_IDS.length} design ids · ${files.length - SHARED.size} components · όλα λογοδοτούν`)
