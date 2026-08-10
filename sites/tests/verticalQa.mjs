import assert from 'node:assert/strict'
import { mediaCategoryFor, withMediaFallback } from '../lib/mediaFallback.js'

const cases = [
  ['dentist-with-aesthetic-service', {
    TRADE: 'Οδοντιατρείο',
    services: [{ title: 'Αισθητική οδοντιατρική' }, { title: 'Θεραπείες' }],
  }, 'health', /1629909613654|1588776814546|1606811841689|1519494026892/],
  ['nail-studio', { TRADE: 'Νυχάδικο', services: [{ title: 'Μανικιούρ' }] }, 'beauty', null],
  ['cafe-not-food', { TRADE: 'Καφετέρια', services: [{ title: 'Brunch' }] }, 'cafe', null],
  ['taverna', { TRADE: 'Ταβέρνα', services: [{ title: 'Σχάρα' }] }, 'food', null],
  ['carpenter', { TRADE: 'Ξυλουργός', services: [{ title: 'Κουζίνες' }] }, 'carpenter', null],
  ['doctor', { TRADE: 'Ιατρείο', services: [{ title: 'Αισθητική θεραπεία' }] }, 'health', null],
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
