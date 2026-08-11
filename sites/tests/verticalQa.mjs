import assert from 'node:assert/strict'
import { mediaCategoryFor, withMediaFallback } from '../lib/mediaFallback.js'

const cases = [
  ['dentist-with-aesthetic-service', {
    TRADE: 'Οδοντιατρείο',
    services: [{ title: 'Αισθητική οδοντιατρική' }, { title: 'Θεραπείες' }],
  }, 'health', /1629909613654|1588776814546|1606811841689|1519494026892/],
  ['nail-studio', { TRADE: 'Νυχάδικο', services: [{ title: 'Μανικιούρ' }] }, 'nails', /1604654894610|1610992015732|1632345031435|1607779097040/],
  ['cafe-not-food', { TRADE: 'Καφετέρια', services: [{ title: 'Brunch' }] }, 'cafe', null],
  ['taverna', { TRADE: 'Ταβέρνα', services: [{ title: 'Σχάρα' }] }, 'food', null],
  ['carpenter', { TRADE: 'Ξυλουργός', services: [{ title: 'Κουζίνες' }] }, 'carpenter', null],
  ['doctor', { TRADE: 'Ιατρείο', services: [{ title: 'Αισθητική θεραπεία' }] }, 'health', null],
  ['aesthetics', { TRADE: 'Κέντρο αισθητικής', services: [{ title: 'Θεραπεία προσώπου' }] }, 'beauty', null],
  ['massage', { TRADE: 'Κέντρο μασάζ', services: [{ title: 'Spa σώματος' }] }, 'wellness', null],
  ['retail', { TRADE: 'Κατάστημα ρούχων', services: [{ title: 'Νέα συλλογή' }] }, 'retail', null],
  ['plumber', { TRADE: 'Υδραυλικός', services: [{ title: 'Επισκευές' }] }, 'technician', null],
  ['rooms', { TRADE: 'Ενοικιαζόμενα δωμάτια', services: [{ title: 'Διαμονή' }] }, 'hospitality', null],
  ['gym', { TRADE: 'Γυμναστήριο', services: [{ title: 'Personal training' }] }, 'gym', null],
  ['garage', { TRADE: 'Συνεργείο αυτοκινήτων', services: [{ title: 'Service' }] }, 'garage', null],
  ['farm', { TRADE: 'Παραγωγός ελαιολάδου', services: [{ title: 'Προϊόντα' }] }, 'farm', null],
  ['lawyer', { TRADE: 'Δικηγορικό γραφείο', services: [{ title: 'Συμβουλευτική' }] }, 'professional', null],
]

for (const [name, data, expected, allowedImages] of cases) {
  assert.equal(mediaCategoryFor(data), expected, `${name}: wrong media category`)
  const completed = withMediaFallback(data)
  assert.ok(completed.HERO_IMAGE, `${name}: missing hero fallback`)
  assert.ok(completed.gallery.length >= 3, `${name}: incomplete fallback gallery`)
  if (allowedImages) {
    for (const item of [completed.HERO_IMAGE, ...completed.gallery.map((x) => x.image)]) {
      assert.match(item, allowedImages, `${name}: unrelated fallback image ${item}`)
    }
  }
}

console.log(`verticalQa: ${cases.length} semantic media cases passed`)
