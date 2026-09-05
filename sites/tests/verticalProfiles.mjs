import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

const source = await readFile(new URL('../lib/verticalProfiles.js', import.meta.url), 'utf8')
const moduleUrl = `data:text/javascript;base64,${Buffer.from(source).toString('base64')}`
const { DESIGN_SYSTEM_IDS, VERTICAL_PROFILES, getVerticalProfile, isDesignCompatible } = await import(moduleUrl)

const demoVerticals = [
  'carpenter', 'taverna', 'salon', 'dentist', 'physician', 'pharmacy', 'aesthetics', 'massage', 'cafe', 'retail', 'realestate', 'lawyer',
  'plumber', 'rooms', 'gym', 'garage', 'education', 'logistics', 'farm',
]
const allowedMotion = new Set(['restrained', 'moderate', 'expressive'])

assert.deepEqual(Object.keys(VERTICAL_PROFILES), [...demoVerticals, 'generic'])

for (const id of [...demoVerticals, 'generic']) {
  const item = VERTICAL_PROFILES[id]
  assert.equal(item.id, id)
  assert.ok(item.conversionGoal.primary)
  assert.ok(item.requiredSections.includes('hero'))
  assert.ok(item.requiredSections.includes('contact'))
  assert.ok(allowedMotion.has(item.motionIntensity))
  assert.ok(item.schemaType)
  assert.equal(typeof item.media.supportsNoPhoto, 'boolean')
  assert.ok(item.media.fallbackStrategy)
  assert.equal(item.compatibleDesignSystemIds.length, 12)
  assert.ok(item.compatibleDesignSystemIds.every((designId) => DESIGN_SYSTEM_IDS.includes(designId)))
  assert.ok(Object.isFrozen(item))
  assert.ok(Object.isFrozen(item.media))
}

assert.equal(getVerticalProfile('Ξυλουργικό Εργαστήριο').id, 'carpenter')
assert.equal(getVerticalProfile('ΟΔΟΝΤΙΑΤΡΕΙΟ').id, 'dentist')
assert.equal(getVerticalProfile('Ιατρείο').id, 'physician')
assert.equal(getVerticalProfile('Έχω φαρμακείο στον Γέρακα').id, 'pharmacy')
assert.equal(getVerticalProfile('Φαρμακείο Μαρία 15344').id, 'pharmacy')
assert.equal(getVerticalProfile('Οδοντιατρείο Μαρία στην Αθήνα').id, 'dentist')
assert.equal(getVerticalProfile('Καφετέρια στη Μάνη με brunch').id, 'cafe')
assert.equal(getVerticalProfile('Ξυλουργικό εργαστήριο με κουζίνες και ντουλάπες').id, 'carpenter')
assert.equal(getVerticalProfile('Κέντρο αισθητικής').id, 'aesthetics')
assert.equal(getVerticalProfile('Κέντρο μασάζ').id, 'massage')
assert.equal(getVerticalProfile('Ηλεκτρολόγος').id, 'plumber')
assert.equal(getVerticalProfile('Λογιστικό γραφείο').id, 'lawyer')
assert.equal(getVerticalProfile('Μεσιτικό γραφείο στον Βόλο').id, 'realestate')
assert.equal(getVerticalProfile('Παιδίατρος').id, 'physician')
assert.equal(getVerticalProfile('Barbershop').id, 'salon')
assert.equal(getVerticalProfile('Νυχάδικο').id, 'salon')
assert.equal(getVerticalProfile('Nail salon').id, 'salon')
assert.equal(getVerticalProfile('Αρτοποιείο').id, 'cafe')
assert.equal(getVerticalProfile('Κατάστημα ρούχων').id, 'retail')
assert.equal(getVerticalProfile('Ανθοπωλείο').id, 'retail')
assert.equal(getVerticalProfile('Βουλκανιζατέρ').id, 'garage')
assert.equal(getVerticalProfile('Οινοποιείο').id, 'farm')
assert.equal(getVerticalProfile('Φροντιστήριο ξένων γλωσσών').id, 'education')
assert.equal(getVerticalProfile('Μεταφορική και μετακομίσεις').id, 'logistics')
assert.equal(getVerticalProfile('Ξενώνας').id, 'rooms')
assert.equal(getVerticalProfile('unknown future vertical').id, 'generic')
assert.equal(isDesignCompatible('υδραυλικός', 'dispatch'), false)
assert.equal(isDesignCompatible('υδραυλικός', 'aegean'), false)
assert.equal(isDesignCompatible('φαρμακείο', 'runway'), false)
// Το reference-approved Service Area theme είναι πλέον το conversion-first
// anchor για τεχνίτες. Το callout παραμένει διαθέσιμο ως δεύτερη κατεύθυνση.
assert.equal(VERTICAL_PROFILES.plumber.compatibleDesignSystemIds[0], 'area-first')
assert.equal(isDesignCompatible('υδραυλικός', 'area-first'), true)
assert.equal(isDesignCompatible('υδραυλικός', 'callout'), true)
assert.equal(VERTICAL_PROFILES.retail.compatibleDesignSystemIds[0], 'bento')
assert.equal(VERTICAL_PROFILES.pharmacy.compatibleDesignSystemIds[0], 'quiet')
assert.equal(VERTICAL_PROFILES.rooms.media.supportsNoPhoto, false)

console.log(`verticalProfiles: ${demoVerticals.length} demo verticals + generic fallback passed`)
