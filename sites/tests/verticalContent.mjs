import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

const source = await readFile(new URL('../lib/demoData.js', import.meta.url), 'utf8')
const moduleUrl = `data:text/javascript;base64,${Buffer.from(source).toString('base64')}`
const { demoBusinesses } = await import(moduleUrl)

const requiredVerticals = [
  'carpenter', 'taverna', 'salon', 'dentist', 'physician', 'aesthetics', 'massage',
  'cafe', 'lawyer', 'plumber', 'rooms', 'gym', 'garage', 'farm',
]

assert.deepEqual(Object.keys(demoBusinesses), requiredVerticals)

for (const id of requiredVerticals) {
  const item = demoBusinesses[id]
  for (const key of ['NAME', 'CITY', 'TRADE', 'PHONE', 'PHONE_INTL', 'TAGLINE', 'STORY_TITLE', 'CTA_TITLE']) {
    assert.ok(item[key], `${id} is missing ${key}`)
  }
  assert.ok(item.services?.length >= 4, `${id} needs at least four services`)
  assert.ok(item.gallery?.length >= 3, `${id} needs at least three gallery items`)
  assert.ok(item.story?.length >= 2, `${id} needs at least two story paragraphs`)
  assert.ok(!JSON.stringify(item).includes('Lorem ipsum'), `${id} contains placeholder copy`)
}

for (const medical of ['dentist', 'physician']) {
  assert.match(demoBusinesses[medical].PRIMARY_CTA, /ραντεβού/i)
  assert.ok(demoBusinesses[medical].SERVICES_EYEBROW)
}
assert.match(demoBusinesses.aesthetics.PRIMARY_CTA, /διάγνωση/i)
assert.match(demoBusinesses.massage.PRIMARY_CTA, /συνεδρία/i)
assert.match(demoBusinesses.lawyer.PRIMARY_CTA, /συνάντηση/i)
assert.match(demoBusinesses.plumber.CTA_TITLE, /βλάβη|πάρε/i)

console.log(`verticalContent: ${requiredVerticals.length} complete demo businesses passed`)
