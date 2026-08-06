import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

const source = await readFile(new URL('../lib/verticalProfiles.js', import.meta.url), 'utf8')
const moduleUrl = `data:text/javascript;base64,${Buffer.from(source).toString('base64')}`
const { DESIGN_SYSTEM_IDS, VERTICAL_PROFILES, getVerticalProfile, isDesignCompatible } = await import(moduleUrl)

const demoVerticals = [
  'carpenter', 'taverna', 'salon', 'dentist', 'cafe', 'lawyer',
  'plumber', 'rooms', 'gym', 'garage', 'farm',
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
  assert.equal(item.compatibleDesignSystemIds.length, 9)
  assert.ok(item.compatibleDesignSystemIds.every((designId) => DESIGN_SYSTEM_IDS.includes(designId)))
  assert.ok(Object.isFrozen(item))
  assert.ok(Object.isFrozen(item.media))
}

assert.equal(getVerticalProfile('Ξυλουργικό Εργαστήριο').id, 'carpenter')
assert.equal(getVerticalProfile('ΟΔΟΝΤΙΑΤΡΕΙΟ').id, 'dentist')
assert.equal(getVerticalProfile('unknown future vertical').id, 'generic')
assert.equal(isDesignCompatible('υδραυλικός', 'dispatch'), true)
assert.equal(isDesignCompatible('υδραυλικός', 'aegean'), false)
assert.equal(VERTICAL_PROFILES.rooms.media.supportsNoPhoto, false)

console.log(`verticalProfiles: ${demoVerticals.length} demo verticals + generic fallback passed`)
