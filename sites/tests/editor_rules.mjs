#!/usr/bin/env node
/**
 * Κανόνες του editor — χωρίς browser, χωρίς δίκτυο, χωρίς εγγραφές.
 *
 *   node sites/tests/editor_rules.mjs
 *
 * Ελέγχει ό,τι μπορεί να ελεγχθεί ΠΡΙΝ στηθεί το staging Supabase: τα όρια που
 * βλέπει ο πελάτης πρέπει να ταιριάζουν με αυτά που επιβάλλει το backend.
 * Αν αποκλίνουν, ο πελάτης παίρνει «εντάξει» και μετά αποτυγχάνει το ανέβασμα.
 */
import {
  PHOTO_TYPES, MAX_PHOTO_MB, MAX_SERVICES,
  validatePhoto, canAddService, countEmptyServices,
  addService, setServiceField, removeService,
} from '../lib/editorRules.js'
import { readFileSync } from 'node:fs'

const pass = [], fail = []
const check = (ok, label, detail = '') => {
  ;(ok ? pass : fail).push(label)
  console.log(`  ${ok ? '✓' : '✗'} ${label}${detail ? `  — ${detail}` : ''}`)
}
const file = (type, mb) => ({ type, size: Math.round(mb * 1024 * 1024) })

console.log('\n[φωτογραφίες — αποδοχή]')
for (const t of PHOTO_TYPES) check(validatePhoto(file(t, 1)).ok, t)

console.log('\n[φωτογραφίες — απόρριψη με σαφές μήνυμα]')
const pdf = validatePhoto(file('application/pdf', 1))
check(!pdf.ok && /JPG/.test(pdf.error), 'PDF απορρίπτεται', pdf.error)
const heic = validatePhoto(file('image/heic', 1))
check(!heic.ok && /image\/heic/.test(heic.error), 'HEIC (iPhone) λέει τι έστειλε', heic.error)
const big = validatePhoto(file('image/jpeg', 12.4))
check(!big.ok && /12\.4MB/.test(big.error) && /10MB/.test(big.error),
      'υπερμεγέθης λέει ΚΑΙ το μέγεθος ΚΑΙ το όριο', big.error)
check(validatePhoto(file('image/jpeg', MAX_PHOTO_MB)).ok, 'ακριβώς στο όριο περνάει')
check(!validatePhoto(file('image/jpeg', MAX_PHOTO_MB + 0.001)).ok, 'λίγο πάνω κόβεται')
check(!validatePhoto(null).ok, 'κενό αρχείο')
const noType = validatePhoto(file('', 1))
check(!noType.ok && /άγνωστου τύπου/.test(noType.error), 'άγνωστος τύπος', noType.error)

console.log('\n[υπηρεσίες]')
let sv = []
for (let i = 0; i < MAX_SERVICES + 3; i += 1) sv = addService(sv)
check(sv.length === MAX_SERVICES, `το όριο κρατάει στις ${MAX_SERVICES}`, `${sv.length}`)
check(!canAddService(sv), 'το κουμπί κρύβεται στο όριο')
check(canAddService(sv.slice(0, 7)), 'με 7 επιτρέπεται ακόμα')

sv = [{ name: 'Α', description: '1' }, { name: 'Β', description: '2' }, { name: 'Γ', description: '3' }]
const edited = setServiceField(sv, 1, 'name', 'ΒΒ')
check(edited.map((x) => x.name).join('') === 'ΑΒΒΓ'.replace('ΒΒ', 'ΒΒ') || edited[1].name === 'ΒΒ',
      'επεξεργασία στη θέση')
check(edited[0].name === 'Α' && edited[2].name === 'Γ', 'η σειρά δεν αλλάζει')
check(edited[1].description === '2', 'το άλλο πεδίο μένει άθικτο')
check(sv[1].name === 'Β', 'ο αρχικός πίνακας δεν μεταλλάσσεται')

const afterDel = removeService(sv, 0)
check(afterDel.length === 2 && afterDel[0].name === 'Β', 'διαγραφή κρατά τη σειρά')
check(setServiceField(sv, 99, 'name', 'X').length === 3, 'άκυρος δείκτης δεν σπάει')

check(countEmptyServices([{ name: '' }, { name: '  ' }, { name: 'ok' }]) === 2,
      'μετράει τις κενές (και τα κενά διαστήματα)')
check(countEmptyServices([]) === 0, 'άδεια λίστα → 0')

console.log('\n[συμφωνία με το backend]')
// Το UI δεν πρέπει ΠΟΤΕ να υπόσχεται περισσότερα απ' όσα δέχεται το backend.
const mainPy = readFileSync(new URL('../../src/main.py', import.meta.url), 'utf8')
const metaPy = readFileSync(new URL('../../src/meta_oauth.py', import.meta.url), 'utf8')
check(new RegExp(`${MAX_PHOTO_MB} \\* 1024 \\* 1024`).test(mainPy),
      `το όριο ${MAX_PHOTO_MB}MB ταιριάζει με το src/main.py`)
for (const t of PHOTO_TYPES) {
  check(mainPy.includes(`"${t}"`), `το backend δέχεται ${t}`)
}
check(metaPy.includes(`][:${MAX_SERVICES}]`),
      `το όριο ${MAX_SERVICES} υπηρεσιών ταιριάζει με το src/meta_oauth.py`)
for (const f of ['email', 'facebook', 'instagram']) {
  check(new RegExp(`"${f}"`).test(metaPy), `το ${f} είναι στο allowlist του backend`)
}

console.log('\n[μητρώο templates — JS ↔ Python]')
// Το clinic-triage ήταν πρώτο στο verticalProfiles.js αλλά ΕΛΕΙΠΕ από το
// REACT_TEMPLATES της Python, που φιλτράρει τις προτάσεις. Αποτέλεσμα: το theme
// που φτιάχτηκε για οδοντιατρεία δεν προτεινόταν ΠΟΤΕ σε οδοντιατρείο.
const idx = readFileSync(new URL('../lib/templates/index.js', import.meta.url), 'utf8')
const gen = readFileSync(new URL('../../src/premium_generator.py', import.meta.url), 'utf8')
const jsKeys = [...idx.match(/export const TEMPLATE_KEYS = \[([^\]]+)\]/)[1]
  .matchAll(/'([^']+)'/g)].map((m) => m[1])
const pyKeys = [...gen.match(/REACT_TEMPLATES = \(([^)]+)\)/)[1]
  .matchAll(/"([^"]+)"/g)].map((m) => m[1])
const missingPy = jsKeys.filter((k) => !pyKeys.includes(k))
const missingJs = pyKeys.filter((k) => !jsKeys.includes(k))
check(missingPy.length === 0, `${jsKeys.length} templates δηλωμένα και στην Python`,
      missingPy.length ? `λείπουν: ${missingPy.join(', ')} — δεν θα προταθούν ΠΟΤΕ` : '')
check(missingJs.length === 0, 'κανένα template μόνο στην Python',
      missingJs.join(', '))

console.log(`\n${'='.repeat(56)}`)
console.log(`ΠΕΡΑΣΑΝ: ${pass.length}   ΕΣΠΑΣΑΝ: ${fail.length}`)
if (fail.length) { console.log('\n❌ ' + fail.join('\n   ')); process.exit(1) }
console.log('\n✅ Οι κανόνες του editor συμφωνούν με το backend.')
